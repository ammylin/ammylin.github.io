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

## Publish the GitHub preview

Repository: https://github.com/ammylin/ammylin.github.io

In the repository’s **Settings → Pages → Build and deployment**, set the source to **GitHub Actions**. Pushing to `main` then builds, checks, and publishes the site at https://ammylin.github.io. The first workflow may need to be rerun after selecting this setting.

The initial version uses `preview: true` in `site.json`, which asks search engines not to index this staging copy. It has no custom domain configured. The public GitHub repository and preview are still accessible to anyone; preview mode is not access control.

## Edit the website

- `site.json`: contact email, website address, description, and preview mode.
- `content/manifest.json`: post titles, dates, excerpts, images, reading times, and performance video details.
- `content/projects.json`: selected projects, tools, summaries, scope, team attribution, source repositories, and figure credits. Set `featured` to `true` for homepage projects.
- `content/*.html`: the original page and post content, with WordPress layout code removed.
- `scripts/build.py`: shared header and footer, homepage, page layouts, and RSS/sitemap generation.
- `assets/style.css`: shared colors, typography, and original content styles.
- `assets/portfolio.css`: data science homepage, project cards and case studies, the consolidated personal page, and responsive layouts.
- `assets/main.js`: mobile menu and project category filters.
- `assets/images/`: local images, compressed as WebP. No images depend on WordPress staying online.

To add a post, create `content/your-post-slug.html` and add its metadata to the `posts` array in `content/manifest.json`. Keep the newest post first. Rebuild and run the checks. You can also ask Codex to do this in plain English.

## Site structure

The main navigation is **Projects**, **About**, and **Beyond data**, plus contact. Data science projects lead the homepage. `/projects/` has category filters and individual project summaries with links to the original work.

`/beyond/` gathers musical performances, teaching and lesson inquiries, the earlier writing archive, and press coverage in one page. Additional material expands with native browser disclosure controls. Earlier writing is presented as an archive rather than a currently updated feed. Individual post URLs remain available for new and old essays.

The former `/blog/`, `/media/`, `/lessons/`, `/press/`, and `/events-gigs/` pages now redirect to the appropriate section of `/beyond/`. GitHub Pages serves these as HTML refresh redirects with a visible fallback link and a canonical URL. The site does not depend on JavaScript for these redirects or disclosure controls.

The initial project selection uses public repositories, including four pinned projects. Descriptions distinguish collaborative work, classroom simulations, and synthetic datasets. Images on case-study pages link to their original repository figures. Update the project file when adding results or changing role descriptions; avoid presenting experimental results as production deployments.
