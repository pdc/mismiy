# Changelog

## [Unreleased changes]

### Added

- Add metadata field `ordinal` to pages. This gives their position in the sequence. [#7]
- Add option `--omit-dot-html`. [#1]
- Page context has `links_by_rel` to allow including specific links in page templates. [#6]
- Posts have `next` and `prev` links. [#6]

## 0.1.0 (2025-07-27)

### Added

- Add command to convert a directory containing Markdown files in to a bare-bones blog:
  - an index page with reverse-chronological list of posts,
  - post pages with a link back to the index,
  - non-post pages like an about page,
  - very basic navigation using tags, and
  - an Atom feed so it can be read in an RSS reader.
