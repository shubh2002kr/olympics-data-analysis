# 🏅 Olympics Data Analysis — Streamlit App  
> **Built by Shubh Kumar**  

[![Streamlit](https://img.shields.io/badge/Made%20With-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)  
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)  
[![Plotly](https://img.shields.io/badge/Charts-Plotly-3DDC84?logo=plotly&logoColor=white)](https://plotly.com/python/)  
[![Pandas](https://img.shields.io/badge/Data-Pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/) 
[![NumPy](https://img.shields.io/badge/Data-NumPy-013243?logo=numpy&logoColor=white)](https://numpy.org/)  

An **interactive dashboard** to explore **Olympics history**: medal trends, country performance, gender participation, sport popularity, and top athletes.  

---

## 🌐 Live Demo  
👉 [Click here to use the app](https://olympics-data-analysis-26y4q7sab9r27rdf2ac5j9.streamlit.app/)  

---

## 📂 Dataset  
This project uses Kaggle’s official dataset:  
👉 [120 Years of Olympic History — Athletes & Results](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results?resource=download)  

Required files:  
- `athlete_events.csv`  
- `noc_regions.csv`  

⚠️ These files are **not included in this repo** (to keep size <25 MB). Upload them in the sidebar when running the app.  

---

## ✨ Features
- 📈 Medal counts over time (team-adjusted for fairness in team events)  
- 🥇 Top countries with medal breakdown  
- ⚖️ Gender participation trends across decades  
- 🏟️ Sport popularity based on athlete entries  
- 👤 Top athletes by medal achievements  
- 🎨 Modern dark-themed UI  

---

## ⚡ Run Locally
If you want to run the app on your machine:  
```bash
pip install -r requirements.txt
streamlit run app.py
