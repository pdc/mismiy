title: Resource description
summary: Embedding and inlining information about a post in a Mismiy post.
author: Damian Cugley
tags:
- RDF
- figures
- Mustache templates


When I feed a [mismiy.dev] post in to Google’s [PageSpeed Insights] it says nice
things about the page speed and accessibility (which are easy because there is not
much clever interaction on the site) but takes points off for SEO because of the
lack of invisible metadata.  What can (or should) we do about this?


## What is page metadata good for?

Search engines, social media apps and microblogging sites want to
generate attractive link previews of URLs mentioned in the post, with an image and
the title or summary of the site.
To create them, they need information like the title of the page and which image from it
to use in the preview—which, while it might be apparent to a human looking the
page, can be difficult for the machine to guess.

More generally, especially in more technical and academic contexts, there is
a lot of information on the Web that could be aggregated, searched, and transformed
in useful ways, if only the programs could identify which text on the page means what.

Hence the need for machine-readable descriptions of these resources.

This is a related but distinct meaning of ‘metadata’ from how it is used in [the previous post].


## Metadata as in resource descriptions

Metadata is information about an image, say, that is not the image itself. For
example, a fashion photo will have a photographer, stylist, and model; will take place in
a location on some date; will be for some magazine and appear in a particular issue—and so on.
This is all information that an archivist might gather about some photo to enrich
their catalogue. Later on someone might be search for photos by photographer,
say, depending on their application.

Like linking, there is a lot of academic work on metadata in theory and the practical
applications are more limited.

The terminology used in this context is _resource_ for something identified by a
URL. We often act as if the resource _is_ the  JPEG or HTML data, but
another way of thinking about it is that the URL
<https://mismiy.dev/2026-06-21-metadata> identifies the Platonic ideal of this
post, and the HTML is a _representation_
of that resource. For a database-backed web site, say, the representation of
the web page in the database may be very different from the HTML representation
you download.

An image resource may have more than one representation
(JPEG and WebP, say),
and some servers will provide different representations to different clients through a
process called [content negotiation].
(One of the simplifying assumptions with Mismiy is that we do not need this!)

The W3C has been working on a framework around resource descriptions called [RDF].
Subjects (resources) are identified by URL, which is referred to as a URI (uniform resource identifier)
in this context, or can be _blank nodes_ (with temporary URIs).
The resource description consists of _properties_ (identified by URI)
whose values are another resource (identified by URI) or a scalar value
(string, number, date, boolean). For example

> Some properties of the fictional resource `https://apples.example/2020-10-01/apple-pie-by-grandma`:
>
>  | Property | Value
>  | --- | ---
>  | `http://www.w3.org/1999/02/22-rdf-syntax-ns#type` | `http://schema.org/Recipe`
>  | `https://schema.org/name`  |  `Apple Pie by Grandma`
>  | `https://schema.org/author`  |  `Elaine Smith`
>  | `https://schema.org/description`  |  `A classic apple pie`

The fact that properties are identified by URI allows for descriptions
from different providers to be combined without name collisions.
Making this work entails URIs for people, places, languages, everything.

All this is used for two main purposes:

1. Academics and researchers smoosh together linked data and analyse it for connectivity,
generating visualizations in the form of rotating clouds of dots with lines
between them, and portals where you can interrogate the data with [SPARQL]; and

2. Google and other search engines encourage authors to add resource descriptions to
their own pages to make Google’s search results look more clever.

Many businesses are dependent on their position in Google’s search rankings and so
they have no choice but to provide the resource descriptions Google wants
(calling it search-engine optimization, or SEO).
The potentially very powerful option of searching vast pools of linked
datasets with SPARQL is, alas! obscure outside of a small corner of
ivory-tower academia.

Given a web page, how do you find its description? The three main ways to provide
this metadata are:

1. External (or alternative) representations, where the metadata is downloaded separately;
2. The metadata is embedded in the HTML of the web page; and
3. Tagging information already visible on the page.


## External metadata

RDF has various representations: as
[RDF 1.2 XML Syntax], [Notation3 (N3)], and more recently as [JSON-LD].
The last of these is a clever application of JSON. It can look like this:

```json
{
    "@context": "https://schema.org/",
    "@id": "https://apples.example/2020-10-01/apple-pie-by-grandma",
    "@type": "Recipe",
    "name": "Apple Pie by Grandma",
    "author": "Elaine Smith",
    "image":"https://apples.example/applepie.jpg",
    "description": "A classic apple pie.",
    "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.8",
        "reviewCount": "13000",
        "bestRating": "5",
        "worstRating": "1"
    },
    "prepTime": "PT3OM",
    "totalTime": "PT1H3OM"
}
```

Ignoring the `@context`, `@id` and `@type` fields, this looks like a straightforward
JSON representation of a recipe on some recipe web site built in single-page-application
style.

A JSON-LD processor uses the `@context` field to expand this to  in to RDF clauses
like those in the table above.
Expanding from JSON to RDF is useful when we want to absorb the data in to a
general-purpose RDF processor for later querying. You can experiment with this
in the [JSON-LD Playground].

Given our fictional URI `https://apples.example/2020-10-01/apple-pie-by-grandma`,
how does one find the metadata resource? One option is [content negotiation]: the application
makes an HTTP request with headers saying it would prefer JSON-LD to HTML, and
the server provides this alternative representation. Another is that the HTML at that
address may have a link header or tag (as discussed in [the prev-next post]) with `rel=alternative`.


## Embedded metadata

There are several ways that metadata can be invisibly embedded in a web page.
The HTML standard defines some specific elements such as `title`. It also defines
`link` and `meta` elements for associating other resources and properties with
the page they are in. For example,

```html
<title>Apple Pie by Grandma – Elaine’s Apple a Day</title>
<meta name="description" content="A classic apple pie.">
```

Facebook has defined a vocabulary called Open Graph which is embedded in HTML with
`meta` tags.

```html
<meta property="og:title" content="Apple pie by Grandma">
<meta property="og:description" content="A classic apple pie.">
<meta property="og:image" content="https://apples.example/applepie.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="https://apples.example/2020-10-01/apple-pie-by-grandma">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Elaine’s Apple a Day">
<meta property="og:locale" content="en_AU">
```

They eccentrically use an attribute named `property` instead of `name`,
and the language tag has an underscore instead of hyphen-minus. But everyone
wants their page to look good on Facebook so it’s a _de facto_ standard now.
You are supposed to add a `prefix="og: https://ogp.me/ns#"` attribute
as well, which in principle allows the description to be extracted as
RDF using conventions of [RDFa].

HTML also allows for files to be embedded in pages as `script` elements.
Usually the related resource is executable JavaScript code, but it can be
other formats. Google advocate adding what they call [structured data markup] to web pages:
[embedding JSON-LD in HTML documents] and using the [Schema.org] vocabulary:

```html
<script type="application/ld+json">
{
    "@context": "https://schema.org/",
    "@type": "Recipe",
    "name": "Apple Pie by Grandma",
    …as above…
}
</script>
```

All of the above are invisible in the sense that they are not shown as part of the
rendered HTML. They also have a lot of redundancy: we have already described how
to add a title property three times, and we have not mentioned the additional
copy for former Twitter. Keeping multiple copies of the same property consistent
may be easy or hard depending on your platform (templating will be more straightforward
than maintaining these properties by hand). Because they are invisible, errors are
more likely to remain unnoticed.

Invisible metadata has been popularly used in attempts to draw the attention of
search engines, starting with stuffing the
the `description`  element with keywords. The continual cold
war between click-hungry web sites and Google’s page ranking meant that the
invisible metadata was often full of misleading data and lies,
making it useless for any sort of serious attempt at indexing the web.

Finally, much of this invisible metadata duplicates visible content on the page.
The title is, generally, visible as a headline, the author name in the byline, and
so on. For this and other reasons there is a lot to be said for making the visible text
on the page machine-readable, rather than embedding a separate data lump.


## Tagging visible text

There are several ways of adding tags to text already on the page so that it can
be discovered by indexers. Some examples of systems for this are

- [microformats 2] (an [IndieWeb] convention)
- [microdata] (part of HTML5)
- [RDFa] (RDF in attributes)

The first of these, Microformats 2, tags elements by adding special HTML classes.
For example here is something approximating the JSON-LD representation:

```html
<article class="h-recipe">
    <h1 class="p-name">Apple Pie by Grandma</h1>
    <img src="https://apples.example/applepie.jpg" alt="Photo of apple pie" class="u-photo">
    <p class="p-summary">A classic apple pie.</p>
    <dl>
        <dt>Author</dt>
        <dd class="h-card p-author">Elaine Smith</dd>
        <dt>Rating</dt>
        <dd><data class="p-rating" value="4.8">★★★★☆ 4.8/5</data></dd>
        <dt>Prep time</dt>
        <dd><time datetime="PT3OM">30 min</time></dd>
        <dt>Total time</dt>
        <dd><time class="dt-duration" datetime="PT1H3OM">1&thinsp;1⁄2 hours</time></dd>
    </dl>
    <p>… Rambiling description of travels to visit Grandma …</p>
</article>
```

The `h-recipe` and `h-card` classes indicate their respective elements represent
an item of some sort. The `dt-`, `p-`, and `u-` classes indicate elements that show
data for one of the fields of the enclosing item. In my made-up example the only
classes are from h-recipe and h-card; in a real page there would also be the
classes used for CSS.

The Microdata and RDFa conventions add new attributes to HTML,
something like this:

```html
<span itemprop="author" itemscope itemtype="http://schema.org/Person">Elaine Smith</span>
```

The advantage of the Microformats approach is that it is standard HTML, and is developed
independently of the search-engine giants, with a focus on simplicity. The downside
is that the vocabulary is limited, implementation mostly confined to personal blogs,
and interoperability with RDF is intentionally out of scope.

The Microdata and RDFa styles can include URLs from whatever schemas they like,
which makes them more flexible, at the expense of being more complicated to
process and requiring attention to these XML-ish details of how the information
is encoded.


## What metadata do we actually need?

Before thinking too hard about how to arrange for metadata to be embedded in pages,
we should consider whether we want to or not. I am an advocate for doing the least code that
meets your goals, and deciding you don’t need any code is the least code of all.

Right now Mismiy is useful for writing text-heavy web sites and not much else.
There are two use cases that come to mind:

1. Just a blog with articles on some topic or many topics.
2. Reviews or descriptions of particular things (book reviews, recipes)

For the second case only we might want to have some facts and figures that go in
the sidebar about the thing we are reviewing
(or otherwise referring to), in the style
of our recipe example. Whether it is inserted as a JSON-LD blob or displayed as
a sidebar on the page with layout generated mechanically from the resource description,
being able to write a template that consumes the JSON-LD representation
will make it easier to be consistent.

In both cases if we are concerned about discovery by Google and Bing, the content of
the article is likely to matter more than any keywords stuffed in to meta tags.
What we _might_ want additional metadata for is making it easy for people
to link to (‘share’) your articles with a pleasing link preview.
Generally this boils down to having an image,
a title, and a description. [Conventional suggestion] is to use Facebook’s
[Open Graph protocol] for this: most sites that generate previews will use it.

But we might not need to define most Open Graph properties, since scanners
(including Meta’s) will use data we already include as a fallback.

Property | Fallback
--- | ---
`og:title` | `title` element
`og:description` | `<meta name=description …>`
`og:type` | `website` (meaning neither video nor audio)
`og:image` | the first image at least 600 px wide on the page
`og:url` | link with `<link rel=canonical …>` or the URL of the page

Having said that it might make sense to set `og:title` differently from the `title` element.
The latter is if often suffixed with the site name, for which OG has a separate property.
So you might want to have something like this:

```graphql
<title>Apple pie by Grandma – Elaine’s Apple A Day</title>
<meta property="og:title" content="Apple pie by Grandma">
<meta property="og:site_name" content="Elaine’s Apple A Day">
```

Most of this can be achieved by simple additions to our post templates.


## How Mismiy can help

First, if we want to support generic templates then passing in the site metadata
to the template will allow code like the following in the head:

```html
<title>{{#title}}{{.}} – {{/title}}{{site.title}}</title>
<meta property="og:title" content="{{title}}">
<meta property="og:site_name" content="{{site.title}}">
```

This uses the `title` field from `META.yaml` in the posts directory—the same
site name used in the Atom feed.

Second, we can add an optional  `summary` field that can be used
to provide a description:

```html
{{#summary}}<meta name="description" content="{{.}}">{{/summary}}
```

The [Atom syndication format] defines a `summary` element that can go in entries
alongside or instead of the `content` element. We can also include it in an article
as a paragraph between the title and the article body. This makes it a slightly
tricky bit of extra composition work for the article author, which is why we might
want to keep it optional. In its absence, Facebook and other social media sites
will use the first sentence or two of the text of the article as a fallback, which
will often be fine.

The third thing needed a link card is a representative image. For a pure text article
there might not be one (this build log has no images on most pages). Otherwise
we have the `figures` list (described in [the figures post]). If we add a lookup
`figures_by_id` to the template context, then we can pick an ID and use that as
the image to mention in the metadata. The conventional term for this is hero image,
so we could use that:

```html
{{#figures_by_id.hero}}
<meta property="og:image" content="{{src}}">
<meta property="og:image:alt" content="{{description}}">
<meta property="og:image:width" content="{{width}}">
<meta property="og:image:height" content="{{height}}">
{{/figures_by_id.hero}}
```

The hero figure might or might not be actually used in the post. The author might
prefer to provide a different crop of their hero image for the social-media metadata.

These three modest additions to Mismiy’s template context will allow for template
authors to provides the invisible data used by Facebook et al. to create link previews.

The second case, structured data for reviews and the like, is more tricky. Like any
other metadata we expect it to be present in the front matter of the post.
The complication is that up until now Mismiy has parsed that front matter with [StrictYAML],
with a schema used to guide type conversion and check for errors. When we want
to allow arbitrary [Schema.org] properties, ideally with a syntax resembling
[JSON-LD], the fixed schema will no longer suffice. There is an escape hatch in the
StrictYAML schema, `Any`, which allows arbitrary strings, maps, and arrays.
So we could have a front-matter property named `data` whose value is expected
to be a JSON-LD blob with an appropriate JSON-LD context; Mismiy can expose it
in the template context as `data_json`.

This would lead to the front matter containing a segment in a Frankenstein format
we could call YAML-LD, something like this:

```yaml
title: Apple pie by Grandma
author: Elaine Smith
summary: Reminiscences of my grandma and her classic apple pie.
data:
    @context: https://schema.org/
    @id: https://apples.example/2020-10-01/apple-pie-by-grandma
    @type: Recipe
    name: Apple Pie by Grandma
    author: Elaine Smith
    image: https://apples.example/applepie.jpg
    description: Reminiscences of my grandma and her classic apple pie.
    aggregateRating:
        @type: AggregateRating
        ratingValue: 4.8
        reviewCount: 13000
        bestRating: 5
        worstRating: 1
    prepTime: PT3OM
    totalTime: PT1H3OM

Last winter I visted my favourite Grandma Smith in her home in the south of
France …
```

So this data might be used straightforwardly to embed a glob of data for Google
in a template fragment like the following:

```html
{{#data_json}}
<script type="application/ld+json">
{{.}}
</script>
{{/data_json}}
```

Also, if we don’t like converting our JSON-LD in to YAML, we can arrange to allow
for the external metadata trick from [the previous post] to include `.json`
files as well as `.yaml`. This will be convenient if the files are being generated
automatically somehow, since it will not require teaching your JSON-LD processor
to generate YAML.

There are some annoyances. This approach  requires repeating the values of
`title`, `summary` and `author` (under
different names, so we can’t simplistically copy them in). A future refinement might
be some kind of data-schema feature that says which known-to-Mismiy
properties should be copied in to the data and with what name. Or alternatively we
could extract `title` and `summary` from the `data` blob if there is one and
they are not otherwise defined?

The other complication comes if we want to use the visible-data approach. We
might want to generate a sidebar with a template fragment like this:

```html
{{#data}}
<aside class="h-entry sidebar">
    <h2 class="p-name">{{name}}</h2>
    <p class="description p-summary">{{description}}</p>
    <dl>
        <dt>Author</dd><dd class="p-author h-card">{{author}}</dd>
        <dt>Prep time</dt><dd><time datetime="{{prepTime}}">??</dd>
        <dt>Total time</dt><dd><time datetime="{{totalTime}}" class="dt-duration">??</dd>
    </dl>
</aside>
{{/data}}
```

But to make this work we need a way to get from the ISO duration code `PT1H30M` to
a readable format like `1 hour 30 min`.

There is also the issue that the template depends on the layout of the JSON-LD data,
even though there are more than one way to express the same RDF information in
JSON-LD format. Mismatches will be hard to spot, unless they cause the visible
part of the page to look odd.


## In summary

(1) New fields that can be defined in post metadata:

- `summary` (plain text) – a sentence or two introducing or describing the post; and
- `data` (arbitrary JSON content) – resource description for the main subject of the post.

The first of these will be added to Atom feeds, assuming that does not break anything.

(2) New format for external metadata, so we can provide JSON-LD in a file named
after the post plus `.data.json`.

(3) New values in the template context:

- the new fields `data` and `summary`;
- `data_json` – the data field converted to JSON;
- `site` – information from the `META.yaml` file, including `title` the site name; and
- `figures_by_id` – allows inserting information about a specific figure.

Of these most authors need only bother adding `summary`, and only when the default
of the first few words of the main content is not satisfactory.


[Atom Syndication Format]: https://datatracker.ietf.org/doc/html/rfc4287
[content negotiation]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Content_negotiation
[Conventional suggestion]: https://webaloha.co/open-graph-tags-complete-guide/
[Embedding JSON-LD in HTML Documents]: https://w3c.github.io/json-ld-syntax/#embedding-json-ld-in-html-documents
[IndieWeb]: https://indieweb.org/IndieWeb
[JSON-LD Playground]: https://json-ld.org/playground/
[JSON-LD]: https://json-ld.org
[microdata]: https://html.spec.whatwg.org/multipage/microdata.html#encoding-microdata
[microformats 2]: http://microformats.org/wiki/microformats2
[mismiy.dev]: https://mismiy.dev/
[Notation3 (N3)]: https://www.w3.org/TeamSubmission/n3/
[Open Graph protocol]: https://ogp.me
[PageSpeed Insights]: https://pagespeed.web.dev
[RDF 1.2 XML Syntax]: https://www.w3.org/TR/rdf12-xml/
[RDF]: https://www.w3.org/RDF/
[RDFa]: https://rdfa.info/docs
[Schema.org]: https://schema.org
[SPARQL]: https://sparql.dev
[StrictYAML]: https://hitchdev.com/strictyaml/
[structured data markup]: https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
[the figures post]: ./2026-03-08-figures.html
[the prev-next post]: ./2025-12-18-prev-next.html
[the previous post]: ./2026-04-12-external-meta.html
