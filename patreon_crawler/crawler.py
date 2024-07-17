import re

import requests

from patreon_crawler.cookie_extractor import get_cookies
from patreon_crawler.crawler_config import CrawlerConfig
from patreon_crawler.patreon_data import PatreonData, PatreonPost
from patreon_crawler.post_downloader import PostDownloader

_PATREON_CAMPAIGN_REGEX = r"patreon-media\/p\/campaign\/(\d+)\/."


class PatreonCrawler:
    _default_request_query = {
        "include": "attachments,images,media",
        "fields[post]": "teaser_text,current_user_can_view,post_metadata,published_at,post_type,title,url,view_count",
        "fields[media]": "id,image_urls,download_url,metadata,mimetype,name,size_bytes",
        "filter[contains_exclusive_posts]": "true",
        "filter[is_draft]": "false",
        "sort": "-published_at",
        "json-api-version": "1.0"
    }
    _patreon_api_url = "https://www.patreon.com/api/posts"

    @property
    def _patreon_url(self) -> str:
        return f"https://www.patreon.com/{self._config.creator}"

    @property
    def _cookie(self) -> str:
        return "; ".join([f"{k}={v}" for k, v in self._config.cookies.items()])

    @property
    def _total_accessible_posts(self) -> int:
        return self._total_posts - self._num_posts_inaccessible

    def __init__(self, config: CrawlerConfig) -> None:
        self._config = config
        self._next_cursor: str | None = None
        self._num_posts_inaccessible: int = 0
        self._total_posts: int = 0
        self.campaign_id: str = self._get_campaign_id()
        self.loaded_posts: list[PatreonPost] = []
        self.downloader = PostDownloader(f"{config.download_dir}/{config.creator}")

    def _load_next_page(self) -> bool:
        url = self._build_url(self._next_cursor)
        request = requests.get(url, headers={"Cookie": self._cookie})
        response = PatreonData.from_json(request.json())

        posts = []
        for post in response.posts:
            if post.current_user_can_view:
                posts.append(post)
            else:
                print(f"Ignoring post {post.title}, as it is inaccessible")

        self._num_posts_inaccessible += len(response.posts) - len(posts)

        self.loaded_posts.extend(response.posts)
        self._total_posts = response.total_posts
        self._next_cursor = response.cursor_next

        return self._next_cursor is not None

    def _get_campaign_id(self) -> str:
        request = requests.get(self._patreon_url)
        campaign_id = re.search(_PATREON_CAMPAIGN_REGEX, request.text).group(1)
        return campaign_id

    def _build_url(self, cursor: str | None = None):
        mod_filter = {
            **self._default_request_query,
            "filter[campaign_id]": self.campaign_id
        }

        if cursor:
            mod_filter["page[cursor]"] = cursor

        return f"{self._patreon_api_url}?{'&'.join([f'{k}={v}' for k, v in mod_filter.items()])}"

    def load(self) -> None:
        while self._load_next_page():
            print(f"Loaded {len(self.loaded_posts)} / {self._total_accessible_posts} posts")
        print(f"Loaded {len(self.loaded_posts)} / {self._total_accessible_posts} posts")

    def download(self) -> None:
        self.downloader.download(self.loaded_posts)
        self.downloader.wait_finish()

    def run(self) -> None:
        self.load()
        self.download()


