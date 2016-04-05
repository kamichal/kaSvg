'''
Created on 1 kwi 2016

@author: kamichal
'''


from lxml import etree
from formencode.doctest_xml_compare import xml_compare

from kaSvg import SvgWindow, SvgDefinitionsContainer, XmlElement
import sys

def _cmpXml(got, ref):
    print " -"*5 + "GOT" + "- "*20
    print got
    print " -"*28
    tree1 = etree.fromstring(str(got))
    tree2 = etree.fromstring(str(ref))
    assert xml_compare(tree1, tree2, lambda x: sys.stdout.write(x + "\n"))


def test_empty_window():
    w = SvgWindow(123, 234)
    _cmpXml(w, '''\
<svg width="123" xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
height="234"/>''')

def test_pretty_xml():
    x = XmlElement("id", node="nodename")
    y = XmlElement("y", node="be")
    z = XmlElement("z")
    a = XmlElement("dd", node="tu")
    
    a.append(y)
    a.append(y)
    a.append(z)
    x.append(XmlElement('empty'))
    x.append(XmlElement('p', text="some text"))
    x.append(a)

    print x
    assert str(x) == """\
<id node="nodename">
    <empty/>
    <p>
        some text
    </p>
    <dd node="tu">
        <y node="be"/>
        <y node="be"/>
        <z/>
    </dd>
</id>
"""

def test_window_params():
    w = SvgWindow(123, 234, stroke_width='0px', background_color='#8AC')

    _cmpXml(w, '''\
<svg
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
height="234"
width="123"
stroke-width="0px"
background-color="#8AC"/>''')


def test_empty_definitions():
    w = SvgWindow(10, 20)
    d = SvgDefinitionsContainer()
    w.append(d)

    _cmpXml(w, '''\
<svg width="10" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="20">
  <defs>
  </defs>
</svg>''')


def test_definitions():
    w = SvgWindow(10, 20)
    d = SvgDefinitionsContainer()

    k = XmlElement("circle", cx=0, cy=30, r=28, fill="red", stroke='#851', stroke_width=10, stroke_opacity=0.5)

    p = XmlElement("rect", x=-30, y=-5, width="80", height="10")
    d.append(k)
    d.append(p)
    w.append(d)

    _cmpXml(w, '''\
<svg width="10" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
   height="20">

  <defs>
    <circle r="28" stroke-opacity="0.5" cy="30" stroke="#851" cx="0" stroke-width="10"
       fill="red"/>
    <rect y="-5" width="80" x="-30" height="10"/>
  </defs>

</svg>
''')

def test_definitions_and_usage():
    w = SvgWindow(10, 20)
    d = SvgDefinitionsContainer()

    k = XmlElement("circle", cx=0, cy=30, r=28, fill="red")

    p = XmlElement("rect", x=-30, y=-5, width="80", height="10")
    d.append(k)
    d.append(p)
    w.append(d)

    w.useElement("k", 12, 23)
    w.useElement("p", 24, 10)

    _cmpXml(w, '''\
<svg width="10" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
   height="20">

  <defs>
    <circle cy="30" cx="0" r="28" fill="red"/>
    <rect y="-5" width="80" x="-30" height="10"/>
  </defs>

  <use xlink:href="#k" transform="translate(12, 23)"/>
  <use xlink:href="#p" transform="translate(24, 10)"/>
</svg>
''')

def test_xml_by_dict_or_kwargs():
    d = {'cx': 0, 'cy': 30, 'r': 28, 'fill': "red"}
    k = XmlElement("circle", dd=d)
    u = XmlElement("circle", cx=0, cy=30, r=28, fill="red")
    _cmpXml(k, '<circle cy="30" cx="0" r="28" fill="red"/>')
    _cmpXml(k, u)

def test_definitions_and_usage_by_dict():
    w = SvgWindow(10, 20)
    d = SvgDefinitionsContainer()

    dd = {'cx': 0, 'cy': 30, 'r': 28, 'fill': "red"}
    k = XmlElement("circle", dd=dd)

    _cmpXml(k, '<circle cy="30" cx="0" r="28" fill="red"/>')

    dd = {"x":-30, "y":-5, "width": 80, "height": 10}

    p = XmlElement("rect", dd=dd)
    d.append(k)
    d.append(p)
    w.append(d)

    w.useElement("k", 12, 23)
    w.useElement("p", 24, 10)

    _cmpXml(w, '''\
<svg width="10" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
   height="20">

  <defs>
    <circle cy="30" cx="0" r="28" fill="red"/>
    <rect y="-5" width="80" x="-30" height="10"/>
  </defs>

  <use xlink:href="#k" transform="translate(12, 23)"/>
  <use xlink:href="#p" transform="translate(24, 10)"/>
</svg>
''')



