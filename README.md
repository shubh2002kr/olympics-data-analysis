# 🏅 Olympics Data Analysis — Streamlit App

An interactive dashboard to explore Olympics data: medal trends, country performance, gender participation, sport popularity, and top athletes.

---

## ⚠️ Keep Repo Under 25 MB (Important)

To keep your GitHub repository/zip **well under 25 MB**:

- **Do NOT commit the datasets** (`athlete_events.csv`, `noc_regions.csv`).  
- Download them yourself from Kaggle and **upload via the app sidebar at runtime**.
- This repo only contains code + small assets.

Already handled for you:
- `.gitignore` excludes `*.csv`, `data/`, archives, and other large files.
- README explains how to place data locally without committing it.

---

## 🚀 Quickstart

```bash
# 1) Install dependencies
pip install -r requirements.txt

# 2) Run the app
streamlit run app.py
```

Then, in the **sidebar**, upload:
- `athlete_events.csv`
- `noc_regions.csv`

> These are standard files from Kaggle's Olympics dataset.

---

## 🧰 Tech Stack
- Python, Pandas, NumPy
- Plotly (interactive charts)
- Streamlit (web app)

---

## 🧭 Features
- 📈 Medals over time (team-adjusted counting for fairness in team events)
- 🥇 Top countries + medal breakdown
- ⚖️ Gender participation trends
- 🏟️ Sport popularity (participation volume)
- 👤 Top athletes by medals

---

## 📁 Data Handling (Local Only)
- Keep datasets **outside the repository** (e.g., in a local `data/` folder).
- **Do not upload datasets** to GitHub or include them in zips.
- The app reads your uploads at runtime via the sidebar.

---

## 📸 Screenshots (optional)
Create a folder `images/` with small screenshots (PNG, each <1 MB) and reference them here.

---

## 📝 License
MIT (optional). Add a `LICENSE` file if you want.
