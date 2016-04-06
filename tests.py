'''
Created on 1 kwi 2016

@author: kamichal
'''


import sys
from os import path as op
# import pytest

from lxml import etree
from formencode.doctest_xml_compare import xml_compare
from tempfile import gettempdir


from kaSvg import SvgWindow, SvgDefs, \
    XmlElement, DefineSvgGroup, ShapesGroup


def _cmpXml(got, ref):
    print "- " * 5 + "GOT:" + " -" * 20
    print got
    print "- " * 28
    tree1 = etree.fromstring(str(got))
    tree2 = etree.fromstring(str(ref))
    assert xml_compare(tree1, tree2, lambda x: sys.stdout.write(x + "\n"))


def test_empty_xml_element():
    w = XmlElement("id")
    _cmpXml(w, """<id/>""")


def test_simple_xml_element():
    w = XmlElement("id", node="nodename")
    _cmpXml(w, """<id node="nodename"/>""")


def test_parent_xml_element():
    w = XmlElement("id", node="nodename")
    w.append(XmlElement("child1", color="#666"))
    w.append(XmlElement("child2", color="#123"))
    _cmpXml(w, """\
<id node="nodename">
    <child1 color= "#666"/>
    <child2 color= "#123"/>
</id>""")


def test_empty_window():
    w = SvgWindow(123, 234)
    _cmpXml(w, '''\
<svg width="123" xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
height="234"/>''')


def test_pretty_xml_1():
    w = XmlElement("parent", node="nodename", long_key_and_val="this is long value of the field quite very long")
    em = XmlElement("emb", node="nodename")
    em.append(XmlElement("mc1", color="#666", st="some"))
    em.append(XmlElement("mc2", color="#666", st="some"))
    w.append(XmlElement("child1", color="#666"))
    w.append(em)
    w.append(XmlElement("child2"))
    w.append(XmlElement("child3", color="#123"))

    print str(w)
    assert str(w) == """\
<parent node="nodename" long-key-and-val="this is long value of the field quite very
    long">
    <child1 color="#666"/>
    <emb node="nodename">
        <mc1 color="#666" st="some"/>
        <mc2 color="#666" st="some"/>
    </emb>
    <child2/>
    <child3 color="#123"/>
</parent>
"""


def test_pretty_xml_2():
    x = XmlElement("id", node="nodename")
    y = XmlElement("y", node="be")
    z = XmlElement("z")
    a = XmlElement("dd", node="tu", text="some text here")

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
        some text here
        <y node="be"/>
        <y node="be"/>
        <z/>
    </dd>
</id>
"""


def test_window_params():
    w = SvgWindow(123, 234, stroke_width='0px', background_color='#8AC')

    _cmpXml(w, '''\
<svg xmlns="http://www.w3.org/2000/svg" height="234" width="123"
    xmlns:xlink="http://www.w3.org/1999/xlink" stroke-width="0px"
    background-color="#8AC"/>
''')


def test_definitions():
    w = SvgWindow(10, 20)
    d = SvgDefs()

    k = XmlElement("circle", cx=0, cy=30, r=28, fill="red", stroke='#851', stroke_width=10, stroke_opacity=0.5)

    p = XmlElement("rect", x=-30, y=-5, width="80", height="10")
    d.append(k)
    d.append(p)
    w.append(d)

    _cmpXml(w, '''\
<svg width="10" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="20">
    <defs>
        <circle r="28" stroke-opacity="0.5" cy="30" stroke="#851" cx="0" stroke-width="10"
            fill="red"/>
        <rect y="-5" width="80" x="-30" height="10"/>
    </defs>
</svg>
''')


def test_pretty_svg():
    w = SvgWindow(200, 100)

    k = XmlElement("circle", id="a", cx=0, cy=30, r=28, fill="red")
    p = XmlElement("rect", x=-30, y=-5, width="80", height="10")

    g = ShapesGroup("group1", k, p)
    w.use(g, 12, 23)
    w.use(g, 34, 45)
    w.use(XmlElement("rect", x=0, y=0, id="re", width="80", height="10"), 45, 56)
    w.use(k, 6, 6)
    w.useElementById("group1", 24, 10)

    print str(w)
    assert str(w) == """\
<svg width="200" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="100">
    <defs>
        <g id="group1">
            <circle cy="30" cx="0" r="28" id="a" fill="red"/>
            <rect y="-5" width="80" x="-30" height="10"/>
        </g>
        <rect y="0" width="80" x="0" id="re" height="10"/>
        <circle cy="30" cx="0" r="28" id="a" fill="red"/>
    </defs>
    <use xlink:href="#group1" transform="translate(12, 23)"/>
    <use xlink:href="#group1" transform="translate(34, 45)"/>
    <use xlink:href="#re" transform="translate(45, 56)"/>
    <use xlink:href="#a" transform="translate(6, 6)"/>
    <use xlink:href="#group1" transform="translate(24, 10)"/>
</svg>
"""


def test_namespaced_xml():
    w = SvgWindow(10, 20, prefix="svg")
    d = SvgDefs(prefix="svg")
    k = XmlElement("circle", prefix="svg", cx=0, cy=30, r=28)
    p = XmlElement("rect", prefix="svg", x=-30, y=-5, width="80", height="10")

    d.append(k)
    d.append(p)
    w.append(d)
    print w
    assert str(w) == '''\
<svg:svg width="10" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="20">
    <svg:defs>
        <svg:circle cy="30" cx="0" r="28"/>
        <svg:rect y="-5" width="80" x="-30" height="10"/>
    </svg:defs>
</svg:svg>
'''


def test_definitions_and_usage():
    w = SvgWindow(10, 20)
    d = SvgDefs()

    k = XmlElement("circle", cx=0, cy=30, r=28, fill="red")

    p = XmlElement("rect", x=-30, y=-5, width="80", height="10")
    d.append(k)
    d.append(p)
    w.append(d)

    w.useElementById("k", 12, 23)
    w.useElementById("p", 24, 10)

    _cmpXml(w, '''\
<svg width="10" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="20">
    <defs>
        <circle cy="30" cx="0" r="28" fill="red"/>
        <rect y="-5" width="80" x="-30" height="10"/>
    </defs>
    <use xlink:href="#k" transform="translate(12, 23)"/>
    <use xlink:href="#p" transform="translate(24, 10)"/>
</svg>
''')


def test_group_usage_1():
    w = SvgWindow(200, 100)

    k = XmlElement("circle", cx=0, cy=30, r=28, fill="red")
    p = XmlElement("rect", x=-30, y=-5, width="80", height="10")

    g = ShapesGroup("grupa1", k, p)
    w.use(g, 12, 23)
    w.use(g, 34, 45)
    w.use(XmlElement("rect", x=0, y=0, id="re", width="80", height="10"), 45, 56)
    w.useElementById("grupa1", 24, 10)

    _cmpXml(w, '''\
<svg width="200" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="100">
    <defs>
        <g id="grupa1">
            <circle cy="30" cx="0" r="28" fill="red"/>
            <rect y="-5" width="80" x="-30" height="10"/>
        </g>
        <rect y="0" width="80" x="0" id="re" height="10"/>
    </defs>
    <use xlink:href="#grupa1" transform="translate(12, 23)"/>
    <use xlink:href="#grupa1" transform="translate(34, 45)"/>
    <use xlink:href="#re" transform="translate(45, 56)"/>
    <use xlink:href="#grupa1" transform="translate(24, 10)"/>
</svg>
''')


def test_group_usage_2():
    w = SvgWindow(200, 100)

    k = XmlElement("circle", cx=0, cy=30, r=28, fill="red")
    p = XmlElement("rect", x=-30, y=-5, width="80", height="10")

    w.append(ShapesGroup("grupa1", k, p))

    w.useElementById("grupa1", 12, 23)
    w.useElementById("grupa1", 24, 10)

    _cmpXml(w, '''\
<svg width="200" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="100">
    <defs>
        <g id="grupa1">
            <circle cy="30" cx="0" r="28" fill="red"/>
            <rect y="-5" width="80" x="-30" height="10"/>
        </g>
    </defs>
    <use xlink:href="#grupa1" transform="translate(12, 23)"/>
    <use xlink:href="#grupa1" transform="translate(24, 10)"/>
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
    d = SvgDefs()

    dd = {'cx': 0, 'cy': 30, 'r': 28, 'fill': "red"}
    k = XmlElement("circle", dd=dd)

    _cmpXml(k, '<circle cy="30" cx="0" r="28" fill="red"/>')

    dd = {"x": -30, "y": -5, "width": 80, "height": 10}

    p = XmlElement("rect", dd=dd)
    d.append(k)
    d.append(p)
    w.append(d)

    w.useElementById("k", 12, 23)
    w.useElementById("p", 24, 10)

    _cmpXml(w, '''\
<svg width="10" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="20">
    <defs>
        <circle cy="30" cx="0" r="28" fill="red"/>
        <rect y="-5" x="-30" width="80" height="10"/>
    </defs>
    <use xlink:href="#k" transform="translate(12, 23)"/>
    <use xlink:href="#p" transform="translate(24, 10)"/>
</svg>
''')


def test_svg_can_be_stored():
    tmpf = op.join(gettempdir(), 'tmp_kaSvg.svg')

    w = SvgWindow(10, 20)
    d = SvgDefs()

    dd = {'cx': 0, 'cy': 30, 'r': 28, 'fill': "red"}
    k = XmlElement("circle", dd=dd)

    _cmpXml(k, '<circle cy="30" cx="0" r="28" fill="red"/>')

    dd = {"x": -30, "y": -5, "width": 80, "height": 10}
    p = XmlElement("rect", dd=dd)

    d.append(k)
    d.append(p)
    w.append(d)

    w.useElementById("k", 12, 23)
    w.useElementById("p", 24, 10)

    w.store(tmpf)

    with open(tmpf) as ff:
        content = ff.read()

    _cmpXml(w, content)


def test_style_definitions():
    svgDefinitions = SvgDefs()

    svg_window = SvgWindow("100%", "100%", viewBox="0 0 500 500",
                           preserveAspectRatio="xMinYMin meet",
                           style='stroke-width: 0px; background-color: #8AC;')

    svgDefinitions.createNewStyle(".klasaA",
                                  stroke="green", stroke_width=0.6,
                                  stroke_opacity=0.4,
                                  fill="green", fill_opacity=0.23, rx=5, ry=5)

    svgDefinitions.createNewStyle(".klasaA:hover",
                                  stroke="yellow", stroke_width=1.2,
                                  stroke_opacity=0.3,
                                  fill="green", fill_opacity=0.35)

    grupa1 = DefineSvgGroup("grupa1", svgDefinitions,
                            Class="klasaA")

    kolko = XmlElement("circle", cx=0, cy=30, r=53)

    prostokat = XmlElement("rect", x=-30, y=-25,
                           width="80", height="10",
                           fill_opacity=0.5)

    prostokat2 = XmlElement("rect", x=-5, y=0, width=60, height=20,
                            rx=5, ry=5,
                            fill_opacity=0.8)

    prostokat3 = XmlElement("rect", x=-40, y=30, width="80", height="70")

    tekstt = XmlElement("text", x="0", y="15", fill="red", text="?Hija")
    tekstt2 = XmlElement("text", x="-40", y="37", fill="black", text="Python")

    grupa1.append(kolko)
    grupa1.append(prostokat)
    grupa1.append(prostokat2)
    grupa1.append(prostokat3)
    grupa1.append(tekstt)
    grupa1.append(tekstt2)

    alink = XmlElement("a", id="tynlik")
    alink._attrs["xlink:href"] = "TestOtherUseCase.svg"
    alink.append(XmlElement("rect", x=15, y=50, width=60, height=20, Class="klasaA"))

    svg_window.append(svgDefinitions)
    svg_window.append(alink)
    svg_window.useElementById("grupa1", 45, 130)
    svg_window.useElementById("grupa1", 180, 100, transform="scale(0.6) rotate(45)")
    svg_window.useElementById("grupa1", 55, 25, transform="scale(0.4) rotate(-15.4) translate(50, 50)")
    svg_window.useElementById("grupa1", 80, 90, transform="scale(0.7) rotate(15.4) translate(50, 50)")
    svg_window.useElementById("grupa1", 220, 80)

    tekstt3 = XmlElement("text", x="0", y="17", text="SVG", Class="klasaA")
    svg_window.append(tekstt3)

    ref = """\
<svg style="stroke-width: 0px; background-color: #8AC;"
    xmlns="http://www.w3.org/2000/svg" height="100%" width="100%"
    preserveaspectratio="xMinYMin meet"
    xmlns:xlink="http://www.w3.org/1999/xlink" viewbox="0 0 500 500">
    <defs>
        <style type="text/css">
            <![CDATA[
                .klasaA {
                    stroke-opacity: 0.4;
                    fill-opacity: 0.23;
                    rx: 5;
                    ry: 5;
                    stroke: green;
                    stroke-width: 0.6;
                    fill: green;
                }
                .klasaA:hover {
                    stroke-width: 1.2;
                    stroke: yellow;
                    fill-opacity: 0.35;
                    stroke-opacity: 0.3;
                    fill: green;
                }
            ]]>
        </style>
        <g class="klasaA" id="grupa1">
            <circle cy="30" cx="0" r="53"/>
            <rect y="-25" width="80" fill-opacity="0.5" x="-30" height="10"/>
            <rect fill-opacity="0.8" rx="5" ry="5" height="20" width="60" y="0" x="-5"/>
            <rect y="30" width="80" x="-40" height="70"/>
            <text y="15" x="0" fill="red">
                ?Hija
            </text>
            <text y="37" x="-40" fill="black">
                Python
            </text>
        </g>
    </defs>
    <a xlink:href="TestOtherUseCase.svg" id="tynlik">
        <rect y="50" width="60" x="15" class="klasaA" height="20"/>
    </a>
    <use xlink:href="#grupa1" transform="translate(45, 130)"/>
    <use xlink:href="#grupa1" transform="translate(180, 100) scale(0.6) rotate(45)"/>
    <use xlink:href="#grupa1" transform="translate(55, 25) scale(0.4) rotate(-15.4)
        translate(50, 50)"/>
    <use xlink:href="#grupa1" transform="translate(80, 90) scale(0.7) rotate(15.4)
        translate(50, 50)"/>
    <use xlink:href="#grupa1" transform="translate(220, 80)"/>
    <text y="17" class="klasaA" x="0">
        SVG
    </text>
</svg>
"""
    _cmpXml(svg_window, ref)
