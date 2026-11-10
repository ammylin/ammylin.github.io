#!/usr/bin/env python3
"""Check built routes, links, assets, and preserved post text before publishing."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_site'
errors=[]

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.ids=set(); self.h1s=0; self.text=[]; self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag=='h1': self.h1s+=1
        if tag=='a' and 'href' in a: self.links.append(a['href'])
        if tag in {'img','script','link'}:
            url=a.get('src') or a.get('href')
            if url: self.links.append(url)
        if tag=='img': self.images.append(a)
    def handle_data(self,text): self.text.append(text)

documents={}
for p in OUT.rglob('*.html'):
    doc=Document(); doc.feed(p.read_text()); documents[p]=doc
    if p.parent.name!='feed' and doc.h1s!=1: errors.append(f'{p.relative_to(OUT)}: expected one H1, found {doc.h1s}')
    for img in doc.images:
        if 'alt' not in img: errors.append(f'{p.relative_to(OUT)}: image is missing alt attribute')

for p,doc in documents.items():
    for link in doc.links:
        url=urlparse(link)
        if url.scheme or url.netloc: continue
        target=OUT/unquote(url.path.lstrip('/')) if url.path.startswith('/') else p.parent/unquote(url.path)
        if not url.path: target=p
        if target.is_dir(): target=target/'index.html'
        if not target.exists():
            errors.append(f'{p.relative_to(OUT)}: missing local link {link}')
        elif url.fragment and target in documents and unquote(url.fragment) not in documents[target].ids:
            errors.append(f'{p.relative_to(OUT)}: missing anchor {link}')

manifest=json.loads((ROOT/'content/manifest.json').read_text())
for post in manifest['posts']:
    original=Document(); original.feed((ROOT/'content'/f'{post["slug"]}.html').read_text())
    target=OUT/post['slug']/'index.html'
    if target not in documents:
        errors.append(f'Original post route missing: {post["slug"]}'); continue
    source_words=re.sub(r'\s+',' ',''.join(original.text)).strip()
    published_words=re.sub(r'\s+',' ',''.join(documents[target].text)).strip()
    if source_words not in published_words: errors.append(f'Post text changed or missing: {post["slug"]}')

for page in ['about','contact','events-gigs','lessons','media','press']:
    if not (OUT/page/'index.html').exists(): errors.append(f'Original page route missing: {page}')
for p in OUT.rglob('*.html'):
    text=p.read_text()
    if re.search(r'(?:src|href)=["\']https?://(?:www\.)?ammylin\.com/wp-',text):
        errors.append(f'{p.relative_to(OUT)}: runtime asset still depends on WordPress')

if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'Passed: {len(documents)} HTML documents; all local links, anchors, and assets resolve.')
print(f'Preserved all {len(manifest["posts"])} post bodies and original post routes. No WordPress runtime assets.')
