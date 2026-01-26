import pandas as pd
from pathlib import Path
import pickle

from data_loader import data_loader



from prepare_sample_to_rsa import prepare_sample_for_analysis
from rsa_calculation import calculate_rsa

from excluded_subs_data import excluded_subs_data

import matplotlib.pyplot as plt
import numpy as np



dic_for_rsa = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/Interpolate IBI data/after interpolation_Moritz.pkl')

parent_dir = Path(__file__).resolve().parent.parent


data_dict = data_loader(dic_for_rsa)

        
valid_sample, excluded_subs = prepare_sample_for_analysis(data_dict, min_session_length_sec= 60 , min_sdrr = 200, is_interpolation = True, missing_ibis_prop=0.20)

rsa_dict, excluded_unmatched_subs = calculate_rsa(valid_sample, require_partner= True, ibi_value_th = 70000)

toys_dyad_num = len(rsa_dict['toys'].keys())      
notoys_dyad_num = len(rsa_dict['no_toys'].keys()) 

# Building united excluded subs data frame

rsa_pickle_name = 'rsa_pickle.pkl'
excluded_sub_name = "All excluded subs after rsa.xlsx"


final_excluded_df_toys_infant,final_excluded_df_toys_mom, final_excluded_df_notoys_infant, final_excluded_df_notoys_mom = excluded_subs_data(excluded_subs, excluded_unmatched_subs, data_dict)
pickle_path = parent_dir/rsa_pickle_name

with open(pickle_path, "wb") as f:
        pickle.dump(rsa_dict, f)

print(f"All data saved to {pickle_path}")


output_path_original = parent_dir / excluded_sub_name

with pd.ExcelWriter(output_path_original, engine="openpyxl") as writer:
    final_excluded_df_toys_infant.to_excel(writer, sheet_name="Infant_9m_Toys", index=True)
    final_excluded_df_toys_mom.to_excel(writer, sheet_name="Mom_9m_Toys", index=True)
    final_excluded_df_notoys_infant.to_excel(writer, sheet_name="Infant_9m_NoToys", index=True)
    final_excluded_df_notoys_mom.to_excel(writer, sheet_name="Mom_9m_NoToys", index=True)


