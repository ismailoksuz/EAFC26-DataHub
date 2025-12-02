# EAFC26 DataHub

This repository hosts the FC26 DataHub Player Explorer, an interactive data processing and visualization platform. The project is designed to utilize a comprehensive FC 26 (formerly FIFA 26) player dataset to generate curated player lists and display them via a dynamic web dashboard.

---

## Data Source

The data is sourced from a dataset available on Kaggle: [FC 26 (FIFA 26) Player Data](https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data).

The primary data file, **`data/players.csv`**, contains over **18,000 player records**, with each player described by more than **110 attributes**. These attributes cover detailed in-game statistics, overall ratings, potential, contractual information, and biographical details.

---

## Technologies Used

The project relies on a modern Python data stack for processing and visualization.

<ul>
  <li>Python</li>
  <li>Streamlit</li>
  <li>Pandas</li>
  <li>CSS</li>
</ul>

---

## Features

* **Immediate Startup:** Generated JSON lists (`output/json/*`) are included in the repository, enabling users to run the dashboard instantly without needing to execute the generation script first.
* **Ready-Made Lists:** Access curated lists (e.g., Wonderkids, Bosman players) directly from the sidebar.
* **Dynamic Filtering:** Use the **"Custom Filters"** section to perform real-time, multi-criteria searches across the entire dataset.
* **Comprehensive Controls:** Filter players based on ratings (Overall, Potential), Age, detailed in-game attributes (Pace, Shooting, Passing, etc.), Skill Moves, Nationality, and Club.
* **Intuitive UI:** A clean dashboard with functional sidebar navigation and clear visual highlighting for the active filter selection.

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ismailoksuz/EAFC26-DataHub
cd FC26-DataHub
```

### 2. Install Dependencies

Install all necessary Python libraries after activating your virtual environment:
```bash
pip install -r requirements.txt
```

### 3. Running the Application

The dashboard can be started immediately:
```bash
streamlit run src/app_dashboard.py
```

### Optional: Rebuilding Data Lists

f you modify the filtering criteria in the source code or update the main `data/players.csv` file, you must run the generation script to update the lists:

```bash
python src/generate.py
```
