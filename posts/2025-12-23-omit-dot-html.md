title: Omitting .html
author: Damian Cugley
tags:
- mismiy command

The simplest static servers map URL paths directly to file names: since HTML
files have names ending in `.html`, the URLs must also end in `.html`. This
is not especially beautiful, and is arguably useless clutter.

Most static servers
can be configured to allow the `.html` suffix to be omitted,
and as it happens, [Neocities] is already configured this way, and
furthermore as it redirects to the
non-`.html` URL, which means using the `.html` suffix in internal hrefs will lead to
a pointless redirect. So it would be nice
to be able to configure Mismiy to generate pages with these slightly shorter URLs.

[GitHub pages] are also configured this way by default.


## Configuring Nginx to make file suffix unnecessary

[Nginx] is a web server (amongst other things) that can be easily configured to
handle a static site with implied `.html`.

```nginx
server {
    …
    root /var/www/mismiy;
    index index.html;

    location / {
        try_files $uri $uri.html =404;
        …
    }
}
```

The interesting part is the expression `$uri.html` in the list of files to try.
A path like `/2024-05-05-first` will map on to the file name `/var/www/mismiy/2024-05-05-first.html`.


## Supporting shorter URLs in Mismiy

To make the generated files use the shorter URLs, add the new `--omit-dot-html` flag
to the `mismiy` command, as in

```sh
mismiy posts pages --omit-dot-html
```

If you are using the Python module `http.server`  to preview the site then this
will create pages whose links do not work; you will want to use the new option
when generating the version of the site for uploading.


[Nginx]: https://nginx.org
[Neocities]: https://neocities.org
[GitHub pages]: https://docs.github.com/en/pages
