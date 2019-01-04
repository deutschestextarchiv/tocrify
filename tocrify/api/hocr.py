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
        self.text = ""
        self.index_struct = {}
        self.index = 0

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

        # collect text and save line numbers
        for carea in self.get_careas():
            for par in self.get_pars_in_carea(carea):
                for line in self.get_lines_in_par(par):
                    if line.text:
                        self.text += line.text
                        for i in range(0, len(line.text)):
                            self.index_struct[self.index] = line
                            self.index += 1
        

    def get_careas(self):
        """
        Returns an iterator on the careas elements.
        """
        for carea in self.tree.xpath(".//xhtml:div[@class=\"ocr_carea\"]", namespaces=ns):
            yield carea

    def get_pars_in_carea(self, carea):
        """
        Returns an iterator on the paragraphs within a carea element.
        """
        for par in carea.xpath("./xhtml:p", namespaces=ns):
            yield par

    def get_lines_in_par(self, par):
        """
        Returns an iterator on the lines within a p element.
        """
        for line in par.xpath("./xhtml:span[@class=\"ocr_line\"]", namespaces=ns):
            yield line

    def ingest_structure(self, logical):
        """
        Modifies the hOCR to incorporate the structural information
        represented by the mets.Logical parameter.
        :param Logical logical: The logical element to be ingested. 
        """
        if logical.label != "Text" or (not self.text):
            pass
        print(logical.label)

        begin = -1
        # restriction on match quality, parameter?
        minimum = len(logical.label) / 2
