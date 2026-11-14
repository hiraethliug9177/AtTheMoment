#!/usr/bin/env python3
"""Build the 小红书小工具 offline package from the website source.

Usage (from the repository root):
    python3 tools/build_xiaohongshu.py [output_dir]

Produces <output_dir>/AtTheMoment-xiaohongshu/ (unpacked) and
<output_dir>/AtTheMoment-xiaohongshu.zip with index.html at the zip root.

Website-only code is wrapped in markers and removed here:
    JS:   /*@web-only*/ ... /*@end-web-only*/
    HTML: <!--web-only--> ... <!--/web-only-->
"""
import os
import re
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'dist'))
PKG = os.path.join(OUT, 'AtTheMoment-xiaohongshu')
ZIP = PKG + '.zip'

JS_FILES = ['time.js', 'i18n.js', 'app.js']
VIEWPORT = ('<meta name="viewport" content="width=device-width, initial-scale=1.0, '
            'maximum-scale=1.0, user-scalable=no, viewport-fit=cover">')


def strip_js(src):
    out, n = re.subn(r'/\*@web-only\*/.*?/\*@end-web-only\*/', '', src, flags=re.S)
    return out, n


def strip_html(src):
    out, n = re.subn(r'<!--web-only-->.*?<!--/web-only-->', '', src, flags=re.S)
    return out, n


def main():
    if os.path.exists(PKG):
        shutil.rmtree(PKG)
    os.makedirs(PKG)

    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    html = re.sub(r'\?v=\d+"', '"', html)  # cache-busting query is website-only
    html, n = strip_html(html)
    assert n == 4, 'expected 4 web-only blocks in index.html, found %d' % n
    html = re.sub(r'<meta name="viewport"[^>]*>', VIEWPORT, html, count=1)
    html = html.replace('<meta charset="utf-8">', '<meta charset="UTF-8">')
    # Classic scripts at the end of <body>, in dependency order.
    html = re.sub(r'<script defer src="[^"]+"></script>', '', html)
    tags = ''.join('<script src="./%s"></script>' % f for f in JS_FILES)
    html = html.replace('</body>', tags + '\n</body>')
    html = html.replace('href="assets/', 'href="./assets/').replace('src="assets/', 'src="./assets/')
    html = html.replace('href="style.css"', 'href="./style.css"')
    open(os.path.join(PKG, 'index.html'), 'w', encoding='utf-8').write(html)

    for f in JS_FILES:
        src = open(os.path.join(ROOT, f), encoding='utf-8').read()
        src, _ = strip_js(src)
        assert '@web-only' not in src and '@end-web-only' not in src, f
        open(os.path.join(PKG, f), 'w', encoding='utf-8').write(src)

    shutil.copy(os.path.join(ROOT, 'style.css'), PKG)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(PKG, 'assets'),
                    ignore=shutil.ignore_patterns('.*'))

    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(PKG):
            dirs[:] = sorted(d for d in dirs if not d.startswith('.'))
            for name in sorted(files):
                if name.startswith('.'):
                    continue
                full = os.path.join(base, name)
                z.write(full, os.path.relpath(full, PKG).replace(os.sep, '/'))
    print('package:', PKG)
    print('zip:', ZIP, os.path.getsize(ZIP), 'bytes')


if __name__ == '__main__':
    main()
