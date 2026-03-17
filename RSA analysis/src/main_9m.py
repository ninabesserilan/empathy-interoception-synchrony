import pandas as pd
from pathlib import Path
import pickle

from data_loader import data_loader



from prepare_sample_to_rsa import prepare_sample_for_analysis
from rsa_calculation import calculate_rsa

from excluded_subs_data import excluded_subs_data

import matplotlib.pyplot as plt
import numpy as np



dic_for_rsa_9m = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Interpolate IBI data/after interpolation_9m.pkl')



parent_dir = Path(__file__).resolve().parent.parent


data_dict_9 = data_loader(dic_for_rsa_9m)

        
valid_sample, excluded_subs = prepare_sample_for_analysis(data_dict_9,'9', min_session_length_sec= 60 , min_sdrr = 200, is_interpolation = True, missing_ibis_prop=0.20)

rsa_dict, excluded_unmatched_subs = calculate_rsa(valid_sample, '9', require_partner= True, ibi_value_th = 70000)

# ---- RSA pickle ----
pickle_path = parent_dir / 'rsa_pickle_9m.pkl'
with open(pickle_path, "wb") as f:
    pickle.dump(rsa_dict, f)
print(f"All data saved to {pickle_path}")

# ---- Excluded subs Excel (single file, 6 sheets) ----
excluded_dfs = excluded_subs_data(excluded_subs, excluded_unmatched_subs, data_dict_9)

output_path = parent_dir / 'excluded_subs_9m.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    for condition in ['chair', 'hammer', 'neutral']:
        for participant in ['infant', 'mom']:
            sheet_name = f"{condition}_{participant}"
            excluded_dfs[participant][condition][condition].to_excel(writer, sheet_name=sheet_name, index=True)

print(f"Saved {output_path}")
