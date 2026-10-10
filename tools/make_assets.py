#!/usr/bin/env python3
"""Build the site's photos and wordmarks from the app's artwork (icon and favicons: tools/sync_from_app.py).

Usage:
    python3 tools/make_assets.py SOURCE_DIR

SOURCE_DIR holds the original files, named as in the app's asset catalog:
    hero.jpg                         the Obelisco photo from the retired Astro site
    LectureFMAnchorMate.jpg, ...     @3x images from Assets.xcassets/Images/<name>.imageset
    light-logo.svg, dark-logo.svg    Assets.xcassets/LaunchScreenLogo.imageset

Needs Pillow (python3 -m pip install pillow). Output goes to assets/img/ and favicons/.
"""
import os
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
FAV = os.path.join(ROOT, "favicons")

# Photos used on the landing page: source name -> published name.
PHOTOS = {
    "LectureFMAnchorMate.jpg": "mate.jpg",
    "LectureAEAnchorAsado.jpg": "asado.jpg",
    "LectureFMAnchorKiosco.jpg": "kiosco.jpg",
    "LectureTZAnchorTaxi.jpg": "taxi.jpg",
}


def save_jpeg(im, path, quality=78):
    im.convert("RGB").save(path, "JPEG", quality=quality, optimize=True, progressive=True)


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

    for name, out in (("light-logo.svg", "wordmark-light.svg"), ("dark-logo.svg", "wordmark-dark.svg")):
        shutil.copyfile(os.path.join(src, name), os.path.join(IMG, out))

    # The icon, favicons and share image now come from tools/sync_from_app.py (current AppIcon.icon).
    print("done")


if __name__ == "__main__":
    main()
