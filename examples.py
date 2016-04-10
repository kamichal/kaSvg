#!/usr/bin/python

'''
Created on 29 Mar 2016

@author: kamichal
'''

from kaSvg import SvgWindow, XmlElement, XmlComment, ShapesGroup

def simple_example():

    w = 300; h = 200; rw = 100; rh = 80; fh = 30
    window = SvgWindow(w, h, stroke_width='0.7px', background_color='#8AF')

    rect = XmlElement("rect", x=(w - rw) / 2, y=(h - rh) / 2,
                      width=rw, height=rh,
                      stroke="green", fill_opacity=0.2)

    circ = XmlElement("circle", cx=w * 0.2568, cy=h * 0.3234,
                      r=fh * 3, stroke="#deb", fill = "#bed",
                      stroke_width="1.3px", fill_opacity=0.3)

    text = XmlElement("text", x=w / 2, y=h / 2, text="SVG",
                      text_anchor="middle", font_size=fh,
                      style="\
font-family: Times New Roman; stroke: #deb; fill: #0000cd; font-weight:700;")

    window.append(circ)
    window.append(rect)
    window.append(text)

    window.store("_test_out/SimpleExample.svg")

def simple_example_2():

    filename = "_test_out/TestSimpliestUseCase.svg"

    svg_window = SvgWindow(300, 200,
                           stroke_width='0px',
                           background_color='#8AC')

    kolko = XmlElement("circle", cx=0, cy=30, r=28, fill="red",
                       stroke='#851', stroke_width=10, stroke_opacity=0.5)

    prostokat = XmlElement("rect", x=-30, y=-5, width="80", height="10")

    prostokat2 = XmlElement("rect", x=-10, y=0,
                            width=60, height=20,
                            rx=5, ry=5,
                            fill_opacity=0.5)

    prostokat3 = XmlElement("rect", x=50, y=50, width="80", height="30",
                            fill_opacity=0.2)

    g = ShapesGroup("grupa1", kolko, prostokat, prostokat2, prostokat3,
                    stroke="green", stroke_width=2, fill="white")

    svg_window.use(g, 45, 130)

    svg_window.use(g, 180, 100, transform="scale(1.123) rotate(45)")
    svg_window.use(g, 55, 25, transform="scale(0.4) rotate(-15.4) translate(50, 50)")
    svg_window.use(g, 200, 100, transform="scale(0.6) rotate(115.4)")

    svg_window.store(filename)
    print "\n-- %s -------------------------\n%s" % (filename, svg_window)

def CSS_example():

    filename = "_test_out/TestCSSUseCase.svg"

    svg_window = SvgWindow("100%", "100%", viewBox="0 0 500 500",
                           preserveAspectRatio="xMinYMin meet",
                           style='stroke-width: 0px; background-color: #8AC;')

    svg_window.style(".klasaA",
                        stroke="green", stroke_width=0.6,
                        stroke_opacity=0.4,
                        fill="green", fill_opacity=0.23, rx=5, ry=5)

    svg_window.style(".klasaA:hover",
                        stroke="yellow", stroke_width=1.2,
                        stroke_opacity=0.3,
                        fill="green", fill_opacity=0.35)

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

    grupa1 = ShapesGroup("grupa1", kolko, prostokat, prostokat2, prostokat3, 
                         tekstt, tekstt2, Class="klasaA")

    alink = XmlElement("a", id="tynlik")
    alink._attrs["xlink:href"] = "TestOtherUseCase.svg"
    alink.append(XmlElement("rect", x=15, y=50, width=60, height=20, Class="klasaA"))

    svg_window.append(alink)
    svg_window.use(grupa1, 45, 130)
    svg_window.use(grupa1, 180, 100, transform="scale(0.6) rotate(45)")
    svg_window.use(grupa1, 55, 25, transform="scale(0.4) rotate(-15.4) translate(50, 50)")
    svg_window.use(grupa1, 80, 90, transform="scale(0.7) rotate(15.4) translate(50, 50)")
    svg_window.use(grupa1, 220, 80)

    tekstt3 = XmlElement("text", x="0", y="17", text="SVG", Class="klasaA")
    svg_window.append(tekstt3)

    svg_window.store(filename)
    print "\n-- %s -------------------------\n%s" % (filename, svg_window)


def example_3():
    svg_window = SvgWindow(300, 200)

    kolko = XmlElement("circle", cx=0, cy=0, r=20, fill="red", id="red_circle",
                       stroke='#851', stroke_width='0.8pt')

    kolko2 = XmlElement("circle", cx=0, cy=0, r=29, id="circle2", stroke='#421',
                        fill_opacity=0.5, stroke_width='0.3pt')

    prostokat = XmlElement("rect", width="10", height="14",
                           style="fill:rgb(200,90,100); stroke-width:1; \
                           stroke:rgb(0,0,0); fill-opacity:0.7")

    kreska = XmlElement("polyline", points="0,0 45,36 49,51 23,0 14,3 0,0", stroke="#146")

    grupa1 = ShapesGroup("grupa1", XmlComment("To jest moja hiper grupa"),
                         kolko2, kreska, prostokat)

    # we now create an svg object, that will make use of the definition above.
    for it in range(1, 7):
        svg_window.use(kolko2, 63 * it / 2, 63 * it / 3,
                       fill="#%d" % (it * 100 + it * 20))

    svg_window.use(grupa1, 30, 120)

    for it in range(1, 8):
        svg_window.use(kolko2, 200 - 17 * it, 30 * it,
                       fill="#%d" % (it * 4 + it * 10),
                       transform="scale(%g)" % (it / 8.0))

    svg_window.use(kolko, 16, 20)
    svg_window.use(kolko2, 190.34, 6.66, fill="magenta")
    svg_window.use(kolko, 10, 45)

    filename = "_test_out/TestOtherUseCase.svg"
    svg_window.store(filename)
    print "\n-- %s -------------------------\n%s" % (filename, svg_window)

if __name__ == "__main__":

    simple_example()
    simple_example_2()
    CSS_example()
    example_3()
