#!/usr/bin/python

'''
Created on 29 Mar 2016

@author: kamichal
'''

from kaSvg import SvgWindow, SvgDefinitionsContainer, \
                  XmlElement, DefineSvgGroup, XmlComment


def __TestSimpliestUseCase():

    filename = "_test_out/TestSimpliestUseCase.svg"

    svg_window = SvgWindow(300, 200,
                           stroke_width='0px',
                           background_color='#8AC')

    svgDefinitions = SvgDefinitionsContainer()

    # define elements to be used
    kolko = XmlElement("circle", cx=0, cy=30, r=28, fill="red",
                       stroke='#851', stroke_width=10, stroke_opacity=0.5)

    prostokat = XmlElement("rect", x=-30, y=-5, width="80", height="10")

    prostokat2 = XmlElement("rect", x=-10, y=0,
                            width=60, height=20,
                            rx=5, ry=5,
                            fill_opacity=0.5)

    prostokat3 = XmlElement("rect", x=50, y=50, width="80", height="30",
                            fill_opacity=0.2)

    grupa1 = DefineSvgGroup("grupa1", svgDefinitions,
                            stroke="green", stroke_width=2, fill="white")

    grupa1.append(kolko)
    grupa1.append(prostokat)
    grupa1.append(prostokat2)
    grupa1.append(prostokat3)

    svg_window.append(svgDefinitions)

    svg_window.useElement("grupa1", 45, 130)

    svg_window.useElement("grupa1", 180, 100,
                          transform="scale(1.123) rotate(45)")
    svg_window.useElement("grupa1", 55, 25,
                          transform="scale(0.4) rotate(-15.4) translate(50, 50)")
    svg_window.useElement("grupa1", 200, 100,
                          transform="scale(0.6) rotate(115.4)")

#     svg_window.append(prostokat3)


    svg_window.store(filename)
    print "\n-- %s -------------------------\n%s" % (filename, svg_window)

def __TestCSSUseCase():

    filename = "_test_out/TestCSSUseCase.svg"

    svgDefinitions = SvgDefinitionsContainer()

    svg_window = SvgWindow("100%", "100%", viewBox="0 0 500 500",
                           preserveAspectRatio="xMinYMin meet",
                           style='stroke-width: 0px; background-color: #8AC;')

    svgDefinitions.newStyle(".klasaA",
                            stroke="green", stroke_width=0.6,
                            stroke_opacity=0.4,
                            fill="green", fill_opacity=0.23, rx=5, ry=5)

    svgDefinitions.newStyle(".klasaA:hover",
                            stroke="yellow", stroke_width=1.2,
                            stroke_opacity=0.3,
                            fill="green", fill_opacity=0.35)

    grupa1 = DefineSvgGroup("grupa1", svgDefinitions,
                            Class="klasaA")

    # define elements to be used
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
    alink.attributes["xlink:href"] = "TestOtherUseCase.svg"
    alink.append(XmlElement("rect", x=15, y=50, width=60, height=20, Class="klasaA"))


    svg_window.append(svgDefinitions)
    svg_window.append(alink)
    svg_window.useElement("grupa1", 45, 130)
    svg_window.useElement("grupa1", 180, 100, transform="scale(0.6) rotate(45)")
    svg_window.useElement("grupa1", 55, 25, transform="scale(0.4) rotate(-15.4) translate(50, 50)")
    svg_window.useElement("grupa1", 80, 90, transform="scale(0.7) rotate(15.4) translate(50, 50)")
    svg_window.useElement("grupa1", 220, 80)

    tekstt3 = XmlElement("text", x="0", y="17", text="SVG", Class="klasaA")
    svg_window.append(tekstt3)

    svg_window.store(filename)
    print "\n-- %s -------------------------\n%s" % (filename, svg_window)


def __TestOtherUseCase():
    # A good practice is to define svg objects, and insert them
    # using the definition; this is overkill for this example, but it
    # provides a test of the class.

    svg_window = SvgWindow(300, 200)
    svgDefinitions = SvgDefinitionsContainer()
    svg_window.append(svgDefinitions)

    kolko = XmlElement("circle", cx=0, cy=0, r=20, fill="red", id="red_circle", stroke='#851')
    kolko.attributes["stroke-width"] = '0.8pt'
    svgDefinitions.append(kolko)

    kolko2 = XmlElement("circle", cx=0, cy=0, r=29, id="circle2", stroke='#421',
                        fill_opacity=0.5, stroke_width='0.3pt')


    prostokat = XmlElement("rect", width="10", height="14",
                           style="fill:rgb(200,90,100); stroke-width:1; stroke:rgb(0,0,0); fill-opacity:0.7")
    kreska = XmlElement("polyline", points="0,0 45,36 49,51 23,0 14,3 0,0", stroke="#146")

    grupa1 = XmlElement("g", id="grupa1")
    grupa1.append(XmlComment("To jest moja hiper grupa"))
    grupa1.append(kolko2)
    grupa1.append(kreska)
    grupa1.append(prostokat)
    svgDefinitions.append(grupa1)

    # we now create an svg object, that will make use of the definition above.
    for it in range(1, 7):
        svg_window.useElement("circle2", 63 * it / 2, 63 * it / 3, fill="#%d" % (it * 100 + it * 20))
    svg_window.useElement("grupa1", 30, 120)
    for it in range(1, 8):
        svg_window.useElement("circle2", 200 - 17 * it, 30 * it,
                              fill="#%d" % (it * 4 + it * 10), transform="scale(%g)" % (it / 8.0))

    svg_window.useElement("red_circle", 16, 20)
    svg_window.useElement("circle2", 190.34, 6.66, fill="magenta")
    svg_window.useElement("red_circle", 10, 45)

    filename = "_test_out/TestOtherUseCase.svg"
    svg_window.store(filename)
    print "\n-- %s -------------------------\n%s" % (filename, svg_window)

if __name__ == "__main__":

    __TestSimpliestUseCase()
    __TestCSSUseCase()
    __TestOtherUseCase()
