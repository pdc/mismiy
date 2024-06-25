"""Classes for generating XML documents, for people fussy about XML formatting."""

import io
from collections.abc import Mapping
from typing import Self
from xml.sax.saxutils import escape
from abc import abstractmethod, ABC

# Default namespace definitions. Individual Doc instances may override these.
NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",  # RFC 4287
    "fh": "http://purl.org/syndication/history/1.0",  # RFC 5005
}


class ElementBase(ABC):
    @abstractmethod
    def iter_prefixes(self):
        """Yield prefixes used for element or attributes.

        This is used when deciding which namespaces need declarations
        on the root element of the document.
        """

    @abstractmethod
    def write_to(self, out, *, indent=None, default_prefix=None):
        """Write the representation of this element and its content.

        Optional argument `indent` is used to add whitespace at
        the start of each line.

        Optional argument `default_prefix` is the prefix of a namespace
        that is assumed to have a default-namespace declaration,
        so qnames using that prefix should be changed to use no prefix.
        """

    def to_string(self):
        """Return the XML representation of this element and its content.

        Used in tests mostly.
        """
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


class Elt(ElementBase):
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

    def write_to(self, out, *, indent=None, default_prefix=None):
        """Write the representation of this element and its content.

        Optional argument `indent` is used to add whitespace at
        the start of each line.
        """
        return self._write_to(self.attrs, indent or "", default_prefix, out)

    def _write_to(self, attrs, indent: str, default_prefix: str | None, out):
        if default_prefix is not None:
            bad_attrs = [k for k in attrs.keys() if k.startswith(default_prefix)]
            if bad_attrs:
                raise ValueError(
                    f'Cannot represent attrs {", ".join(bad_attrs)} '
                    f'with default prefix {default_prefix.removesuffix(":")}'
                )
            etype = self.etype.removeprefix(default_prefix)
            attrs = {k.removeprefix(default_prefix): v for k, v in attrs.items()}
        else:
            etype = self.etype
        formatted = formatted = "".join(f' {k}="{escape(v)}"' for k, v in attrs.items())

        if self.elements:
            out.write(f"{indent}<{etype}{formatted}>\n")
            for elt in self.elements:
                elt.write_to(out, indent=indent + "  ", default_prefix=default_prefix)
            out.write(f"{indent}</{etype}>\n")
        elif self.text is not None:
            out.write(f"{indent}<{etype}{formatted}>{escape(self.text)}</{etype}>\n")
        else:
            out.write(f"{indent}<{etype}{formatted}/>\n")


class HtmlAsXhtml(ElementBase):
    """An XHTML div element containing XHTML supplied as an HTML string."""

    def __init__(self, html: str):
        pass

    def iter_prefixes():
        pass

    def write_to(self, attrs, indent: str, default_prefix: str | None, out):
        pass


class Doc(Elt):
    """A simple XML generator for XML.

    Disclaimer: this is not a general-purpose XML representation.
    It does *not* support mixed content (where text and elements
    are mixed up together), just a tree of elements with only the leaves
    containing text. This is the subset of XML used by Atom,
    site maps, and so on, if we ignore XHTML inclusions for now.

    The dictionary of namespaces is supplied in advance, but only
    the prefixes that are actually used will be declared in the output
    —this allows us to define all the prefixes we *might* use
    without worrying abut whether they are or not.

    As a further affectation the namespace of the root element will
    be made the default namespace at the root, and the qnames of
    elements and attributes adjusted accordingly. This makes no
    difference to the meaning of an XML document with namespaces,
    but might make a difference to parsers hacked together out of
    regexes.
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
        attrs = self.attrs

        # We need to add namespace declarations to the attrs of the root elt.
        prefixes = set(self.iter_prefixes())
        prefixes.discard("xml")
        prefix, colon, local_name = self.etype.partition(":")
        if colon:
            # Use namepsace prefix to root element as default namespace.
            default_prefix = prefix + ":"
            prefixes.discard(prefix)
            attrs["xmlns"] = self.namespaces[prefix]
        else:
            default_prefix = None
        attrs.update(
            {
                f"xmlns:{prefix}": self.namespaces[prefix]
                for prefix in sorted(prefixes)
                if prefix
            }
        )

        return self._write_to(attrs, "", default_prefix, out)

    @classmethod
    def from_element(cls, element: Elt, namespaces: Mapping[str, str]) -> Self:
        doc = cls(element.etype, element.attrs, namespaces, text=element.text)
        doc.elements = element.elements
        return doc
