# Mismiy – (yet another) super simple static site generator

Mismiy is an exercise in finding how little we can do to create a site generator
from scratch. It’s implemented in Python, so very little code is needed to
iterate over files, stuff them though [Markdown] and [Mustache], and write
the results in to a directory. Modern CSS and HTML5 between them mean there
is little need for preprocessing CSS or elaborate JavaScript.

Status: We have the bare minimum to be a blog:

- an index page with reverse-chronological list of posts,
- post pages with a link back to the index,
- non-post pages like an about page,
- very basic navigation using tags, and
- an Atom feed so it can be read in an RSS reader.

_Mismiy_ is pronounced /ˈmɪsmɪj/ ‘Miss me?’

## Getting started

For now the way to use this package is a bit primitive:

1. You need to have installed [Python] and [Python Poetry].
2. Copy the Mismiy project in to a directory, say `~/src/mismiy`.
3. Create a separate folder, say `~/my-bloggy-blog`, copy  `~/src/mismiy/templates` in
  to it, and create directories `posts`, `static`, and `pub`.
4. Create posts in the `posts` directory (in the format described below).
5. Copy stylesheets and the files they need to the `static` directory.
6. In `~/src/mismiy` run `eval $(poetry env activate)` to activate the virtual environment,
  then `cd` to `~/my-bloggy-blog` and run the command `mismiy -w`.
7. In a separate terminal window, visit `~/my-bloggy-blog/pub`. There should be
  some HTML files here now. Run the command `python -mhttp.server`.
8. Open <http://localhost:8000/> and you should have an index page.
9. Edit the templates or the style sheets to change the appearance of your blog.

Future versions may automate away some of the above steps.

## Posts

A _post_ is a file that looks a like this:

```markdown
title: Greetings from Blefuscu
author: Lalcom

**Lilliput** and **Blefuscu** are two fictional island nations that appear
in the first part of the 1726 novel _Gulliver's Travels_ by [Jonathan Swift].

[Jonathan Swift]: https://en.wikipedia.org/wiki/Jonathan_Swift
```

The first section defines metadata like the title and author name. It ends with
the first blank line. The rest of the file is [Markdown] text.

Within the Markdown code a paragraph containing only an image tag is used to
insert a figure. For example, `![A sunny meadow](fig1)` looks up the figure with
`id` value `fig1` and renders the partial template `figure.html` to produce the
HTML representation of the figure and its caption.

The file name is used in the URL of the post, with the `.md` or `.markdown` suffix
replaced by `.html`.
The index pages list the posts in alphabetical order by file name. The usual convention
is to start the file name with the date in ISO format. For example, `2025-07-22-british-pi-day.md`,
or by creating subdirectories so your posts have file names like `2025/07/22/british-pi-day.md`.

## Post metadata

The `title` field is required, and supplies the heading for the post, also used to link to it in the index.

The `author` field can be a string, or can be a nested object with `name` (required),
`uri` and `email` fields (both optional). Nested objects are shown indented below `author:` key, like this:

```yaml
author:
    name: Quizzog the Magnificent
    email: quiz@snaggleheim.example
    url: https://snaggleheim.example/bibliocrats/quiz
```

The `id` field is a URI uniquely identifying this post. It is used in the Atom feed.
It should be guaranteed
unique, and persistent. If not supplied then one will be
generated based on the blog’s id. Common choices for `id` fields are as follows:

- the URL of the post itself, as in `https://snaggleheim.example/blog/2025-07-22-pi-day.html`
- a [UUID], as in `urn:uuid:955d36c7-8ec0-49f7-be73-c455daadb97a`
- a tag ([RFC 4151]), as in `tag:snaggleheim.example,2025:blog:2025-07-22-pi-day`

The `published` field gives the date and optionally the time the post is intended
to be publicly available. If the time is omitted, then midnight at the start of
the day is assumed (so `2025-07-22` is interpreted as `2025-07-22T00:00:00+00:01`
if the local time zone is `Europe/London`). If omitted then Mismiy guesses a date
based on the name of the file.

The `updated` field the date and optionally the time the post was last modified
in a meaningful way, such as adding a correction or more information. There is no need to set
the `updated` field after merely adjusting whitespace or correcting a simple misspelling.

An optional `summary` field should be a plain-text summary of the post. It will be
made available in the Atom feed. It can also be used in page templates.

You can provide `tags` field to classify posts by subject in some way. Extra index
pages will be generated listing pages associated with a given tag. The tags are provided
as a list of strings, using dashes or asterisks as bullets:

```yaml
tags:
  - recipe
  - pie
  - old recipe book
```

You can also include metadata about **figures** (images included in the post).

```yaml
figures:
  - id: foo
    src: pics/foo.png
    width: 560
    height: 315
    caption: How the foo is bar.
```

Figures have mandatory field `src`, which can be either a string (URL reference)
or a map from pixel density to URL reference, like so:

```yaml
figures:
  - id: foo
    src:
      1x: pics/foo.png
      2x: pics/foo.1120.png
    width: 560
    height: 315
    caption: How the foo is bar.
```

The `id` field for the figure is optional, and will be default to `fig1`, `fig2`, and so on.
The `caption` field is optional; it supplies text that goes next to the figure.
An optional `description` field supplies a long description of the appearance of
the figure.

An arbitrary structured data blob may be supplied as `data`. This can be used to
provide machine-readable data about the subject of the page (for example, a
review might have a summary of some data about the item being reviewed). It
can be embedded in the page via the page templates.

All of the fields are optional except `title`. The metadata is parsed using [Strict Yaml], a less-confusing subset
of the full YAML language.

A field from a post can be supplied as a parallel file. The file name is the same
as the post, minus the `.md` suffix, plus the field name and `.yaml`. For example,
given a post `2026/08/05/cats.md`, the value for the `figures` field could go in
a file `2026/08/05/cats.figures.yaml`. This can be useful for fields that are
automatically generated.

## Blog metadata

The `posts` directory can contain a file named `META.yaml` containing metadata
about the posts collectively. For example:

```yaml
title: Lilliput Tourism Guide
url: https://tourism.lilliput.example/blog/
id: https://tourism.lilliput.example/blog/
tz: Lilliput/Mildendo
icon: /logo-square-144.png
logo: /logo-wide-80.png
```

The following fields are all optional.

The `title` field is the title for the blog as a whole, in the form to be used in the Atom feed.

The `url` field is used to construct absolute URLs for posts. Generally if it includes
a path component it should end with a slash.

The `id` field is a unique, persistent identifier for the blog as a whole, in the form
of a URL (like the post ids). Be sure to use different ids for different blogs.
If posts do not specify `id` fields, then the blog id will be used to generate the post ids.
If the `url` field is known, it is often a reasonable choice for `id`.

Specify the time zone to be used for dates with the `tz` field. This uses the
uniform naming convention of the [tz database], which looks like `Europe/Paris`,
`America/New_York`, and so on. It is used when writing timestamps in to the Atom feed.

The `icon` and `logo` fields are both optional URLs of images to use in the Atom
feed to identify the blog. The `icon` image is expected to be square.

There are two sorts of page in the Mismiy system: regular pages and posts.
The convention is that Markdown files in the `posts` directory are posts, and
other pages are regular pages. The field `kind` can be used to override this.
Its value is one of the values `post` or `page`.

The fields `title`, `url`, and `id` really only matter for blogs (where `kind` is `post`).

## Regular pages

The difference between posts and regular pages is that posts are included in the
blog index. They also use a different template, though the two templates may
be very similar.

Pages are generated from Markdown files in a separate directory from the `posts`
directory. For example, you can create a directory called `pages` and add
a file `about.md`. This will generate a page `about.html` in the blog.

Note that even though the source files come from different directories, they all
go together on the finished web site. If you want to have all the `about`
pages’ URLs to have a common prefix, create a subdirectory within the `pages`
directory.

## Templates

The `templates` directory contains [Mustache] templates. _All_ files in that
directory are templates, so there is no need for `.mustache` suffixes.

When rendering a page the template named for the kind of page is used:

- `post.html` for posts;
- `page.html` for other pages;
- `index.html` for the index page; and
- `tagged.html` for the index page for a set of tags.

The other files, like `header.html` and `inline.css` are partial templates
(partials) referenced from the other templates.

The special templates `figure.html` and `atom_figure.html` are used for rendering figures.

The context for a page or post template includes the following:

Key | Value
--- | ---
`author` | An object with fields `name`, `uri`, and `email`; the latter two may be null
`body_html` | The text of the page, converted to HTML fragments
`dotdotslash` | Relative URL to the root of the blog: a sequence zero or more repetitions of `../` that can be prepended to a relative URL
`href` | URL of the page, relative to the base URL of the blog
`name` | Name of the page, formed from the file name without `.md` or `.markdown` suffix
`published` | A date object, as described below
`tags` | If this page has tags, then a list of tag objects with `label`, `href`, and `count` fields
`updated` | A date object, as described below, or null
`summary` | Plain-text summary of the page, if supplied.
`data` | Structured data for the page, if supplied.
`data_json` | The `data` field, formatted as JSON.
`links` | List of objects with `rel`, `href`, optional `title` and optional `type`
`links_by_rel` | The same link objects, but indexed by their `rel` value
`figures` | Normalized metadata about figures in the page
`figures_by_id` | The figures data, indexed by `id` value.
`ordinal` | The position of this post within the sequence of posts.
`as_date` | A lambda that interprets the context as a date and adds a date object to the context (as table below).
`as_duration` | A lambda that interprets the context as an ISO duration literal and adds an object to the context.

Date objects are a halfway house to proper localization of dates. They contain
the following fields:

Key | Value | Example
--- | --- | ---
`day_2digits` | Day of month as two digit number | `27`
`day` | Day of month (1 or 2 digits) | `27`
`iso_date` | Numeric date in ISO order | `2025-07-27`
`iso_datetime` | Numeric date and time in ISO order | `2025-07-27T18:02:55.672711+01:00`
`month_2digits` | Month as a two-digit number | `07`
`month_name` | Full name of month | `July`
`month` | Month as a number (1 or 2 digits) | `7`
`year` | Year as a four-digit number | `2025`

The objects representing figures have the following fields:

Key | Value
--- | ---
`id` | Shorthand used to reference the image in the Markdown code
`src` | URL of image data
`srcset` | URLs of image data for high-density displays, or blank.
`width` | Width on page in CSS units
`height` | Height on page on CSS units
`caption_html` | Optional caption for the figure
`description_html` | Optional long description for the figure

When rendering the `figure.html` template, the above fields comprise the context
for the template. There is an additional field
`alt`, the alternative text provided in the image reference.

Index pages have the following context:

Key | Value
---|---
`is_index` | Always true
`links` | List of objects with `rel`, `href`, optional `title` and optional `type`
`links_by_rel` | The same link objects, but indexed by their `rel` value
`reverse_chronological` | List of objects with the same fields as pages except without the `body` and `tags`

The index page is the root of the site, so `dotdotslash` is always empty.

Pages for combinations of tags are like index pages

Key | Value
---|---
`dotdotslash` | Relative URL to the root of the blog: a sequence zero or more repetitions of `../` that can be prepended to a relative URL
`links` | List of objects with `rel`, `href`, optional `title` and optional `type`
`links_by_rel` | The same link objects, but indexed by their `rel` value
`reverse_chronological` | List of objects with the same fields as pages except without the `body` and `tags`
`tags` | List of tag objects
`widenings` | List of tag objects with few tags (and therefore linking to more pages)
`narrowings` | List of tag objects with one more tag (and therefore linking to fewer pages)

## The mismiy command

So far the command does one thing: generate the site. It does this by
reading pages from `posts`, generating HTML with templates in `templates`,
and writing files in a directory called `pub`. Posts whose published date is in
the future are omitted.

This behaviour can be adjusted with options:

Option | Effect
--- | ---
`--as-of` _date_ | Change the cut-off date for unpublished articles.
`--drafts`, `-d` | Include unpublished articles.
`--locale` _locale_ | Override the default locale. Must be a locale specifier like `en_GB.UTF-8`.
`--omit-dot-html` | If set, strip the `.html` from internal hrefs. You need a server that adds the `.html` suffix.
`--out-dir`, `-o` _path_ | Root of generated HTML tree. Default is `pub`.
`--static-dir`, `-s` _path_ | Root of static files. Default is `static`.
`--templates-dir`, `-t` _path_ | Directory containing mustache templates. Default is `templates`.
`--watch`, `-w` | Watch files & rerun when they change. Implies `--draft`.

Directories of pages to include in addition to `posts` can be specified on the command line.

A convenient way to work on a post is to have one terminal window running `mismiy -w`,
and another running `python -mhttp.server` from the `pub` directory. Then when you have saved edits to your
posts or templates, refresh the web browser window to see the updated HTML.

[Markdown]: https://commonmark.org
[Mustache]: https://mustache.github.io
[Python Poetry]: https://python-poetry.org/docs/
[Python]: https://www.python.org
[RFC 4151]: https://www.rfc-editor.org/rfc/rfc4151
[Strict Yaml]: https://hitchdev.com/strictyaml/
[tz database]: https://en.wikipedia.org/wiki/Tz_database
[UUID]: https://www.rfc-editor.org/rfc/rfc9562
