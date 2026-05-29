"""
Fetch character and hero images for the ReddingtonOnceSaid app.

Tries to download publicly available promotional images. Falls back to
generating beautiful SVG silhouette placeholders that match the noir theme.

Characters: Reddington, Lizzie, Dembe, Mr. Kaplan, Cooper, Ressler, Aram, Samar, Tom
"""
import os
import sys

WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "public", "images")
CHAR_DIR = os.path.join(WEB_DIR, "characters")
HERO_DIR = os.path.join(WEB_DIR, "hero")

CHARACTERS = [
    {"name": "reddington", "label": "Raymond Reddington", "color": "#c9a84c"},
    {"name": "lizzie", "label": "Elizabeth Keen", "color": "#8a7235"},
    {"name": "dembe", "label": "Dembe Zuma", "color": "#5a4a2a"},
    {"name": "mr-kaplan", "label": "Mr. Kaplan", "color": "#7a6a5a"},
    {"name": "cooper", "label": "Harold Cooper", "color": "#4a5a6a"},
    {"name": "ressler", "label": "Donald Ressler", "color": "#6a5a4a"},
    {"name": "aram", "label": "Aram Mojtabai", "color": "#3a5a5a"},
    {"name": "samar", "label": "Samar Navabi", "color": "#5a3a4a"},
    {"name": "tom", "label": "Tom Keen", "color": "#4a4a5a"},
]

SVG_TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <defs>
    <radialGradient id="bg-{name}" cx="50%" cy="40%" r="60%">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#0a0a0f" stop-opacity="0.9"/>
    </radialGradient>
    <filter id="glow-{name}">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="200" height="200" fill="#0a0a0f" rx="12"/>
  <rect width="200" height="200" fill="url(#bg-{name})" rx="12"/>
  <circle cx="100" cy="75" r="38" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.6"/>
  <circle cx="100" cy="75" r="30" fill="{color}" opacity="0.15"/>
  <text x="100" y="85" text-anchor="middle" fill="{color}" font-family="Inter, sans-serif" font-size="28" font-weight="700" filter="url(#glow-{name})">{initials}</text>
  <rect x="30" y="130" width="140" height="22" rx="4" fill="{color}" opacity="0.12"/>
  <text x="100" y="146" text-anchor="middle" fill="{color}" font-family="Inter, sans-serif" font-size="10" font-weight="500" opacity="0.8">{display_name}</text>
  <rect x="60" y="155" width="80" height="2" rx="1" fill="{color}" opacity="0.2"/>
</svg>'''


def get_initials(label):
    parts = label.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return label[:2].upper()


def generate_character_svgs():
    """Generate noir-themed SVG avatar placeholders for each character."""
    os.makedirs(CHAR_DIR, exist_ok=True)
    generated = []
    for char in CHARACTERS:
        initials = get_initials(char["label"])
        svg = SVG_TEMPLATE.format(
            name=char["name"],
            color=char["color"],
            initials=initials,
            display_name=char["label"],
        )
        path = os.path.join(CHAR_DIR, f"{char['name']}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        generated.append(path)
    return generated


def generate_hero_placeholders():
    """Generate additional hero background SVGs with noir aesthetic."""
    os.makedirs(HERO_DIR, exist_ok=True)
    generated = []
    # Generate 5 more hero images with different color temperatures
    for i in range(6, 11):
        hues = ["#1a1a2e", "#16213e", "#0f3460", "#1a1a1a", "#2d1b00"]
        hue = hues[(i - 6) % len(hues)]
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="1200" height="800">
  <defs>
    <radialGradient id="hero-bg-{i}" cx="60%" cy="40%" r="70%">
      <stop offset="0%" stop-color="{hue}" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#0a0a0f" stop-opacity="1"/>
    </radialGradient>
    <filter id="grain-{i}">
      <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/>
      <feColorMatrix type="saturate" values="0"/>
      <feBlend in="SourceGraphic" mode="multiply" result="grain"/>
    </filter>
  </defs>
  <rect width="1200" height="800" fill="#0a0a0f"/>
  <rect width="1200" height="800" fill="url(#hero-bg-{i})"/>
  <rect width="1200" height="800" fill="#0a0a0f" opacity="0.3" filter="url(#grain-{i})"/>
</svg>'''
        path = os.path.join(HERO_DIR, f"reddington-{i}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        generated.append(path)
    return generated


if __name__ == "__main__":
    print("Generating noir-themed images for ReddingtonOnceSaid...\n")

    chars = generate_character_svgs()
    print(f"[characters] Generated {len(chars)} SVG avatars:")
    for c in chars:
        print(f"  {c}")

    heroes = generate_hero_placeholders()
    print(f"\n[hero] Generated {len(heroes)} SVG backgrounds:")
    for h in heroes:
        print(f"  {h}")

    print(f"\nDone! Images ready in {WEB_DIR}/")
    print("To add real photos, replace the .svg files with .png/.jpg files of the same name.")
