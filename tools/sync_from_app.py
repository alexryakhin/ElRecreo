#!/usr/bin/env python3
"""Refresh the site's icon, favicons, share image, cast portraits and voice samples from the app repo.

Usage (from the app repo, where this site is the ElRecreoWebsite submodule):
    python3 ElRecreoWebsite/tools/sync_from_app.py

Reads ../ElRecreo/Resources (icon layers, cast portraits, sounds) and ../Audio (recorded lines).
Needs Pillow (python3 -m pip install pillow) and Xcode's `swift` for the icon render.
Photos and wordmarks still come from tools/make_assets.py.
"""
import json
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.dirname(SITE)
RES = os.path.join(APP, "ElRecreo", "Resources")
IMG = os.path.join(SITE, "assets", "img")
FAV = os.path.join(SITE, "favicons")
AUDIO = os.path.join(SITE, "assets", "audio")

# AppIcon.icon: fill gradient (icon.json) and layers, bottom first.
ICON_TOP, ICON_BOTTOM = "12827E", "004D4C"
ICON_LAYERS = ["sun", "gourd", "virola", "bombilla"]

CAST = ["sofi", "ruben", "marta", "lucho", "caro"]  # Mili has no portrait yet: the page shows her initial

# Lines played on the site: published name -> (speaker role, exact text in Audio/manifest.json).
LINES = {
    "sofi-hola": ("sofi", "¡Hola! Soy Sofi, del cuarto be. ¿Cómo te llamás?"),
    "sofi-llamas": ("sofi", "¡Hola! ¿Cómo te llamás?"),
    "ruben-hola": ("ruben", "¡Buenas tardes! Soy Rubén, el encargado. ¿Cómo te llamás?"),
    "ruben-andas": ("ruben", "¿Qué tal? ¿Cómo andás?"),
    "marta-familia": ("marta", "Tomá, es de dulce de leche. ¡Ya sos de la familia!"),
    "lucho-cancha": ("lucho", "¡Genial! En la cancha aprendés todo… ¡las malas palabras también!"),
    "lucho-donde": ("lucho", "Che, ¿y vos de dónde sos?"),
    "lucho-hermanos": ("lucho", "Y vos, ¿tenés hermanos?"),
    "caro-laburo": ("caro", "¡Primer día de laburo! ¿Querés un café?"),
    "scene-1": ("ruben", "Sofi, son las cuatro de la tarde. ¿Te levantás ahora?"),
    "scene-2": ("sofi", "¡No, Rubén! Me levanto a la una. Desayuno, me ducho… ¡y ahora, la merienda!"),
    "scene-3": ("ruben", "¡A la una! Yo me levanto a las cinco y barro la vereda todos los días."),
    "scene-4": ("sofi", "Y yo dibujo hasta las tres de la mañana. ¡Laburo a la noche!"),
    "scene-5": ("mili", "¿Y quién tiene razón?"),
    "scene-sofi": ("sofi", "¡Muy bien! ¡Ya sos de acá!"),
    "scene-ruben": ("sofi", "¡Ay, sos igual que Rubén!"),
    "word-che": ("narrator", "Che"),
    "word-laburo": ("narrator", "laburo"),
    "word-bondi": ("narrator", "bondi"),
    "word-re": ("narrator", "re"),
    "word-dale": ("narrator", "¡Dale!"),
}
SOUNDS = ["correct", "incorrect"]


def render_icon(size, rounded):
    out = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
    layers = [os.path.join(RES, "AppIcon.icon", "Assets", f"{name}.svg") for name in ICON_LAYERS]
    subprocess.run(["swift", os.path.join(SITE, "tools", "render_icon.swift"), out, str(size), ICON_TOP, ICON_BOTTOM,
                    "rounded" if rounded else "square", *layers], check=True)
    return Image.open(out).convert("RGBA")


def icons():
    square, rounded = render_icon(1024, False), render_icon(1024, True)
    # The page rounds the icon itself (CSS); favicons use the rounded render.
    square.resize((192, 192), Image.LANCZOS).save(os.path.join(IMG, "app-icon.png"), optimize=True)
    for size, name in [(16, "favicon-16x16.png"), (32, "favicon-32x32.png"), (96, "favicon-96x96.png")]:
        rounded.resize((size, size), Image.LANCZOS).save(os.path.join(FAV, name), optimize=True)
    rounded.resize((48, 48), Image.LANCZOS).save(os.path.join(FAV, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    # Home-screen icons are masked by the system, so they stay square and opaque.
    for size, name in [(180, "apple-touch-icon.png"), (192, "android-chrome-192x192.png"), (512, "android-chrome-512x512.png")]:
        square.resize((size, size), Image.LANCZOS).convert("RGB").save(os.path.join(FAV, name), optimize=True)
    return rounded


def font(size, bold=True):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", size, index=0 if bold else 7)
    except OSError:
        return ImageFont.load_default()


def share_image(icon):
    """1200x630 Open Graph image: paper background, icon, headline, Obelisco photo card."""
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (247, 247, 241))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((808, 78, 1168, 598), radius=44, fill=(255, 214, 8))
    photo = Image.open(os.path.join(IMG, "hero-obelisco.jpg")).convert("RGB")
    pw, ph = 380, 530
    scale = max(pw / photo.width, ph / photo.height)
    photo = photo.resize((round(photo.width * scale), round(photo.height * scale)), Image.LANCZOS)
    left, top = (photo.width - pw) // 2, (photo.height - ph) // 2
    photo = photo.crop((left, top, left + pw, top + ph))
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw, ph), radius=40, fill=255)
    im.paste(photo, (770, 40), mask)
    small = icon.resize((120, 120), Image.LANCZOS)
    im.paste(small, (72, 72), small)
    teal, ink, brown = (0, 102, 102), (44, 46, 44), (142, 73, 0)
    d.text((72, 228), "El Recreo", font=font(84), fill=teal)
    d.text((72, 336), "Spanish the way", font=font(46), fill=ink)
    d.text((72, 392), "Buenos Aires speaks it.", font=font(46), fill=ink)
    d.text((72, 478), "15-minute lessons · vos · porteño life", font=font(28, bold=False), fill=brown)
    d.text((72, 528), "Coming soon to iPhone, iPad and Mac", font=font(28, bold=False), fill=ink)
    im.save(os.path.join(IMG, "og.jpg"), "JPEG", quality=84, optimize=True, progressive=True)


def cast():
    folder = os.path.join(IMG, "cast")
    os.makedirs(folder, exist_ok=True)
    for name in CAST:
        src = os.path.join(RES, "Assets.xcassets", "Cast", f"avatar-{name}.imageset", f"avatar-{name}.png")
        im = Image.open(src).convert("RGBA")
        im.thumbnail((256, 256), Image.LANCZOS)
        im.save(os.path.join(folder, f"{name}.png"), optimize=True)


def audio():
    os.makedirs(AUDIO, exist_ok=True)
    manifest = json.load(open(os.path.join(APP, "Audio", "manifest.json")))
    by_line = {(c["role"], c["text"]): c["id"] for c in manifest["clips"]}
    for name, line in LINES.items():
        clip = by_line.get(line)
        if not clip:
            raise SystemExit(f"No recorded clip for {line}")
        shutil.copyfile(os.path.join(APP, "Audio", "Clips", f"{clip}.m4a"), os.path.join(AUDIO, f"{name}.m4a"))
    for name in SOUNDS:
        shutil.copyfile(os.path.join(RES, "Sounds", f"{name}.m4a"), os.path.join(AUDIO, f"{name}.m4a"))


def main():
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(FAV, exist_ok=True)
    share_image(icons())
    cast()
    audio()
    print("done")


if __name__ == "__main__":
    main()
