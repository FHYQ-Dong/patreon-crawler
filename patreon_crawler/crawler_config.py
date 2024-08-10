from dataclasses import dataclass
from typing import Literal

type PostGroupingStrategy = Literal["none", "all", "dynamic"]
"""
The strategy to use for grouping posts into directories.
- "none": All posts are downloaded into the same directory
- "all": Each post is downloaded into a separate directory
- "dynamic": Posts with more than one file are grouped into a directory
"""


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

    post_grouping_strategy: PostGroupingStrategy = "dynamic"
    """
    Controls how posts are grouped into directories
    """
