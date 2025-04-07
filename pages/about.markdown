title: Mismiy, yet another simple static-site generator
updated: 2024-06-18

Mismiy is a static-site generator: it takes a directory full of posts
and pages in [Markdown], formats them as HTML, then creates
pages using [Mustache] templates. Posts and pages are pretty
much the same, except that the index page has a reverse-chronological
list of posts. It also generates an [Atom] feed, so readers can
subscribe to your blog in their choice of feed reader (RSS reader).

A ‘static’ site means that all the pages people can view are already
rendered in advance, rather than on-demand using information from some
database backend. This means the web server can be exceptionally
simple, which is good for security, and cheap to host. The trade-off is
they treat all visitors equally: they’re good for a public blog, less so
for premium content or secret notes.

The word ‘simple’ is a bit slippery, but the intention is get a lot of
utility out of a minimum of code, and to saddle the site editor with
the minimum of boilerplate. Part of keeping it simple is leaving out as
many features as possible, by delaying implementing things until we
have convinced ourselves we can’t really manage without them.

_Mismiy_ is pronounced /<code>ˈmɪsmɪj</code>/ ‘Miss me?’


[Atom]: https://datatracker.ietf.org/doc/html/rfc4287
[markdown]: https://commonmark.org
[mustache]: http://mustache.github.io
