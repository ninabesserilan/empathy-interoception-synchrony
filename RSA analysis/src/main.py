import pandas as pd
from pathlib import Path
import pickle

from data_loader import data_loader



from prepare_sample_to_rsa import prepare_sample_for_analysis
from rsa_calculation import calculate_rsa

from excluded_subs_data import excluded_subs_data

import matplotlib.pyplot as plt
import numpy as np



dic_for_rsa = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Interpolate IBI data/after interpolation_Moritz.pkl')

parent_dir = Path(__file__).resolve().parent.parent


data_dict = data_loader(dic_for_rsa)

        
valid_sample, excluded_subs = prepare_sample_for_analysis(data_dict, min_session_length_sec= 60 , min_sdrr = 200, is_interpolation = True, missing_ibis_prop=0.20)

rsa_dict, excluded_unmatched_subs = calculate_rsa(valid_sample, require_partner= True, ibi_value_th = 70000)

# ---- RSA pickle ----
pickle_path = parent_dir / 'rsa_pickle.pkl'
with open(pickle_path, "wb") as f:
    pickle.dump(rsa_dict, f)
print(f"All data saved to {pickle_path}")

# ---- Excluded subs Excel (one per condition) ----
excluded_dfs = excluded_subs_data(excluded_subs, excluded_unmatched_subs, data_dict)

for condition in ['chair', 'hammer']:
    output_path = parent_dir / f'excluded_subs_{condition}.xlsx'
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for task in ['distress', 'freeplay', 'reunion']:
            for participant in ['infant', 'mom']:
                sheet_name = f"{task}_{participant}"
                excluded_dfs[participant][condition][task].to_excel(writer, sheet_name=sheet_name, index=True)
    print(f"Saved {output_path}")
