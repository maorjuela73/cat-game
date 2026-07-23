# Michi Slot!

A cat-themed slot machine game built with Python and pygame. Spin the cells, match three identical cats to win!

## Play

[Play in your browser](https://maorjuela73.github.io/cat-game/) — installable as an app on iOS and Android.

## Features

- 3x3 grid of animated cat sprites
- Each cell spins independently with easing animation
- Win detection when all cells match
- Statistics tracking: click history, heat maps, sprite distribution
- Stats persist across sessions (localStorage in browser, JSON file on desktop)

## Tech Stack

- **Python 3.12** + **pygame-ce**
- **pygbag** — compiles to WebAssembly for browser play
- **GitHub Actions** — auto-deploys to GitHub Pages
- **PWA** — installable on mobile via manifest + service worker

## Run Locally

```bash
pip install pygame-ce
python main.py
```

## Build for Web

```bash
pip install pygbag pygame-ce
pygbag --build --template template.tmpl --width 380 --height 660 --ume_block 0 --disable-sound-format-error main.py
```

Output goes to `build/web/`.

## Project Structure

```
├── main.py              # Entry point + game loop
├── models.py            # Game logic (Cell, StatsManager)
├── ui.py                # Rendering (colors, fonts, sprites, draw functions)
├── template.tmpl        # HTML template for web build
├── pygbag.ini           # Build exclusions
├── assets/
│   ├── audio/           # Music + SFX (MP3 + OGG)
│   ├── fonts/           # PixelPurl.ttf
│   └── graphics/        # Cat sprite sheets
├── static/
│   ├── favicon.png      # App icon
│   ├── manifest.webmanifest
│   └── sw.js            # Service worker
└── .github/workflows/
    └── deploy.yml       # CI/CD to GitHub Pages
```
