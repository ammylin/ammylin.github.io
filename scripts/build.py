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
PROJECTS = json.loads((ROOT / 'content/projects.json').read_text())
EXPERIENCE = json.loads((ROOT / 'content/experience.json').read_text())
BASE = CONFIG['url'].rstrip('/')
POSTS = DATA['posts']
PAGES = {p['slug']: p for p in DATA['pages']}
E = escape
NAV = [('/projects/', 'Projects'), ('/about/', 'About'), ('/beyond/', 'Music & more')]
BUILT = []

def content(slug):
    return (ROOT / 'content' / (slug + '.html')).read_text()

def date_label(iso):
    return datetime.fromisoformat(iso).strftime('%B %d, %Y').replace(' 0', ' ')

def arrow():
    return '<span aria-hidden="true">↗</span>'

def header(active):
    links = ''.join(f'<a href="{url}"'+(' aria-current="page"' if active == url else '')+f'>{E(label)}</a>' for url,label in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
    <header class="site-header"><div class="header-inner">
      <a class="wordmark" href="/" aria-label="Ammy Lin, home">Ammy Lin<span class="brand-dot" aria-hidden="true">.</span></a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="navigation"><span>Menu</span><span class="menu-lines" aria-hidden="true"></span></button>
      <nav id="navigation" aria-label="Main navigation">{links}<a class="nav-contact" href="/contact/"{' aria-current="page"' if active=='/contact/' else ''}>Say hello {arrow()}</a></nav>
    </div></header>'''

def footer():
    return f'''<footer class="site-footer"><div class="footer-top"><a class="wordmark" href="/">Ammy Lin<span class="brand-dot" aria-hidden="true">.</span></a><p>Thank you for visiting!</p>
    <div class="footer-links"><a href="https://github.com/ammylin">GitHub {arrow()}</a><a href="https://www.linkedin.com/in/ammy-lin/">LinkedIn {arrow()}</a><a href="mailto:{E(CONFIG['email'])}">Email {arrow()}</a><a href="/feed.xml">RSS {arrow()}</a></div></div>
    <div class="footer-bottom"><span>© {datetime.now().year} Ammy Lin</span><span>Duke University · MIDS 2027</span><a href="/beyond/">Music &amp; more {arrow()}</a></div></footer>'''

def page(path, title, body, *, active='', description=None, image=None, article=None, redirect=None):
    desc = description or CONFIG['description']
    full_title = title + ' | Ammy Lin' if title else 'Ammy Lin | Data Science at Duke University'
    canonical = BASE + (redirect or path)
    refresh = f'<meta http-equiv="refresh" content="0;url={E(redirect,quote=True)}">' if redirect else ''
    og_image = BASE + (image or DATA['landscape'])
    robots = '<meta name="robots" content="noindex, nofollow">' if CONFIG.get('preview') else ''
    structured = {'@context':'https://schema.org','@type':'Person','name':CONFIG['name'],'url':BASE,'affiliation':{'@type':'CollegeOrUniversity','name':'Duke University'},'sameAs':['https://github.com/ammylin','https://www.linkedin.com/in/ammy-lin/','https://www.youtube.com/@ammy-lin']}
    if article:
        structured={'@context':'https://schema.org','@type':'BlogPosting','headline':article['title'],'datePublished':article['date'],'author':{'@type':'Person','name':CONFIG['name']},'url':canonical,'image':og_image}
    html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title><meta name="description" content="{E(desc,quote=True)}">{robots}{refresh}
<link rel="canonical" href="{E(canonical)}"><meta name="theme-color" content="#f7f5ef">
<meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:title" content="{E(full_title,quote=True)}"><meta property="og:description" content="{E(desc,quote=True)}"><meta property="og:url" content="{E(canonical)}"><meta property="og:image" content="{E(og_image)}">
<meta name="twitter:card" content="summary_large_image"><link rel="icon" href="{DATA['favicon']}" type="image/webp">
<link rel="stylesheet" href="/assets/style.css"><link rel="stylesheet" href="/assets/portfolio.css"><script src="/assets/main.js" defer></script>
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

def project_visual(project):
    if project.get('image'):
        return f'<img src="{E(project["image"])}" alt="" width="900" height="560" loading="lazy" decoding="async">'
    motif = project.get('motif', 'risk')
    labels = {'risk': ['Environmental data', 'Interpretable models', 'Decision rules'], 'simulation': ['Default scenarios', 'Loss distributions', 'Tail risk'], 'ethics': ['Consumer', 'Executive', 'Buyer', 'Data scientist']}
    items = ''.join(f'<span>{E(label)}</span>' for label in (project.get('visual_labels') or labels.get(motif, labels['risk'])))
    return f'<div class="project-motif motif-{motif}" aria-hidden="true"><span class="motif-caption">{E(project["category"])}</span><div class="motif-items">{items}</div><span class="motif-note">{E(project["motif_label"])}</span></div>'

def project_card(project, heading='h3'):
    tags=''.join(f'<span>{E(tool)}</span>' for tool in project['tools'])
    url=f'/projects/{project["slug"]}/'
    return f'''<article class="project-card" data-project-category="{E(project['category'])}"><a class="project-image" href="{url}" tabindex="-1" aria-hidden="true">{project_visual(project)}</a><p class="project-category">{E(project['category'])}</p><{heading} class="project-title"><a href="{url}">{E(project['title'])} {arrow()}</a></{heading}><p class="project-summary">{E(project['summary'])}</p><div class="project-tags">{tags}</div><a class="project-more" href="{url}">Read about this project {arrow()}</a></article>'''

def build_projects():
    filters=''.join(f'<button type="button" data-project-filter="{E(category)}" aria-pressed="false">{E(category)}</button>' for category in dict.fromkeys(p['category'] for p in PROJECTS))
    body=f'''<section class="wrap">{page_intro('Projects &amp; teaching','A few things<br><em>I’ve worked on.</em>', 'Here are some projects from my coursework, math comps, and teaching. Many were done with classmates; you’ll find team credits and links to the code on each page.')}<div class="projects-toolbar"><div class="project-filters" role="group" aria-label="Filter projects by area"><button type="button" data-project-filter="all" aria-pressed="true">All projects</button>{filters}</div><p id="project-count" role="status" aria-live="polite">{len(PROJECTS)} projects</p></div><div class="project-grid project-grid-full" id="project-list">{''.join(project_card(p,heading='h2') for p in PROJECTS)}</div><div class="project-source-note"><p>You can find more of my coursework and other projects on GitHub.</p><a class="text-link" href="https://github.com/ammylin">My GitHub profile {arrow()}</a></div></section>'''
    page('/projects/', 'Projects', body, active='/projects/',description='My work in data science, NLP, mathematics, and teaching. Each project has a summary, links to the code or reports, and team credits.')
    for project in PROJECTS:
        tags=''.join(f'<span>{E(tool)}</span>' for tool in project['tools'])
        methods=''.join(f'<li>{E(step)}</li>' for step in project['approach'])
        image=''
        if project.get('image'):
            image=f'''<figure class="project-figure"><a href="{E(project['image'])}" aria-label="Open project figure at full size"><img src="{E(project['image'])}" alt="{E(project['image_alt'],quote=True)}" loading="lazy"></a><figcaption>{E(project['image_caption'])} <a href="{E(project['image_source'])}">Source figure {arrow()}</a></figcaption></figure>'''
        role=f'<section><h2>My part in the project</h2><p>{E(project["role"])}</p></section>' if project.get('role') else ''
        credits=f'<p class="project-credits">{E(project["credits"])}</p>' if project.get('credits') else ''
        extra=''
        for key,label in [('report',project.get('report_label','Read the report')),('demo',project.get('demo_label','Try the demo'))]:
            if project.get(key): extra+=f'<a class="text-link" href="{E(project[key])}">{E(label)} {arrow()}</a>'
        for link in project.get('additional_links', []):
            extra+=f'<a class="text-link" href="{E(link["url"])}">{E(link["label"])} {arrow()}</a>'
        body=f'''<article class="wrap project-detail"><a class="text-link back-link" href="/projects/">← All projects</a>{page_intro(E(project['category']),E(project['title']),E(project['summary']))}<div class="project-detail-meta"><p>{E(project['context'])}</p><div class="project-tags">{tags}</div></div><div class="project-actions"><a class="button" href="{E(project['github'])}">View repository {arrow()}</a>{extra}</div><div class="prose project-narrative"><section><h2>{E(project.get("question_heading", "The question"))}</h2><p>{E(project['question'])}</p></section>{role}<section><h2>{E(project.get("approach_heading", "What we did"))}</h2><ul>{methods}</ul></section></div>{image}<div class="prose project-narrative"><section><h2>Results &amp; discussion</h2><p>{E(project['takeaway'])}</p></section><section><h2>Limitations</h2><p>{E(project['limitation'])}</p></section></div><div class="project-credit-block">{credits}<p>For the code and full project details, see the <a href="{E(project['github'])}#readme">project repository</a>.</p></div><div class="project-bottom"><a class="text-link" href="/projects/">Back to all projects {arrow()}</a></div></article>'''
        page(f'/projects/{project["slug"]}/',project['title'],body,active='/projects/',description=project['summary'],image=project.get('image'))

def performance_card(video):
    image=f'<img src="{video["thumbnail"]}" alt="" width="480" height="360" loading="lazy">' if video.get('thumbnail') else ''
    return f'''<article class="video-card"><a class="video-poster" href="{E(video['url'])}" aria-label="Watch {E(video['title'],quote=True)} on YouTube">{image}<span class="play-icon" aria-hidden="true">▶</span></a><p class="project-category">{E(video['group'])}</p><h3>{E(video['title'])}</h3><a class="video-fallback" href="{E(video['url'])}">Watch on YouTube {arrow()}</a></article>'''

def writing_row(post):
    return f'<li><a href="/{post["slug"]}/"><span>{E(post["title"])}</span>{arrow()}</a><time datetime="{post["date"]}">{date_label(post["date"])}</time></li>'

def build_beyond():
    selected=[next(v for v in DATA['videos'] if v['group']==group) for group in ['Flute','Dizi','Piano']]
    remaining=[v for v in DATA['videos'] if v not in selected]
    lessons=content('lessons')
    lessons=re.sub(r"<p>I'm currently based.*?</p>", '<p>If you’re interested in lessons, please get in touch to ask about availability.</p>', lessons, flags=re.DOTALL)
    lessons=lessons.replace('the form below','the lesson interest form').replace('https://ammylin.com/media/','/beyond/#music').replace('https://ammylin.com/press/','/beyond/#press')
    years=sorted({post['date'][:4] for post in POSTS})
    archive_years=years[0] if len(years)==1 else years[0]+'–'+years[-1]
    body=f'''<section class="wrap beyond-page">{page_intro('Music &amp; writing','Music, writing,<br><em>and more.</em>', 'Music has been part of my life since I was young. I also write here occasionally, usually about things I’ve been thinking about or experiences I want to remember.')}<nav class="beyond-jumps" aria-label="On this page"><a href="#music">Music</a><a href="#writing">Writing archive</a><a href="#press">Press &amp; features</a></nav><section class="beyond-section" id="music"><div class="section-heading"><div><p class="eyebrow">Piano · Flute · Viola · Dizi</p><h2>Music<span class="brand-dot">.</span></h2></div><a class="text-link" href="https://www.youtube.com/@ammy-lin">YouTube {arrow()}</a></div><p class="beyond-intro">Here’s a little about how I got started, followed by some recordings.</p>{content("music-journey")}<h3 class="recordings-heading">A few performances</h3><div class="video-grid">{''.join(performance_card(v) for v in selected)}</div><details class="personal-details"><summary>More performances <span>{len(remaining)} recordings</span></summary><div class="video-grid expanded-videos">{''.join(performance_card(v) for v in remaining)}</div></details><details class="personal-details" id="lessons"><summary>Teaching &amp; lesson inquiries</summary><div class="prose teaching-story">{lessons}</div></details></section><section class="beyond-section" id="writing"><div class="section-heading"><div><p class="eyebrow">From the blog</p><h2>Writing<span class="brand-dot">.</span></h2></div><span class="archive-years">{archive_years}</span></div><p class="beyond-intro">A place to share my thoughts and document my growth. I don’t write here as often as I’d like, but I’m glad to have these posts to look back on.</p><ul class="writing-list">{''.join(writing_row(p) for p in POSTS[:3])}</ul><details class="personal-details"><summary>More from the archive <span>{len(POSTS)-3} essays</span></summary><ul class="writing-list">{''.join(writing_row(p) for p in POSTS[3:])}</ul></details></section><section class="beyond-section" id="press"><p class="eyebrow">In the news</p><h2>Press &amp; features<span class="brand-dot">.</span></h2><p class="beyond-intro">A few articles and interviews about my music and other experiences.</p><details class="personal-details"><summary>Browse press coverage</summary><div class="prose press-list">{content('press')}</div></details></section></section>'''
    page('/beyond/','Music & more',body,active='/beyond/',description='My musical background, some performances, and earlier blog posts about what I’ve been learning and thinking about.')

def build_legacy_routes():
    routes={'/blog/':('Writing archive','/beyond/#writing'),'/media/':('Music','/beyond/#music'),'/lessons/':('Music lessons','/beyond/#lessons'),'/press/':('Press','/beyond/#press'),'/events-gigs/':('Performance inquiries','/beyond/#music'),'/about-me/':('About','/about/')}
    for path,(label,target) in routes.items():
        body=f'<section class="wrap narrow">{page_intro("Moved page",E(label))}<p class="page-deck">You can now find this on the page linked below.</p><a class="button" href="{target}">Continue to {E(label.lower())} {arrow()}</a></section>'
        page(path,label,body,active='/beyond/',redirect=target)

def home():
    featured=[p for p in PROJECTS if p.get('featured')]
    body=f"""<section class="data-hero wrap"><div class="data-hero-copy"><p class="eyebrow"><span class="academic-dot" aria-hidden="true"></span> Duke University · Data science</p><h1>Hi, I’m Ammy.<br><em>Welcome!</em></h1><p class="data-hero-intro">I’m a master’s student in Interdisciplinary Data Science at Duke University. I also play a few instruments and write here from time to time. This is where I share what I’m working on and a little of what I’m learning along the way.</p><div class="hero-actions"><a class="button" href="/projects/">See my projects {arrow()}</a><a class="text-link" href="https://github.com/ammylin">GitHub {arrow()}</a></div><p class="data-hero-note">I’m an explorer, learner, and person constantly striving for growth.</p></div><aside class="portfolio-profile" aria-label="About Ammy"><div class="profile-topline"><span class="eyebrow">Hello, I’m Ammy</span><span aria-hidden="true">AL / 01</span></div><img src="{DATA['portrait']}" alt="Portrait of Ammy Lin" width="922" height="1152" fetchpriority="high"><div class="profile-caption"><span>Duke University</span><p>Interdisciplinary Data Science · M.S. 2027</p></div><div class="profile-bottom"><span>Previously at Carleton College</span><p>Mathematics · Chinese · Music</p></div></aside></section>
    <div class="focus-strip wrap"><p class="eyebrow">Areas I’m exploring</p><span>Machine learning</span><span>Data engineering</span><span>Statistical analysis</span><span>Data ethics</span></div>
    <section class="lately-section wrap" aria-labelledby="lately-heading"><div class="section-heading"><div><p class="eyebrow">Lately</p><h2 id="lately-heading">What I’ve been up to<span class="brand-dot">.</span></h2></div><a class="text-link" href="/about/#experience">My experience {arrow()}</a></div><div class="lately-grid"><a href="/about/#experience"><p class="eyebrow">Research · TRUST Lab</p><h3>LLM agent research</h3><p>I’m studying how language-model agents’ public statements compare with what they actually do in a negotiation.</p><span class="lately-link">More about my research {arrow()}</span></a><a href="/about/#experience"><p class="eyebrow">Teaching · Duke</p><h3>Data engineering TA</h3><p>I hold office hours and lead demos for IDS 706: Data Engineering Systems at Duke.</p><span class="lately-link">More about teaching {arrow()}</span></a><a href="/about/#experience"><p class="eyebrow">Summer 2026 · Liberty Mutual</p><h3>Data science internship</h3><p>Over the summer of 2026, I worked on insurance models using claim photos and structured data at Liberty Mutual.</p><span class="lately-link">About my internship {arrow()}</span></a></div></section>
    <section class="selected-projects wrap"><div class="section-heading"><div><p class="eyebrow">Coursework &amp; team projects</p><h2>Selected projects<span class="brand-dot">.</span></h2></div><a class="text-link" href="/projects/">All {len(PROJECTS)} projects {arrow()}</a></div><div class="project-grid">{''.join(project_card(p) for p in featured)}</div></section>
    <section class="background-note wrap"><figure class="background-photo"><img src="{DATA['landscape']}" alt="Ammy sitting on a rocky shoreline, looking out over the water" width="1600" height="1280" loading="lazy" decoding="async"></figure><div><p class="eyebrow">My background</p><h2>A little<br><em>about me.</em></h2><p>I graduated from Carleton College with majors in mathematics and Chinese and a minor in music performance. While I was there, I worked with other students on math, writing, and public speaking. Teaching has continued to be part of my life since then, both in music lessons and now at Duke.</p><a class="text-link" href="/about/">More about me {arrow()}</a></div></section>
    <section class="beyond-teaser wrap"><div class="beyond-teaser-copy"><p class="eyebrow">Outside of data science</p><h2>Music, writing,<br><em>and other things.</em></h2><p>I started with piano, then took up flute and viola in sixth grade. In college, I joined the Chinese Music Ensemble and began learning the dizi (Chinese bamboo flute). You can find a few performances here, along with some of my earlier writing.</p><a class="text-link" href="/beyond/">Music &amp; writing {arrow()}</a></div><figure class="teaser-music-photo"><img src="/assets/images/8c33ca86a2-9A723BA5-6BAD-4A8E-A196-6A9269BE5A39_Original-1024x683-632x427.webp" alt="Ammy playing viola in a performance" width="632" height="427" loading="lazy" decoding="async"></figure></section>
    <section class="hello-section wrap"><p class="eyebrow">Get in touch</p><h2>Feel free to<br><em>say hello!</em></h2><p>If you’d like to connect or chat, you can reach me by email.</p><a class="text-link" href="/contact/">Get in touch {arrow()}</a></section>"""
    page('/','',body)

def build_about():
    biography=content('about')
    split=biography.index('<h2')
    opening,values=biography[:split],biography[split:]
    roles=[]
    for role in EXPERIENCE['current']:
        tags=''.join(f'<span>{E(tag)}</span>' for tag in role['tags'])
        roles.append(f'''<article class="experience-row"><div class="experience-when"><p>{E(role['dates'])}</p><span>{E(role['organization'])}</span></div><div><h3>{E(role['title'])}</h3><p class="experience-summary">{E(role['summary'])}</p><div class="project-tags">{tags}</div></div></article>''')
    earlier=''.join(f'''<article><p class="eyebrow">{E(role['dates'])}</p><h3>{E(role['organization'])}</h3><p class="earlier-title">{E(role['title'])}</p><p>{E(role['summary'])}</p></article>''' for role in EXPERIENCE['earlier'])
    body=f'''<section class="wrap about-page">{page_intro('A little about me','Always learning.<br><em>Always becoming.</em>')}<div class="about-opening"><div class="prose">{opening}</div><figure class="portrait"><img src="{DATA['portrait']}" alt="Portrait of Ammy Lin" width="922" height="1152"></figure></div>
    <nav class="about-jumps" aria-label="On this page"><a href="#values">Ideas &amp; values</a><a href="#education">Education</a><a href="#experience">Experience</a><a href="#personal">Fun facts</a><a href="/beyond/#music">My musical journey {arrow()}</a></nav>
    <section class="prose values-section restored-values" id="values">{values}</section>
    <section class="about-section" id="education"><div class="section-heading"><div><p class="eyebrow">Education</p><h2>Where I’ve studied<span class="brand-dot">.</span></h2></div></div><div class="education-grid"><article><p class="eyebrow">2025–2027 · Expected</p><h3>Duke University</h3><p>M.S., Interdisciplinary Data Science</p></article><article><p class="eyebrow">Class of 2024</p><h3>Carleton College</h3><p>B.A., Mathematics &amp; Chinese<br>Minor in Music Performance</p></article><article><p class="eyebrow">Summer 2023</p><h3>National Taiwan University</h3><p>Chinese studies</p></article></div></section>
    <section class="about-section" id="experience"><div class="section-heading"><div><p class="eyebrow">Research, practice &amp; teaching</p><h2>Experience<span class="brand-dot">.</span></h2></div><a class="text-link" href="https://www.linkedin.com/in/ammy-lin/">LinkedIn {arrow()}</a></div><div class="experience-list">{''.join(roles)}</div><details class="personal-details earlier-experience"><summary>Earlier experience <span>Education, writing &amp; analysis</span></summary><div class="earlier-grid">{earlier}</div></details></section>
    {content('about-personal')}
    </section>'''
    page('/about/','About',body,active='/about/',description='About me, my studies at Duke and Carleton, and some of my work in data science, teaching, and music.')

def build_articles():
    for p in POSTS:
        related=[q for q in POSTS if q['slug']!=p['slug']][:2]
        body=f'''<article class="wrap article-wrap"><a class="text-link back-link" href="/beyond/#writing">← All writing</a><header class="article-header"><p class="eyebrow">From the blog</p><h1>{E(p['title'])}</h1><p class="post-meta"><time datetime="{p['date']}">{date_label(p['date'])}</time><span>{p['minutes']} min read</span></p></header><div class="prose article-body">{content(p['slug'])}</div><div class="article-signoff"><p>Thanks for reading!</p><span>Ammy</span><a class="text-link rss-link" href="/feed.xml">Subscribe with RSS {arrow()}</a></div><section class="related"><p class="eyebrow">Other posts</p><div class="related-grid">{''.join(f'<a href="/{q["slug"]}/">{E(q["title"])} {arrow()}</a>' for q in related)}</div></section></article>'''
        page('/'+p['slug']+'/',p['title'],body,active='/beyond/',description=p['excerpt'],image=p['image'],article=p)

def build_contact():
    email=E(CONFIG['email'])
    body=f"""<section class="wrap contact-page">{page_intro('Contact','Say hello!', 'You’re welcome to reach out about data science, music, lessons, or anything else you’d like to chat about.')}<a class="email-link" href="mailto:{email}">{email} {arrow()}</a><div class="contact-options"><div><p class="eyebrow">Find me online</p><p>Find project code on GitHub, or connect on LinkedIn for more about my experience.</p><div class="contact-profile-links"><a class="text-link" href="https://github.com/ammylin">GitHub {arrow()}</a><a class="text-link" href="https://www.linkedin.com/in/ammy-lin/">LinkedIn {arrow()}</a></div></div><div><p class="eyebrow">Music &amp; writing</p><p>You can listen to some performances, read earlier blog posts, or ask about music lessons here.</p><a class="text-link" href="/beyond/">Music &amp; more {arrow()}</a></div></div></section>"""
    page('/contact/','Contact',body,active='/contact/')

def build_feeds():
    sitemap=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for path in BUILT:
        if path in {'/404.html','/about-me/','/blog/','/media/','/lessons/','/press/','/events-gigs/'}: continue
        url=ET.SubElement(sitemap,'url'); ET.SubElement(url,'loc').text=BASE+path
    ET.indent(sitemap)
    (OUT/'sitemap.xml').write_bytes(ET.tostring(sitemap,encoding='utf-8',xml_declaration=True))
    (OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n' if CONFIG.get('preview') else f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    rss=ET.Element('rss',version='2.0'); channel=ET.SubElement(rss,'channel')
    for tag,val in [('title','Ammy Lin’s blog'),('link',BASE+'/beyond/#writing'),('description',CONFIG['description']),('language','en-us')]: ET.SubElement(channel,tag).text=val
    for p in POSTS:
        item=ET.SubElement(channel,'item')
        for tag,val in [('title',p['title']),('link',BASE+'/'+p['slug']+'/'),('guid',BASE+'/'+p['slug']+'/'),('description',p['excerpt']),('pubDate',datetime.fromisoformat(p['date']).strftime('%a, %d %b %Y %H:%M:%S +0000'))]: ET.SubElement(item,tag).text=val
    (OUT/'feed').mkdir(exist_ok=True)
    (OUT/'feed/index.xml').write_bytes(ET.tostring(rss,encoding='utf-8',xml_declaration=True))
    (OUT/'feed.xml').write_bytes(ET.tostring(rss,encoding='utf-8',xml_declaration=True))
    # Preserve the original WordPress /feed/ path with a link to the RSS document.
    (OUT/'feed/index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/feed.xml"><title>Ammy Lin | RSS feed</title></head><body><a href="/feed.xml">Read the RSS feed</a></body></html>')

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/'assets',OUT/'assets')
    (OUT/'.nojekyll').touch()
    home(); build_projects(); build_about(); build_articles(); build_beyond(); build_contact(); build_legacy_routes()
    page('/404.html','Page not found',f'<section class="wrap narrow">{page_intro("Page not found","This page isn’t here.","The link may have changed. You can head back to the homepage or look through my projects below.")}<a class="button" href="/">Back home {arrow()}</a><a class="text-link" href="/projects/">See my projects {arrow()}</a></section>')
    build_feeds()
    if not CONFIG.get('preview'):
        hostname=urlparse(BASE).hostname
        if hostname and not hostname.endswith('.github.io'): (OUT/'CNAME').write_text(hostname+'\n')
    print(f'Built {len(BUILT)} pages in {OUT}')
    if CONFIG.get('preview'): print('Preview mode: search indexing is disabled; custom domain is not configured.')

if __name__=='__main__': main()
