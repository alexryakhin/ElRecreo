#!/usr/bin/env python3
"""Build the site's images, favicons and share image from the app's artwork.

Usage:
    python3 tools/make_assets.py SOURCE_DIR

SOURCE_DIR holds the original files, named as in the app's asset catalog:
    icon.png                         AppIcon.icon/Assets/*.png (transparent, 1080 px)
    hero.jpg                         the Obelisco photo from the retired Astro site
    LectureFMAnchorMate.jpg, ...     @3x images from Assets.xcassets/Images/<name>.imageset
    light-logo.svg, dark-logo.svg    Assets.xcassets/LaunchScreenLogo.imageset

Needs Pillow (python3 -m pip install pillow). Output goes to assets/img/ and favicons/.
"""
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
FAV = os.path.join(ROOT, "favicons")

# Icon background: the AppIcon.icon fill (teal gradient, top to bottom).
ICON_TOP = (44, 100, 101)
ICON_BOTTOM = (5, 78, 79)

# Photos used on the landing page: source name -> published name.
PHOTOS = {
    "LectureFMAnchorMate.jpg": "mate.jpg",
    "LectureAEAnchorAsado.jpg": "asado.jpg",
    "LectureFMAnchorKiosco.jpg": "kiosco.jpg",
    "LectureTZAnchorTaxi.jpg": "taxi.jpg",
}


def save_jpeg(im, path, quality=78):
    im.convert("RGB").save(path, "JPEG", quality=quality, optimize=True, progressive=True)


def gradient(size, top, bottom):
    w, h = size
    g = Image.new("RGB", (1, h))
    for y in range(h):
        t = min(1.0, y / (h * 0.7))
        g.putpixel((0, y), tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return g.resize((w, h))


def app_icon(src, size):
    """Square app icon: the mate artwork at 90 % on the teal gradient (as in AppIcon.icon)."""
    base = gradient((size, size), ICON_TOP, ICON_BOTTOM).convert("RGBA")
    art = Image.open(src).convert("RGBA")
    inner = round(size * 0.9)
    art = art.resize((inner, inner), Image.LANCZOS)
    off = (size - inner) // 2
    base.alpha_composite(art, (off, off))
    return base


def font(size, bold=True):
    path = "/System/Library/Fonts/Avenir Next.ttc"
    try:
        return ImageFont.truetype(path, size, index=0 if bold else 7)
    except OSError:
        return ImageFont.load_default()


def share_image(src_dir):
    """1200x630 Open Graph image: paper background, icon, headline, Obelisco photo card."""
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (247, 247, 241))
    d = ImageDraw.Draw(im)
    # sun-yellow glow behind the photo card
    d.rounded_rectangle((808, 78, 1168, 598), radius=44, fill=(255, 214, 8))
    photo = Image.open(os.path.join(src_dir, "hero.jpg")).convert("RGB")
    pw, ph = 380, 530
    scale = max(pw / photo.width, ph / photo.height)
    photo = photo.resize((round(photo.width * scale), round(photo.height * scale)), Image.LANCZOS)
    left, top = (photo.width - pw) // 2, (photo.height - ph) // 2
    photo = photo.crop((left, top, left + pw, top + ph))
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw, ph), radius=40, fill=255)
    im.paste(photo, (770, 40), mask)

    icon = app_icon(os.path.join(src_dir, "icon.png"), 120)
    imask = Image.new("L", (120, 120), 0)
    ImageDraw.Draw(imask).rounded_rectangle((0, 0, 120, 120), radius=28, fill=255)
    im.paste(icon.convert("RGB"), (72, 72), imask)

    teal, ink, brown = (0, 102, 102), (44, 46, 44), (142, 73, 0)
    d.text((72, 228), "El Recreo", font=font(84), fill=teal)
    d.text((72, 336), "Spanish the way", font=font(46), fill=ink)
    d.text((72, 392), "Buenos Aires speaks it.", font=font(46), fill=ink)
    d.text((72, 478), "15-minute lessons · vos · porteño life", font=font(28, bold=False), fill=brown)
    d.text((72, 528), "Coming soon to iPhone, iPad and Mac", font=font(28, bold=False), fill=ink)
    save_jpeg(im, os.path.join(IMG, "og.jpg"), quality=84)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = os.path.abspath(sys.argv[1])
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(FAV, exist_ok=True)

    hero = Image.open(os.path.join(src, "hero.jpg"))
    hero.thumbnail((1600, 1600))
    save_jpeg(hero, os.path.join(IMG, "hero-obelisco.jpg"), quality=80)

    for name, out in PHOTOS.items():
        im = Image.open(os.path.join(src, name))
        im.thumbnail((1600, 1600))
        save_jpeg(im, os.path.join(IMG, out))

    icon_src = os.path.join(src, "icon.png")
    app_icon(icon_src, 192).save(os.path.join(IMG, "app-icon.png"), optimize=True)
    for size, name in [(16, "favicon-16x16.png"), (32, "favicon-32x32.png"),
                       (96, "favicon-96x96.png"), (180, "apple-touch-icon.png"),
                       (192, "android-chrome-192x192.png"), (512, "android-chrome-512x512.png")]:
        app_icon(icon_src, size).convert("RGB").save(os.path.join(FAV, name), optimize=True)
    app_icon(icon_src, 48).convert("RGB").save(
        os.path.join(FAV, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

    for name, out in (("light-logo.svg", "wordmark-light.svg"), ("dark-logo.svg", "wordmark-dark.svg")):
        shutil.copyfile(os.path.join(src, name), os.path.join(IMG, out))

    share_image(src)
    print("done")


if __name__ == "__main__":
    main()
