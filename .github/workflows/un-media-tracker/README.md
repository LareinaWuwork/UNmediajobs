# UN Media & Communications Jobs Tracker

A simple GitHub Pages website that tracks UN-related jobs focused on media, communications, public information, digital content, social media, video, advocacy and partnerships.

## How to use

1. Create a GitHub repo named `un-media-tracker`.
2. Upload all files in this folder.
3. Go to GitHub repo → Settings → Pages.
4. Set source to `Deploy from a branch`, branch `main`, folder `/root`.
5. Go to Actions → enable workflows.
6. The scraper will run daily and update `jobs.json`.

## Run locally

```bash
pip install -r requirements.txt
python scraper.py
python -m http.server 8000
```

Then open `http://localhost:8000`.
