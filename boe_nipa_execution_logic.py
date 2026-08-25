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
    
    # Construct API parameters strictly
    params = {
        "UserID": api_key,
        "method": "GetData",
        "DatasetName": config["dataset"],
        "TableName": meta["table_name"],
        "Frequency": meta["frequency"],
        "Year": f"LAST,{config['default_years']}",
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
    filtered_df = df[df['LineDescription'].str.lower().str.contains(target)]
    
    if filtered_df.empty:
        raise ValueError(f"Target description '{meta['target_description']}' not found in Table {meta['table_name']}.")
        
    # Format for LLM consumption (TimeSeries -> Value)
    return filtered_df[['TimePeriod', 'DataValue', 'LineDescription']].rename(
        columns={'TimePeriod': 'Date', 'DataValue': 'Value'}
    )