import base64
import os
import re
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip install pillow")

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(ROOT, "images")
RAW_DIR = os.path.join(ROOT, "raw_images")
TARGET_W, TARGET_H = 640, 480
QUALITY = 72

CSS_START = "/*__CSS_START__*/"
CSS_END = "/*__CSS_END__*/"
JS_START = "/*__JS_START__*/"
JS_END = "/*__JS_END__*/"

V_BIAS = {
    "13-frappe.jpg": 0.55,
    "15-irish-coffee.jpg": 0.58,
    "16-turkish-coffee.jpg": 0.75,
    "17-vietnamese-coffee.jpg": 0.62,
    "22-coconut-cold-brew.jpg": 0.62,
    "14-affogato.jpg": 0.55,
}

try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_LANCZOS = 1

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png")


def _fail(message):
    sys.exit(f"error: {message}")


def _open_rgb(path):
    try:
        img = Image.open(path)
    except OSError as exc:
        _fail(f"cannot read image {path}: {exc}")
    return img.convert("RGB")


def _crop_to_target(img, bias):
    w, h = img.size
    target_ratio = TARGET_W / TARGET_H
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    new_h = int(w / target_ratio)
    top = int((h - new_h) * bias)
    return img.crop((0, top, w, top + new_h))


def compress_images():
    src_dir = RAW_DIR if os.path.isdir(RAW_DIR) else IMG_DIR
    os.makedirs(IMG_DIR, exist_ok=True)
    names = sorted(
        n for n in os.listdir(src_dir) if n.lower().endswith(IMAGE_SUFFIXES)
    )
    if not names:
        print("  (no source images found, nothing to do)")
        return
    skipped = 0
    for name in names:
        src = os.path.join(src_dir, name)
        base = os.path.splitext(name)[0] + ".jpg"
        dst = os.path.join(IMG_DIR, base)
        if os.path.abspath(src) == os.path.abspath(dst):
            skipped += 1
            continue
        img = _open_rgb(src)
        bias = V_BIAS.get(base, 0.5)
        img = _crop_to_target(img, bias)
        img = img.resize((TARGET_W, TARGET_H), RESAMPLE_LANCZOS)
        img.save(dst, "JPEG", quality=QUALITY, optimize=True)
        print(f"  compressed {name} -> {base} ({os.path.getsize(dst)//1024} KB)")
    if skipped:
        print(f"  skipped {skipped} already-compressed image(s)")


def extract(markup, start, end, out_path=None):
    pattern = re.escape(start) + r"(.*?)" + re.escape(end)
    m = re.search(pattern, markup, re.DOTALL)
    if not m:
        _fail(f"markers not found: {start} .. {end}")
    body = m.group(1).strip("\n")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(body + "\n")
        print(f"  wrote {os.path.basename(out_path)} ({len(body)//1024} KB)")
    return body


def strip_markers(markup):
    for mk in (CSS_START, CSS_END, JS_START, JS_END):
        markup = markup.replace(mk, "")
    return markup


def externalize_blocks(markup):
    css_pattern = (
        r"<style\b[^>]*>\s*" + re.escape(CSS_START) + r".*?</style>"
    )
    link_tag = '<link rel="stylesheet" href="style.css">'
    markup, n = re.subn(css_pattern, link_tag, markup, count=1, flags=re.DOTALL)
    if not n:
        _fail("could not find the <style> block containing the CSS markers")
    js_pattern = (
        r"<script\b[^>]*>\s*" + re.escape(JS_START) + r".*?</script>"
    )
    script_tag = '<script src="script.js"></script>'
    markup, n = re.subn(
        js_pattern, script_tag, markup, count=1, flags=re.DOTALL
    )
    if not n:
        _fail("could not find the <script> block containing the JS markers")
    return markup


def main():
    print("Compressing images ...")
    compress_images()

    tpl_path = os.path.join(ROOT, "template.html")
    if not os.path.isfile(tpl_path):
        _fail(f"missing template file: {tpl_path}")
    with open(tpl_path, encoding="utf-8") as f:
        tpl = f.read()

    print("Extracting CSS / JS ...")
    extract(tpl, CSS_START, CSS_END, os.path.join(ROOT, "style.css"))
    extract(tpl, JS_START, JS_END, os.path.join(ROOT, "script.js"))

    split = strip_markers(externalize_blocks(tpl))
    with open(os.path.join(ROOT, "index-split.html"), "w", encoding="utf-8") as f:
        f.write(split)
    print("  wrote index-split.html")

    inline = strip_markers(tpl)
    names = sorted(
        n for n in os.listdir(IMG_DIR) if n.lower().endswith(".jpg")
    )
    for name in names:
        with open(os.path.join(IMG_DIR, name), "rb") as f:
            raw = f.read()
        uri = "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii")
        ref = "images/" + name
        if ref not in inline:
            print(f"  warn: template does not reference {ref}")
        inline = inline.replace(ref, uri)
    out_path = os.path.join(ROOT, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(inline)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"  wrote index.html ({size_kb} KB, self-contained)")
    print("Done.")


if __name__ == "__main__":
    main()
