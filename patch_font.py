import fontforge
import os
import subprocess

def patch():
    font_path = "/usr/share/fonts/TTF/ShureTechMonoNerdFontPropo-Regular.ttf"
    out_dir = os.path.expanduser("~/.local/share/fonts")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ShureTechMonoNerdFontPropo-Regular.ttf")

    print("Opening font:", font_path)
    font = fontforge.open(font_path)

    # 1. Patch Gemini (0xf1a0)
    print("Importing Gemini SVG...")
    g_gemini = font[0xf1a0]
    g_gemini.clear()
    g_gemini.importOutlines("gemini.svg")
    
    # Scale and center Gemini to match typical Nerd Font dimensions (approx 800 width, centered)
    bbox = g_gemini.boundingBox()
    print("Gemini raw bbox:", bbox)
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
    print("Gemini final bbox:", g_gemini.boundingBox())

    # 2. Patch Claude (0xf299)
    print("Importing Claude SVG...")
    g_claude = font[0xf299]
    g_claude.clear()
    g_claude.importOutlines("claude.svg")
    
    bbox = g_claude.boundingBox()
    print("Claude raw bbox:", bbox)
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
    print("Claude final bbox:", g_claude.boundingBox())

    print("Generating patched font at:", out_path)
    font.generate(out_path)
    print("Font cache update...")
    subprocess.run(["fc-cache", "-f"], check=True)
    print("Done patching font!")

if __name__ == "__main__":
    patch()
