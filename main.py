import os
import time
import json
import random
import hashlib
import argparse
from typing import Any
from pathlib import Path

import yt_dlp

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


def main():
    """
    Process and download videos from YouTube watch history.

    Args:
        --watch_history_file (str): Path to the watch history JSON file.
        --done_directory (str): Directory to save downloaded videos marker.
        --resume_timestamp (str): Timestamp to resume from (ISO 8601 format).
        --sleep_min (float): Minimum sleep duration in seconds.
        --sleep_max (float): Maximum sleep duration in seconds.
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
        "--done_directory",
        type=Path,
        default=Path("./done"),
        help="Directory to save downloaded videos marker.",
    )
    parser.add_argument(
        "--resume_timestamp",
        type=str,
        default="2022-08-17T11:50:00.000Z",
        help="Timestamp to resume from (ISO 8601 format).",
    )
    parser.add_argument(
        "--sleep_min",
        type=float,
        default=1,
        help="Minimum sleep duration in seconds.",
    )
    parser.add_argument(
        "--sleep_max",
        type=float,
        default=2,
        help="Maximum sleep duration in seconds.",
    )
    parser.add_argument(
        "--removeshorts",
        type=bool,
        default=False,
        help="To remove shorts from history.",
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--cookiesfrombrowser",
        type=str,
        default="chrome",
        choices=VALID_BROWSERS,
        help="Browser to use for cookies.",
    )

    group.add_argument(
        "--cookiefile",
        type=str,
        default=None,
        help="Path of netscaped cookie file.",
    )

    args = parser.parse_args()

    # Use the arguments as Path objects
    WATCH_HISTORY_FILE = args.watch_history_file
    DONE_DIRECTORY = args.done_directory
    RESUME_TIMESTAMP = args.resume_timestamp
    SLEEP_MIN = args.sleep_min
    SLEEP_MAX = args.sleep_max
    COOKIES_FROM_BROWSER = args.cookiesfrombrowser
    COOKIE_FILE = args.cookiefile
    REMOVE_SHORTS = args.removeshorts

    # Create 'done' directory if not exists
    DONE_DIRECTORY.mkdir(parents=True, exist_ok=True)

    # Load watch history data
    with WATCH_HISTORY_FILE.open(encoding="utf8") as f:
        data = json.load(f)

    if REMOVE_SHORTS is True:
        removed = 0
        for index in reversed(range(len(data))):
            if data[index]["title"].lower().find("#short") > 0:
                data.pop(index)
                print(f"Removed: {data[index]['title']}")
                removed += 1
        print(f"Total shorts removed {removed}")

    # Filter and keep relevant video events
    kept: list[dict[str, Any]] = filter_video_events(data, RESUME_TIMESTAMP)

    print(f"Found {len(kept)} videos to watch")

    # Deduplicate video events based on URL
    kept = deduplicate_videos(kept)

    print(f"Found {len(kept)} videos to watch after de-duplication")

    # Sort videos based on timestamp
    kept.sort(key=lambda x: x["time"])

    # Download videos
    download_videos(kept, DONE_DIRECTORY, SLEEP_MIN,
                    SLEEP_MAX, COOKIES_FROM_BROWSER, COOKIE_FILE)


def filter_video_events(
    data: list[dict[str, Any]], RESUME_TIMESTAMP: str
) -> list[dict[str, Any]]:
    """
    Filter video events from the provided data.

    Args:
        data: A list of events.

    Returns:
        A list of filtered video events.
    """
    filtered_events: list[dict[str, Any]] = []

    for event in data:
        if event.get("header") != "YouTube":
            continue
        if "details" in event and event["details"][0]["name"] == "From Google Ads":
            continue
        if event["time"] < RESUME_TIMESTAMP:
            continue
        if "titleUrl" not in event:
            continue
        filtered_events.append(event)

    return filtered_events


def deduplicate_videos(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Deduplicate video events based on URL.

    Args:
        events: A list of video events.

    Returns:
        A list of deduplicated video events.
    """
    unique_events = {event["titleUrl"]: event for event in events}.values()
    return list(unique_events)


def download_videos(
    events: list[dict[str, Any]],
    DONE_DIRECTORY: Path,
    SLEEP_MIN: float,
    SLEEP_MAX: float,
    COOKIES_FROM_BROWSER: str,
    COOKIE_FILE: str,
):
    """
    Download videos from the provided list of events.

    Args:
        events: list of video events to download.
    """
    opts = {
        "mark_watched": True,
        "simulate": True,
        "quiet": True,
        "cookiesfrombrowser": (COOKIES_FROM_BROWSER,),
        "cookiefile": COOKIE_FILE,
        "format": "worstaudio",
    }

    if COOKIE_FILE != None:
        opts.pop("cookiesfrombrowser")
    else:
        opts.pop("cookiefile")

    with yt_dlp.YoutubeDL(opts) as ydl:
        for i, event in enumerate(events):
            timestamp = event["time"]
            url = event["titleUrl"]
            title = event["title"][8:]

            marker_path = os.path.join(
                DONE_DIRECTORY, hashlib.sha256(url.encode("utf-8")).hexdigest()
            )

            print(
                f"{i}/{len(events)} \t {timestamp} \t {url} \t {title} ... ",
                end="",
                flush=True,
            )

            if os.path.exists(marker_path):
                print(" -> Already done")
                continue

            try:
                ydl.download(url)
                print(" -> Sleeping ... ", end="", flush=True)
                time.sleep(SLEEP_MIN + random.random()
                           * (SLEEP_MAX - SLEEP_MIN))
                print(" -> Done")
            except yt_dlp.utils.DownloadError:
                print(" -> DownloadError")

            with open(marker_path, "w"):
                pass


if __name__ == "__main__":
    main()
