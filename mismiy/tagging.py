import itertools
import re
from collections.abc import Generator, Iterable, Set
from dataclasses import dataclass


@dataclass
class TagInfo:
    label: str
    href: str
    count: int


unword_re = re.compile(r"\W+")


def tagify(term: str) -> str:
    """Convert a term to the form used in URLs and searches."""
    return unword_re.sub("", term).lower()


class Tagging:
    pages_by_tags: dict[frozenset, list]

    def __init__(self, href_format="tagged/{tags}.html"):
        self.pages_by_tags = {}
        self.tag_labels = {}
        self.href_format = href_format

    def add(self, page):
        if terms := page.meta.get("tags"):
            # Reduce the labels to all-lower-case to make matching case-insensitive.
            tags = []
            for term in terms:
                tag = tagify(term)
                self.tag_labels[tag] = term
                tags.append(tag)

            # Now index page under all combinations of tags.
            for subset in iter_subsets(tags):
                self.pages_by_tags.setdefault(subset, []).append(page)

    def tag_info(self, term: str) -> TagInfo:
        """Info about one tag."""
        tag = tagify(term)
        return TagInfo(
            self.tag_labels[tag],
            self.tags_file((tag,)),
            len(self.pages_by_tags[frozenset((tag,))]),
        )

    def pages_for_terms(self, terms: Iterable[str]) -> list:
        """Return the list of pages matching these terms."""
        return self.pages_by_tags.get(frozenset(tagify(term) for term in terms))

    def page_tags(self, page) -> list[TagInfo] | None:
        """Create tag info suitable for use in templates."""
        if terms := page.meta.get("tags"):
            infos = [self.tag_info(term) for term in terms]
            infos.sort(key=lambda info: (-info.count, info.label))
            return infos

    def tags_file(self, tags: Iterable[str]) -> str:
        """Return href and hence file name for page about this combination of tags.

        Assumes tags are already tagified.
        """
        urlified = "+".join(sorted(tags))
        return self.href_format.format(tags=urlified)

    def narrowing_tags(self, tags: Iterable[str]) -> list[TagInfo]:
        """Find tags that, when combined with these tags, yield fewer pages.

        The tag infos are for tags that might be added, with the href set to
        the page for the combination.

        Assumes tags are already tagified.
        """
        tag_set = frozenset(tags)
        tag_count = len(tag_set) + 1  # How many tags we want in results.
        page_count = len(self.pages_by_tags[tag_set])
        narrowings = [
            (k, len(pages))
            for k, pages in self.pages_by_tags.items()
            if k > tag_set and len(k) == tag_count and len(pages) < page_count
        ]
        return [
            TagInfo(self.tag_labels[next(iter(k - tag_set))], self.tags_file(k), count)
            for k, count in narrowings
        ]

    def widening_tags(self, tags: Iterable[str]) -> list[TagInfo]:
        """Find tags in this set of tags that, when removed, yield more pages.

        The tag infos are for tags that might be removed, with the href set to
        the page for the combination of the remaining tags.

        Assumes tags are already tagified.
        """
        tag_set = frozenset(tags)
        min_count = len(self.pages_by_tags[tag_set]) + 1
        widenings = [
            (tag_subset, count)
            for tag_subset in iter_subsets(tags)
            if (count := len(self.pages_by_tags.get(tag_subset))) and count >= min_count
        ]
        tag_infos = [
            TagInfo(
                " + ".join(sorted(self.tag_labels[tag] for tag in tag_subset)),
                self.tags_file(tag_subset),
                count,
            )
            for tag_subset, count in widenings
        ]
        tag_infos.sort(key=lambda info: (info.count, info.label))
        return tag_infos


def iter_subsets(xs: Set) -> Generator[frozenset]:
    """Yield all the subsets of the"""
    for x in xs:
        yield frozenset((x,))
    for k in range(2, len(xs)):
        for combo in itertools.combinations(xs, k):
            yield frozenset(combo)
    if len(xs) > 1:
        yield frozenset(xs)
