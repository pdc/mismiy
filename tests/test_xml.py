"""Tests for XML generation."""

import io
import unittest

from mismiy.xml import Doc, Elt


class TestDoc(unittest.TestCase):
    def test_starts_with_a_root_element(self):
        doc = Doc("foo:bar", {"baz": "quux"}, {"foo": "https://foo.example/blort"})

        f = io.StringIO()
        doc.write_to(f)

        self.assertEqual(
            f.getvalue(),
            '<foo:bar baz="quux" xmlns:foo="https://foo.example/blort"/>\n',
        )

    def test_can_add_text_elements_and_they_are_indented(self):
        doc = Doc("foo:bar", namespaces={"foo": "https://foo.example/blort"})

        doc.element("foo:baz", {"xml:lang": "en"}, "quux")
        doc.element("foo:baz", {}, "quux2")

        self.assertEqual(
            doc.to_string(),
            '<foo:bar xmlns:foo="https://foo.example/blort">\n'
            '  <foo:baz xml:lang="en">quux</foo:baz>\n'
            "  <foo:baz>quux2</foo:baz>\n"
            "</foo:bar>\n",
        )

    def test_omits_unused_namespaces(self):
        doc = Doc(
            "foo:bar",
            namespaces={
                "foo": "https://foo.example/blort",
                "bar": "https://bar.example/zum",
                "baz": "https://baz.example/wibble",
            },
        )

        doc.element("bar:glum")

        self.assertEqual(
            doc.to_string(),
            '<foo:bar xmlns:bar="https://bar.example/zum" xmlns:foo="https://foo.example/blort">\n'
            "  <bar:glum/>\n"
            "</foo:bar>\n",
        )

    def test_allows_default_namespace(self):
        doc = Doc("html", namespaces={"": "http://www.w3.org/1999/xhtml"})
        doc.element("div", {"xml:lang": "en"}, "Hello, world.")

        self.assertEqual(
            doc.to_string(),
            '<html xmlns="http://www.w3.org/1999/xhtml">\n'
            '  <div xml:lang="en">Hello, world.</div>\n'
            "</html>\n",
        )

    def test_escapes_element_content(self):
        doc = Doc("foo:bar", namespaces={"foo": "https://foo.example/blort"})
        doc.element("foo:baz", "Hello & <world>!")

        self.assertEqual(
            doc.to_string(),
            '<foo:bar xmlns:foo="https://foo.example/blort">\n'
            "  <foo:baz>Hello &amp; &lt;world&gt;!</foo:baz>\n"
            "</foo:bar>\n",
        )

    def test_escapes_attribute_content(self):
        doc = Doc(
            "foo:bar",
            {"greet": "Hello & <world>!"},
            namespaces={"foo": "https://foo.example/blort"},
        )

        self.assertEqual(
            doc.to_string(),
            '<foo:bar greet="Hello &amp; &lt;world&gt;!" xmlns:foo="https://foo.example/blort"/>\n',
        )

    def test_can_create_doc_from_elt(self):
        elt = Elt("foo:bar", {"foo:foo": "quux"})
        elt.element("foo:baz", "Hello, <world>!")

        doc = Doc.from_element(elt, {"foo": "https://foo.example/blort"})

        self.assertEqual(
            doc.to_string(),
            '<foo:bar foo:foo="quux" xmlns:foo="https://foo.example/blort">\n'
            "  <foo:baz>Hello, &lt;world&gt;!</foo:baz>\n"
            "</foo:bar>\n",
        )
