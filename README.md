# E-commerce Visitor Dashboard (Streamlit) — Multi-part Download

This project supports **multi-part data** to keep downloads small.

## Files
- `app.py`, `requirements.txt`, `index.html`, `style.css`, `README.md`
- Data parts: `data/parts/visitor_events_100k_part1.csv` … `part4.csv`

## How to assemble
1. Unzip **code** zip into a folder/repo.
2. Unzip each **data-part** zip into the same folder, so the files end up under `data/parts/`.
3. Run locally:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```
The app will automatically load from `data/parts/*` if `data/visitor_events_100k.csv` is missing.

## Netlify + Streamlit Cloud
- Netlify hosts the landing page (`index.html`, `style.css`).
- Streamlit Cloud runs the app from `app.py` (push repo to GitHub and create the app).
- The data parts should be committed to the repo or uploaded to the app storage (recommended for the demo size).
