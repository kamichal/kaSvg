#!/usr/bin/python
'''
Created on 30 Dec 2015

@author: kamichal, basing on aroberge work

This module contains all the classes required to easily create an xml
document containing svg diagrams.

'''
from random import choice
from textwrap import TextWrapper

_MAX_LINE_WIDTH = 80

def _indentStr(level):
    return level * '    '

def _randomID():
    s = 'abcdefghijklmnopqrstuvwxyz'
    s += s.upper() + '1234567890' + '_' * 30
    return 'id_' + ''.join(choice(s) for _ in xrange(10))

class kaSvgError(Exception):
    pass

class XmlElement(object):
    def __init__(self, tag, prefix='', **attributes):
        self._tag = tag
        self._prefix = prefix
        self._subs = []
        self._attrs = {}
        if attributes:
            if len(attributes) == 1 and 'dd' in attributes:
                if isinstance(attributes['dd'], dict):
                    attributes = attributes['dd']
            for key in attributes:
                fixattr = key.replace('_', '-').lower()
                self._attrs[fixattr] = attributes[key]
                '''lower case is needed for converting 'Class'
                (class is forbiden in such use)
                you pass stroke_width=0.2 and it's being converted to
                stroke-widt=0.2'''

    def addAttr(self, **attributes):
        if attributes:
            for key in attributes:
                fixattr = key.replace('_', '-').lower()
                self._attrs[fixattr] = attributes[key]

    def append(self, other):
        self._subs.append(other)

    def __repr__(self):
        return self.indRepr(0)

    def _reprAttributes(self, indent_level):
        r = ['%s="%s"' % (k, self._attrs[k]) for k in self._attrs if k != 'text']
        w = TextWrapper(width=_MAX_LINE_WIDTH, break_on_hyphens=False,
                        subsequent_indent=_indentStr(indent_level))
        l = w.wrap(' '.join(r))
        return '\n'.join(l)

    def _reprSubelements(self, indent_level):
        r = []
        if 'text' in self._attrs:
            r.append('%s%s\n' % (_indentStr(indent_level),
                                 self._attrs['text']))
        if self._subs:
            for elem in self._subs:
                r.append('%s' % elem.indRepr(indent_level))
        return ''.join(filter(None, r))

    def indRepr(self, indent_level=0):
        ind = _indentStr(indent_level)
        tag = ':'.join(filter(None, [self._prefix, self._tag]))
        atts = self._reprAttributes(indent_level + 1)
        h = ' '.join(filter(None, [tag, atts]))
        subs = self._reprSubelements(indent_level + 1)
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
        self._attrs = {}
        if attrList is not None:
            for attKey in attrList.keys():
                fixattr = attKey.replace('_', '-').lower()
                self._attrs[fixattr] = attrList[attKey]

    def indRepr(self, indent_level=0):
        render = ['%s%s {\n' % (_indentStr(indent_level), self.name)]
        for att in self._attrs:
            render.append('%s%s: %s;\n' % (_indentStr(indent_level + 1), att, self._attrs[att]))
        render.append('%s}\n' % (_indentStr(indent_level)))
        return ''.join(render)

    def append(self, **attrList):
        '''not sure if it's ok'''
        # self._attrs = {self._attrs, attrList}
        self._attrs = dict(zip(self._attrs, attrList))


class SvgStylesContainer(XmlElement):
    def __init__(self):
        XmlElement.__init__(self, 'style', type="text/css")

    def append(self, _SvgStyleDefinitionEntry):
        self._subs.append(_SvgStyleDefinitionEntry)

    def _reprSubelements(self, indent_level):
        if self._subs:
            s = []
            for elem in self._subs:
                s.append('%s' % elem.indRepr(indent_level + 1))
            stylesstr = ''.join(filter(None, s))
            return '{0}<![CDATA[\n{1}{0}]]>\n'.format(_indentStr(indent_level),
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

    def _reprSubelements(self, indent_level):
        r = []
        if not self._styles.isEmpty():
            r.append(self._styles.indRepr(indent_level))
        if self._subs:
            for elem in self._subs:
                r.append('%s' % elem.indRepr(indent_level))
        return ''.join(r)

class SvgWindow(XmlElement):
    def __init__(self, width, height, **attributes):
        attributes['width'] = width
        attributes['height'] = height
        XmlElement.__init__(self, 'svg', **attributes)
        self._attrs['xmlns'] = 'http://www.w3.org/2000/svg'
        self._attrs['xmlns:xlink'] = 'http://www.w3.org/1999/xlink'
        self._defs = SvgDefs()

    def append(self, other):
        if isinstance(other, SvgStyleDefinitionEntry):
            self._defs._styles.append(other)
        elif isinstance(other, ShapesGroup):
            self._defs.append(other)
        else:
            self._subs.append(other)

    def _reprSubelements(self, indent_level):
        r = []
        if not self._defs.isEmpty():
            r.append(self._defs.indRepr(indent_level))
        if 'text' in self._attrs:
            r.append('%s%s\n' % (_indentStr(indent_level),
                                 self._attrs['text']))
        if self._subs:
            for elem in self._subs:
                r.append('%s' % elem.indRepr(indent_level))
        return ''.join(filter(None, r))

    def __repr__(self):
        return self.indRepr(0)

    def useElementById(self, xlinkId, x, y, **attributes):
        extraTransform = ''
        if attributes and 'transform' in attributes:
            extraTransform = extraTransform + ' ' + attributes['transform']
        attributes['transform'] = 'translate(%g, %g)%s' % (x, y, extraTransform)
        attributes['xlink:href'] = '#%s' % (xlinkId)
        self.append(XmlElement('use', **attributes))

    def use(self, element, x, y, **attributes):
        if not isinstance(element, XmlElement):
            raise kaSvgError('ussage allows only XmlElement type')
        if element not in self._defs._subs:
            self._defs.append(element)
        if 'id' not in element._attrs:
            element.addAttr(id=_randomID())
        xlinkId = element._attrs['id']
        self.useElementById(xlinkId, x, y, **attributes)


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

    def indRepr(self, indent_level):
        return '%s%s' % (_indentStr(indent_level), self)

