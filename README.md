# El Recreo — website

Marketing site for El Recreo, the app for learning Rioplatense (Buenos Aires) Spanish in 15-minute
lessons on iPhone, iPad and Mac. The app isn't released yet: the site announces it ("Coming soon")
and nothing is sold here. Static HTML served by GitHub Pages, planned at
https://alexriakhin.com/ElRecreo/. This repository is the `ElRecreoWebsite` submodule of the app
repository.

No build step, no framework, no npm, no analytics and no cookies: edit the HTML and push.

## Files

| Path | What |
|---|---|
| `index.html` | Landing page: hero (playable speech bubbles), a try-it step, the story and cast with voice samples, the Sofi vs. Rubén scene, why Rioplatense, banda sonora, A1–C1 path, privacy promises |
| `support.html` | FAQ and contact (`<details>` accordions, no JavaScript) |
| `privacy.html`, `terms.html` | Legal pages — keep these paths stable, the App Store listing will link to them |
| `404.html` | Not-found page; self-contained (inline CSS, inline icon, absolute links) because GitHub Pages serves it at any depth |
| `assets/css/site.css` | All styles. Tokens from the app's design system ("The Social Estancia"): paper surfaces, teal `#006666`, orange `#8E4900`, sun yellow `#FFD608`; Plus Jakarta Sans + Be Vietnam Pro from Google Fonts; light and dark (`prefers-color-scheme`) |
| `assets/js/site.js` | Header shadow on scroll, reveal-on-scroll (off with reduced motion), footer year, and the voice samples (one line at a time), the try-it step and the scene. The page reads fine without it |
| `assets/img/` | Hero photo, culture photos, app icon, wordmarks, `og.jpg` share image (1200×630), `cast/` portraits |
| `assets/audio/` | Voice samples copied from the app's recorded lines, plus the right/wrong sounds |
| `favicons/` | `favicon.ico`, PNG favicons, `apple-touch-icon.png`, Android icons, `site.webmanifest` |
| `tools/sync_from_app.py` | Icon, favicons, share image, cast portraits and voice samples, straight from the app repo |
| `tools/render_icon.swift` | Flat render of the app's `AppIcon.icon` layers (used by `sync_from_app.py`) |
| `tools/make_assets.py` | Photos and wordmarks from the app's artwork (needs Pillow) |
| `robots.txt`, `sitemap.xml` | For search engines |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are |

The header and footer are repeated in each page; when you change one, change it everywhere
(`grep -l 'class="bar"' *.html`).

## Preview

```bash
python3 -m http.server 8765        # then open http://localhost:8765
```

## Images

`tools/make_assets.py` takes a folder with the original artwork, named as in the app's asset catalog
(`@3x` images from `Assets.xcassets/Images/<name>.imageset`
renamed to `<name>.jpg`, `light-logo.svg`/`dark-logo.svg` from `LaunchScreenLogo.imageset`, and
`hero.jpg`, the Obelisco photo from the retired Astro site's `public/images/hero-buenos-aires.jpg`):

```bash
python3 tools/make_assets.py ~/path/to/artwork
```

It writes the compressed photos and copies the wordmarks.

## Icon, cast and voices

Everything that mirrors the app comes from `tools/sync_from_app.py`, run from the app repo (this site is
its `ElRecreoWebsite` submodule). It renders the icon from `ElRecreo/Resources/AppIcon.icon`, rebuilds the
favicons and `og.jpg`, copies the cast portraits, and copies the voice samples listed in `LINES` from
`Audio/Clips` (looked up by speaker and exact text in `Audio/manifest.json`):

```bash
python3 ElRecreoWebsite/tools/sync_from_app.py
```

To change a sample, edit `LINES` and the matching text in `index.html`, then run it again.
Keep the whole site small (about 2.5 MB with the voices).

## Deploy (GitHub Pages)

1. Create the GitHub repository (e.g. `alexryakhin/ElRecreo`, which gives
   `https://alexriakhin.com/ElRecreo/` through the account's custom domain) and push `main`.
2. Repository **Settings → Pages → Build and deployment**: *Deploy from a branch*, `main`, `/ (root)`.
3. Pushing to `main` deploys.

**Base URL.** Canonical, Open Graph, sitemap, robots and 404 links use
`https://alexriakhin.com/ElRecreo/`. If the site ends up elsewhere, replace it everywhere:

```bash
grep -rl 'https://alexriakhin.com/ElRecreo/' --include='*.html' --include='*.xml' --include='*.txt' . \
  | xargs sed -i '' 's#https://alexriakhin.com/ElRecreo/#https://NEW-URL/#g'
```

**Custom domain.** There is no `CNAME` yet. To use one (say `elrecreo.app`): add a `CNAME` file
containing just the domain, point the domain's DNS at GitHub Pages (`A`/`ALIAS` records for the
apex or a `CNAME` record to `alexryakhin.github.io` for a subdomain), set it under Settings → Pages,
enable *Enforce HTTPS*, and update the base URL as above.

## As a submodule of the app repository

From the app repository root, once this repo has a GitHub remote:

```bash
git submodule add https://github.com/alexryakhin/ElRecreo.git ElRecreoWebsite
git commit -m "Add website submodule"
```

Afterwards: commit and push here first, then commit the updated submodule pointer in the app repo
(`git add ElRecreoWebsite && git commit`).

## When the app launches

- In `index.html`, replace the "Coming soon" badge in the hero with the App Store badge — the
  commented `APP STORE LINK` block marks the spot — and update the "Coming soon" pill in each page's
  header and the closing section.
- Add `"downloadUrl"` and `"offers"` to the JSON-LD in `index.html`, and an
  `<meta name="apple-itunes-app" content="app-id=…">` tag.
- Update the launch and pricing answers in `support.html`.

## Languages

English only for now, at the site root. To add a language, copy the pages into `/<lang>/`
(e.g. `/es/index.html`), prefix asset paths with `../`, set `<html lang>`, and add
`<link rel="alternate" hreflang="…">` tags for every language on every page (English keeps
`x-default`) plus the new URLs in `sitemap.xml`. Translated privacy and terms pages should note that
the English version applies.

## Facts on the page

The site makes no claims about users, ratings or reviews — there are none yet. The privacy page
describes the app as specified for launch: no account, no third-party analytics or ads, progress on
device + the user's iCloud (CloudKit private database), optional microphone/speech recognition for
speaking exercises, on-device text-to-speech. Re-check it against the shipping app before release,
and update "Last updated" when it changes.
