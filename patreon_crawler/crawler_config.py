from dataclasses import dataclass


@dataclass
class CrawlerConfig:
    creator: str
    cookies: dict[str, str]
    download_dir: str
