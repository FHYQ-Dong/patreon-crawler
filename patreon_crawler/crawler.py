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
        "fields[post]": "change_visibility_at,comment_count,commenter_count,content,current_user_can_comment,current_user_can_delete,current_user_can_report,current_user_can_view,current_user_comment_disallowed_reason,current_user_has_liked,embed,image,impression_count,insights_last_updated_at,is_paid,like_count,meta_image_url,min_cents_pledged_to_view,post_file,post_metadata,published_at,patreon_url,post_type,pledge_url,preview_asset_type,thumbnail,thumbnail_url,teaser_text,title,upgrade_url,url,was_posted_by_campaign_owner,has_ti_violation,moderation_status,post_level_suspension_removal_date,pls_one_liners_by_category,video_preview,view_count",
        "fields[user]": "full_name,image_url,thumb_url,url",
        "fields[media]": "id,image_urls,download_url,metadata,mimetype,name,size_bytes,thumbnail_url,upload_url,url",
        "fields[access_rule]": "access_rule_type%2Camount_cents",
        "fields[native_video_insights]": "average_view_duration%2Caverage_view_pct%2Chas_preview%2Cid%2Clast_updated_at%2Cnum_views%2Cpreview_views%2Cvideo_duration",
        "filter[contains_exclusive_posts]": "true",
        "filter[is_draft]": "false",
        "sort": "-published_at",
        "json-api-version": "1.0"
    }
    _patreon_api_url = "https://www.patreon.com/api/posts"

    def __init__(self, patreon_creator: str, cookie: str):
        self.patreon_url: str = "https://www.patreon.com/" + patreon_creator
        self.creator: str = patreon_creator
        self.cookie: str = cookie
        self.campaign_id: str = self.get_campaign_id()
        self.loaded_posts: list[PatreonPost] = []
        self.next_cursor: str | None = None
        self.total_posts: int = 0

    @property
    def all_loaded(self) -> bool:
        return self.next_cursor is None

    def load_next(self) -> bool:

        url = self._build_url(self.next_cursor)

        response = self.get_posts(url)

        self.loaded_posts.extend(response.posts)

        self.next_cursor = response.cursor_next
        self.total_posts = response.total_posts

        return self.next_cursor is not None

    def load_all(self):
        while self.load_next():
            print(f"Loaded {len(self.loaded_posts)} / {self.total_posts} posts")
        print(f"Loaded {len(self.loaded_posts)} / {self.total_posts} posts")

    def get_campaign_id(self) -> str:
        request = requests.get(self.patreon_url)
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

    def get_posts(self, url: str) -> PatreonData:
        request = requests.get(url, headers={"Cookie": self.cookie})
        return PatreonData.from_json(request.json())


def run_crawl(config: CrawlerConfig):
    raw_cookies = get_cookies(config.cookies_file, "patreon.com")
    parsed_cookies = "; ".join([f"{cookie[0]}={cookie[1]}" for cookie in raw_cookies])

    crawler = PatreonCrawler(config.creator, parsed_cookies)
    crawler.load_all()

    out_dir = f"{config.download_dir}/{config.creator}"

    downloader = PostDownloader(out_dir)

    filtered_posts = []

    for post in crawler.loaded_posts:
        if post.current_user_can_view:
            filtered_posts.append(post)
        else:
            print(f"Skipping post {post.id} as it is not viewable")

    downloader.download(filtered_posts)
    downloader.wait_finish()
