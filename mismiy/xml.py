"""Classes for generating XML documents, for people fussy about XML formatting."""

import io
from collections.abc import Mapping
from typing import Self
from xml.sax.saxutils import escape

# Default namespace definitions. Individual Doc instances may override these.
NAMESPACES = {
    "": "http://www.w3.org/1999/xhtml",
    "atom": "http://www.w3.org/2005/Atom",
}


class Elt:
    """One element in the XML document.

    The assumption is that it falls in to one of three categories:
    - no content at all;
    - content that is just text; or
    - content that is just nested elements/

    In other words, we do not support mixed content.
    """

    def __init__(self, etype: str, attrs: Mapping[str, str] = None, text: str = None):
        self.etype = etype
        self.attrs = attrs or {}
        self.text = text

        self.elements = []

    def element(
        self, etype: str, attrs: Mapping[str, str] | str = None, text: str = None
    ) -> "Elt":
        """Add a child element to this element."""
        if isinstance(attrs, str) and text is None:
            # Carelssly omitted the attributes.
            text = attrs
            attrs = {}
        return self.append(Elt(etype, attrs, text))

    def append(self, elt: "Elt") -> "Elt":
        self.elements.append(elt)
        return elt

    def iter_prefixes(self):
        """Yield prefixes used for element or attributes.

        This is used when deciding which namespaces need declarations
        on the root element of the document.
        """
        # If etype has no colon, it is default namespace.
        first, _, second = self.etype.partition(":")
        yield first if second else ""

        for qname in self.attrs:
            # If attr name has no colon, it is in no namespace.
            first, _, second = qname.partition(":")
            if second:
                yield first

        for elt in self.elements:
            yield from elt.iter_prefixes()

    def write_to(self, out, *, indent=None):
        """Write the representation of this ekement and its content.

        Optional argument `indent` is used to add whitespace at
        the start of each line.
        """
        return self._write_to(self.attrs, indent or "", out)

    def _write_to(self, attrs, indent: str, out):
        formatted = "".join(f' {k}="{escape(v)}"' for k, v in attrs.items())

        if self.elements:
            out.write(f"{indent}<{self.etype}{formatted}>\n")
            for elt in self.elements:
                elt.write_to(out, indent=indent + "  ")
            out.write(f"{indent}</{self.etype}>\n")
        elif self.text is not None:
            out.write(
                f"{indent}<{self.etype}{formatted}>{escape(self.text)}</{self.etype}>\n"
            )
        else:
            out.write(f"{indent}<{self.etype}{formatted}/>\n")

    def to_string(self):
        buf = io.StringIO()
        self.write_to(buf)
        return buf.getvalue()

    def find(self, etype: str, attrs: Mapping[str, str] = None) -> Self | None:
        """Used in tests to find a matching child element."""
        for element in self.elements:
            if element.etype == etype and (
                attrs is None or all(element.attrs[k] == v for k, v in attrs.items())
            ):
                return element


class Doc(Elt):
    """A simple XML generator for XML.

    Disclaimer: this is not a general-purpose XML representation.
    It does *not* support mixed content (where text and elements)
    are mixed up together, just a tree of elements with only the leaves
    containing text. This is the subset of XML used by Atom,
    site maps, and so on, if we ignore XHTML inclusions for now.

    The dictionary of namespaces is supplied in advance, but only
    the prefixes that are actually used will be declared in the output
    —this allos us to define all the prefixes we *might* use
    without worrying abut whether they are or not. The empty string
    is used for the entry for the default namespace. If it is not
    given a definition then it will be assumed it is bound to the
    XHTML namespace.
    """

    def __init__(
        self,
        etype: str,
        attrs: Mapping[str, str] = None,
        namespaces: Mapping[str, str] = None,
        *,
        text=None,
    ):
        super().__init__(etype, attrs, text)
        self.namespaces = NAMESPACES | (dict(namespaces) if namespaces else {})

    def write_to(self, out):
        prefixes = set(self.iter_prefixes())
        prefixes.discard("xml")
        namespaces = {
            (f"xmlns:{prefix}" if prefix else "xmlns"): self.namespaces[prefix]
            for prefix in sorted(prefixes)
        }
        attrs = self.attrs | namespaces
        return self._write_to(attrs, "", out)

    @classmethod
    def from_element(cls, element: Elt, namespaces: Mapping[str, str]) -> Self:
        doc = cls(element.etype, element.attrs, namespaces, text=element.text)
        doc.elements = element.elements
        return doc
