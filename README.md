# FastF1 Web Preview

This bundle contains a lightweight HTML/CSS viewer to open your locally-generated FastF1 plot in a browser.

## Files
- `index.html` — Web page that displays `plot.png`.
- `styles.css` — Styling for the page.
- `plot_annotate_speed_trace.py` — (included if you uploaded it) your example plotting script.

## How to use
1. Place your Python script in the same folder and generate a plot image called **plot.png**.
2. Double‑click **index.html** (or use VS Code Live Server) to view the image.
3. If you don't see an image, ensure your script saved `plot.png` to the same directory as `index.html`.

> Tip: You can change the `<img src="plot.png">` path in `index.html` to point to another filename if needed.

Generated: 2025-09-18T19:14:52
