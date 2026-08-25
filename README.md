# BEA Macro Data Analyzer Skill

AI Agent Skill for Macro Data Analysis using BEA.gov NIPA API.

This repository contains an institutional-grade macroeconomic AI skill that ingests U.S. National Income and Product Accounts (NIPA) data from the BEA API and provides structural decomposition, vintage revision analysis, and nowcasts based on semantic keys.

Contents
- SKILL.md — Skill definition, guardrails, and workflows.
- bea_nipa_dictionary.json — Semantic mapping for BEA NIPA tables and allowed indicator keys.
- boe_nipa_execution_logic.py — Deterministic Python backend to fetch and pre-process BEA data.

Requirements
- Python 3.10+
- pip

Installation
1. Clone the repository:
   git clone https://github.com/ImLimonH/BEA_macro_data_analyzer_skill.git
   cd BEA_macro_data_analyzer_skill

2. (Optional) Create and activate a virtual environment:
   python -m venv .venv
   source .venv/bin/activate  # macOS / Linux
   .venv\Scripts\activate     # Windows

3. Install dependencies:
   pip install -r requirements.txt

If a requirements.txt is not present, install the following packages:
   pip install requests pandas pytest

Configuration
- Store your BEA API key in an environment variable before running scripts:
  export BEA_API_KEY="your_api_key_here"    # macOS / Linux
  setx BEA_API_KEY "your_api_key_here"      # Windows (new shell)

Usage
- The deterministic backend is boe_nipa_execution_logic.fetch_bea_indicator(indicator_key, api_key).
- Allowed indicator keys (must use exactly these strings):
  - gdp_real_growth
  - gdp_real_level
  - core_pce_inflation
  - personal_income_monthly
  - savings_rate_monthly
  - final_sales_domestic
  - change_inventories

Example (Python):

```python
from boe_nipa_execution_logic import fetch_bea_indicator
import os

api_key = os.getenv('BEA_API_KEY')
if not api_key:
    raise RuntimeError('BEA_API_KEY environment variable not set')

# Fetch latest GDP real growth series
df = fetch_bea_indicator('gdp_real_growth', api_key)
print(df.tail())
```

Testing
- Run unit tests (if present) with:
  pytest

CI / CD
- GitHub Actions workflows (python-ci.yml and skill-deploy.yml) are included under .github/workflows/.
- The deploy workflow requires a repository secret (e.g., SKILLMD_TOKEN) to publish to skillmd.com.

License
- This project is licensed under the MIT License. See LICENSE for details.

Security & Guardrails
- The LLM skill must not construct BEA API URLs or guess LineCodes directly. Use the provided backend and the semantic keys defined in bea_nipa_dictionary.json.
- Do not extrapolate missing government data; if data is unavailable the backend will raise an error and the agent must report: "Data unavailable via NIPA API.".

Contributing
- Contributions are welcome. Please open issues or pull requests. For major changes, open an issue first to discuss the proposed change.
