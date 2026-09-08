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

The code that expands the list of tags labels (on the page) into
a list of info objects. This means that the page references in the
`reverse_chronological` list will be a subset of the pages used when
rendering the page proper (that is, the fields it does have are the
same as the same-named field in the Page objects).

We can supply the tags as a field named `tags` and `tags_json`.
I considered trying to create a lambda for conversion to JSON,
but  the techniques in [the post about lambdas] won’t work if the
data is a list (because of the way Mustache’s rules about sections
work).

[the post about lambdas]: ./2026-07-19-lambdas
