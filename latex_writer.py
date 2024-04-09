import xml.etree.ElementTree as ET
from io import BytesIO
import cairosvg
import subprocess
import os
from PIL import Image

default_latex="""
\\documentclass{article}
\\pagestyle{empty}
\\usepackage[english]{babel}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{mathrsfs}
\\linespread{1}
\\begin{document}
$2+2$
\\end{document}
""".strip()

def create_latex(full_latex, tmp_folder):
    tmp_tex_file = f"{tmp_folder}/ltx.tex"
    if not os.path.exists(tmp_folder):
        os.mkdir(tmp_folder)
    with open(tmp_tex_file, "w") as f:
        f.write(full_latex)
    p = subprocess.Popen(["latex", "-halt-on-error", f"-output-directory={tmp_folder}", tmp_tex_file],
        stdout=subprocess.DEVNULL)
    p.wait()
    if p.returncode == 1:
        # todo: maybe make program check installation
        # and equation
        # just execute latex by itself to see it if exists
        # and read the log if theres any error messages
        raise ValueError("Latex failed, check installation and equation")

def create_svg(svg_file, tmp_folder):
    expected_output_file = f"{tmp_folder}/ltx.dvi"
    p = subprocess.Popen(["dvisvgm", expected_output_file, "-e", "-c", "15,15", "-n", "-o", svg_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    p.wait()

def process_svg(svg_file):
    # add padding
    tree = ET.parse(svg_file)
    root = tree.getroot()

    x, y, width, height = [float(n) for n in root.attrib['viewBox'].split(" ")]
    
    # 1%
    x_padding = width*.01
    y_padding = height*.01

    x-=x_padding
    y-=y_padding
    width+=x_padding*2
    height+=y_padding*2
    
    root.attrib['width'] = f"{width}pt"
    root.attrib['height'] = f"{height}pt"
    root.attrib['viewBox'] = f"{x} {y} {width} {height}"

    tree.write(svg_file)

def render_latex(latex, folder):
    svg = f"{folder}/ltx.svg"

    create_latex(latex, folder)
    create_svg(svg, folder)
    process_svg(svg)

    background_color = "#323337"

    out = BytesIO()
    cairosvg.svg2png(url=svg, write_to=out, negate_colors=True, background_color=background_color)
    image = Image.open(out)

    image.save(f"{folder}/ltx.png")