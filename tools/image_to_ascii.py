"""Utility tool to convert any image to ASCII art for update_profile.py.

Usage:
    python3 tools/image_to_ascii.py [path_to_image] [--width 40] [--height 27] [--apply]
"""

import argparse
import os
import sys

try:
    from PIL import Image, ImageOps, ImageEnhance
except ImportError:
    print("Error: PIL (Pillow) is required to run this converter.")
    print("Run: pip install Pillow")
    sys.exit(1)


# Ramp from dark to bright
ASCII_CHARS = " .:-=+*#%@"


def convert_image_to_ascii(
    image_path: str,
    width: int = 40,
    height: int = 27,
    contrast: float = 1.8,
    invert: bool = False,
    charset: str = ASCII_CHARS,
) -> str:
    im = Image.open(image_path).convert("L")
    if invert:
        im = ImageOps.invert(im)

    if contrast != 1.0:
        im = ImageEnhance.Contrast(im).enhance(contrast)

    im = im.resize((width, height), Image.Resampling.LANCZOS)

    lines = []
    char_len = len(charset)
    for y in range(height):
        row = "".join(
            charset[min(int(im.getpixel((x, y)) / 256.0 * char_len), char_len - 1)]
            for x in range(width)
        )
        lines.append(row)

    return "\n".join(lines)


def update_profile_py(ascii_art: str, profile_path: str = "update_profile.py"):
    if not os.path.exists(profile_path):
        print(f"Error: {profile_path} not found.")
        return False

    with open(profile_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = 'ART = r"""\n'
    end_marker = '"""\n'

    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Error: could not find ART definition in update_profile.py")
        return False

    end_idx = content.find(end_marker, start_idx + len(start_marker))
    if end_idx == -1:
        print("Error: could not find end of ART in update_profile.py")
        return False

    new_content = (
        content[: start_idx + len(start_marker)]
        + ascii_art.strip("\n")
        + "\n"
        + content[end_idx:]
    )

    with open(profile_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Successfully updated ART in {profile_path}!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Convert image to ASCII art for profile banner")
    parser.add_argument("image", help="Path to input image (PNG/JPG)")
    parser.add_argument("--width", type=int, default=40, help="Width in characters (default: 40)")
    parser.add_argument("--height", type=int, default=27, help="Height in lines (default: 27)")
    parser.add_argument("--contrast", type=float, default=1.8, help="Contrast multiplier (default: 1.8)")
    parser.add_argument("--invert", action="store_true", help="Invert brightness")
    parser.add_argument("--apply", action="store_true", help="Automatically inject result into update_profile.py")

    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"File not found: {args.image}")
        sys.exit(1)

    art = convert_image_to_ascii(
        args.image,
        width=args.width,
        height=args.height,
        contrast=args.contrast,
        invert=args.invert,
    )

    print("\n--- ASCII PREVIEW ---")
    print(art)
    print("---------------------\n")

    if args.apply:
        update_profile_py(art)


if __name__ == "__main__":
    main()
