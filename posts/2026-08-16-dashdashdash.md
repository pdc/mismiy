---
title: Dash dash dash
author: Damian Cugley
tags:
- Markdown documents
- Mismiy command
---

The format for a page or post in Mismiy is a Markdown body with a header that
contains some metadata about the page. Other software uses a slightly different
syntax from Mismiy, and I am considering supporting this variation since it will
make editing pages a little easer.


## Background on Mismiy’s file format

When I first designed the file format,
I was inspired by the conventions of [RFC 822] (superseded by [RFC 5322 Internet
Message Format]), though I did not follow them exactly. Internet messages have
headers separated from the body of the message by a blank line. The format for
headers in the simple case is header name, a colon, and the content of the header.

```markdown
title: Dash dash dash
author: Damian Cugley

The format for a page or post in Mismiy is a Markdown body with a header that
```

Where Mismiy departs from RFC 822 is that the values can be [StrictYAML] structures,
and these do not follow the RFC-822 rules for continuation lines:

```yaml
tags:
- Markdown documents
- Mismiy command
```

The attraction of this syntax is it is very simple—more or less the least possible
syntax, in fact. The downside is that text editors with syntax highlighting try
to process the front matter as a Markdown paragraph,which looks bad. Worse,
the editors I use have linters that will generate several complaints as they try
to interpret YAML as Markdown.


## The other format

There is an emergent convention, used by software like
[Eleventy],
[Hugo],
[Jekyll],
[Obsidian],
and probably others, where the [YAML] front matter is bracketed by lines consisting
of three dashes, like this:

```markdown
---
title: Dash dash dash
author: Damian Cugley
tags:
- Markdown documents
- Mismiy command
---
The format for a page or post in Mismiy is a Markdown body with a header that
```

The great thing about this is (a) it is easy to check a file to see whether this
convention is in use, and (b) it is unlikely to be confused with a Markdown file
*not* using a front-matter syntax.
So the text editors I use act as if this were a standard part of Markdown syntax,
and highlight the headers as YAML and the body as Markdown—which makes for
a nicer editing experience.


## Changes to Mismiy

The alteration to Mismiy is pretty simple. We can allow the triple-dash-delimitated
syntax as an alternative to the existing one with little risk of confusion,
and without forcing users to rewrite all existing files.

I still think the original Mismiy syntax is more elegant, but the convenience of
ready-made support in text editors and other software makes it expedient to switch.


[Eleventy]: https://www.11ty.dev
[Hugo]: https://gohugo.io
[Jekyll]: https://jekyllrb.com
[Obsidian]: https://obsidian.md
[RFC 5322 Internet Message Format]: https://www.rfc-editor.org/info/rfc5322/
[RFC 822]: https://www.rfc-editor.org/info/rfc822/
[StrictYAML]: https://hitchdev.com/strictyaml/
[YAML]: https://yaml.org
