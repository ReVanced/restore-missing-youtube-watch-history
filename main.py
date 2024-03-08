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

logger: logging.Logger = logging.getLogger()


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

    # Filter and keep relevant video events
    kept: list[dict[str, Any]] = await filter_video_events(data, RESUME_TIMESTAMP)

    logger.info(f"Found {len(kept)} videos to watch")

    # Deduplicate video events based on URL
    kept = await deduplicate_videos(kept)

    logger.info(f"Found {len(kept)} videos to watch after de-duplication")

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

    logger.info(f"Marking {len(urls)} videos as watched. Please wait...")

    with yt_dlp.YoutubeDL(opts) as ydl:
        with ThreadPoolExecutor() as _:
            loop = asyncio.get_running_loop()
            tasks = map(
                lambda url: worker(
                    url=url,
                    semaphore=semaphore,
                    max_retries=MAX_RETRIES,
                    ytdlp_downloader=ydl.download,
                    loop=loop,
                ),
                urls,
            )
            _: list[Any] = await asyncio.gather(*tasks)

    logger.info("All videos have been marked as watched.")


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

    valid_events = list(filter(is_valid_event, data))

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
    unique_events = {event["titleUrl"]: event for event in events}.values()

    yield list(unique_events)


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
        async with open("execution_history.log", "r+") as f:
            processed: list[str] = [line.rstrip() for line in await f.readlines()]

            if url in processed:
                logger.info(f"URL {url} has already been processed. Skipping...")
                return

            for attempt in range(max_retries):
                try:
                    result: Any = await loop.run_in_executor(
                        None, lambda: ytdlp_downloader(url)
                    )
                    break
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts.")
                        result = None
                        break

            await f.write(url + "\n")
            await asyncio.sleep(random.uniform(1, 3))

            return result


if __name__ == "__main__":
    asyncio.run(main())
