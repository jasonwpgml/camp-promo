"""Render the share cards in cards.html to PNG with headless Edge.

Usage: python render_cards.py
Writes PNGs next to camp.html (one folder up) and reports any element that
overflows its card.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
CARDS = {
    "portrait": "camp-1080x1350.png",
    "square1": "camp-1080x1080-1.png",
    "square2": "camp-1080x1080-2.png",
    "ad": "ad-1080x1080.png",
}

OVERFLOW_JS = """
(card) => {
  const r = card.getBoundingClientRect();
  const bad = [];
  for (const el of card.querySelectorAll('*')) {
    const b = el.getBoundingClientRect();
    if (b.width === 0 && b.height === 0) continue;
    if (b.right > r.right - 40 || b.bottom > r.bottom - 30 || b.left < r.left + 40)
      bad.push(el.tagName + '.' + el.className + ' ' + JSON.stringify(el.textContent.slice(0, 30)));
  }
  return {w: r.width, h: r.height, scrollH: card.scrollHeight, bad};
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    page = browser.new_page(viewport={"width": 1200, "height": 1400}, device_scale_factor=1)
    page.goto((HERE / "cards.html").as_uri())
    page.evaluate("document.fonts.ready")
    for card_id, name in CARDS.items():
        el = page.locator(f"#{card_id}")
        info = el.evaluate(OVERFLOW_JS)
        el.screenshot(path=str(OUT / name))
        print(card_id, info["w"], "x", info["h"], "scrollH", info["scrollH"], "overflow:", info["bad"] or "none")
    fam = page.evaluate("getComputedStyle(document.body).fontFamily")
    used = page.evaluate("document.fonts.check('900 70px \"Noto Sans KR\"')")
    print("font-family:", fam, "| Noto Sans KR available:", used)
    browser.close()
