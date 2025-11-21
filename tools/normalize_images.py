"""
Batch-normalize day background images to a consistent resolution.
Creates an output folder `normalized_backgrounds` in the project root and writes images there.

Behavior:
- Target resolution defaults to 1920x1080 (can be changed via CLI args).
- For each `* day.png` image: create a blurred cover (cover-resize to target), then paste a fit-resized copy of the original centered on top.
- Does not overwrite originals.

Usage:
    python tools\normalize_images.py [--width 1920] [--height 1080]

"""
from PIL import Image, ImageFilter
import glob, os, argparse

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PATTERN = os.path.join(ROOT, '* day.png')

parser = argparse.ArgumentParser()
parser.add_argument('--width', type=int, default=1920)
parser.add_argument('--height', type=int, default=1080)
parser.add_argument('--out', type=str, default=os.path.join(ROOT, 'normalized_backgrounds'))
args = parser.parse_args()

os.makedirs(args.out, exist_ok=True)

for p in sorted(glob.glob(PATTERN)):
    name = os.path.basename(p)
    try:
        img = Image.open(p).convert('RGBA')
        orig_w, orig_h = img.size
        target_w, target_h = args.width, args.height

        # Cover resized (fill target) for blurred background
        cover = img.resize((target_w, target_h), Image.Resampling.LANCZOS).convert('RGB')
        cover = cover.filter(ImageFilter.GaussianBlur(radius=18))

        # Fit-resize original so whole image is visible
        fit_scale = min(target_w / orig_w, target_h / orig_h)
        new_w = max(1, int(orig_w * fit_scale))
        new_h = max(1, int(orig_h * fit_scale))
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS).convert('RGB')

        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        cover.paste(img_resized, (offset_x, offset_y))

        out_path = os.path.join(args.out, name)
        cover.save(out_path)
        print('Saved', out_path)
    except Exception as e:
        print('Error processing', p, e)
print('Done.')
