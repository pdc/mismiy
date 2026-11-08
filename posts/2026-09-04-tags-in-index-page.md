---
title: Tags on the index page
author: Damian Cugley
tags:
- Mustache templates
- mismiy command
- tagging
---

We want to add tags to the index page in two ways

- In the list of posts we could augment the post titles with the
  tags of that post; and
- To allow us to add a tag cloud (or searchable tag list) to the page
  so that readers have a way in to the tag navigation.

The former was already almost possible: the page references in the
`reverse_chronological` item in the template context includes the
`tags` field as supplied in the front matter for the post—but this
is just a list of strings, and does not expose the URLs for the links
to the tags (although as it happens the template writer could guess).


## Tag cloud

Tag clouds come in two main flavours. First, an alphabetical list
of tags, with the font size varying according to the popularity of
the tag (often proportional to the square root of the count). This
has the advantage that if you know the tag you want, finding it is
easy (because alphabetical).

The second approach is to use a clever layout to pack the words
in to a tightly fitted pattern in an attempt to make something that
expresses the relative popularity of tags in a more aesthetic way
than the alphabetical approach. Processing the tag list to calculate
this layout is out of scope of Mismiy, but there are plenty of
JavaScript packages for generating tag clouds, so all that is really
required is to provide the list of tags with counts and links
in a form that can be fed to the JavaScript.

Clouds are not the only (or necessarily the best) way to visualize
a set of tags. A simple list might be better for a limited list.
For a really long list a searchable user interface might be nice
(although it would be less code to just list the tags and let the
user use their web browser’s search-in-page feature).


## How Mismiy can help

In the template context for the index page, the page references in the
`reverse_chronological` list are not complete pages (since the content of the
page is not required). But the fields that the references do have are generally
the same as the same-named field in the page proper (that is, the `title`
in the page reference is the same as the `title` when rendering the page itself).

One exception was the `tags` field. It was present, but it was just a copy
of the field from the YAML front matter of the page, rather than the `TagInfo`
objects used on the real page. So the change required here was to bring this
field in line with the convention that the page-reference fields are a proper
subset of the page fields. In the Python code this meant rearranging the
code for generating the context so that the same function provides both.

We also add a `tags_json` field. This can be used to pass the tag info in to
some JavaScript that produces a flashy user interface to the tag list.
(I considered trying to create a template lambda for conversion to JSON,
but  the techniques in [the post about lambdas] won’t work if the
data is a list because of the way Mustache’s rules about sections
work.)


## Changes to the index page

After all this, I did not use the elaborate tag-cloud or tag-selection user interface
approaches: at present the tag list on the index page for this blog is short
enough that there is no point. But the data is available in the template context
for when I do want to.

The tag list is shown as a plain list to the right of the blog index—or just below
it on small screens. The tags are augmented with the post count so the reader
gets an idea of which ones narrow down the index the most. More about that in
[the next post].

[the post about lambdas]: ./2026-07-19-lambdas.html
[the next post]: ./2026-09-08-pluralization.html
