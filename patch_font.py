import os
import subprocess

import sys

# Styling setup respecting NO_COLOR
if not os.environ.get("NO_COLOR") and sys.stdout.isatty():
    C_INFO = '\033[1;34m'
    C_SUCCESS = '\033[1;32m'
    C_ERROR = '\033[1;31m'
    C_BOLD = '\033[1m'
    C_DIM = '\033[2m'
    C_RESET = '\033[0m'
else:
    C_INFO = ''
    C_SUCCESS = ''
    C_ERROR = ''
    C_BOLD = ''
    C_DIM = ''
    C_RESET = ''

def step(msg): print(f"\n{C_DIM}---{C_RESET}\n{C_BOLD}{msg}{C_RESET}")
def info(msg): print(f"  {C_INFO}•{C_RESET} {msg}")
def success(msg): print(f"  {C_SUCCESS}✔{C_RESET} {msg}")
def error(msg): print(f"  {C_ERROR}✖ ERROR:{C_RESET} {msg}", file=sys.stderr)
def dim(msg): print(f"    {C_DIM}↳ {msg}{C_RESET}")

try:
    import fontforge
except ImportError:
    print(file=sys.stderr)
    error("Missing required dependency: fontforge")
    print(f"    {C_DIM}↳ Please install it (e.g., sudo pacman -S fontforge){C_RESET}", file=sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)

def patch():
    font_path = "/usr/share/fonts/TTF/ShureTechMonoNerdFontPropo-Regular.ttf"
    out_dir = os.path.expanduser("~/.local/share/fonts")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ShureTechMonoNerdFontPropo-Regular.ttf")

    step("1. Initialization")
    info(f"Opening font: {C_BOLD}{font_path}{C_RESET}")
    font = fontforge.open(font_path)

    step("2. Patch Gemini (0xf1a0)")
    info("Importing Gemini SVG...")
    g_gemini = font[0xf1a0]
    g_gemini.clear()
    g_gemini.importOutlines("gemini.svg")
    
    # Scale and center Gemini to match typical Nerd Font dimensions (approx 800 width, centered)
    bbox = g_gemini.boundingBox()
    dim(f"Raw bbox: {bbox}")
    # Scale to height of ~800 units
    h = bbox[3] - bbox[1]
    if h > 0:
        scale_factor = 800.0 / h
        g_gemini.transform([scale_factor, 0, 0, scale_factor, 0, 0])
    # Center horizontally and adjust width to match original (880)
    bbox = g_gemini.boundingBox()
    w = bbox[2] - bbox[0]
    shift_x = (880.0 - w) / 2.0 - bbox[0]
    # Move vertically to center around the baseline / ascender (baseline is 0, ascender is ~768, descender is -126)
    # Original centered vertically around ~321. New center:
    new_h = bbox[3] - bbox[1]
    shift_y = 321.0 - (bbox[1] + new_h / 2.0)
    g_gemini.transform([1, 0, 0, 1, shift_x, shift_y])
    g_gemini.width = 880
    dim(f"Final bbox: {g_gemini.boundingBox()}")

    step("3. Patch Claude (0xf299)")
    info("Importing Claude SVG...")
    g_claude = font[0xf299]
    g_claude.clear()
    g_claude.importOutlines("claude.svg")
    
    bbox = g_claude.boundingBox()
    dim(f"Raw bbox: {bbox}")
    h = bbox[3] - bbox[1]
    if h > 0:
        scale_factor = 800.0 / h
        g_claude.transform([scale_factor, 0, 0, scale_factor, 0, 0])
    bbox = g_claude.boundingBox()
    w = bbox[2] - bbox[0]
    shift_x = (880.0 - w) / 2.0 - bbox[0]
    new_h = bbox[3] - bbox[1]
    shift_y = 321.0 - (bbox[1] + new_h / 2.0)
    g_claude.transform([1, 0, 0, 1, shift_x, shift_y])
    g_claude.width = 880
    dim(f"Final bbox: {g_claude.boundingBox()}")

    step("4. Output Generation")
    info(f"Generating patched font at: {C_BOLD}{out_path}{C_RESET}")
    font.generate(out_path)
    info("Updating font cache...")
    subprocess.run(["/usr/bin/fc-cache", "-f"], check=True)

    print()
    success("Done patching font!")
    print()

if __name__ == "__main__":
    patch()
