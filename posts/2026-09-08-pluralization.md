---
title: Plural rules
author: Damian Cugley
tags:
  - Mustache templates
  - localization
---

Tag objects have a `count` field that is the number of pages with
that tag. How can we arrange for the count to be followed by the
correct form of the noun—‘1 post’ versus ‘2 posts’?

This is a little detail but if we want to allow for the possibility of internationalization
of our software it gets a bit more involved.

## Plural forms

To handle [plural rules], the template will contain different versions of the
message, marked up in some way so that one is selected based on
the value of the count.

When we are writing in English there are two versions of the phrase—one
message for the singular case, a second for the plural cases. The latter is also
used for the zero case. This convention is not the same in all languages.
The French language uses singular forms with zero, for example.
Some languages have more complicated conventions, such as a separate form
used when the number is 2.

The [Unicode CLDR Project] publishes (amongst other things) a database
of language rules where each variation has a code name like `one`, `two`, `few`, `many`, or `other`;
details are in [Unicode Technical Standard #35].
In English the tags are `one` and `other`.

There is an ICU message format that uses these tags to select
different variations on a sentence:

```
{count, plural, one{There is # post.} other{There are # posts.}}
```

We won’t be using this format directly, but will be taking some
ideas from it.


## How Mismiy can help

We will define a lambda named `plural` in the template context.
It expects the top of the context stack to be an integer. It then
renders its content with new data on the stack: a tag field named
after the plural form of the number, and the formatted number itself.

The upshot is that it can be used in a template
fragment like the following:

```html
{{#count}}
    {{#plural}}
        {{#one}}There is {{number}} post.{{/one}}
        {{#other}}There are {{number}} posts.{{/other}}
    {{/plural}}
{{/count}}
```

Where in this case `count` is a field whose value is an integer.
For a given value of `count`, only one of `one` or `other` will be
defined, so the other phrase will be omitted.

I am not sure whether this is clever and elegant or horribly obscure
and verbose. Fortunately it should not be needed often.

How does Mismiy get the pluralization information? We can use
[Babel], a Python package that includes an implementation of the
CLDR plural rules. This seems a little more elegant than hard-coding
the English plural forms in to the template.


## More Babel

Since we are adding Babel to the project, we can re-examine
the approach taken to rendering dates (see [the post about dates]).
This depended on the Python standard library’s `locale` package. Having
having two locale implementations in one application is just going
to create confusion, so we are switching the existing locale-sensitive
code to use Babel as well.

To this end, the `Gen` constructor has a `locale` parameter,
which it converts to a `Locale` instance. It then passes this in to
the methods it calls to create the context for the templates.
The lambdas that are added to the context also
now have the `Locale` object supplied when they are added to the context.
We no longer call the standard library `setlocale` function.


## In the templates

The only place we use this new feature in the Mismiy templates is in the list
of tags on the index pages. A lot of machinery for [one little ‘s’].



[Babel]: https://babel.pocoo.org/en/latest/api/core.html#babel.core.Locale.plural_form
[Plural Rules]: https://cldr.unicode.org/index/cldr-spec/plural-rules
[the post about dates]: ./2024-05-19-dates.html
[Unicode CLDR Project]: https://cldr.unicode.org
[Unicode Technical Standard #35]: https://www.unicode.org/reports/tr35/tr35-33/tr35-numbers.html#Language_Plural_Rules
[one little ‘s’]: https://www.youtube.com/watch?v=o8WeXem5YMQ
