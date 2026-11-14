#!/usr/bin/env python3
"""Generate every page of the El Recreo website in all site languages.

Strings live in i18n/<lang>.json (English, i18n/en.json, is the source; every language has the same
keys), the page bodies in src/<page>.html with {{key}} slots, and the legal page bodies in
i18n/legal/<lang>/<page>.html. Edit those, never the generated HTML.

    python3 tools/build_pages.py

Writes index.html, support.html, privacy.html and terms.html for English at the site root, the same
four pages under /<folder>/ for every other language, and sitemap.xml.

Slots in src/*.html:
    {{key}}        the string, as HTML (strings may contain <span lang="es">…</span> and links)
    {{key|arg}}    the string with %s replaced by arg (e.g. a song title in an aria-label)
    {{>name}}      a shared snippet from SNIPPETS (icons repeated across the page)
Strings that end up inside an attribute must not contain double quotes or markup.
"""
import html
import json
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
I18N = SITE / "i18n"
SRC = SITE / "src"
ORIGIN = "https://alexriakhin.com/ElRecreo/"
APP_STORE = "https://apps.apple.com/app/id6761676545"
GOOGLE_PLAY = "https://play.google.com/store/apps/details?id=com.dor.elrecreo"

# code (json name), html lang / hreflang, folder, og:locale, name in its own language
LANGS = [
    ("en", "en", "", "en_US", "English"),
    ("ru", "ru", "ru/", "ru_RU", "Русский"),
    ("pt-br", "pt-BR", "pt-br/", "pt_BR", "Português (Brasil)"),
    ("fr", "fr", "fr/", "fr_FR", "Français"),
    ("de", "de", "de/", "de_DE", "Deutsch"),
]
# Plus Jakarta Sans and Be Vietnam Pro have no Cyrillic; Russian pages use Manrope (site.css, :lang(ru)).
CYRILLIC_FONT = ('  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800'
                 '&subset=cyrillic&display=swap" rel="stylesheet">\n')
PAGES = {"index": "", "support": "support.html", "privacy": "privacy.html", "terms": "terms.html"}

SAY = ('<svg class="say-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9.5h3.2L12 5.5v13l-4.8-4H4z"/>'
       '<path class="wave wave-1" d="M15.5 9.2a4 4 0 0 1 0 5.6"/><path class="wave wave-2" d="M18.3 6.6a7.6 7.6 0 0 1 0 10.8"/></svg>')
SNIPPETS = {
    "say": SAY,
    "app_store": APP_STORE,
    "google_play": GOOGLE_PLAY,
    "apple_music": '<img src="assets/img/services/apple-music.svg" alt="" width="20" height="20">',
    "spotify": '<img src="assets/img/services/spotify.svg" alt="" width="20" height="20">',
}


def page_url(folder, page):
    return f"{ORIGIN}{folder}{PAGES[page]}"


def fill(template, t, where):
    def slot(m):
        name = m.group(1)
        if name.startswith(">"):
            return SNIPPETS[name[1:]]
        key, _, arg = name.partition("|")
        if key not in t:
            sys.exit(f"{where}: no string for {{{{{key}}}}}")
        value = t[key].replace("%s", arg) if arg else t[key]
        in_attribute = m.string[:m.start()].endswith('="')
        return attr(value) if in_attribute else value
    return re.sub(r"\{\{([^{}]+?)\}\}", slot, template)


def attr(text):
    return html.escape(text, quote=True)


def head(lang, page, t, extra=""):
    code, hl, folder, locale, _ = lang
    title, description = t[f"{page}_title"], t[f"{page}_description"]
    og_title = t.get(f"{page}_og_title", title)
    og_description = t.get(f"{page}_og_description", description)
    alternates = "\n".join(f'  <link rel="alternate" hreflang="{l[1]}" href="{page_url(l[2], page)}">' for l in LANGS)
    other_locales = "\n".join(f'  <meta property="og:locale:alternate" content="{l[3]}">' for l in LANGS if l[0] != code)
    return f"""<!doctype html>
<html lang="{hl}" dir="ltr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{attr(title)}</title>
  <meta name="description" content="{attr(description)}">
  <meta name="theme-color" content="#F7F7F1" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#141715" media="(prefers-color-scheme: dark)">
  <meta name="color-scheme" content="light dark">
  <link rel="canonical" href="{page_url(folder, page)}">
{alternates}
  <link rel="alternate" hreflang="x-default" href="{page_url('', page)}">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="El Recreo">
  <meta property="og:title" content="{attr(og_title)}">
  <meta property="og:description" content="{attr(og_description)}">
  <meta property="og:url" content="{page_url(folder, page)}">
  <meta property="og:image" content="{ORIGIN}assets/img/og.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{attr(t['og_image_alt'])}">
  <meta property="og:locale" content="{locale}">
{other_locales}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{attr(og_title)}">
  <meta name="twitter:description" content="{attr(og_description)}">
  <meta name="twitter:image" content="{ORIGIN}assets/img/og.jpg">

  <link rel="icon" href="favicons/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="96x96" href="favicons/favicon-96x96.png">
  <link rel="icon" type="image/png" sizes="32x32" href="favicons/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="favicons/favicon-16x16.png">
  <link rel="apple-touch-icon" href="favicons/apple-touch-icon.png">
  <link rel="manifest" href="favicons/site.webmanifest">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
{CYRILLIC_FONT if code == "ru" else ""}  <link rel="stylesheet" href="assets/css/site.css">
  <meta name="apple-itunes-app" content="app-id=6761676545">
{extra}</head>
"""


def picker(lang, page, t):
    current = ' aria-current="true"'

    def href(other):
        return ("../" if lang[2] else "") + other[2] + PAGES[page] or "./"
    items = "\n".join(
        f'          <li><a href="{href(l)}" hreflang="{l[1]}" lang="{l[1]}"'
        f'{current if l[0] == lang[0] else ""}>{l[4]}</a></li>' for l in LANGS)
    globe = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
             '<path d="M3 12h18M12 3c2.5 2.7 3.7 5.7 3.7 9s-1.2 6.3-3.7 9c-2.5-2.7-3.7-5.7-3.7-9S9.5 5.7 12 3z"/></svg>')
    return f"""      <details class="lang">
        <summary aria-label="{attr(t['language'])}: {lang[4]}">{globe}<span class="lang-code">{lang[1].split('-')[0].upper()}</span></summary>
        <ul>
{items}
        </ul>
      </details>"""


def header(lang, page, t):
    on_home = page == "index"
    to = "" if on_home else "./"
    story = f'\n        <a href="#cast">{t["nav_story"]}</a>' if on_home else ""
    return f"""<body{'' if on_home else ' class="page"'}>
  <a class="skip" href="#main">{t['skip']}</a>

  <header class="bar">
    <div class="bar-inner">
      <a class="brand" href="./" aria-label="{attr(t['home_label'])}">
        <img src="assets/img/app-icon.png" alt="" width="40" height="40">
        <span>El Recreo</span>
      </a>
      <nav class="bar-nav" aria-label="{attr(t['nav_label'])}">
        <a href="{to}#how">{t['nav_how']}</a>{story}
        <a href="{to}#rioplatense">{t['nav_rio']}</a>
        <a href="{to}#path">{t['nav_levels']}</a>
        <a href="{to}#privacy">{t['nav_privacy']}</a>
      </nav>
{picker(lang, page, t)}
      <a class="bar-soon" href="{to}#download">{t['nav_download']}</a>
    </div>
  </header>
"""


def footer(page, t):
    def link(target, label):
        current = ' aria-current="page"' if target == page else ""
        return f'<a href="{PAGES[target]}"{current}>{label}</a>'
    return f"""
  <footer class="foot">
    <div class="wrap foot-grid">
      <div class="foot-brand">
        <a href="./" aria-label="{attr(t['home_label'])}">
          <picture>
            <source srcset="assets/img/wordmark-dark.svg" media="(prefers-color-scheme: dark)">
            <img src="assets/img/wordmark-light.svg" alt="El Recreo · Rioplatense" width="176" height="60" loading="lazy">
          </picture>
        </a>
        <p>{t['foot_about']}</p>
      </div>
      <nav class="foot-links" aria-label="{attr(t['foot_label'])}">
        {link('support', t['foot_support'])}
        {link('privacy', t['foot_privacy'])}
        {link('terms', t['foot_terms'])}
        <a href="mailto:support@alexriakhin.com">support@alexriakhin.com</a>
      </nav>
    </div>
    <div class="wrap foot-fine">
      <p>© <span data-year>2026</span> Aleksandr Riakhin. {t['foot_trademarks']}</p>
    </div>
  </footer>
  <script src="assets/js/site.js" defer></script>
</body>
</html>
"""


def home_extra(lang, t):
    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "El Recreo",
          "operatingSystem": "iOS, iPadOS, macOS, Android", "applicationCategory": "EducationalApplication",
          "inLanguage": lang[1], "description": t["ld_description"], "url": page_url(lang[2], "index"),
          "downloadUrl": [APP_STORE, GOOGLE_PLAY]}
    return f"""  <link rel="preload" as="image" href="assets/img/hero-obelisco.jpg">
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
"""


def relocate(page_html, lang):
    """Pages under /<lang>/ reach the shared files one folder up."""
    if not lang[2]:
        return page_html
    return re.sub(r'((?:href|src|srcset)=")(assets/|favicons/)', r"\1../\2", page_html)


def build(lang, page, t):
    if page in ("index", "support"):
        body = fill((SRC / f"{page}.html").read_text(), t, f"{lang[0]}/{page}")
    else:
        body = (I18N / "legal" / lang[0] / f"{page}.html").read_text().rstrip("\n")
        if lang[0] != "en":  # the translation is a courtesy; say which text counts
            body = body.replace("</p>\n    </div>", f"</p>\n      <p class=\"meta legal-note\">{t['legal_note']}</p>\n    </div>", 1)
        body = f'  <main id="main">\n{body}\n  </main>\n'
    extra = home_extra(lang, t) if page == "index" else ""
    return relocate(head(lang, page, t, extra) + header(lang, page, t) + "\n" + body + footer(page, t), lang)


def main():
    english = json.loads((I18N / "en.json").read_text())
    for lang in LANGS:
        own = json.loads((I18N / f"{lang[0]}.json").read_text())
        missing, extra = set(english) - set(own), set(own) - set(english)
        if missing or extra:
            sys.exit(f"{lang[0]}.json: missing {sorted(missing)}, unknown {sorted(extra)}")
        folder = SITE / lang[2]
        folder.mkdir(exist_ok=True)
        for page, path in PAGES.items():
            (folder / (path or "index.html")).write_text(build(lang, page, own))
    urls = [page_url(l[2], p) for l in LANGS for p in PAGES]
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    print(f"{len(LANGS)} languages × {len(PAGES)} pages, sitemap with {len(urls)} URLs")


if __name__ == "__main__":
    main()
