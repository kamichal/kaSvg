#!/usr/bin/python
'''
Created on 30 Dec 2015

@author: kamichal, basing on aroberge work

This module contains all the classes required to easily create an xml
document containing svg diagrams.

'''
from random import choice

def _indentStr(level):
    return level * '  '

def _randomID():
    s = 'abcdefghijklmnopqrstuvwxyz'
    s += s.upper() + '1234567890' + '_' * 30
    return 'id_' + ''.join(choice(s) for _ in xrange(10))

class XmlElement(object):
    def __init__(self, tag, prefix='', **attributes):
        self._tag = tag
        self._prefix = prefix
        self._subs = []
        self._attributes = {}
        if attributes:
            if len(attributes) == 1 and 'dd' in attributes:
                if isinstance(attributes['dd'], dict):
                    attributes = attributes['dd']
            for key in attributes:
                fixattr = key.replace('_', '-').lower()
                self._attributes[fixattr] = attributes[key]
                '''lower case is needed for converting 'Class'
                (class is forbiden in such use)
                you pass stroke_width=0.2 and it's being converted to
                stroke-widt=0.2'''

    def addAttr(self, **attributes):
        if attributes:
            for key in attributes:
                fixattr = key.replace('_', '-').lower()
                self._attributes[fixattr] = attributes[key]

    def append(self, other):
        self._subs.append(other)

    def __repr__(self):
        return self.indRepr(0)

    def _reprAttributes(self, indentLevel):
        render = []
        lines = 1
        for i, att in enumerate(self._attributes):
            if att != 'text':
                render.append('%s="%s"' % (att, self._attributes[att]))
                # wrap line if too long, unless it's the last element
                if len(' '.join(render)) > lines * 80 and i < len(self._attributes) - 1:
                    render.append('\n%s' % (_indentStr(indentLevel + 1)))
                    lines = lines + 1
        return ' '.join(render)

    def _reprSubelements(self, indentLevel):
        r = []
        if 'text' in self._attributes:
            r.append('%s%s\n' % (_indentStr(indentLevel + 1),
                                 self._attributes['text']))
        if self._subs:
            for elem in self._subs:
                r.append('%s' % elem.indRepr(indentLevel + 1))
        return ''.join(filter(None, r))

    def indRepr(self, indentLevel=0):
        ind = _indentStr(indentLevel)
        tag = ':'.join(filter(None, [self._prefix, self._tag]))
        atts = self._reprAttributes(indentLevel)
        h = ' '.join(filter(None, [tag, atts]))
        subs = self._reprSubelements(indentLevel + 1)
        if subs:
            r = '''{0}<{1}>\n{2}{0}</{3}>\n'''.format(ind, h, subs, tag)
        else:
            r = '''{0}<{1}/>\n'''.format(ind, h)
        return r

    def store(self, thatfilename):
        with open(thatfilename, 'w') as ff:
            ff.write(str(self))


class SvgStyleDefinitionEntry(object):
    def __init__(self, name, **attrList):
        self.name = name
        self._attributes = {}
        if attrList is not None:
            for attKey in attrList.keys():
                fixattr = attKey.replace('_', '-').lower()
                self._attributes[fixattr] = attrList[attKey]

    def indRepr(self, indentLevel=0):
        render = ['%s%s {\n' % (_indentStr(indentLevel), self.name)]
        for att in self._attributes:
            render.append('%s%s: %s;\n' % (_indentStr(indentLevel + 1), att, self._attributes[att]))
        render.append('%s}\n' % (_indentStr(indentLevel)))
        return ''.join(render)

    def append(self, **attrList):
        '''not sure if it's ok'''
        # self._attributes = {self._attributes, attrList}
        self._attributes = dict(zip(self._attributes, attrList))


class SvgStylesContainer(XmlElement):
    def __init__(self):
        XmlElement.__init__(self, 'style', type="text/css")

    def append(self, _SvgStyleDefinitionEntry):
        self._subs.append(_SvgStyleDefinitionEntry)

    def _reprSubelements(self, indentLevel):
        if self._subs:
            s = []
            for elem in self._subs:
                s.append('%s' % elem.indRepr(indentLevel + 1))
            stylesstr = ''.join(filter(None, s))
            return '{0}<![CDATA[\n{0}{1}]]>'.format(_indentStr(indentLevel),
                                                    stylesstr)
        else:
            return ''

    def isEmpty(self):
        return not self._subs

class SvgDefs(XmlElement):
    def __init__(self, **attributes):
        XmlElement.__init__(self, 'defs', **attributes)
        self._styles = SvgStylesContainer()

    def createNewStyle(self, name, **attrList):
        '''http://blogs.adobe.com/webplatform/2013/01/08/svg-styling/'''
        self._styles.append(SvgStyleDefinitionEntry(name, **attrList))

    def isEmpty(self):
        return not self._subs and self._styles.isEmpty()

    def _reprSubelements(self, indentLevel):
        r = []
        if not self._styles.isEmpty():
            r.append(self._styles.indRepr(indentLevel + 1))
        if self._subs:
            for elem in self._subs:
                r.append('%s' % elem.indRepr(indentLevel + 1))
        return ''.join(r)

class SvgWindow(XmlElement):
    def __init__(self, width, height, **attributes):
        attributes['width'] = width
        attributes['height'] = height
        XmlElement.__init__(self, 'svg', **attributes)
        self._attributes['xmlns'] = 'http://www.w3.org/2000/svg'
        self._attributes['xmlns:xlink'] = 'http://www.w3.org/1999/xlink'
        self._defs = SvgDefs()

    def append(self, other):
        if isinstance(other, SvgStyleDefinitionEntry):
            self._defs._styles.append(other)
        elif isinstance(other, ShapesGroup):
            self._defs.append(other)
        else:
            self._subs.append(other)

    def _reprSubelements(self, indentLevel):
        r = []
        if not self._defs.isEmpty():
            r.append(self._defs.indRepr(indentLevel))
        if 'text' in self._attributes:
            r.append('%s%s\n' % (_indentStr(indentLevel + 1),
                                 self._attributes['text']))
        if self._subs:
            for elem in self._subs:
                r.append('%s' % elem.indRepr(indentLevel + 1))
        return ''.join(filter(None, r))

    def __repr__(self):
        return self.indRepr(0)

    def useElement(self, xlinkId, x, y, **attributes):
        extraTransform = ''
        for att in attributes:
            if att == 'transform':
                extraTransform = extraTransform + ' ' + attributes[att]
                break
        attributes['transform'] = 'translate(%g, %g)%s' % (x, y, extraTransform)
        attributes['xlink:href'] = '#%s' % (xlinkId)
        self.append(XmlElement('use', **attributes))


class DefineSvgGroup(XmlElement):
    def __init__(self, defId, SvgDefContainer, **attributes):
        attributes['id'] = defId
        XmlElement.__init__(self, 'g', **attributes)
        SvgDefContainer.append(self)


class ShapesGroup(XmlElement):
    def __init__(self, group_ID, *objects, **attributes):
        if not group_ID:
            group_ID = _randomID()
        attributes['id'] = group_ID
        XmlElement.__init__(self, 'g', **attributes)
        if objects:
            for o in objects:
                self._subs.append(o)


class XmlComment(object):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return '<!-- [ ' + self.text + ' ] -->\n'

    def indRepr(self, indentLevel):
        return '%s%s' % (_indentStr(indentLevel), self)

