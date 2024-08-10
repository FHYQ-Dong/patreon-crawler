import os
import time
from dataclasses import dataclass
from threading import Thread

import requests
from pathvalidate import sanitize_filename

from patreon_crawler.crawler_config import PostGroupingStrategy
from patreon_crawler.patreon_data import PatreonPost, PatreonMedia


@dataclass
class _QueueItem:
    media: PatreonMedia
    directory: str


class PostDownloader:
    _DEFAULT_MAX_IN_FLIGHT = 10

    @property
    def max_in_flight(self):
        return self._max_in_flight or self._DEFAULT_MAX_IN_FLIGHT

    def __init__(self, download_dir: str, max_in_flight: int = _DEFAULT_MAX_IN_FLIGHT,
                 grouping_strategy: PostGroupingStrategy = "dynamic"):
        self.download_dir = download_dir
        self.grouping_strategy = grouping_strategy
        self._max_in_flight = max_in_flight
        self.num_in_flight = 0
        self.total_to_download = 0
        self.downloaded = 0
        self.queue: list[_QueueItem] = []

        if not os.path.exists(self.download_dir):
            os.mkdir(self.download_dir)

    def _get_post_download_directory(self, post: PatreonPost) -> str:
        post_title = sanitize_filename(post.title)

        match self.grouping_strategy:
            case "none":
                return self.download_dir
            case "all":
                return f"{self.download_dir}/{post_title}"
            case "dynamic":
                if len(post.media) > 1:
                    return f"{self.download_dir}/{post_title}"
                return self.download_dir

    def download_media(self, media: PatreonMedia, directory: str):
        def run():
            if not os.path.exists(directory):
                os.mkdir(directory)

            mime = media.mimetype.split("/")[-1]
            request = requests.get(media.url)
            download_file = f"{directory}/{media.id}.{mime}"
            with open(download_file, "wb") as file:
                file.write(request.content)

            self.downloaded += 1
            print(f"({self.downloaded} / {self.total_to_download}) Downloaded {media.id}.{mime}")

        try:
            run()
        except Exception as e:
            print(f"Failed to download {media.id}: {e}")
        finally:
            self.num_in_flight -= 1
            self.process_queue()

    def process_queue(self):
        while self.queue and self.num_in_flight < self.max_in_flight:
            self.num_in_flight += 1
            next_item = self.queue.pop(0)
            thread = Thread(target=self.download_media, args=(next_item.media, next_item.directory), daemon=True)
            thread.start()

    def download(self, posts: list[PatreonPost]):
        queue_items: list[_QueueItem] = []

        for post in posts:
            directory = self._get_post_download_directory(post)

            for media in post.media:
                queue_items.append(_QueueItem(media, directory))

        self.queue.extend(queue_items)
        self.total_to_download += len(queue_items)

        print(f"Enqueued {len(queue_items)} downloads from {len(posts)} posts")
        self.process_queue()

    def wait_finish(self):
        while self.num_in_flight > 0:
            time.sleep(1)
        print("Download finished")
