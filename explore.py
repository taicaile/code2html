"""This script is used to generate online source code html pages"""
import json
import os
import sys
import shutil
import logging
from pathlib import Path

import pygments
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_for_filename
from tqdm import tqdm

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logger = logging.getLogger()


files = set()
FILES_DIR = Path("lib")
FILE_EXTs = [".html", ".js"]

for f in FILES_DIR.rglob("*.*"):
    if not f.is_file() or not f.suffix in FILE_EXTs:
        continue
    files.add(f.__str__())

logger.info(f"found {len(files)} files.")

HTMLS_DIR = "html"
if os.path.exists(HTMLS_DIR):
    shutil.rmtree(HTMLS_DIR)
os.mkdir(HTMLS_DIR)

index = []

for f in tqdm(sorted(files)):
    if f.startswith("./"):
        f = f[2:]

    formatter = HtmlFormatter(
        linenos=True,
        cssclass="source",
        # tagsfile="tags", # byte error
        full=True,
        lineanchors="line",
        anchorlinenos=True,
        filename=f,
    )

    try:
        lexer = get_lexer_for_filename(f)
        # lexer.encoding = "utf-8"
    except pygments.util.ClassNotFound as e:
        logger.error("ClassNotFound, %s: %s", f, e)
        continue
    except UnicodeDecodeError as e:
        logger.error("lexer error: %s", f)
        logger.error("UnicodeDecodeError, %s", e)
        continue

    outfile = os.path.join(HTMLS_DIR, f + ".html")
    html_dir = os.path.dirname(outfile)
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)

    try:
        with open(f, "r", encoding="utf-8") as text:
            result = pygments.highlight(text.read(), lexer, formatter)

    except UnicodeDecodeError as e:
        try:
            with open(f, "r", encoding="ISO-8859-1") as text:
                result = pygments.highlight(text.read(), lexer, formatter)
        except UnicodeDecodeError as e:
            logger.error("highlgith error: %s", f)
            logger.error("UnicodeDecodeError, %s", e)
            continue

    with open(outfile, "w", encoding="utf-8") as out:
        out.write(result)

    index.append(f'<li><a href="{f}.html">{f}</a></li>')

logger.info("Prepare to format %d/%d files", len(index), len(files))

import bs4

# load the file
with open("index.html", "r", encoding="utf-8") as file:
    soup = bs4.BeautifulSoup(file.read(), "html5lib")
filelist_tag = soup.select("#filelist")
for file in sorted(files):
    li = soup.new_tag("li")
    a = soup.new_tag("a", href="#", onclick="on_click(this)", file=file)
    a.string = Path(file).relative_to(Path(FILES_DIR)).__str__()
    li.append(a)
    soup.ul.append(li)
# save the file again
with open(f"{HTMLS_DIR}/index.html", "w") as outf:
    outf.write(str(soup.prettify()))
