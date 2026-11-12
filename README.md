# Peresonal

A personal website with selected projects and a personal page for music, earlier writing, and press. Built for free hosting on GitHub Pages. 

## Preview locally

With Python 3.12 or newer installed, run these commands from the project folder:

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Open http://127.0.0.1:8000. After changing a file, rebuild and refresh the browser. Stop the server with Control-C.

## Publish the website

Repository: https://github.com/ammylin/ammylin.github.io

The repository’s **Settings → Pages → Build and deployment** uses **GitHub Actions**. Pushing to `main` builds, checks, and publishes the site at https://ammylin.com. Its custom domain is configured in the repository’s Pages settings.

The public address in `site.json` is `https://ammylin.com`, with `preview: false` to allow search indexing. Canonical links, social metadata, RSS, and the sitemap use that address. For a future staging copy, set `preview: true` to request that search engines not index it; that setting does not provide access control.

## Edit the website

- `site.json`: contact email, website address, description, and preview mode.
- `content/manifest.json`: post titles, dates, excerpts, images, reading times, and performance video details.
- `content/projects.json`: selected projects, tools, summaries, scope, team attribution, source repositories, and figure credits. Optional fields include `additional_links`, `report_label`, and `visual_labels` for projects without a figure. Set `featured` to `true` for homepage projects.
- `content/*.html`: the original page and post content, with WordPress layout code removed.
- `scripts/build.py`: shared header and footer, homepage, page layouts, and RSS/sitemap generation.
- `assets/style.css`: shared colors, typography, and original content styles.
- `assets/portfolio.css`: data science homepage, project cards and case studies, the consolidated personal page, and responsive layouts.
- `assets/main.js`: mobile menu and project category filters.
- `assets/images/`: local images, compressed as WebP. No images depend on WordPress staying online.

Performance videos use `popularity_rank` in `content/manifest.json`, taken from the YouTube channel’s **Popular** tab. The top three are featured, and the remaining recordings use the same order. `video_popularity_checked_on` records the date of that snapshot; refresh the ranks there when updating the selection.

To add a post, create `content/your-post-slug.html` and add its metadata to the `posts` array in `content/manifest.json`. Keep the newest post first. Rebuild and run the checks. You can also ask Codex to do this in plain English.

When editing copy, use Ammy’s original essays and About page as the voice reference. Keep her original writing intact unless she asks for edits. New copy should be conversational and specific, with varied sentence lengths and few em dashes. Avoid slogans, repeated sentence patterns, and invented feelings or personal takeaways. Keep project results, limitations, and team contributions accurate.

## Site structure

The main navigation is **Projects**, **About**, and **Music & more**, plus contact. Data science projects lead the homepage. `/projects/` has category filters and individual project summaries with links to the original work.

`/beyond/` gathers musical performances, teaching and lesson inquiries, the earlier writing archive, and press coverage in one page. Additional material expands with native browser disclosure controls. Earlier writing is presented as an archive rather than a currently updated feed. Individual post URLs remain available for new and old essays.

The former `/blog/`, `/media/`, `/lessons/`, `/press/`, and `/events-gigs/` pages now redirect to the appropriate section of `/beyond/`. GitHub Pages serves these as HTML refresh redirects with a visible fallback link and a canonical URL. The site does not depend on JavaScript for these redirects or disclosure controls.

The portfolio includes 14 projects and teaching examples selected from public repositories, including collaborative work with Ammy named as a coauthor. The homepage keeps three featured projects; the full index adds filters for NLP, mathematics, and teaching. Personal photos appear beside the homepage background and music sections. Descriptions distinguish collaborative work, classroom simulations, and synthetic datasets. Images on case-study pages link to their original repository figures. Update the project file when adding results or changing role descriptions; avoid presenting experimental results as production deployments.
