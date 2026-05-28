# Changelog

## [Unreleased changes]

### Added

- [Add support for external metadata.](https://mismiy.dev/2026-04-12-external-meta)
- [Add support for embedding figures in pages.](https://mismiy.dev/2026-03-08-figures)
- [Add metadata field `ordinal` to pages. This gives their position in the sequence.](https://mismiy.dev/2026-03-03-ordinal)
- [Add option `--omit-dot-html`.](https://mismiy.dev/2025-12-23-omit-dot-html)
- [Page context has `links_by_rel` to allow including specific links in page templates.](https://mismiy.dev/2025-12-18-prev-next)
- [Posts have `next` and `prev` links.](https://mismiy.dev/2025-12-18-prev-next)

### Changed

- In the template context the body of the page is now `body_html`. This is so that HTML-valued
  fields—which have to be interpolated with triple-braces—all have names ending in `_html`.

## [0.1.0] (2025-07-27)

### Added

- Add command to convert a directory containing Markdown files in to a bare-bones blog:
  - an index page with reverse-chronological list of posts,
  - post pages with a link back to the index,
  - non-post pages like an about page,
  - very basic navigation using tags, and
  - an Atom feed so it can be read in an RSS reader.


[0.1.0]: https://github.com/pdc/mismiy/releases/tag/0.1.0
