# -*- coding: utf-8 -*-

from lxml import etree

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

class Mets:

    def __init__(self):
        """
        The constructor.
        """

        self.tree = None
        self.structMap_logical = None
        self.structMap_physical = None
        self.structLink = {}

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
        i._fromfile(path)
        return i

    def _fromfile(self, path):
        """
        Reads in METS from a given file source.
        :param str path: Path to a METS document.
        """
        self.tree = etree.parse(path)
        self._spur(self.tree)

    def _spur(self, tree):
        """
        Assigns the METS-related class members given an XML tree.
        """
        self.structMap_logical = tree.getroot().find(".//" + METS + "structMap[@TYPE='LOGICAL']")
        self.structMap_physical = tree.getroot().find(".//" + METS + "structMap[@TYPE='PHYSICAL']")
        self.structLink = tree.getroot().find(".//" + METS + "structLink")


    def get_logicals(self):
        """
        Returns an iterator over the elements if the logical struct map.
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
                    if (e.tag == METS + "div") and e.get("DMDID") == None:
                        yield (Logical(e, stack.__len__() - skipped - 1))
                    else:
                        skipped += 1

    def get_first_physical_for_logical(self, logical):
        """
        Returns the first exisiting div element from the physical struct map corresponding to
        the given logical element (via a struct link).
        """
        if self.structLink is not None:
            for sm_link in self.structLink.xpath("./mets:smLink[@xlink:from=\"%s\"]" % logical.log_id, namespaces=ns):
                phys_id = sm_link.get(XLINK + 'to')
                physicals = self.structMap_physical.xpath(".//mets:div[@TYPE=\"page\" and @ID=\"%s\"]" % phys_id, namespaces=ns)
                if len(physicals) > 0:
                    return physicals[0]
        return None
