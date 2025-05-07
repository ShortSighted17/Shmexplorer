class Element:
    def __init__(self, tag, attributes, parent):
        # handling attributes
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.parent = parent
        
    def __repr__(self):
        printable_attributes = ""
        for attr in self.attributes:
            printable_attributes += " " + attr + " = " + self.attributes[attr]
        return "<" + self.tag +  printable_attributes + ">"