from dataclasses import dataclass


@dataclass
class CrawlerConfig:
    """
    Configuration for the Patreon crawler
    """

    creator: str
    """
    The creators unique handle
    """

    cookies: dict[str, str]
    """
    The cookies to use for the request
    """

    download_dir: str
    """
    The base directory to download the posts to
    """

    max_posts: int = 0
    """
    The maximum number of posts to crawl
    """

    download_inaccessible: bool = False
    """
    Whether to download inaccessible posts (blurred)
    """

    max_parallel_downloads: int = 10
    """
    The maximum number of parallel downloads to run at once
    """
