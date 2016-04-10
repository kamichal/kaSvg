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

class KaSvgError(Exception):
    pass


class XmlElement(object):
    def __init__(self, tag, prefix='', **attributes):
        self._tag = tag
        self._prefix = prefix
        self._subs = []
        self._attrs = {}
        if attributes:
            if 'dd' in attributes:
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

        if _MAX_LINE_WIDTH > 0:
            w = TextWrapper(width=_MAX_LINE_WIDTH, break_on_hyphens=False,
                              subsequent_indent=_indentStr(indent_level))
            return w.fill(' '.join(r))
        else:
            return ' '.join(r)

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


class SvgElement(XmlElement):
    def __init__(self, tag, prefix='', **attributes):
        XmlElement.__init__(self, tag, prefix, **attributes)

    def style(self, *obj_or_id):
        style_objs = [x for x in obj_or_id if isinstance(x, SvgDefs.SvgCssClass)]
        style_ids = [x for x in obj_or_id if isinstance(x, str)]
        for style_obj in style_objs:
            name = style_obj.name.replace('.', '')
            if 'class' not in self._attrs:
                self._attrs['class'] = name
            else:
                self._attrs['class'] += ' %' % name
        for style_id in style_ids:
            name = style_id.replace('.', '')
            if 'class' not in self._attrs:
                self._attrs['class'] = style_id
            else:
                self._attrs['class'] += ' %' % style_id


class SvgDefs(XmlElement):
    class SvgCssClass(object):
        def __init__(self, name, **attrList):
            self.name = name
            self._attrs = {}
            if attrList is not None:
                for attKey in attrList.keys():
                    fixattr = attKey.replace('_', '-').lower()
                    self._attrs[fixattr] = attrList[attKey]

        def indRepr(self, indent_level=0):
            ind1 = _indentStr(indent_level)
            ind2 = _indentStr(indent_level + 1)
            render = ['%s%s {\n' % (ind1, self.name)]
            for att in self._attrs:
                render.append('%s%s: %s;\n' % (ind2, att, self._attrs[att]))
            render.append('%s}\n' % ind1)
            return ''.join(render)

        def update_style(self, **attrList):
            self._attrs.update(attrList)

    class SvgCssContainer(XmlElement):
        '''http://blogs.adobe.com/webplatform/2013/01/08/svg-styling/'''
        def __init__(self):
            XmlElement.__init__(self, 'style', type="text/css")

        def append(self, _SvgCssClass):
            self._subs.append(_SvgCssClass)

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

    def __init__(self, **attributes):
        XmlElement.__init__(self, 'defs', **attributes)
        self._styles = self.SvgCssContainer()

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
        self._defs = SvgDefs(prefix=self._prefix)

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
        if not isinstance(xlinkId, str):
            raise KaSvgError('ussage by ID requires the ID to be a string')
        extraTransform = ''
        if attributes and 'transform' in attributes:
            extraTransform = extraTransform + ' ' + attributes['transform']
        attributes['transform'] = 'translate(%g, %g)%s' % (x, y, extraTransform)
        attributes['xlink:href'] = '#%s' % (xlinkId)
        self.append(XmlElement('use', prefix=self._prefix, **attributes))

    def use(self, element, x, y, **attributes):
        if not isinstance(element, XmlElement):
            raise KaSvgError('ussage allows only XmlElement type')
        if 'id' not in element._attrs:
            element.addAttr(id=_randomID())
        xlinkId = element._attrs['id']
        if element not in self._defs._subs:
            self._defs.append(element)
        self.useElementById(xlinkId, x, y, **attributes)
        return element

    def style(self, name, style_string = '', **attrList):
        if style_string and not attrList:
            for ch in [' ', '\n', '\r', '\t']:
                style_string = style_string.replace(ch,'')
            st = filter(None,style_string.split(";"))
            attrList = dict(x.split("=") for x in st)
        for s in self._defs._styles._subs:
            if s.name == name:
                s.update_style(**attrList)
                break
        else:
            s = self._defs.SvgCssClass(name, **attrList)
            self._defs._styles.append(s)
        return s

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

