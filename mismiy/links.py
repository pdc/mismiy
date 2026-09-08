from dataclasses import dataclass, replace
from typing import Protocol, TypeVar


@dataclass
class Link:
    rel: str
    href: str
    title: str | None = None
    type: str | None = None
    ordinal: int | None = None


class LinkBase(Protocol):
    href: str


TLink = TypeVar("TLink", bound=LinkBase)


def munged(link: TLink, *, omit_dot_html=False) -> TLink:
    """Munge the href field of the input.

    The input must be a dataclass with an attribute named `href`.

    If the href field does not need munging, the original object is returned.
    """
    if omit_dot_html and link.href.endswith(".html"):
        return replace(link, href=link.href[:-5])  # pyright: ignore[reportArgumentType]
    return link


def url_relative_to(target: str, base: str) -> str:
    """Given an URL reference, return one relative to base URL."""

    # ASSUMPTION. Both target and base are relative URLs.
    # Neither starts with a slash.
    # Neither contains ../

    target_parts = target.split("/")
    base_parts = base.split("/")

    while len(target_parts) > 1 and target_parts[0] == base_parts[0]:
        target_parts = target_parts[1:]
        base_parts = base_parts[1:]

    result_parts = [".."] * (len(base_parts) - 1) + target_parts
    return "/".join(result_parts)
