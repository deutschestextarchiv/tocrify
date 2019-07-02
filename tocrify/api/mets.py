# -*- coding: utf-8 -*-

from lxml import etree

import os

ns = {
     'mets': 'http://www.loc.gov/METS/',
     'xlink' : "http://www.w3.org/1999/xlink",
}
METS = "{%s}" % ns['mets']
XLINK = "{%s}" % ns['xlink']

class Logical:
    """
    Represents a div node in the logical struct map.
    """

    def __init__(self,node,depth=0):
        """
        The constructor.
        """

        self.log_id = node.get("ID")
        self.type = node.get("TYPE")
        self.label = node.get("LABEL", "")
        self.order = node.get("ORDER", "")
        self.depth = depth

class Physical:
    """
    Represents a page-related div node in the physical struct map.
    """

    def __init__(self, node):
        """
        The constructor.
        """
        self.phys_id = node.get("ID")
        # addressed ID formats:
        # HOCR+ID (e.g. 'HOCR1856940')
        # ID+HOCR (e.g. 'FILE_0010_FULLTEXT_HOCR')
        self.hocr_id = node.xpath("./mets:fptr[contains(@FILEID, \"HOCR\")]", namespaces=ns)[0].get("FILEID")

class FileHocr:
    """
    Represents a hOCR-related file node in the fulltext file group.
    """

    def __init__(self, node):
        """
        The constructor.
        """
        self.hocr_id = node.get("ID")
        self.file_name = node.find("./" + METS + "FLocat").get(XLINK + "href")

class Mets:

    def __init__(self):
        """
        The constructor.
        """

        self.tree = None
        self.structMap_logical = None
        self.structMap_physical = None
        self.structLink = None
        self.fileGrp_hocr = None
        self.file_order = {}

    @classmethod
    def read(cls, source):
        """
        Reads in METS from a given (file) source.
        :param source: METS (file) source.
        """
        if hasattr(source, 'read'):
            return cls.fromfile(source)
        if os.path.exists(source):
            return cls.fromfile(source)

    @classmethod
    def fromfile(cls, path):
        """
        Reads in METS from a given file source.
        :param str path: Path to a METS document.
        """
        i = cls()
        i.__fromfile(path)
        return i

    def __fromfile(self, path):
        """
        Reads in METS from a given file source.
        :param str path: Path to a METS document.
        """
        self.tree = etree.parse(path)
        self.__spur(self.tree)

    def __spur(self, tree):
        """
        Assigns the METS-related class members given an XML tree.
        """
        self.structMap_logical = tree.getroot().find(".//" + METS + "structMap[@TYPE='LOGICAL']")
        self.structMap_physical = tree.getroot().find(".//" + METS + "structMap[@TYPE='PHYSICAL']")
        self.structLink = tree.getroot().find(".//" + METS + "structLink")
        self.fileGrp_hocr = tree.getroot().find(".//" + METS + "fileGrp[@USE='FULLTEXT HOCR']")
        self.__determine_file_order()

    def __determine_file_order(self):
        """
        Determines the file order given the ORDER attributes of the divs in the physical structMap
        """
        for physSequence in self.structMap_physical.findall("./" + METS + "div[@TYPE='physSequence']"):
            for div in physSequence.findall(METS + "div"):
                self.file_order[int(div.get("ORDER"))] = div.get("ID")

    def get_physical(self, phys_id):
        """
        Returns the element of the physical structMap which has the given
        phys_id.
        :param str phys_id: Id of the requested element.
        """
        return Physical(self.structMap_physical.xpath(".//mets:div[@ID=\"%s\"]" % phys_id, namespaces=ns)[0])

    def get_logicals(self):
        """
        Returns an iterator on the elements in the logical struct map.
        """
        if self.structMap_logical is not None:
            stack = []
            stack.append(iter([self.structMap_logical]))
            skipped = 0
            while stack:
                e = next(stack[-1], None)
                if e == None:
                    stack.pop()
                else:
                    stack.append(iter(e))
                    # skip the title element (has ADMID)
                    if (e.tag == METS + "div") and not e.get("ADMID"):
                        yield (Logical(e, stack.__len__() - skipped - 1))
                    else:
                        skipped += 1

    def get_first_physical_for_logical(self, logical, backwards=False):
        """
        Returns the first exisiting div element from the physical struct map corresponding to
        the given logical element (via a struct link).
        :param Logical logical: The logical element to be evaluated.
        :param Boolean backwards: Search backwards if no direct match is possible
        """
        if self.structLink is not None:
            sm_links = self.structLink.xpath("./mets:smLink[@xlink:from=\"%s\"]" % logical.log_id, namespaces=ns)
            first_phys_id = sm_links[0].get(XLINK + 'to')
            physicals = self.structMap_physical.xpath(".//mets:div[@TYPE=\"page\" and @ID=\"%s\"]" % first_phys_id, namespaces=ns)
            # direct match, i.e. same strategy for forward and backward search
            if len(physicals) > 0:
                return Physical(physicals[0])
            # search for the first existing ID
            else:
                for sm_link in sm_links[1:]:
                    phys_id = sm_link.get(XLINK + 'to')
                    physicals = self.structMap_physical.xpath(".//mets:div[@TYPE=\"page\" and @ID=\"%s\"]" % phys_id, namespaces=ns)
                    if len(physicals) > 0:
                        # forward search is simple
                        if backwards == False:
                            return Physical(physicals[0])
                        # backward search uses `ORDER`
                        else:
                            order = int(physicals[0].get("ORDER"))
                            return self.get_physical(self.file_order[order - 1])

    def get_hocr_for_physical(self, physical):
        """
        Returns the file element which has an ID which corresponds to the hocr_id of the physical
        parameter.
        :param Physical physical: Div element from the METS's structMap[@TYPE="physical"].
        """
        if self.fileGrp_hocr is not None:
            return FileHocr(self.fileGrp_hocr.xpath("./mets:file[@ID=\"%s\"]" % physical.hocr_id, namespaces=ns)[0])
