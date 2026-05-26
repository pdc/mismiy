title: External metadata
author: Damian Cugley
tags:
- Mismiy command
- Markdown documents
updated: 2026-05-26


It makes sense for metadata about the figures in a post to be included in the metadata
of the post itself, but it does make the front matter inconveniently long. We
can address this by allowing _external_ metadata.


## External metadata

For now we will use _external metadata_ to just means the data in the same format
as the metadata at the top of a page,
but in a separate file. We will use file-name conventions to link the metadata to the post—avoiding having
explicit links or includes, which are all to likely to create dangling references.

One advantage of this—beyond decluttering the post file itself—is that the metadata
is an ordinary YAML file, so it is relatively straightforward to generate it from
some other source. Or at least easier than having to edit it in to the front matter
of the post itself.


## Metadata for one field of a page

Suppose a site has a post whose file name is `2026-04-12-picasso.md`.
Then if there is a file named `2026-04-12-picasso.figures.yaml`, then it provides the content of the
`figures` field. The content of the file has to satisfy the same StrictYAML
schema as the field value would have.

So if this file contains the following YAML:

```yaml
- id: poker
   src: pics/2026/picasso-poker-600.jpeg
- id: child-with-dove
   src: pics/2026/picasso-dove-600.jpeg
```

Then it is is treated exactly as if it appeared in the front of the post:

```
title: A successful heist
figures:
- id: poker
   src: pics/2026/picasso-poker-600.jpeg
- id: child-with-dove
   src: pics/2026/picasso-dove-600.jpeg

So last Saturday, some friends and I raided the Louvre …
```

This generalizes to any field: the name of the field is determined by the file name.


## Metadata for one field of many pages

Another obvious use case is when a field is always automatically generated.
Let’s suppose we have some system for generating IDs for posts. It can generate
a file named `id.field.yaml` containing a map from page name to the value of the
`id` field:

```yaml
2026-04-12-picasso: 'urn:uuid:88bdcf81-1518-44f3-a2e3-f8cd4a51b1eb'
2026-04-05-knox: 'urn:uuid:ea2361ef-0c71-4571-8106-ccb2625fabce'
```

This is equivalent to adding `id: 'urn:uuid:88bdcf81-1518-44f3-a2e3-f8cd4a51b1eb'`
to the front matter of `2026-04-12-picasso.md`.



## Conflicts

There are now potentially 3 places a given field might be defined, and page authors
should use only one for any given piece of data. If there are contradictory
values for a field then Mismiy will treat this as an error and nor work until this
has been fixed.
