from dataclasses import dataclass


@dataclass
class CrawlerConfig:
    creator: str
    cookies_file: str
    download_dir: str
