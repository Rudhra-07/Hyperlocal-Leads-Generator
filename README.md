# 🎯 AI-Powered Hyperlocal Business Lead Generation Tool

An advanced, modular, and production-ready CLI pipeline designed to discover local businesses, crawl their websites, and extract high-quality contact details (emails, phone numbers, and social links) using an intelligent combination of Regex Parsers and LLM extraction (LangChain + Gemini 2.5 Flash).

---

## ⚡ Highlights & Key Capabilities

- **📍 Intelligent Geocoding & Discovery**: Uses the **Google Places API** to discover hyper-localized business listings based on location, radius, and business type.
- **🌐 Dual-Engine Web Crawler**: Combines lightweight **BeautifulSoup4** fetching with a headless **Selenium** fallback engine to crawl dynamic single-page applications (SPAs).
- **🧠 Hybrid Contact Extraction**: 
  - **Primary**: Ultra-fast Regex patterns matching localized phone numbers, emails, and social media handles.
  - **Fallback**: LangChain orchestrator with **Gemini 2.5 Flash** to reason through unstructured web text and extract contacts that traditional regex patterns miss.
- **⚖️ Scoring & Quality Tiering**: Automatic lead validation, deduplication, and quality scoring (0 to 10 scale) based on contact availability.
- **📥 Enterprise-Ready Storage**: Outputs results instantly to localized **CSV files** and supports seamless integration with **MongoDB** databases.

---

## 🏗️ Architecture & Data Flow

The pipeline executes standard data engineering and AI extraction steps:

```mermaid
graph TD
    A[CLI Input: Location, Category, Radius] --> B[Geocoding: Resolve Coordinates]
    B --> C[Discovery Module: Search Businesses]
    C -->|Google Places API| D[Retrieve Metadata]
    C -.->|Fallback: OSM Nominatim| D
    D --> E[Parallel Lead Processing]
    E --> F{Has Website?}
    F -->|Yes| G[Website Crawler]
    F -->|No| K[Process Lead directly]
    G -->|BeautifulSoup| H[Scrape Homepage & Contacts]
    G -.->|Fallback: Selenium| H
    H --> I[Regex Contact Extractor]
    I --> J{Has Email & Phone?}
    J -->|Yes| K
    J -->|No| L[LLM Extractor: LangChain + Gemini 2.5 Flash]
    L --> K
    K --> M[Lead Processor: Deduplication & Scoring]
    M --> N[Exporter Module]
    N --> O[CSV File Generation]
    N -.->|Optional| P[MongoDB Import]
```

---

## 📂 Project Directory Structure

```text
hyperlocal_lead_generator/
├── config.py                 # Central config schema and environment validation
├── main.py                   # CLI Entrypoint & Pipeline Orchestrator
├── requirements.txt          # Python library dependencies
├── .env.example              # Template configuration for environment keys
├── .gitignore                # Optimized Git exclusions list
├── app.log                   # Logging file (auto-generated)
├── data/                     # Output directory for leads
│   └── .gitkeep              # Ensures folder existence in version control
├── modules/                  # Pipeline core subsystems
│   ├── business_discovery.py # Places API search & OSM geocoding fallback
│   ├── website_crawler.py    # BeautifulSoup & Selenium webdriver engines
│   ├── contact_extractor.py  # High-efficiency regex parsing
│   ├── llm_extractor.py      # LangChain + Gemini structured extraction fallback
│   ├── lead_processor.py     # Deduplication and quality grading logic
│   └── exporter.py           # Exports records to CSV & MongoDB
├── utils/                    # Shared helper functions
│   ├── helpers.py            # Scoring models & general string utilities
│   ├── logger.py             # Pre-configured global rotating logger
│   └── validators.py         # URL, email, and phone validation helpers
└── tests/                    # Robust test suite
    └── test_pipeline.py      # Automated unit tests for lead pipeline
```

---

## 🚀 Setup & Installation

Follow these step-by-step instructions to set up the tool locally:

### 1. Prerequisites
- **Python 3.10+** installed on your machine.
- A **Google Cloud Console** account with the **Places API** enabled.
- A **Google AI Studio** account for a **Gemini API Key**.
- **Google Chrome** browser installed (required for the Selenium crawling fallback).

### 2. Clone the Repository
```bash
git clone <your-repository-url>
cd hyperlocal_lead_generator
```

### 3. Create and Activate a Virtual Environment
We recommend using a virtual environment to manage dependencies neatly.

- **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure the Environment
Duplicate the environment template file and insert your API credentials:
```bash
cp .env.example .env
```
Open the `.env` file in your preferred text editor and fill in your keys:
```ini
# Google Maps Places API Key
GOOGLE_MAPS_API_KEY=AIzaSyYourGoogleMapsAPIKeyHere

# Gemini API Key
GEMINI_API_KEY=AIzaSyYourGeminiAPIKeyHere

# Optional: MongoDB Connection (Leave commented if not using)
# MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/dbname

# Optional: Headless Browser Config
SELENIUM_HEADLESS=true
```

---

## 💻 CLI Usage & Examples

Run the orchestrator script using python command line options.

### Basic Run
Discover up to 10 cafes in London within a 5km radius:
```bash
python main.py --location "London" --radius 5 --category "cafe" --limit 10
```

### Advanced Run
Query up to 30 software firms in Boston with custom arguments:
```bash
python main.py --location "Boston, MA" --radius 10 --category "software agency" --limit 30
```

### CLI Arguments Reference

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--location` | `str` | *(Required)* | The focal point target (city name, zip code, or latitude/longitude coordinates). |
| `--radius` | `int` | `5` | The search radius in kilometers (Minimum: `1`, Maximum: `25`). |
| `--category` | `str` | `"restaurant"` | The category of businesses to look up (e.g., `gym`, `salon`, `cafe`). |
| `--limit` | `int` | `30` | The maximum number of places to retrieve and process. |

---

## 📊 Output Schema & Scoring

Results are written to the `data/` directory with filenames stamped with the target parameters, e.g., `data/leads_20260601_london_cafe.csv`.

### Lead Scoring Rules
The lead quality score is on a `0-10` index, computed as follows:
- **Website Available**: `+3` points
- **Email Address Extracted**: `+3` points
- **Phone Number Extracted**: `+2` points
- **Social Media Link Found**: `+2` points (Facebook, Twitter, LinkedIn, Instagram, etc.)

### Lead Quality Tiers
| Score Range | Quality Tier | Sales Action Recommendation |
| :---: | :--- | :--- |
| **8 – 10** | 🌟 High Quality | High-priority target. Perfect contact data; execute automated/manual outreach. |
| **5 – 7** | ⚡ Medium Quality | Solid target. Missing either email or phone; consider supplementary manual search. |
| **0 – 4** | ⚠️ Low Quality | Low-priority target. Lacks essential digital channels; requires high manual validation. |

---

## 🧪 Running Automated Tests

Run unit tests using Python's standard `unittest` module to verify that core extractors, parsers, and processing models function correctly:

```bash
python -m unittest tests/test_pipeline.py
```

---

## 🛠️ Roadmap & Future Improvements

- **⚡ Asynchronous Crawling**: Integrate `playwright` or `asyncio` to speed up heavy website crawls.
- **🤖 Built-in Email Agent**: Connect outbound SMTP or SendGrid service to draft/send personalized introductory emails to "High Quality" leads automatically.
- **🗺️ Interactive Map Dashboard**: Build a React/Next.js dashboard to plot generated leads on an interactive map visual.
