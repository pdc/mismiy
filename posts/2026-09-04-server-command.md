---
title: Development server
author: Damian Cugley
tags:
- Mismiy command
---

The usual set-up for working on a post is to have `mismiy -w`
running in one terminal window and `python -mhttp.server` running
in another—but wouldn’t it be nicer if we could make `mismiy` handle
the HTTP side of things as well so we just need one command?




The `mismiy` command currently has two modes: build-once and watch.
We will add a new mode triggered with `--server` that runs a development
web server.

Argument | Config | Effect
--- | --- | ---
`--server` | – |  Run a web server on the output directory. Implies `‑‑watch` and `--draft`.
`--port` _n_, `‑p` _n_ | `port` | Override the default port number 8000.
`--bind` _addr_ | `bind` | Bind to a specific IP address rather than all available interfaces.

Might be nice to have a one-letter argument for this, but, alas! `-s` is
already taken for the unlikely use case of having a static directory
with a custom name.




[`http.server`]: https://docs.python.org/3/library/http.server.html
[Watchdog]: https://python-watchdog.readthedocs.io/
