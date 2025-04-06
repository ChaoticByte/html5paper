#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from jinja2 import Template
from yaml import safe_load

# Paper CSS by cognitom
# https://github.com/cognitom/paper-css
# LICENSE: MIT
PAPER_CSS = """@page { margin: 0 }
body { margin: 0 }
.sheet {
  margin: 0;
  overflow: hidden;
  position: relative;
  box-sizing: border-box;
  page-break-after: always;
}
/** Paper sizes **/
body.A3               .sheet { width: 297mm; height: 419mm }
body.A3.landscape     .sheet { width: 420mm; height: 296mm }
body.A4               .sheet { width: 210mm; height: 296mm }
body.A4.landscape     .sheet { width: 297mm; height: 209mm }
body.A5               .sheet { width: 148mm; height: 209mm }
body.A5.landscape     .sheet { width: 210mm; height: 147mm }
body.letter           .sheet { width: 216mm; height: 279mm }
body.letter.landscape .sheet { width: 280mm; height: 215mm }
body.legal            .sheet { width: 216mm; height: 356mm }
body.legal.landscape  .sheet { width: 357mm; height: 215mm }
/** Padding area **/
.sheet.padding-10mm { padding: 10mm }
.sheet.padding-15mm { padding: 15mm }
.sheet.padding-20mm { padding: 20mm }
.sheet.padding-25mm { padding: 25mm }
/** For screen preview **/
@media screen {
  body { background: #e0e0e0 }
  .sheet {
    background: white;
    box-shadow: 0 .5mm 2mm rgba(0,0,0,.3);
    margin: 5mm auto;
  }
}
/** Fix for Chrome issue #273306 **/
@media print {
           body.A3.landscape { width: 420mm }
  body.A3, body.A4.landscape { width: 297mm }
  body.A4, body.A5.landscape { width: 210mm }
  body.A5                    { width: 148mm }
  body.letter, body.legal    { width: 216mm }
  body.letter.landscape      { width: 280mm }
  body.legal.landscape       { width: 357mm }
}"""

BASE_TEMPLATE = Template(
"""<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
<meta charset="UTF-8">
<title>{{ title }}</title>
</head>
<body class="{{ paper_size }} {{ orientation }}">
<style>
/* paper.css -> https://github.com/cognitom/paper-css */
{{ paper_css }}
/* predefined */
@page { size: {{ paper_size }} {{ orientation }}; }
/* own rules */
{{ css }}
</style>
{{ content }}
</body>
</html>""")


if __name__ == "__main__":
    argp = ArgumentParser()
    argp.add_argument(
        "-t", "--template",
        help="The path to the html content template",
        metavar="PATH",
        type=Path, required=True)
    argp.add_argument(
        "-s", "--css",
        help="The path to the css file",
        metavar="PATH",
        type=Path)
    argp.add_argument(
        "-d", "--data",
        help="The path to the yaml file containing the variables used in the templates",
        metavar="PATH",
        type=Path, required=True)
    argp.add_argument(
        "--size",
        help="The paper size (default: A4)",
        choices=["A3", "A4", "A5", "letter", "legal"],
        default="A4"
    )
    argp.add_argument(
        "--orientation",
        help="The page orientation (default: portrait)",
        choices=["portrait", "landscape"],
        default="portrait"
    )
    args = argp.parse_args()
    # load data
    with args.data.open("r") as f:
        data = safe_load(f)
    # load css
    if args.css is None:
        css = "/* empty */"
    else:
        with args.css.open("r") as f:
            css = f.read()
    # template content
    with args.template.open("r") as f:
        content_template = Template(f.read())
    # additional functions
    content_template.globals['now'] = datetime.now
    content_template.globals['strftime'] = datetime.strftime
    # render
    content = content_template.render(data)
    # template out complete html document
    result = BASE_TEMPLATE.render(
        lang=data["lang"],
        title=data["title"],
        paper_size=args.size,
        orientation=args.orientation,
        paper_css=PAPER_CSS,
        css=css,
        content=content
    )
    print(result)
