#!/usr/bin/env python3
"""Build the complete website with Python's standard library. No dependencies."""
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
CONFIG = json.loads((ROOT / 'site.json').read_text())
DATA = json.loads((ROOT / 'content/manifest.json').read_text())
BASE = CONFIG['url'].rstrip('/')
POSTS = DATA['posts']
PAGES = {p['slug']: p for p in DATA['pages']}
E = escape
NAV = [('/about/', 'About'), ('/blog/', 'Writing'), ('/media/', 'Music'), ('/lessons/', 'Lessons'), ('/press/', 'Press')]
BUILT = []

def content(slug):
    return (ROOT / 'content' / (slug + '.html')).read_text()

def date_label(iso):
    return datetime.fromisoformat(iso).strftime('%B %d, %Y').replace(' 0', ' ')

def arrow():
    return '<span aria-hidden="true">↗</span>'

def header(active):
    links = ''.join(f'<a href="{url}"'+(' aria-current="page"' if active == url else '')+f'>{label}</a>' for url,label in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
    <header class="site-header"><div class="header-inner">
      <a class="wordmark" href="/" aria-label="Ammy Lin, home">Ammy Lin<span class="brand-dot" aria-hidden="true">.</span></a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="navigation"><span>Menu</span><span class="menu-lines" aria-hidden="true"></span></button>
      <nav id="navigation" aria-label="Main navigation">{links}<a class="nav-contact" href="/contact/"{' aria-current="page"' if active=='/contact/' else ''}>Say hello {arrow()}</a></nav>
    </div></header>'''

def footer():
    return f'''<footer class="site-footer"><div class="footer-top"><a class="wordmark" href="/">Ammy Lin<span class="brand-dot" aria-hidden="true">.</span></a><p>Stay curious. Keep growing.</p>
    <div class="footer-links"><a href="mailto:{E(CONFIG['email'])}">Email {arrow()}</a><a href="https://www.youtube.com/@ammy-lin">YouTube {arrow()}</a><a href="/feed.xml">RSS {arrow()}</a></div></div>
    <div class="footer-bottom"><span>© {datetime.now().year} Ammy Lin</span><span>A little corner of the internet, made with care.</span><a href="/events-gigs/">Events &amp; gigs</a></div></footer>'''

def page(path, title, body, *, active='', description=None, image=None, article=None):
    desc = description or CONFIG['description']
    full_title = title + ' — Ammy Lin' if title else 'Ammy Lin — Writing, music & everyday discoveries'
    canonical = BASE + path
    og_image = BASE + (image or DATA['landscape'])
    robots = '<meta name="robots" content="noindex, nofollow">' if CONFIG.get('preview') else ''
    structured = {'@context':'https://schema.org','@type':'Person','name':CONFIG['name'],'url':BASE,'sameAs':['https://www.youtube.com/@ammy-lin']}
    if article:
        structured={'@context':'https://schema.org','@type':'BlogPosting','headline':article['title'],'datePublished':article['date'],'author':{'@type':'Person','name':CONFIG['name']},'url':canonical,'image':og_image}
    html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title><meta name="description" content="{E(desc,quote=True)}">{robots}
<link rel="canonical" href="{E(canonical)}"><meta name="theme-color" content="#f7f5ef">
<meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:title" content="{E(full_title,quote=True)}"><meta property="og:description" content="{E(desc,quote=True)}"><meta property="og:url" content="{E(canonical)}"><meta property="og:image" content="{E(og_image)}">
<meta name="twitter:card" content="summary_large_image"><link rel="icon" href="{DATA['favicon']}" type="image/webp">
<link rel="stylesheet" href="/assets/style.css"><script src="/assets/main.js" defer></script>
<link rel="alternate" type="application/rss+xml" title="Ammy Lin’s writing" href="/feed.xml">
<script type="application/ld+json">{json.dumps(structured,ensure_ascii=False).replace('</','<\\/')}</script>
</head><body>{header(active)}<main id="main">{body}</main>{footer()}</body></html>'''
    dest = OUT / (path.lstrip('/') + 'index.html' if path.endswith('/') else path.lstrip('/'))
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(html)
    BUILT.append(path)

def post_card(p):
    return f'''<article class="post-card"><a class="card-image" href="/{p['slug']}/" tabindex="-1" aria-hidden="true"><img src="{p['image']}" alt="" width="640" height="480" loading="lazy" decoding="async"></a><div class="post-meta"><time datetime="{p['date']}">{date_label(p['date'])}</time><span>{p['minutes']} min read</span></div><h3><a href="/{p['slug']}/">{E(p['title'])} {arrow()}</a></h3><p>{E(p['excerpt'])}</p></article>'''

def page_intro(eyebrow, title, subtitle=''):
    return f'<div class="page-intro"><p class="eyebrow">{eyebrow}</p><h1>{title}</h1>' + (f'<p class="page-deck">{subtitle}</p>' if subtitle else '') + '</div>'

def home():
    body=f'''<section class="hero wrap"><div class="hero-copy"><p class="eyebrow"><span class="tiny-sun" aria-hidden="true">✳</span> Hello, I’m Ammy</p><h1>A life of<br><em>curiosity.</em></h1><p class="hero-intro">An explorer, musician, and lifelong learner. Finding meaning in the little things, and sharing what I discover along the way.</p><a class="button" href="/about/">A little about me {arrow()}</a><a class="text-link hero-secondary" href="/blog/">Read my writing <span aria-hidden="true">↓</span></a><div class="hero-footnote"><span class="small-line" aria-hidden="true"></span> Writing · Music · Everyday discoveries</div></div><figure class="hero-photo"><img src="{DATA['landscape']}" alt="Ammy sitting on a rocky overlook, looking out across the water" width="1600" height="1280" fetchpriority="high"><figcaption>A little room to pause. A little more to discover.</figcaption><span class="photo-corner" aria-hidden="true">AL</span></figure></section>
    <div class="intro-strip wrap"><span class="eyebrow">Welcome to my corner<br>of the internet</span><p>I hope to use this space to share my thoughts, document my growth, and build deeper connections with the world.<br><span>I’m glad you’re here.</span></p><span class="intro-star" aria-hidden="true">✳</span></div>
    <section class="writing-section wrap"><div class="section-heading"><div><p class="eyebrow">Notes along the way</p><h2>From my journal<span class="brand-dot">.</span></h2></div><a class="text-link" href="/blog/">All my writing {arrow()}</a></div><div class="post-grid">{''.join(post_card(p) for p in POSTS[:3])}</div></section>
    <section class="music-feature wrap"><div class="music-photo"><img src="/assets/images/8c33ca86a2-9A723BA5-6BAD-4A8E-A196-6A9269BE5A39_Original-1024x683-632x427.webp" alt="Ammy playing the viola at a performance" width="632" height="427" loading="lazy"></div><div class="music-copy"><p class="eyebrow">Another way to tell a story</p><h2>A life with<br><em>music in it.</em></h2><p>From flute and viola to dizi and piano, music has been a constant thread in my life. Come listen to a few of my performances.</p><a class="button button-light" href="/media/">Explore my music {arrow()}</a></div></section>
    <section class="hello-section wrap"><p class="eyebrow">A conversation starts somewhere</p><h2>Let’s connect<span class="brand-dot">.</span></h2><p>A question, a shared interest, or just a hello.<br>I’d love to hear from you.</p><a class="text-link" href="/contact/">Say hello {arrow()}</a></section>'''
    page('/','',body)

def build_about():
    text=content('about')
    # The original portrait is displayed once, alongside the opening biography.
    text=re.sub(r'<img\b[^>]*>', '', text)
    split=text.find('<h2')
    opening=text[:split] if split>=0 else text
    values=text[split:] if split>=0 else ''
    body=f'''<section class="wrap">{page_intro('A little about me','Always learning.<br><em>Always becoming.</em>')}<div class="about-opening"><div class="prose">{opening}</div><figure class="portrait"><img src="{DATA['portrait']}" alt="Portrait of Ammy Lin" width="291" height="331"><figcaption>Hi, I’m Ammy. It’s lovely to meet you.</figcaption></figure></div><div class="prose values-section">{values}</div></section>'''
    page('/about/','About',body,active='/about/')
    page('/about-me/','About',f'<section class="wrap narrow">{page_intro("Welcome","Hello, I’m Ammy.")}<p class="page-deck">An explorer, musician, and lifelong learner.</p><a class="button" href="/about/">Read my biography {arrow()}</a></section>',active='/about/')

def build_blog():
    body=f'<section class="wrap">{page_intro("The journal","Thoughts, stories,<br><em>and small discoveries.</em>","Reflections on growth, gratitude, and the everyday moments that stay with me.")}<div class="blog-toolbar"><span>{len(POSTS)} stories, and counting</span><label class="search-label" for="story-search">Find a story<input id="story-search" type="search" placeholder="Search my writing…" autocomplete="off"></label></div><div class="post-grid blog-grid" id="stories">'+''.join(post_card(p) for p in POSTS)+'</div><p id="search-empty" class="empty-state" hidden>No stories found. Try another word.</p><p id="search-status" class="sr-only" role="status" aria-live="polite"></p></section>'
    page('/blog/','Writing',body,active='/blog/')
    for n,p in enumerate(POSTS):
        related=[q for q in POSTS if q['slug']!=p['slug']][:2]
        body=f'''<article class="wrap article-wrap"><a class="text-link back-link" href="/blog/">← All writing</a><header class="article-header"><p class="eyebrow">Notes along the way</p><h1>{E(p['title'])}</h1><p class="post-meta"><time datetime="{p['date']}">{date_label(p['date'])}</time><span>{p['minutes']} min read</span></p></header><div class="prose article-body">{content(p['slug'])}</div><div class="article-signoff"><p>Thanks for reading.</p><span>— Ammy</span><a class="text-link rss-link" href="/feed.xml">Follow along with RSS {arrow()}</a></div><section class="related"><p class="eyebrow">A little more to explore</p><div class="related-grid">{''.join(f'<a href="/{q["slug"]}/">{E(q["title"])} {arrow()}</a>' for q in related)}</div></section></article>'''
        page('/'+p['slug']+'/',p['title'],body,active='/blog/',description=p['excerpt'],image=p['image'],article=p)

def build_music():
    groups=[]
    for group in dict.fromkeys(v['group'] for v in DATA['videos']):
        cards=[]
        for v in DATA['videos']:
            if v['group']!=group: continue
            thumb=f'<img src="{v["thumbnail"]}" alt="" width="480" height="360" loading="lazy">' if v.get('thumbnail') else ''
            cards.append(f'''<article class="video-card"><a class="video-poster" href="{E(v['url'])}" aria-label="Watch {E(v['title'],quote=True)} on YouTube">{thumb}<span class="play-icon" aria-hidden="true">▶</span></a><h3>{E(v['title'])}</h3><a class="video-fallback" href="{E(v['url'])}">Watch on YouTube {arrow()}</a></article>''')
        groups.append(f'<section class="instrument-section" id="{group.lower()}"><div class="instrument-heading"><h2>{group}</h2><span>{len(cards):02d} performances</span></div><div class="video-grid">'+''.join(cards)+'</div></section>')
    body=f'''<section class="wrap">{page_intro('In good company','A few notes.<br><em>A lot of heart.</em>', 'A selection of my musical performances. Thank you to everyone who has supported me along the way.')}<div class="music-toolbar"><div class="instrument-links"><a href="#flute">Flute</a><a href="#dizi">Dizi</a><a href="#piano">Piano</a></div><a class="text-link" href="https://www.youtube.com/@ammy-lin">My YouTube channel {arrow()}</a></div>{''.join(groups)}<div class="page-callout"><h2>Music is better together.</h2><p>Explore lessons or get in touch about a performance.</p><a class="button" href="/lessons/">About lessons {arrow()}</a><a class="text-link" href="/events-gigs/">Events &amp; gigs {arrow()}</a></div></section>'''
    page('/media/','Music & performances',body,active='/media/')

def build_lessons():
    text=content('lessons')
    text=text.replace('Interested? Please fill out the form below and I will get in contact with you promptly.', 'Interested? Please fill out the lesson interest form and I will get in contact with you promptly.')
    body=f'<section class="wrap narrow">{page_intro("Room to grow","Make room<br><em>for music.</em>","Flute and viola lessons, shaped around your goals.")}<div class="prose lessons-body">{text}</div><div class="page-callout"><p>Questions about lessons?</p><a class="text-link" href="mailto:{E(CONFIG["email"])}">Send me an email {arrow()}</a></div></section>'
    page('/lessons/','Music lessons',body,active='/lessons/')

def build_press():
    body=f'<section class="wrap narrow">{page_intro("In the news","Stories from<br><em>elsewhere.</em>","A collection of features, conversations, and milestones over the years.")}<div class="prose press-list">{content("press")}</div></section>'
    page('/press/','Press',body,active='/press/')

def build_contact():
    email=E(CONFIG['email'])
    body=f'''<section class="wrap contact-page">{page_intro('Good things start with hello','Let’s make<br><em>a connection.</em>', 'A question, a musical collaboration, or something that made you think of me. My inbox is open.')}<a class="email-link" href="mailto:{email}">{email} {arrow()}</a><div class="contact-options"><div><p class="eyebrow">Interested in lessons?</p><p>Tell me a little about yourself and what you’d like to learn.</p><a class="text-link" href="https://forms.gle/bvyfdC7ao5cuSAj58">Lesson interest form {arrow()}</a></div><div><p class="eyebrow">Come listen</p><p>Find more of my musical performances on YouTube.</p><a class="text-link" href="https://www.youtube.com/@ammy-lin">Visit my channel {arrow()}</a></div></div></section>'''
    page('/contact/','Contact',body,active='/contact/')

def build_events():
    page('/events-gigs/','Events & gigs',f'''<section class="wrap narrow">{page_intro('Out in the world','Events <em>&amp; gigs.</em>', 'This page is taking shape.')}<div class="page-callout"><h2>Let’s talk music.</h2><p>For performance inquiries or information about upcoming events, please get in touch.</p><a class="button" href="mailto:{E(CONFIG['email'])}">Contact Ammy {arrow()}</a><a class="text-link" href="/media/">Listen to past performances {arrow()}</a></div></section>''')

def build_feeds():
    sitemap=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for path in BUILT:
        if path=='/404.html' or path=='/about-me/': continue
        url=ET.SubElement(sitemap,'url'); ET.SubElement(url,'loc').text=BASE+path
    ET.indent(sitemap)
    (OUT/'sitemap.xml').write_bytes(ET.tostring(sitemap,encoding='utf-8',xml_declaration=True))
    (OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n' if CONFIG.get('preview') else f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    rss=ET.Element('rss',version='2.0'); channel=ET.SubElement(rss,'channel')
    for tag,val in [('title','Ammy Lin — Notes along the way'),('link',BASE+'/blog/'),('description',CONFIG['description']),('language','en-us')]: ET.SubElement(channel,tag).text=val
    for p in POSTS:
        item=ET.SubElement(channel,'item')
        for tag,val in [('title',p['title']),('link',BASE+'/'+p['slug']+'/'),('guid',BASE+'/'+p['slug']+'/'),('description',p['excerpt']),('pubDate',datetime.fromisoformat(p['date']).strftime('%a, %d %b %Y %H:%M:%S +0000'))]: ET.SubElement(item,tag).text=val
    (OUT/'feed').mkdir(exist_ok=True)
    (OUT/'feed/index.xml').write_bytes(ET.tostring(rss,encoding='utf-8',xml_declaration=True))
    (OUT/'feed.xml').write_bytes(ET.tostring(rss,encoding='utf-8',xml_declaration=True))
    # Preserve the original WordPress /feed/ path with a link to the RSS document.
    (OUT/'feed/index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/feed.xml"><title>Ammy Lin — RSS feed</title></head><body><a href="/feed.xml">Read the RSS feed</a></body></html>')

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/'assets',OUT/'assets')
    (OUT/'.nojekyll').touch()
    home(); build_about(); build_blog(); build_music(); build_lessons(); build_press(); build_contact(); build_events()
    page('/404.html','Page not found',f'<section class="wrap narrow">{page_intro("A small detour","A little <em>lost?</em>","This page isn’t here, but there’s plenty more to explore.")}<a class="button" href="/">Back home {arrow()}</a><a class="text-link" href="/blog/">Explore my writing {arrow()}</a></section>')
    build_feeds()
    if not CONFIG.get('preview'):
        hostname=urlparse(BASE).hostname
        if hostname and not hostname.endswith('.github.io'): (OUT/'CNAME').write_text(hostname+'\n')
    print(f'Built {len(BUILT)} pages in {OUT}')
    if CONFIG.get('preview'): print('Preview mode: search indexing is disabled; custom domain is not configured.')

if __name__=='__main__': main()
