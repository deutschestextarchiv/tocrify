# -*- coding: utf-8 -*-

from lxml import etree

import os

ns = {
     'xlink' : "http://www.w3.org/1999/xlink",
     'xhtml' : "http://www.w3.org/1999/xhtml"
}
XLINK = "{%s}" % ns['xlink']
XHTML = "{%s}" % ns['xhtml']

class Hocr:

    def __init__(self):
        """
        The constructor.
        """

        self.tree = None
        self.path = ""

    @classmethod
    def read(cls, source):
        """
        Reads in hOCR from a given (file) source.
        :param source: hOCR (file) source.
        """
        if hasattr(source, 'read'):
            return cls.fromfile(source)
        if os.path.exists(source):
            return cls.fromfile(source)

    @classmethod
    def fromfile(cls, path):
        """
        Reads in hOCR from a given file source.
        :param str path: Path to a hOCR document.
        """
        i = cls()
        i._fromfile(path)
        return i

    def _fromfile(self, path):
        """
        Reads in hOCR from a given file source.
        :param str path: Path to a hOCR document.
        """
        self.tree = etree.parse(path)
        self._spur(self.tree, path)

    def _spur(self, tree, path):
        """
        Assigns the hOCR-related class members given an XML tree.
        """
        self.path = path

    def get_careas(self):
        """
        Returns an iterator on the careas elements.
        """
        for carea in self.tree.xpath()
            yield carea

    def ingest_structure(self, logical):
        """
        Modifies the hOCR to incorporate the structural information
        represented by the mets.Logical parameter.
        :param Logical logical: The logical element to be ingested. 
        """
        if logical.label != "Text":
            pass
