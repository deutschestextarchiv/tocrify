# -*- coding: utf-8 -*-

from lxml import etree

import os
import Levenshtein
import yaml
import logging

ns = {
     'xlink' : "http://www.w3.org/1999/xlink",
     'xhtml' : "http://www.w3.org/1999/xhtml"
}
XLINK = "{%s}" % ns['xlink']
XHTML = "{%s}" % ns['xhtml']

class Mets2hocr:

    def __init__(self):
        """
        The constructor.
        """
        self.map = None

    @classmethod
    def read(cls, source):
        """
        Reads in mapping from a given (file) source.
        :param source: mapping (file) source.
        """
        if hasattr(source, 'read'):
            return cls.fromfile(source)
        if os.path.exists(source):
            return cls.fromfile(source)

    @classmethod
    def fromfile(cls, path):
        """
        Reads in mapping from a given file source.
        :param str path: Path to the mapping.
        """
        i = cls()
        i._fromfile(path)
        return i

    def _fromfile(self, path):
        """
        Reads in mapping from a given file source.
        :param str path: Path to the mapping.
        """
        self.map = yaml.safe_load(path)

    def get(self, mets_type, depth):
        """
        Returns the hOCR strucutural type for a
        given METS structural type and its depth.
        :param str mets_type: Name of the METS structural type.
        :param int depth: Depth of the METS structure within the struct_map
        """
        # FIXME: depth should never be less than 0
        if depth < 0:
            depth = 0
        return self.map[mets_type][depth]

class Hocr:

    def __init__(self, mets2hocr):
        """
        The constructor.
        """

        self.tree = None
        self.insert_index = 0
        self.path = ""
        self.text = ""
        self.line_index_struct = {}
        self.line_index = 0
        self.mets2hocr = mets2hocr

        # logging
        self.logger = logging.getLogger(__name__)
    
    def write(self, stream):
        """
        Writes the hOCR tree to stream.
        :param stream: The output stream.
        """
        stream.write(etree.tostring(self.tree.getroot(), encoding="utf-8"))

    @classmethod
    def read(cls, source, mets2hocr):
        """
        Reads in hOCR from a given (file) source.
        :param source: hOCR (file) source.
        """
        if hasattr(source, 'read'):
            return cls.fromfile(source, mets2hocr)
        if os.path.exists(source):
            return cls.fromfile(source, mets2hocr)

    @classmethod
    def fromfile(cls, path, mets2hocr):
        """
        Reads in hOCR from a given file source.
        :param str path: Path to a hOCR document.
        """
        i = cls(mets2hocr)
        i._fromfile(path)
        return i

    def _fromfile(self, path):
        """
        Reads in hOCR from a given file source.
        :param str path: Path to a hOCR document.
        """
        self.logger.info("Reading %s" % str(path))
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
                    # removes multiple whitespace introduced by pretty printing
                    # adds a final whitespace
                    line_text = " ".join("".join(line.itertext()).split()) + " "
                    if line_text:
                        self.text += line_text
                        for i in range(0, len(line_text)):
                            self.line_index_struct[self.line_index] = line
                            self.line_index += 1
        

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

    def get_next_unmodified_carea(self):
        """
        Returns the next available unmodified carea (or None).
        """
        try:
            return self.line_index_struct[self.insert_index].getparent().getparent()
        except:
            return None

    def set_carea_as_modified(self, carea):
        """
        Set the given carea as modified by adjusting the insert index.
        :param Element carea: The carea element to set as modified
        """
        for i in range(self.insert_index, len(self.line_index_struct)):
            if self.line_index_struct[self.insert_index].getparent().getparent() != carea:
                break
            self.insert_index = i
    
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
            for k in range(self.insert_index, len(text) - len(label)):
                distance = Levenshtein.distance(label, text[k:k+len(label)])
                if distance <= minimum:
                    minimum = distance
                    index = k
                if distance == 0:
                    break
            return (index, len(text[index:index+len(label)].strip()))
        return (-1,-1)

    def ingest_structure(self, logical):
        """
        Modifies the hOCR to incorporate the structural information
        represented by the mets.Logical parameter.
        :param Logical logical: The logical element to be ingested. 
        """
        ingested = False
        
        # ignore leading and closing whitespace
        label = logical.label.strip()
        # many structures are (regretfully) only labelled with 'Text'
        if len(label) > 0 and self.text and label != "Text":

            self.logger.debug("Search for '%s' %i" % (label, len(label)))

            begin, length = self.__get_best_insert_index(self.text, label, 0, True)

            # we have a suitable match (i.e. below the quality restriction),
            # full line labels are assumed,
            # all lines which contribute to the matching window are collected
            # to deal with multi-line labels
            if begin != -1:
                end = begin + length - 1
                cmp_lines = []
                pars = []
                for l in range(0, end - begin):
                    # append each line only once!
                    if (not cmp_lines) or cmp_lines[-1] != self.line_index_struct[begin + l]:
                        cmp_lines.append(self.line_index_struct[begin + l])
                        # get paragraph of line
                        par = cmp_lines[-1].getparent()
                        # add it to the first paragraph containing the match and subsequently
                        # move the lines around in order to create a single paragraph
                        # for each match
                        if not pars:
                            pars.append(par)
                        if pars[0] != par:
                            pars[0].append(self.line_index_struct[begin + l])

                            # FIXME: something is odd here, try catch should not be necessary
                            try:
                                par.remove(self.line_index_struct[begin + l])
                            except:
                                pass
                            # eventually delete paragraph
                            if len(par) == 0:
                                par.getparent().remove(par)

                if len(pars[0]) == len(cmp_lines):
                    # replace paragraph elment with hOCR element representation
                    pars[0].tag = XHTML + "h%i" % (logical.depth + 1)
                    # replace type attribute
                    pars[0].set("class", self.mets2hocr.get(logical.type, logical.depth))
                    ingested = True
                # par has to be split!
                # we create a new element and insert it before the paragraph which
                # contains multiple headings
                elif len(pars[0]) > len(cmp_lines):
                    new_h = etree.Element(XHTML + "h%i" % (logical.depth + 1))
                    new_h.set("class", self.mets2hocr.get(logical.type, logical.depth))
                    pars[0].getparent().insert(pars[0].getparent().index(pars[0]), new_h)
                    for i in range(0, len(cmp_lines)):
                        cmp_lines[i].getparent().remove(cmp_lines[i])
                        new_h.append(cmp_lines[i])
                    ingested = True

                # adjust the position for searching for the next match
                self.insert_index = end + 1
        
        # textless structures
        else:
            # covers and title pages span the whole page, insert an element directly under ocr_page
            if logical.type == "cover_front" or logical.type == "cover_back" or logical.type == "title_page" or logical.type == "spine":
                cover = etree.Element(XHTML + "div")
                cover.set("class", "ocr_%s" % logical.type)
                insert_node = self.tree.getroot().find(".//" + XHTML + "div[@class='ocr_page']")
                insert_node.insert(0, cover)
                for child in insert_node[1:]:
                    cover.append(child)
            # not sure what to do with textless structures of type other
            elif logical.type == u"other":
                pass
            # generic insertion
            else:
                carea = self.get_next_unmodified_carea()
                if carea is not None:
                    struct = etree.Element(XHTML + "h%i" % (logical.depth + 1))
                    struct.set("class", self.mets2hocr.get(logical.type, logical.depth))
                    carea.insert(0, struct)
                    self.set_carea_as_modified(carea)

        return ingested
