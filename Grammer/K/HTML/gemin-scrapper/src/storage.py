import pandas as pd
import os
from . import config
import logging

logger = logging.getLogger(__name__)

def save_to_csv(data_list, filename="results.csv"):
    if not data_list:
        logger.warning("No data to save.")
        return

    filepath = os.path.join(config.DATA_DIR, filename)
    
    try:
        df = pd.DataFrame(data_list)
        
        # Append if file exists, write new if not
        if os.path.exists(filepath):
            df.to_csv(filepath, mode='a', header=False, index=False)
        else:
            df.to_csv(filepath, mode='w', header=True, index=False)
            
        logger.info(f"💾 Saved {len(data_list)} records to {filepath}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save data: {e}")