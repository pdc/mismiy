# Mismiy – (yet another) super simple static site generator

Disclaimer: Other static site generators are available.

Mismiy is an exercise in finding how little we can do to create a site generator
from scratch. It’s implemented in Python, so very little code is needed to
iterate over files, stuff them though Markdown and Mustache, and write
the results in to a directory. Modern CSS and HTML5 between them mean there
is little need for preprocessing CSS or elaborate JavaScript.

Status: We have the bare minimum to be a blog:
- an index page with links to posts,
- post pages with a link back to the index, and
- an Atom feed.
