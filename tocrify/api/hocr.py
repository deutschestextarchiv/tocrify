# -*- coding: utf-8 -*-

from lxml import etree

import os
import Levenshtein

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
        # many structures are (regretfully) only labelled with 'Text'
        if len(logical.label) > 0 and self.text and logical.label != "Text":

            # restriction on match quality, parameter?
            minimum = len(logical.label) / 2
            
            # the moving window
            begin = -1
            for k in range(0, len(self.text) - len(logical.label)):
                distance = Levenshtein.distance(logical.label, self.text[k:k+len(logical.label)])
                if distance <= minimum:
                    minimum = distance
                    begin = k
                if distance == 0:
                    break

            # we have a suitable match (i.e. below the quality restriction),
            # full line labels are assumed,
            # all lines which contribute to the matching window are collected
            # to deal with multi-line labels
            if begin != -1:
                end = begin + len(logical.label) - 1
                cmp_lines = []
                pars = []
                for l in range(0, end - begin):
                    # append each line only once!
                    if (not cmp_lines) or cmp_lines[-1] != self.index_struct[begin + l]:
                        cmp_lines.append(self.index_struct[begin + l])
                        # get paragraph of line
                        par = cmp_lines[-1].getparent()
                        # add it to the first paragraph containing the match and subsequenty
                        # move the lines around in order to create a single paragraph
                        # for each match
                        if not pars:
                            pars.append(par)
                        elif pars[0] != par:
                            pars[0].append(self.index_struct[begin + l])
                            par.remove(self.index_struct[begin + l])
                            # eventually delete paragraph
                            if len(par) == 0:
                                par.getparent().remove(par)

                # TODO: compare number of lines in paragraph to number of matched lines!!!
                print(len(pars[0]),len(cmp_lines))

                for cmp_line in cmp_lines:
                    print(cmp_line.text)
