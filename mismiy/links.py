from dataclasses import dataclass


@dataclass
class Link:
    rel: str
    href: str
    title: str | None = None
    type: str | None = None


def url_relative_to(target: str, base: str) -> str:
    """Given an URL reference, return one relativbe to base URL."""

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
