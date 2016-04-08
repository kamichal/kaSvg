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


from kaSvg import SvgWindow, SvgElement, SvgElement, ShapesGroup


def _cmpXml(got, ref):
    print "- " * 5 + "GOT:" + " -" * 20
    print got
    print "- " * 28
    tree1 = etree.fromstring(str(got))
    tree2 = etree.fromstring(str(ref))
    assert xml_compare(tree1, tree2, lambda x: sys.stdout.write(x + "\n"))


def test_empty_xml_element():
    w = SvgElement("id")
    _cmpXml(w, """<id/>""")


def test_simple_xml_element():
    w = SvgElement("id", node="nodename")
    _cmpXml(w, """<id node="nodename"/>""")


def test_parent_xml_element():
    w = SvgElement("id", node="nodename")
    w.append(SvgElement("child1", color="#666"))
    w.append(SvgElement("child2", color="#123"))
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
    w = SvgElement("parent", node="nodename", long_key_and_val="this is long value of the field quite very long")
    em = SvgElement("emb", node="nodename")
    em.append(SvgElement("mc1", color="#666", st="some"))
    em.append(SvgElement("mc2", color="#666", st="some"))
    w.append(SvgElement("child1", color="#666"))
    w.append(em)
    w.append(SvgElement("child2"))
    w.append(SvgElement("child3", color="#123"))

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
    x = SvgElement("id", node="nodename")
    y = SvgElement("y", node="be")
    z = SvgElement("z")
    a = SvgElement("dd", node="tu", text="some text here")

    a.append(y)
    a.append(y)
    a.append(z)
    x.append(SvgElement('empty'))
    x.append(SvgElement('p', text="some text"))
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
    k = SvgElement("circle", id="a", cx=0, cy=30, r=28, fill="red", stroke='#851', stroke_width=10, stroke_opacity=0.5)
    p = SvgElement("rect", id="b", x=-30, y=-5, width="80", height="10")
    w.use(k, 0, 0)
    w.use(p, 0, 0)

    _cmpXml(w, '''\
<svg width="10" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="20">
    <defs>
        <circle r="28" stroke-opacity="0.5" cy="30" stroke="#851" cx="0" stroke-width="10"
            id="a" fill="red"/>
        <rect y="-5" width="80" x="-30" id="b" height="10"/>
    </defs>
    <use xlink:href="#a" transform="translate(0, 0)"/>
    <use xlink:href="#b" transform="translate(0, 0)"/>
</svg>
''')


def test_pretty_svg():
    w = SvgWindow(200, 100)

    k = SvgElement("circle", id="a", cx=0, cy=30, r=28, fill="red")
    p = SvgElement("rect", x=-30, y=-5, width="80", height="10")

    g = ShapesGroup("group1", k, p)
    w.use(g, 12, 23)
    w.use(g, 34, 45)
    w.use(SvgElement("rect", x=0, y=0, id="re", width="80", height="10"), 45, 56)
    w.use(k, 6, 6)
    w.useElementById("group1", 24, 10)

    print str(w)
    assert str(w) == """\
<svg width="200" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="100">
    <defs>
        <g id="group1">
            <circle cy="30" cx="0" r="28" id="a" fill="red"/>
            <rect y="-5" width="80" height="10" x="-30"/>
        </g>
        <rect y="0" width="80" height="10" id="re" x="0"/>
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
    k = SvgElement("circle", id='a', prefix="svg", cx=0, cy=30, r=28)
    p = SvgElement("rect", id='b', prefix="svg", x=-30, y=-5, width="80", height="10")

    w.use(k, 0, 0)
    w.use(p, 0, 0)
    print w
    assert str(w) == '''\
<svg:svg width="10" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="20">
    <svg:defs>
        <svg:circle cy="30" cx="0" r="28" id="a"/>
        <svg:rect y="-5" width="80" x="-30" id="b" height="10"/>
    </svg:defs>
    <svg:use xlink:href="#a" transform="translate(0, 0)"/>
    <svg:use xlink:href="#b" transform="translate(0, 0)"/>
</svg:svg>
'''


def test_definitions_and_usage():
    w = SvgWindow(10, 20)

    k = SvgElement("circle", id='k', cx=0, cy=30, r=28, fill="red")
    p = SvgElement("rect", id='p', x=-30, y=-5, width="80", height="10")

    w.use(k, 12, 23)
    w.use(p, 24, 10)

    _cmpXml(w, '''\
<svg width="10" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="20">
    <defs>
        <circle cy="30" cx="0" r="28" id="k" fill="red"/>
        <rect y="-5" width="80" x="-30" id="p" height="10"/>
    </defs>
    <use xlink:href="#k" transform="translate(12, 23)"/>
    <use xlink:href="#p" transform="translate(24, 10)"/>
</svg>
''')


def test_group_usage_1():
    w = SvgWindow(200, 100)

    k = SvgElement("circle", cx=0, cy=30, r=28, fill="red")
    p = SvgElement("rect", x=-30, y=-5, width="80", height="10")

    g = ShapesGroup("grupa1", k, p)
    w.use(g, 12, 23)
    w.use(g, 34, 45)
    w.use(SvgElement("rect", x=0, y=0, id="re", width="80", height="10"), 45, 56)
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

    k = SvgElement("circle", cx=0, cy=30, r=28, fill="red")
    p = SvgElement("rect", x=-30, y=-5, width="80", height="10")

    w.use(ShapesGroup("grupa1", k, p), 23, 4)

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
    <use xlink:href="#grupa1" transform="translate(23, 4)"/>
    <use xlink:href="#grupa1" transform="translate(12, 23)"/>
    <use xlink:href="#grupa1" transform="translate(24, 10)"/>
</svg>
''')

def test_xml_by_dict_or_kwargs():
    d = {'cx': 0, 'cy': 30, 'r': 28, 'fill': "red"}
    k = SvgElement("circle", dd=d)
    u = SvgElement("circle", cx=0, cy=30, r=28, fill="red")
    _cmpXml(k, '<circle cy="30" cx="0" r="28" fill="red"/>')
    _cmpXml(k, u)


def test_definitions_and_usage_by_dict():
    w = SvgWindow(10, 20)
    dd = {"id":"k", 'cx': 0, 'cy': 30, 'r': 28, 'fill': "red"}
    k = SvgElement("circle", dd=dd, id='k')

    dd = {"id":"p", "x":-30, "y":-5, "width": 80, "height": 10}
    p = SvgElement("rect", dd=dd)

    _cmpXml(k, '<circle cy="30" cx="0" r="28" id="k" fill="red"/>')

    w.use(k, 12, 23)
    w.use(p, 24, 10)

    _cmpXml(w, '''\
<svg width="10" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" height="20">
    <defs>
        <circle cy="30" cx="0" r="28" id="k" fill="red"/>
        <rect y="-5" x="-30" width="80" id="p" height="10"/>
    </defs>
    <use xlink:href="#k" transform="translate(12, 23)"/>
    <use xlink:href="#p" transform="translate(24, 10)"/>
</svg>
''')


def test_svg_can_be_stored():
    tmpf = op.join(gettempdir(), 'tmp_kaSvg.svg')

    w = SvgWindow(10, 20)
    k = SvgElement("circle")
    p = SvgElement("rect")

    w.use(k, 12, 23)
    w.use(p, 24, 10)

    w.store(tmpf)

    with open(tmpf) as ff:
        content = ff.read()

    _cmpXml(w, content)


def test_style_definitions():
    svg_window = SvgWindow("100%", "100%", viewBox="0 0 500 500",
                           preserveAspectRatio="xMinYMin meet",
                           style='stroke-width: 0px; background-color: #8AC;')

    svg_window.newStyle(".klasaA",
                        stroke="green", stroke_width=0.6,
                        stroke_opacity=0.4,
                        fill="green", fill_opacity=0.23, rx=5, ry=5)

    svg_window.newStyle(".klasaA:hover",
                        stroke="yellow", stroke_width=1.2,
                        stroke_opacity=0.3,
                        fill="green", fill_opacity=0.35)

    kolko = SvgElement("circle", cx=0, cy=30, r=53)

    prostokat = SvgElement("rect", x=-30, y=-25,
                           width="80", height="10",
                           fill_opacity=0.5)

    prostokat2 = SvgElement("rect", x=-5, y=0, width=60, height=20,
                            rx=5, ry=5,
                            fill_opacity=0.8)

    prostokat3 = SvgElement("rect", x=-40, y=30, width="80", height="70")

    tekstt = SvgElement("text", x="0", y="15", fill="red", text="?Hija")
    tekstt2 = SvgElement("text", x="-40", y="37", fill="black", text="Python")

    grupa1 = ShapesGroup("grupa1", kolko, prostokat, prostokat2,
                         prostokat3, tekstt, tekstt2, Class="klasaA")

    alink = SvgElement("a", id="tynlik")
    alink._attrs["xlink:href"] = "TestOtherUseCase.svg"
    alink.append(SvgElement("rect", x=15, y=50, width=60, height=20, Class="klasaA"))

    svg_window.append(alink)
    svg_window.use(grupa1, 45, 130)
    svg_window.use(grupa1, 180, 100, transform="scale(0.6) rotate(45)")
    svg_window.use(grupa1, 55, 25, transform="scale(0.4) rotate(-15.4) translate(50, 50)")
    svg_window.use(grupa1, 80, 90, transform="scale(0.7) rotate(15.4) translate(50, 50)")
    svg_window.use(grupa1, 220, 80)

    tekstt3 = SvgElement("text", x="0", y="17", text="SVG", Class="klasaA")
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


def test_styles():
    w = SvgWindow("100%", "100%", viewBox="0 0 500 500",
                  preserveAspectRatio="xMinYMin meet",
                  style='stroke-width: 0px; background-color: #8AC;')

    w.newStyle(".styl_1", stroke="green", stroke_width=0.6, 
               stroke_opacity=0.4, fill="green", fill_opacity=0.23, rx=5, ry=5)

    s2 = w.newStyle(".styl_2", stroke="yellow", stroke_width=1.2,
                    stroke_opacity=0.3, fill="green", fill_opacity=0.35)

    p1 = SvgElement("rect", x=-30, y=-25, width="80", height="10",
                    fill_opacity=0.5)

    p1.style("styl_1")

    p2 = SvgElement("rect", x=-5, y=0, width=60, height=20,
                    rx=5, ry=5, fill_opacity=0.8)
    p2.style(s2)

    w.use(ShapesGroup("g1", p1, p2), 123, 234)
    print w

    _cmpXml(w, """\
<svg style="stroke-width: 0px; background-color: #8AC;"
    xmlns="http://www.w3.org/2000/svg" height="100%" width="100%"
    preserveaspectratio="xMinYMin meet"
    xmlns:xlink="http://www.w3.org/1999/xlink" viewbox="0 0 500 500">
    <defs>
        <style type="text/css">
            <![CDATA[
                .styl_1 {
                    stroke-opacity: 0.4;
                    fill-opacity: 0.23;
                    rx: 5;
                    ry: 5;
                    stroke: green;
                    stroke-width: 0.6;
                    fill: green;
                }
                .styl_2 {
                    stroke-width: 1.2;
                    stroke: yellow;
                    fill-opacity: 0.35;
                    stroke-opacity: 0.3;
                    fill: green;
                }
            ]]>
        </style>
        <g id="g1">
            <rect fill-opacity="0.5" height="10" width="80" y="-25" x="-30" class="styl_1"/>
            <rect fill-opacity="0.8" rx="5" ry="5" height="20" width="60" y="0" x="-5"
                class="styl_2"/>
        </g>
    </defs>
    <use xlink:href="#g1" transform="translate(123, 234)"/>
</svg>
""")