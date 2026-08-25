import requests
import pandas as pd
import json

# Load dictionary at runtime
with open('bea_nipa_dictionary.json', 'r') as f:
    BEA_DICT = json.load(f)

def fetch_bea_indicator(indicator_key: str, api_key: str) -> pd.DataFrame:
    """
    Fetches BEA data deterministically. The LLM only sees the final DataFrame.
    """
    config = BEA_DICT["api_config"]
    
    if indicator_key not in BEA_DICT["indicators"]:
        raise ValueError(f"Indicator {indicator_key} not found in NIPA dictionary.")
        
    meta = BEA_DICT["indicators"][indicator_key]
    
    # Determine explicit year range (last N years including current)
    from datetime import datetime
    current_year = datetime.now().year
    year_start = current_year - config['default_years'] + 1
    params = {
        "UserID": api_key,
        "method": "GetData",
        "DatasetName": config["dataset"],
        "TableName": meta["table_name"],
        "Frequency": meta["frequency"],
        "Year": f"{year_start},{current_year}",
        "ResultFormat": "JSON"
    }
    
    response = requests.get(config["base_url"], params=params)
    response.raise_for_status()
    raw_data = response.json()
    
    # BEA API JSON structure is deeply nested. Extract the data payload.
    try:
        df = pd.DataFrame(raw_data["BEAAPI"]["Results"]["Data"])
    except KeyError:
        raise ConnectionError("BEA API returned an unexpected JSON structure or rate limit error.")
    
    # Smart filtering: Match the target description instead of relying on brittle LineCodes
    target = meta["target_description"].lower()
    # Exclude market-based variants if the target is the standard PCE measure
    if "market-based" not in target:
        filtered_df = df[
            df['LineDescription'].str.lower().str.contains(target, na=False) &
            ~df['LineDescription'].str.lower().str.contains('market-based', na=False)
        ]
    else:
        filtered_df = df[df['LineDescription'].str.lower().str.contains(target, na=False)]
    
    # Debug: if no match, check available descriptions
    if filtered_df.empty:
        available = df['LineDescription'].unique() if 'LineDescription' in df.columns else []
        print(f"DEBUG: No match for '{target}' in {len(df)} rows")
        print(f"DEBUG: Available descriptions: {list(available)[:10]}")
        raise ValueError(f"Target description '{meta['target_description']}' not found in Table {meta['table_name']}. Available: {list(available)}")
        
    # Format for LLM consumption (TimeSeries -> Value)
    result = filtered_df[['TimePeriod', 'DataValue', 'LineDescription']].rename(
        columns={'TimePeriod': 'Date', 'DataValue': 'Value'}
    ).sort_values('Date', ascending=False)
    
    # Ensure Value column is numeric
    result['Value'] = pd.to_numeric(result['Value'], errors='coerce')
    
    # For inflation indicators, also compute quarter-over-quarter percent change
    if 'inflation' in indicator_key or 'price' in indicator_key:
        result_df = result.copy()
        result_df = result_df.sort_values('Date')
        result_df['QoQ_Pct_Change'] = result_df['Value'].pct_change() * 100
        result_df['YoY_Pct_Change'] = result_df['Value'].pct_change(periods=4) * 100
        result_df = result_df.sort_values('Date', ascending=False)
        return result_df[['Date', 'Value', 'QoQ_Pct_Change', 'YoY_Pct_Change', 'LineDescription']]
    
    return result
