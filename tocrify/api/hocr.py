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

hocr2mets = {
    ("chapter", 0 ) : "ocr_chapter",
    ("section", 0 ) : "ocr_chapter",
    ("title_page", 0 ) : "ocr_title_page",
    ("contents", 0 ) : "ocr_contents",
    ("preface", 0 ) : "ocr_preface",
    ("illustration", 0 ) : "ocr_illustration",
    ("index", 0 ) : "ocr_index",
    ("index", 1 ) : "ocr_index",
    ("cover_back", 0 ) : "ocr_chapter",
    ("dedication", 0 ) : "ocr_dedication",
    ("map", 0 ) : "ocr_map",
    ("additional", 0 ) : "ocr_additional",
    ("chapter", 1 ) : "ocr_section",
    ("section", 1 ) : "ocr_section",
    ("preface", 1 ) : "ocr_preface",
    ("illustration", 1 ) : "ocr_illustration",
    ("dedication", 1 ) : "ocr_dedication",
    ("title_page", 1 ) : "",
    ("contents", 1 ) : "ocr_contents",
    ("chapter", 2 ) : "ocr_subsection",
    ("section", 2 ) : "ocr_subsection",
    ("chapter", 3 ) : "ocr_subsubsection",
    ("section", 3 ) : "ocr_subsubsection"
}

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
    
    def write(self, stream):
        """
        Writes the hOCR tree to stream.
        :param stream: The output stream.
        """
        stream.write(etree.tostring(self.tree.getroot(), encoding="utf-8"))

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
        :param Element par: The paragraph element to iterate on.
        """
        for line in par.xpath("./xhtml:span[@class=\"ocr_line\"]", namespaces=ns):
            yield line
    
    def __get_best_insert_index(self, text, label, minimum=0, lower=False):
        """
        Finds the "closest" match (wrt. to Levenshtein distance)
        for a shorter within a longer string. Returns -1 if a
        given minimal string distance is not reached.
        :param String text: The longer string.
        :param String label: The shorter string.
        :param Integer minimum: The maximal allowed edit distance between the two.
        :param Boolean lower: Compute the edit distance on lowercased strings.
        """
        if lower:
            text = text.lower()
            label = label.lower()

        if len(text) >= len(label):
            if not minimum:
                minimum = len(label) / 2
            index = -1
            # the moving window
            for k in range(0, len(text) - len(label)):
                distance = Levenshtein.distance(label, text[k:k+len(label)])
                if distance <= minimum:
                    minimum = distance
                    index = k
                if distance == 0:
                    break
            return index
        return -1

    def ingest_structure(self, logical):
        """
        Modifies the hOCR to incorporate the structural information
        represented by the mets.Logical parameter.
        :param Logical logical: The logical element to be ingested. 
        """
        ingested = False

        # many structures are (regretfully) only labelled with 'Text'
        if len(logical.label) > 0 and self.text and logical.label != "Text":
            
            begin = self.__get_best_insert_index(self.text, logical.label, 0, True)

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

                            # Fixme: something is odd here, try catch should not be necessary
                            try:
                                par.remove(self.index_struct[begin + l])
                            except:
                                pass
                            # eventually delete paragraph
                            if len(par) == 0:
                                par.getparent().remove(par)

                # TODO: compare number of lines in paragraph to number of matched lines!!!
                if len(pars[0]) == len(cmp_lines):
                    # replace paragraph elment with hOCR element representation
                    pars[0].tag = XHTML + "h%i" % logical.depth
                    # replace type attribute
                    pars[0].set("class", hocr2mets[(logical.type,logical.depth)])
                    ingested = True

        return ingested
