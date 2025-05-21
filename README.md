
# 🎵 Spotify Song Dataset Analysis  
### *An End-to-End Data Engineering & Analysis Pipeline*  

👋 Hi! I'm Christian, and this project showcases a full data science workflow built from scratch. Using Spotify’s top tracks from 1998–2020, a complete pipeline was created which handles data cleaning, storage, analysis, and visualisation—wrapped in a user-friendly, interactive dashboard.

---

## 🎬 Demo  
> Here’s a sneak peek of the interactive dashboard in action:

<p align="center">
  <img src="demo.gif" alt="Spotify Analysis Dashboard Demo" width="75%">
</p>

> 🛠️ Replace `demo.gif` with your own screen recording saved as a GIF, and `banner.png` with your custom banner.

---

## 📦 Dataset Overview  
- **Source:** [Kaggle – Spotify Top Hits (2000–2019)](https://www.kaggle.com/datasets/paradisejoy/top-hits-spotify-from-20002019)
- **Size:** ~2,000 tracks  
- **Features Include:**
  - **Metadata:** Song name, artist, year, genre, popularity  
  - **Audio Features:** Danceability, energy, speechiness, tempo, loudness, duration (ms), etc.

---

## 🚀 What I Built

### 🔧 1. Data Preprocessing & Database Creation ([`Preprocessing.py`](./Preprocessing.py))
- Implements a full ETL pipeline to clean and transform the raw dataset
- Filters: popularity > 50, speechiness between 0.33–0.66, danceability > 0.2
- Stores data in a **fully normalized SQLite database** with `Songs`, `Artists`, `Genres`, and a junction table
- Uses batch operations and idempotent inserts to ensure efficiency and data integrity

### 🗃️ 2. Database Schema
- Designed relational tables with foreign key constraints
- Supports one-to-many and many-to-many relationships
- Optimised for fast querying and scalability

### 📊 3. Genre Statistics Analysis ([`Genres.py`](./Genres.py))
- Calculates genre-based metrics by year: popularity, danceability, distribution
- Interactive input for year selection (1998–2020)
- Generates **publication-ready** pie charts and bar plots using `Matplotlib`
- Includes year validation, error handling, and smart SQL joins

### 🎤 4. Artist Popularity Comparison ([`Artist.py`](./Artist.py))
- Benchmarks an artist's average popularity against genre averages
- Produces dual-bar charts and data tables with dynamic highlights
- Handles case sensitivity and missing data gracefully
- Uses aggregate SQL functions and efficient joins

### 🏆 5. Top 5 Artist Ranking Tool ([`Top5.py`](./Top5.py))
- Ranks artists using a **weighted formula**: 60% by song count, 40% by average popularity
- Accepts custom year ranges and highlights top performers annually
- Includes interactive validation and trend line visualisations
- Interpolates missing values to smooth visuals

### 🧩 6. Interactive Analysis Dashboard ([`menu.ipynb`](./menu.ipynb))
- Combines all core scripts into one Jupyter Notebook with `ipywidgets`
- Clean GUI with dropdowns, sliders, and text input
- Allows users to explore data insights **without touching code**
- Output areas update dynamically based on user selections

---

## 📸 Assets


---

## ✅ Summary of Features

| Feature | Description |
|--------|-------------|
| **ETL Pipeline** | Cleans, transforms, and stores Spotify data in SQLite |
| **Genre Insights** | Stats per genre per year + visual distribution |
| **Artist Comparisons** | Visual and statistical artist vs genre benchmarking |
| **Ranking System** | Top 5 artists ranked by custom logic and trend analysis |
| **User Interface** | Fully interactive dashboard (Jupyter + ipywidgets) |

---

## ⚙️ Engineering Highlights

- Built using **modular OOP architecture**
- Extensive use of **Pandas**, **SQL**, and **Matplotlib**
- Robust **error handling**, **input validation**, and **data integrity checks**
- Smart separation between GUI and business logic
- Designed for scalability and future dataset compatibility

---

## 💡 Why This Project?

I created this project not just to explore Spotify’s data, but to showcase real-world skills in:
- **Data Engineering & Pipeline Design**
- **Relational Database Management**
- **Analytical Reporting & Visualisation**
- **Building Usable, Interactive Tools**

It reflects how I think about solving problems: make it structured, insightful, and accessible.

---

## 📂 Explore the Code  
Each script in the repository is clearly documented and independently testable:
- [`Preprocessing.py`](./Preprocessing.py)
- [`Genres.py`](./Genres.py)
- [`Artist.py`](./Artist.py)
- [`Top5.py`](./Top5.py)
- [`menu.ipynb`](./menu.ipynb)

---

Thanks for checking out my project! 🙌  
If you're an employer or collaborator interested in data science, analytics, or software development—I'd love to connect.
