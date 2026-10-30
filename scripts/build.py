#!/usr/bin/env python3
"""Build 3togo's public, non-fork repository directory using public API data."""
import html
import json
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
OWNER = '3togo'

def fetch_repositories():
    # This public endpoint cannot enumerate private repositories. Paginate fully.
    result = subprocess.run(
        ['gh', 'api', '--paginate',
         f'users/{OWNER}/repos?type=owner&sort=updated&per_page=100',
         '--jq', '.[]'], check=True, capture_output=True, text=True)
    repos = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    return sorted((r for r in repos if not r['fork'] and not r['private']),
                  key=lambda r: r['updated_at'], reverse=True)

def esc(value):
    return html.escape(str(value or ''), quote=True)

def card(repo, featured=False):
    language = repo['language'] or 'Other'
    date = repo['updated_at'][:10]
    status = 'Archived' if repo['archived'] else 'Public'
    description = repo['description'] or 'Explore the source, files, and history on GitHub.'
    topics = ' '.join(repo.get('topics', []))
    return f'''<article class="repo{' featured-card' if featured else ''}" data-name="{esc(repo['name'])}" data-language="{esc(language)}" data-archived="{str(repo['archived']).lower()}" data-updated="{esc(repo['updated_at'])}" data-stars="{repo['stargazers_count']}" data-search="{esc(repo['name']+' '+description+' '+topics+' '+language)}">
      <div class="repo-top"><span class="repo-icon" aria-hidden="true">{'↗' if featured else '⌘'}</span><span class="badge">{status}</span></div>
      <h3><a href="{esc(repo['html_url'])}">{esc(repo['name'])}<span aria-hidden="true"> ↗</span></a></h3>
      <p>{esc(description)}</p>
      <div class="repo-bottom"><span><i class="language-dot" aria-hidden="true"></i>{esc(language)}</span><span>☆ {repo['stargazers_count']}</span></div>
      <div class="repo-date">Updated <time datetime="{date}">{date}</time></div>
    </article>'''

def build(repos):
    out = ROOT / '_site'
    out.mkdir(exist_ok=True)
    for file in (ROOT / 'static').iterdir():
        shutil.copy(file, out / file.name)
    featured_names = ['libwakeguard', 'wuming-player', 'relayforge', 'amule-weekly-builds']
    featured = [r for name in featured_names for r in repos if r['name'] == name]
    languages = sorted({r['language'] or 'Other' for r in repos})
    options = ''.join(f'<option value="{esc(l)}">{esc(l)}</option>' for l in languages)
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    page = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>3togo — Code, experiments &amp; open source</title>
<meta name="description" content="Explore 3togo’s public source repositories: desktop tools, media players, libraries, and experiments. Forks excluded.">
<meta name="color-scheme" content="light dark"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"><script src="app.js" defer></script></head>
<body><a class="skip" href="#repositories">Skip to repositories</a>
<header class="shell"><a class="wordmark" href="./" aria-label="3togo home"><span class="logo" aria-hidden="true">3</span>3togo<span class="wordmark-dot">.</span></a><nav aria-label="Main"><a href="#selected">Selected work</a><a href="#repositories">Repositories</a><a href="https://github.com/3togo">GitHub ↗</a></nav></header>
<main class="shell"><section class="hero" aria-labelledby="hero-title"><div class="eyebrow"><span class="status-dot"></span> THE PUBLIC COLLECTION</div><h1 id="hero-title">Code, experiments<br>&amp; <em>open source.</em></h1><div class="hero-bottom"><p>A home for my public repositories.<br>Desktop tools, media, libraries, and the occasional experiment.</p><a class="primary" href="#repositories">Explore the collection <span aria-hidden="true">↓</span></a></div>
<div class="stats"><div><strong>__COUNT__</strong><span>public repositories</span></div><div><strong>__LANGUAGES__</strong><span>languages</span></div><div class="stats-note"><span class="status-dot"></span><span>Source repositories only<br>Refreshed daily from GitHub</span></div></div></section>
<section id="selected" aria-labelledby="selected-title"><div class="section-heading"><div><span class="eyebrow">01 / IN FOCUS</span><h2 id="selected-title">Selected work</h2></div><p>A few places to start.</p></div><div class="featured-grid">__FEATURED__</div></section>
<section id="repositories" aria-labelledby="repositories-title"><div class="section-heading"><div><span class="eyebrow">02 / THE DIRECTORY</span><h2 id="repositories-title">All repositories<span class="count-pill">__COUNT__</span></h2></div><p>Public source repositories. Forks excluded.</p></div>
<div class="filters" id="filters" hidden><div class="search-wrap"><span aria-hidden="true">⌕</span><label class="sr-only" for="search">Search repositories</label><input id="search" type="search" placeholder="Search names, descriptions, topics…" autocomplete="off"></div><label class="sr-only" for="language">Language</label><select id="language"><option value="">All languages</option>__OPTIONS__</select><label class="sr-only" for="sort">Sort by</label><select id="sort"><option value="updated">Recently updated</option><option value="name">Name: A–Z</option><option value="stars">Most stars</option></select><label class="archive-filter"><input type="checkbox" id="active">Active only</label></div>
<p class="results" id="results" aria-live="polite">__COUNT__ repositories</p><div class="repo-grid" id="repo-grid">__CARDS__</div><div class="empty" id="empty" hidden><h3>No matching repositories</h3><p>Try another search or reset the filters.</p><button id="reset" type="button">Reset filters</button></div></section>
<section class="outro"><span class="eyebrow">KEEP EXPLORING</span><h2>The next idea starts<br>with a little curiosity.</h2><a href="https://github.com/3togo">Find me on GitHub <span aria-hidden="true">↗</span></a></section></main>
<footer class="shell"><span>3togo · Built in the open.</span><span>Directory refreshed __STAMP__</span><a href="https://github.com/3togo/3togo.github.io">Website source ↗</a></footer></body></html>'''
    replacements = {'__COUNT__': str(len(repos)), '__LANGUAGES__': str(len([l for l in languages if l != 'Other'])),
                    '__FEATURED__': ''.join(card(r, True) for r in featured), '__OPTIONS__': options,
                    '__CARDS__': ''.join(card(r) for r in repos), '__STAMP__': stamp}
    for key, value in replacements.items():
        page = page.replace(key, value)
    (out / 'index.html').write_text(page)
    # Only the rendered public fields are retained as a portable snapshot.
    public_fields = ['name', 'html_url', 'description', 'language', 'archived', 'stargazers_count', 'updated_at', 'topics']
    (out / 'repositories.json').write_text(json.dumps([{k: r.get(k) for k in public_fields} for r in repos], ensure_ascii=False, indent=2))
    (out / '.nojekyll').touch()
    print(f'Built {len(repos)} public non-fork repositories → {out}')

if __name__ == '__main__':
    build(fetch_repositories())
