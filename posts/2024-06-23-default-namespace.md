title: Making the feed document use the default XML namespace
published: 2024-06-23
author: Damian Cugley
tags:
- Atom
- XML

When I wrote about [implementing the Atom format][1], I said that XML
processors should not care what namespace prefix we use in the XML.
The [Feed Validator] suggests that some readers might still be confused
by this. So I have, somewhat annoyed, elaborated my XML writer to use
the default namespace feature.

Before it would generate something starting as follows:

```xml
<atom:feed xmlns:atom="http://www.w3.org/2005/Atom">
  <atom:id>urn:uuid:25082a25-c80c-520b-82dc-b36ed5123c3d</atom:id>
  <atom:title>Mismiy build log</atom:title>
```

This has changed to start like this:

```xml
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>urn:uuid:25082a25-c80c-520b-82dc-b36ed5123c3d</id>
  <title>Mismiy build log</title>
```

To a namespace-aware XML processor the two are equivalent. To a
processor that attempts to second-guess XML to cope with badly
formatted feeds, this might make all the difference.






[1]: 2024-05-26-atom.html
[Feed Validator]: https://validator.w3.org/feed/
