import sys
import json
import random
import yt_dlp
import asyncio
import logging
import aiofiles
import argparse
from pathlib import Path
from typing import Any, AsyncGenerator
from concurrent.futures import ThreadPoolExecutor
from tqdm.asyncio import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

VALID_BROWSERS = (
    "brave",
    "chrome",
    "chromium",
    "edge",
    "firefox",
    "opera",
    "safari",
    "vivaldi",
)

# Set up logging
log_formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)

file_handler = logging.FileHandler("execution.log")
file_handler.setFormatter(log_formatter)

logger: logging.Logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

async def main():
    """
    Process and download videos from YouTube watch history.

    Args:
        --watch_history_file (str): Path to the watch history JSON file.
        --resume_timestamp (str): Timestamp to resume from (ISO 8601 format).
        --concurrency (int): Number of concurrent downloads.
        --max_retries (int): Number of retries for each video.
        --cookiesfrombrowser (str): The name of the browser from where cookies are loaded.
        --cookiefile (str): File name or text stream from where cookies should be read and dumped to.
    """

    parser = argparse.ArgumentParser(
        description="Process and download videos from YouTube watch history."
    )

    parser.add_argument(
        "--watch_history_file",
        type=Path,
        default=Path("./watch-history.json"),
        help="Path to the watch history JSON file.",
    )

    parser.add_argument(
        "--resume_timestamp",
        type=str,
        default="2022-08-17T11:50:00.000Z",
        help="Timestamp to resume from (ISO 8601 format).",
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Number of concurrent downloads.",
    )

    parser.add_argument(
        "--max_retries",
        type=int,
        default=3,
        help="Number of retries for each video.",
    )

    group: argparse._MutuallyExclusiveGroup = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--cookiesfrombrowser",
        type=str,
        default="chrome",
        choices=VALID_BROWSERS,
        help="The name of the browser from where cookies are loaded",
    )

    group.add_argument(
        "--cookiefile",
        type=Path,
        default=None,
        help="File name or text stream from where cookies should be read and dumped to.",
    )

    args = parser.parse_args()

    # Use the arguments as Path objects
    WATCH_HISTORY_FILE: Path = args.watch_history_file
    RESUME_TIMESTAMP: str = args.resume_timestamp
    COOKIES_FROM_BROWSER: str = args.cookiesfrombrowser
    COOKIE_FILE: Path = args.cookiefile
    CONCURRENCY: float = args.concurrency
    MAX_RETRIES: float = args.max_retries

    # Load watch history data
    with WATCH_HISTORY_FILE.open(encoding="utf8") as f:
        data = json.load(f)
        # Remove shorts to avoid the error 400
        data = list(filter(is_not_short, data))

    # Filter and keep relevant video events
    kept: list[dict[str, Any]] = [
        event async for event in filter_video_events(data, RESUME_TIMESTAMP)
    ]

    # Deduplicate video events based on URL
    kept = [unique async for unique in deduplicate_videos(kept)][0]

    logger.info(f"Found {len(kept)} videos to mark as watched.")

    # Sort videos based on timestamp
    kept.sort(key=lambda x: x["time"])

    semaphore = asyncio.Semaphore(CONCURRENCY)

    opts = {
        "mark_watched": True,
        "simulate": True,
        "quiet": True,
        "cookiesfrombrowser": (COOKIES_FROM_BROWSER,),
        "cookiefile": COOKIE_FILE,
        "format": "worstaudio",
    }

    if COOKIE_FILE:
        opts.pop("cookiesfrombrowser")
    else:
        opts.pop("cookiefile")

    urls = [video["titleUrl"] for video in kept if "titleUrl" in video]

    async with aiofiles.open("history.log", "a+") as h_file:
        await h_file.seek(0)
        processed: list[str] = [line.rstrip() for line in await h_file.readlines()]

    async with aiofiles.open("failed.log", "a+") as f_file:
        await f_file.seek(0)
        failed: list[str] = [line.rstrip() for line in await f_file.readlines()]

        urls = list(set(urls) - set(processed + failed))
        logger.info(f"{len(processed)} URL has already been processed. Skipping...")

    logger.info(f"Marking {len(urls)} videos as watched. Please wait...")

    tasks = []
    queue = asyncio.Queue()

    for url in urls:
        await queue.put(url)

    with yt_dlp.YoutubeDL(opts) as ydl:
        with ThreadPoolExecutor() as _:
            loop = asyncio.get_running_loop()
            pbar = tqdm(total=len(urls), desc="Precessed: ")

            for _ in range(CONCURRENCY):
                task = asyncio.create_task(
                    worker_task(
                        semaphore,
                        queue,
                        MAX_RETRIES,
                        ydl.download,
                        loop,
                        pbar,
                    )
                )

                tasks.append(task)
                # print(f"total task {len(tasks)}")

            _: list[Any] = await asyncio.gather(*tasks)
            pbar.close()

    logger.info("All videos have been marked as watched.")


def is_not_short(item) -> bool:
    """
    Checks if the given item is not a short video.

    Args:
        item (dict): The item to check.

    Returns:
        bool: True if the item is not a short video, False otherwise.
    """
    return item["title"].lower().find("short") == -1


async def filter_video_events(
    data: list[dict[str, Any]], RESUME_TIMESTAMP: str
) -> AsyncGenerator[list[dict[str, Any]], None]:
    """
    Filters video events based on certain conditions.

    Args:
        data (list[dict[str, Any]]): The list of video events to filter.
        RESUME_TIMESTAMP (str): The timestamp to compare against.

    Yields:
        AsyncGenerator[list[dict[str, Any]], None]: A generator that yields the filtered video events.

    """

    def is_valid_event(event: dict[str, Any]) -> bool:
        match event:
            case {
                "header": header,
                "time": time,
            } if header != "YouTube" or time < RESUME_TIMESTAMP:
                return False
            case {"details": [{"name": "From Google Ads"}]}:
                return False
            case {"titleUrl": _}:
                return True
            case _:
                return False

    valid_events = filter(is_valid_event, data)

    yield valid_events


async def deduplicate_videos(
    events: list[dict[str, Any]]
) -> AsyncGenerator[list[dict[str, Any]], None]:
    """
    Deduplicates a list of video events based on their title URL.

    Args:
        events (list[dict[str, Any]]): A list of video events, where each event is a dictionary.

    Yields:
        AsyncGenerator[list[dict[str, Any]], None]: An asynchronous generator that yields a list of deduplicated video events.

    """
    unique_events = list({event["titleUrl"]: event for event in events[0]}.values())

    yield unique_events


async def worker_task(semaphore, queue, max_retries, ytdlp_downloader, loop, pbar):
    """
    A task that processes URLs from a queue and calls the worker function to perform the actual work.

    Args:
        semaphore (asyncio.Semaphore): A semaphore used to limit the number of concurrent workers.
        queue (asyncio.Queue): A queue containing the URLs to be processed.
        max_retries (int): The maximum number of retries for each URL.
        ytdlp_downloader (YtdlpDownloader): An instance of the YtdlpDownloader class.
        loop (asyncio.AbstractEventLoop): The event loop to run the task on.
    """
    while not queue.empty():
        url = await queue.get()

        await worker(url, semaphore, max_retries, ytdlp_downloader, loop)
        pbar.update(1)
        queue.task_done()


async def worker(
    url: str,
    semaphore: asyncio.Semaphore,
    max_retries: int,
    ytdlp_downloader: callable,
    loop: asyncio.AbstractEventLoop,
) -> Any:
    """
    Executes a work function asynchronously with a semaphore.

    Args:
        url (str): The URL to be processed.
        semaphore (asyncio.Semaphore): The semaphore to limit the number of concurrent workers.
        max_retries (int): The maximum number of retries for the work function.
        ytdlp_downloader (callable): a callable ref to the yt_dlp.YoutubeDL.download() method.
        loop (asyncio.AbstractEventLoop): The event loop to run the work function.

    Returns:
        Any: The result of the work function.

    """
    async with semaphore:
        async with aiofiles.open("history.log", "a+") as f:
            await f.seek(0)

            for attempt in range(max_retries):
                try:
                    result: Any = await loop.run_in_executor(
                        None, lambda: ytdlp_downloader(url)
                    )
                    await f.write(url + "\n")
                    break
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    if attempt == max_retries - 1:
                        async with aiofiles.open("failed.log", "a+") as f_file:
                            await f_file.seek(0)
                            await f_file.write(url + "\n")
                            logger.error(f"Failed after {max_retries} attempts.")
                            result = None
                            break
        await asyncio.sleep(random.uniform(1, 3))
        logger.info(f"Processed URL: {url}.")
        return result


if __name__ == "__main__":
    with logging_redirect_tqdm():
        asyncio.run(main())
