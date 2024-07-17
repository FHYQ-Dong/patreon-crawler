from dataclasses import dataclass


@dataclass
class CrawlerConfig:
    creator: str
    cookies: dict[str, str]
    download_dir: str
    max_posts: int = 0
    download_inaccessible: bool = False
    max_parallel_downloads: int = 10
