# 🎮 Steam Scraper

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-2088FF?logo=githubactions&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-See%20repository-lightgrey)

A Python-based **Steam web scraping and data collection pipeline** designed to collect, process, and analyze Steam data automatically.

The project combines a modular Python codebase with **GitHub Actions automation**, structured data storage, notebooks for analysis, and Docker support.

---

## 📌 Overview

**Steam Scraper** automates the process of collecting data from Steam and organizing it into a format suitable for downstream analysis.

The project was built with a focus on:

- 🕷️ Web scraping
- 🐍 Python-based data pipelines
- 📊 Data analysis and exploration
- ⚙️ Workflow automation with GitHub Actions
- 🐳 Containerized execution with Docker
- 📁 Structured data storage
- 🔄 Reproducible data collection

This makes the project useful as a foundation for **Steam market analysis, gaming analytics, exploratory data analysis, and data engineering experiments**.

---

## ✨ Features

### 🕷️ Steam Data Scraping

Collects publicly available Steam data through an automated scraping workflow.

### ⚙️ Automated Execution

The project includes **GitHub Actions workflows**, allowing scraping jobs to be automated without requiring the scraper to be manually executed each time.

### 📊 Data Analysis

The repository includes Jupyter notebooks for exploring and analyzing the collected dataset.

### 🧩 Modular Architecture

The codebase separates application logic into dedicated components under `src/`, making the scraper easier to maintain and extend.

### 🐳 Docker Support

A Dockerfile is included for running the project inside a consistent, isolated environment.

### 📦 Structured Project Layout

The repository separates source code, application components, datasets, notebooks, and automation workflows.

---

## 🏗️ Project Structure

```text
steam_scraper/
│
├── .github/
│   └── workflows/          # GitHub Actions automation
│
├── app/                    # Application-related components
│
├── data/                   # Scraped / processed data
│
├── notebooks/              # Data exploration and analysis
│
├── src/                   # Core scraper and processing logic
│
├── .dockerignore
├── .gitattributes
├── .gitignore
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.x
- Git
- Docker *(optional)*

---

### 1. Clone the Repository

```bash
git clone https://github.com/howlingwolfs/steam_scraper.git
cd steam_scraper
```

---

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

The exact entry point may depend on the scraper workflow configured in the repository.

A typical Python execution pattern is:

```bash
python <entrypoint>.py
```

If you are running the project through its automated workflow, GitHub Actions can be used to execute the scraping pipeline according to the configured workflow.

> **Tip:** Check `.github/workflows/` for the current automation configuration and `src/` for the scraper implementation.

---

## 🐳 Docker

Build the Docker image:

```bash
docker build -t steam-scraper .
```

Run the container:

```bash
docker run --rm steam-scraper
```

Docker provides a reproducible environment for running the scraper without installing project dependencies directly on the host machine.

---

## ⚙️ GitHub Actions

One of the main goals of this project is automated Steam data collection.

The repository contains GitHub Actions workflows under:

```text
.github/workflows/
```

These workflows can be used to automate tasks such as:

- Running the scraper
- Updating collected data
- Scheduling recurring scraping jobs
- Executing the pipeline in a clean environment

This approach turns the repository from a simple scraping script into an **automated data collection pipeline**.

---

## 📊 Data & Analysis

Collected data is stored under:

```text
data/
```

The project also includes Jupyter notebooks under:

```text
notebooks/
```

These notebooks can be used for:

- Exploratory Data Analysis (EDA)
- Data cleaning
- Visualization
- Trend analysis
- Feature exploration
- Further experimentation

---

## 🔄 Pipeline

At a high level, the project follows this workflow:

```text
                 ┌──────────────────┐
                 │      Steam       │
                 │  Public Website  │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Steam Scraper   │
                 │    (Python)      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Raw / Stored   │
                 │      Data        │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Notebooks /    │
                 │     Analysis     │
                 └──────────────────┘

        GitHub Actions
              │
              ▼
       Automated Execution
```

---

## 🧪 Development

When modifying the project:

1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Make changes inside the appropriate `src/` or `app/` module.
4. Test the scraper locally.
5. Review generated data.
6. Verify the GitHub Actions workflow before pushing production changes.

---

## ⚠️ Responsible Scraping

This project is intended for educational, research, and data-analysis purposes.

When running the scraper:

- Respect Steam's terms and policies.
- Avoid excessive request rates.
- Do not attempt to bypass authentication, access controls, CAPTCHAs, or other security mechanisms.
- Use reasonable delays and request volumes.
- Be mindful of the impact automated requests can have on external services.

---

## 💡 Potential Use Cases

The collected Steam data can serve as a foundation for projects such as:

- 🎮 Game popularity analysis
- 📈 Price and discount analysis
- ⭐ Review sentiment analysis
- 🏷️ Genre and tag analysis
- 🔥 Trending game detection
- 📊 Steam market analytics
- 🤖 Recommendation systems
- 🧠 Machine learning experiments
- 📉 Historical trend analysis

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Scraping and data processing |
| **GitHub Actions** | Workflow automation |
| **Docker** | Containerized execution |
| **Jupyter Notebook** | Data exploration and analysis |
| **Git** | Version control |

---

## 📁 Repository

**GitHub:**  
https://github.com/howlingwolfs/steam_scraper

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

A simple contribution workflow:

```bash
git checkout -b feature/your-feature
```

Make your changes, test them locally, then open a pull request.

---

## 📄 License

See the repository for the applicable license and usage terms.

---

## 👤 Author

**Howlingwolfs**

GitHub:  
https://github.com/howlingwolfs
