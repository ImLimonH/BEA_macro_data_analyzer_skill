# BEA Macro Data Analyzer Skill

An institutional-grade AI agent skill for structural macroeconomic analysis using the U.S. Bureau of Economic Analysis (BEA) NIPA API. This repository provides a deterministic Python backend and semantic dictionary to prevent LLM hallucinations, enabling safe, quantitative analysis of GDP decomposition, vintage revisions, and nowcasting.

> ⚠️ **CRITICAL PREREQUISITE**  
> Before deploying this skill or requesting a BEA API key, you **must** read the official [BEA Web Service API User Guide](https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf). Understanding BEA's rate limits, dataset structures, and revision schedules is mandatory for maintaining data integrity and avoiding IP throttling.

## Repository Contents

| File | Purpose |
| :--- | :--- |
| `SKILL.md` | Agent definition, operational guardrails, analytical workflows, and required output formats. |
| `bea_nipa_dictionary.json` | Semantic mapping of allowed indicator keys to BEA NIPA tables. Prevents LLM API hallucinations. |
| `boe_nipa_execution_logic.py` | Deterministic Python backend for fetching, parsing, and validating BEA data. |
| `.github/workflows/` | CI/CD pipelines for testing (`python-ci.yml`) and publishing to skillmd.com (`skill-deploy.yml`). |

## Requirements

-   Python 3.10+
-   `pip`
-   Valid BEA API Key ([Register here](https://apps.bea.gov/api/signup/))

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/ImLimonH/BEA_macro_data_analyzer_skill.git
    cd BEA_macro_data_analyzer_skill
    ```

2.  *(Optional but recommended)* Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate      # macOS / Linux
    .venv\Scripts\activate         # Windows
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    > **Note:** If `requirements.txt` is missing from your clone, install manually:
    > `pip install requests pandas pytest`

## Configuration

Store your BEA API key as an environment variable. **Never hardcode keys in agent prompts or source files.**

```bash
# macOS / Linux
export BEA_API_KEY="your_api_key_here"

# Windows (PowerShell)
$env:BEA_API_KEY = "your_api_key_here"

# Windows (CMD - persists across new shells)
setx BEA_API_KEY "your_api_key_here"
```

## Usage & Allowed Semantic Keys

The LLM agent **must never** construct BEA API URLs directly. All data retrieval must go through the deterministic backend using the exact semantic keys defined in `bea_nipa_dictionary.json`.

### Backend Function

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

### Allowed Semantic Keys Reference

| Semantic Key | BEA NIPA Table | Target Line Description | Frequency | Unit | Analytical Use | Agent Guardrail |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `gdp_real_growth` | T10101 | Gross domestic product | Quarterly | Percent | Measures headline real GDP momentum. | Must be reconciled with `final_sales_domestic` and `change_inventories`. |
| `gdp_real_level` | T10106 | Gross domestic product | Quarterly | Billions of chained dollars | Measures absolute inflation-adjusted U.S. economic output. | Use for baseline output level, not short-term momentum only. |
| `core_pce_inflation` | T20304 | Personal consumption expenditures excluding food and energy | Quarterly | Index number | Tracks sticky inflation pressure using the Fed's preferred inflation framework. | Do not treat as headline CPI. Label clearly as Core PCE. |
| `personal_income_monthly` | T20100 | Personal income | Monthly | Billions of dollars | High-frequency proxy for consumer strength and GDP nowcasting. | Use for nowcasts before quarterly GDP releases. |
| `savings_rate_monthly` | T20100 | Personal saving rate | Monthly | Percent | Measures consumer financial buffer and spending sustainability. | Falling savings rate may indicate consumption supported by balance-sheet drawdown. |
| `final_sales_domestic` | T10102 | Final sales to domestic purchasers | Quarterly | Billions of dollars | Measures true underlying domestic demand, excluding inventory distortion. | Required for GDP quality checks. |
| `change_inventories` | T10101 | Change in private inventories | Quarterly | Billions of dollars | Identifies whether GDP growth is being supported by inventory buildup. | If GDP rises while final sales weaken, flag low-quality growth. |

## Testing

Run unit tests (if present) with:

```bash
pytest
```

## CI / CD

GitHub Actions workflows are included under `.github/workflows/`:
- **`python-ci.yml`** — Automated testing on pull requests and commits.
- **`skill-deploy.yml`** — Publishing to skillmd.com (requires repository secret `SKILLMD_TOKEN`).

## License

This project is licensed under the MIT License. See `LICENSE` for details.

## Security & Guardrails

- **No API URL Construction:** The LLM skill must not construct BEA API URLs or guess LineCodes directly. Use the provided backend and the semantic keys defined in `bea_nipa_dictionary.json`.
- **No Data Extrapolation:** Do not extrapolate missing government data. If data is unavailable, the backend will raise an error and the agent must report: **"Data unavailable via NIPA API."**
- **API Key Security:** Never embed API keys in prompts, code, or configuration files. Always use environment variables.

## Contributing

Contributions are welcome. Please open issues or pull requests. For major changes, open an issue first to discuss the proposed change.
