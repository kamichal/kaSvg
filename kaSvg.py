#!/usr/bin/python
'''
Created on 30 Dec 2015

@author: kamichal, basing on aroberge work

This module contains all the classes required to easily create an xml
document containing svg diagrams.

'''
import random

def _indentStr(level):
    return level * "  "

def _randomID():
    s = 'abcdefghijklmnopqrstuvwxyz'
    s += s.upper() + '1234567890' + '_' * 30
    return 'id_' + ''.join(random.choice(s) for _ in xrange(10))

class XmlElement(object):
    '''Prototype from which all the xml elements are derived.
       By design, this enables all elements to automatically give a
       text representation of themselves.'''

    def __init__(self, tag, **attributes):
        '''A basic definition that will be replaced by the specific
           one required by any element.'''
        self.tag = tag
        self.prefix = ""
        self.sub_elements = []
        self.attributes = {}
        if attributes:
            if len(attributes) == 1 and "dd" in attributes:
                if isinstance(attributes["dd"], dict):
                    attributes = attributes["dd"]
            for key in attributes:
                fixattr = key.replace('_', '-').lower()
                self.attributes[fixattr] = attributes[key]
                '''lower case is needed for converting 'Class'
                (class is forbiden in such use)
                you pass stroke_width=0.2 and it's being converted to
                stroke-widt=0.2'''

    def addAttr(self, **attributes):
        if attributes:
            for key in attributes:
                fixattr = key.replace('_', '-').lower()
                self.attributes[fixattr] = attributes[key]

    def __repr__(self):
        return self.indRepr(0)

    def append(self, other):
        self.sub_elements.append(other)

    def indRepr(self, indentLevel=0):
        render = ["%s<%s%s" % (_indentStr(indentLevel), self.prefix, self.tag)]
        lines = 1
        for i, att in enumerate(self.attributes):
            if att != 'text':
                render.append(' %s="%s"' % (att, self.attributes[att]))
                # wrap line if too long, unless it's the last element
                if len(''.join(render)) > lines * 80 and i < len(self.attributes) - 1:
                    render.append("\n%s" % (_indentStr(indentLevel + 1)))
                    lines = lines + 1

        if 'text' in self.attributes:
            render.append(">%s</%s%s>\n" % (self.attributes['text'],
                                            self.prefix, self.tag))
        elif self.sub_elements:
            render.append(">\n")
            for elem in self.sub_elements:
                render.append("%s" % elem.indRepr(indentLevel + 1))
            render.append("%s</%s%s>\n" % (_indentStr(indentLevel), self.prefix, self.tag))
        else:
            render.append("/>\n")

        return ''.join(render)


class SvgWindow(XmlElement):
    def __init__(self, width, height, **attributes):
        attributes["width"] = width
        attributes["height"] = height
        XmlElement.__init__(self, "svg", **attributes)
        self.attributes["xmlns"] = "http://www.w3.org/2000/svg"
        self.attributes["xmlns:xlink"] = "http://www.w3.org/1999/xlink"

    def __repr__(self):
        return self.indRepr(0)

    def useElement(self, xlinkId, x, y, **attributes):
        extraTransform = ""
        for att in attributes:
            if att == "transform":
                extraTransform = extraTransform + " " + attributes[att]
                break
        attributes["transform"] = "translate(%g, %g)%s" % (x, y, extraTransform)
        attributes["xlink:href"] = "#%s" % (xlinkId)
        self.append(XmlElement("use", **attributes))

    def store(self, thatfilename):
        with open(thatfilename, 'w') as ff:
            ff.write(str(self))


class SvgStyleDefinitionEntry(object):
    def __init__(self, name, **attrList):
        self.name = name
        self.attributes = {}
        if attrList is not None:
            for attKey in attrList.keys():
                fixattr = attKey.replace('_', '-').lower()
                '''you pass stroke_width=0.2 and it needs to be
                converted to stroke-widt=0.2'''
                self.attributes[fixattr] = attrList[attKey]

    def indRepr(self, indentLevel=0):
        render = ["%s%s {\n" % (_indentStr(indentLevel), self.name)]
        for att in self.attributes:
            render.append("%s%s: %s;\n" % (_indentStr(indentLevel + 1), att, self.attributes[att]))
        render.append("%s}\n" % (_indentStr(indentLevel)))
        return ''.join(render)

    def append(self, **attrList):
        '''not sure if it's ok'''
        # self.attributes = {self.attributes, attrList}
        self.attributes = dict(zip(self.attributes, attrList))


class SvgStylesContainer(XmlElement):
    def __init__(self):
        self.styles = []

    def append(self, _SvgStyleDefinitionEntry):
        self.styles.append(_SvgStyleDefinitionEntry)

    def indRepr(self, indentLevel=0):
        if self.styles:
            render = ["%s<style type=\"text/css\">\n" % (_indentStr(indentLevel))]
            render.append("%s<![CDATA[\n" % (_indentStr(indentLevel + 1)))
            for styleClass in self.styles:
                render.append(styleClass.indRepr(indentLevel + 2))
            render.append("%s]]>\n" % (_indentStr(indentLevel + 1)))
            render.append("%s</style>\n" % (_indentStr(indentLevel)))
            return ''.join(render)
        else:
            return ''


class SvgDefinitionsContainer(XmlElement):
    '''Short-cut to create svg defs.  A user creates an instance of this
    object and simply appends other svg Elements'''
    def __init__(self):
        # self.root = XmlElement("svg", width=0, height=0)
        self.root = XmlElement("defs")
        self.styles = SvgStylesContainer()
        self.root.append(self.styles)

    def append(self, other):
        '''appends other to defs sub-element, instead of root element'''
        self.root.append(other)

    def newStyle(self, name, **attrList):
        '''http://blogs.adobe.com/webplatform/2013/01/08/svg-styling/'''
        self.styles.append(SvgStyleDefinitionEntry(name, **attrList))

    def indRepr(self, indentLevel):
        return "\n" + self.root.indRepr(indentLevel) + "\n"


class DefineSvgGroup(XmlElement):
    def __init__(self, defId, SvgDefContainer, **attributes):
        if not defId:
            defId = _randomID()
        attributes["id"] = defId
        XmlElement.__init__(self, "g", **attributes)
        SvgDefContainer.append(self)


class XmlComment(object):
    '''Comment that can be inserted in code xml documents'''
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "<!-- [ " + self.text + " ] -->\n"

    def indRepr(self, indentLevel):
        return "%s%s" % (_indentStr(indentLevel), self)

