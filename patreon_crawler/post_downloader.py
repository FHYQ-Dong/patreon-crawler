import os
import time
from threading import Thread

import requests

from patreon_crawler.patreon_data import PatreonPost, PatreonMedia


class PostDownloader:
    MAX_IN_FLIGHT = 10

    def __init__(self, download_dir: str):
        self.download_dir = download_dir
        self.num_in_flight = 0
        self.total_to_download = 0
        self.downloaded = 0
        self.queue: list[PatreonMedia] = []

        if not os.path.exists(self.download_dir):
            os.mkdir(self.download_dir)

    def download_media(self, media: PatreonMedia):
        def run():
            mime = media.mimetype.split("/")[-1]
            request = requests.get(media.url)
            download_file = f"{self.download_dir}/{media.id}.{mime}"
            with open(download_file, "wb") as file:
                file.write(request.content)

            self.downloaded += 1
            print(f"({self.downloaded} / {self.total_to_download}) Downloaded {media.id}.{mime} from {media.url}")

        try:
            run()
        except Exception as e:
            print(f"Failed to download {media.id}: {e}")
        finally:
            self.num_in_flight -= 1
            self.process_queue()

    def process_queue(self):
        while self.queue and self.num_in_flight < self.MAX_IN_FLIGHT:
            self.num_in_flight += 1
            media = self.queue.pop(0)
            thread = Thread(target=self.download_media, args=(media,))
            thread.start()

    def download(self, posts: list[PatreonPost]):

        medias = [media for post in posts for media in post.media]
        self.queue.extend(medias)
        self.total_to_download += len(medias)

        print(f"Enqueued {len(medias)} downloads")
        self.process_queue()

    def wait_finish(self):
        while self.num_in_flight > 0:
            time.sleep(1)
        print("Download finished")
