"""Tests for XML generation."""

import io
import unittest

from mismiy.xml import Doc, Elt


class TestDoc(unittest.TestCase):
    def test_makes_root_element_namespace_the_default(self):
        doc = Doc("foo:bar", {"baz": "quux"}, {"foo": "https://foo.example/blort"})

        f = io.StringIO()
        doc.write_to(f)

        self.assertEqual(
            f.getvalue(),
            '<bar baz="quux" xmlns="https://foo.example/blort"/>\n',
        )

    def test_can_add_text_elements_and_they_are_indented(self):
        doc = Doc("foo:bar", namespaces={"foo": "https://foo.example/blort"})

        doc.element("foo:baz", {"xml:lang": "en"}, "quux")
        doc.element("foo:baz", {}, "quux2")

        self.assertEqual(
            doc.to_string(),
            '<bar xmlns="https://foo.example/blort">\n'
            '  <baz xml:lang="en">quux</baz>\n'
            "  <baz>quux2</baz>\n"
            "</bar>\n",
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
            '<bar xmlns="https://foo.example/blort" xmlns:bar="https://bar.example/zum">\n'
            "  <bar:glum/>\n"
            "</bar>\n",
        )

    def test_escapes_element_content(self):
        doc = Doc("foo:bar", namespaces={"foo": "https://foo.example/blort"})
        doc.element("foo:baz", "Hello & <world>!")

        self.assertEqual(
            doc.to_string(),
            '<bar xmlns="https://foo.example/blort">\n'
            "  <baz>Hello &amp; &lt;world&gt;!</baz>\n"
            "</bar>\n",
        )

    def test_escapes_attribute_content(self):
        doc = Doc(
            "foo:bar",
            {"greet": "Hello & <world>!"},
            namespaces={"foo": "https://foo.example/blort"},
        )

        self.assertEqual(
            doc.to_string(),
            '<bar greet="Hello &amp; &lt;world&gt;!" xmlns="https://foo.example/blort"/>\n',
        )

    def test_can_create_doc_from_elt(self):
        elt = Elt("foo:bar", {"baz": "quux"})
        elt.element("foo:quux2", "Hello, <world>!")

        doc = Doc.from_element(elt, {"foo": "https://foo.example/blort"})

        self.assertEqual(
            doc.to_string(),
            '<bar baz="quux" xmlns="https://foo.example/blort">\n'
            "  <quux2>Hello, &lt;world&gt;!</quux2>\n"
            "</bar>\n",
        )
