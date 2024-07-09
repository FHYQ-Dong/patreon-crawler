from __future__ import annotations
from dataclasses import dataclass, field


def obj_get(obj: dict, key: str):
    splits = key.split(".")
    for split in splits:
        if not obj:
            return None
        obj = obj.get(split)
    return obj


@dataclass
class PatreonMedia:
    id: str
    height: int
    width: int
    url: str
    mimetype: str

    @staticmethod
    def from_json(json_: dict) -> PatreonMedia:
        attributes = json_["attributes"]
        dimensions = attributes["metadata"]["dimensions"]
        return PatreonMedia(
            id=json_["id"],
            height=dimensions["h"],
            width=dimensions["w"],
            url=attributes["image_urls"]["original"],
            mimetype=attributes["mimetype"]
        )


@dataclass
class PatreonPost:
    id: str
    title: str
    media: list[PatreonMedia]
    current_user_can_view: bool

    @staticmethod
    def from_json(json_: dict, media: list[PatreonMedia]) -> PatreonPost:
        attributes = json_["attributes"]
        media_ids = obj_get(attributes, "post_metadata.image_order") or []
        media = [media for media in media if media.id in media_ids]
        return PatreonPost(
            id=json_["id"],
            title=attributes["title"],
            media=media,
            current_user_can_view=attributes["current_user_can_view"]
        )


@dataclass
class PatreonData:
    posts: list[PatreonPost]
    cursor_next: str | None = None
    total_posts: int = 0

    @staticmethod
    def from_json(json_: dict) -> PatreonData:
        data = json_["data"]
        included = json_["included"]
        media = [PatreonMedia.from_json(post) for post in included if post["type"] == "media"]
        posts = [PatreonPost.from_json(post, media) for post in data if post["type"] == "post"]

        return PatreonData(
            posts=posts,
            cursor_next=obj_get(json_, "meta.pagination.cursors.next"),
            total_posts=obj_get(json_, "meta.pagination.total")
        )
