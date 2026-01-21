import pandas as pd
from pathlib import Path
import pickle

from data_loader import data_loader
from spline_interpolation import apply_gap_filling_to_data_dict

from spline_interpolation_2 import apply_gap_filling_to_data_dict_2


from prepare_sample_to_rsa import prepare_sample_for_analysis
from rsa_calculation import calculate_rsa

from excluded_subs_data import excluded_subs_data

import matplotlib.pyplot as plt
import numpy as np


ibis_pickle_path = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/Best ch pipeline/all data improved and original chs.pkl')

data_dict = data_loader(ibis_pickle_path)

parent_dir = Path(__file__).resolve().parent.parent

is_interpolation = True


if is_interpolation:

        interpolation_pickle_output_path = parent_dir / 'Improved best ch after interpolation.pkl'
        interpolation_pickle_output_path_2 = parent_dir / 'Improved best ch after interpolation_2.pkl'


        intrpolat_ibi = apply_gap_filling_to_data_dict(data_dict, factor=2, infant_ibis_th=600, 
                                   mom_ibis_th=1000, tension=0.2, save_path=interpolation_pickle_output_path)
        

        intrpolat_ibi_2 = apply_gap_filling_to_data_dict_2(data_dict, factor=2, infant_ibis_th=600, 
                                   mom_ibis_th=1000, tension=0.2, save_path=interpolation_pickle_output_path_2)

        
        
        sample_for_analyis = intrpolat_ibi
else:
        sample_for_analyis = data_dict

# valid_sample, excluded_subs = prepare_sample_for_analysis(sample_for_analyis, min_session_length_sec= 60 , min_sdrr = 200, is_interpolation = is_interpolation, missing_ibis_prop=0.20)
# rsa_dict, excluded_unmatched_subs = calculate_rsa(valid_sample, require_partner= True, ibi_value_th = 70000)

# toys_dyad_num = len(rsa_dict['toys'].keys())      
# notoys_dyad_num = len(rsa_dict['no_toys'].keys()) 

# # Building united excluded subs data frame

# if is_interpolation:
#        rsa_pickle_name = 'rsa_pickle_ibis_interpolation.pkl'
#        excluded_sub_name = "All excluded subs after ibis interpolation.xlsx"
# else:
#         rsa_pickle_name = 'rsa_pickle.pkl'
#         excluded_sub_name = "All excluded subs.xlsx"



# final_excluded_df_toys_infant,final_excluded_df_toys_mom, final_excluded_df_notoys_infant, final_excluded_df_notoys_mom = excluded_subs_data(excluded_subs, excluded_unmatched_subs, sample_for_analyis)
# pickle_path = parent_dir/rsa_pickle_name

# with open(pickle_path, "wb") as f:
#         pickle.dump(rsa_dict, f)

# print(f"All data saved to {pickle_path}")


# output_path_original = parent_dir / excluded_sub_name

# with pd.ExcelWriter(output_path_original, engine="openpyxl") as writer:
#     final_excluded_df_toys_infant.to_excel(writer, sheet_name="Infant_9m_Toys", index=True)
#     final_excluded_df_toys_mom.to_excel(writer, sheet_name="Mom_9m_Toys", index=True)
#     final_excluded_df_notoys_infant.to_excel(writer, sheet_name="Infant_9m_NoToys", index=True)
#     final_excluded_df_notoys_mom.to_excel(writer, sheet_name="Mom_9m_NoToys", index=True)


for key in sample_for_analyis['no_toys']['mom']['refined_best_channel_data']['ibis_after_interpolation']['data'].keys():

        after_interpolation = sample_for_analyis['no_toys']['mom']['refined_best_channel_data']['ibis_after_interpolation']['data'][key]
        after_interpolation_2 = intrpolat_ibi_2['no_toys']['mom']['refined_best_channel_data']['ibis_after_interpolation']['data'][key]

        # Plot 1 – version 1
        plt.figure()
        plt.plot(after_interpolation)
        plt.title(f'IBI interpolation – version 1 ({key})')
        plt.xlabel('IBI index')
        plt.ylabel('IBI (ms)')
        plt.tight_layout()
        plt.show()

        # Plot 2 – version 2
        plt.figure()
        plt.plot(after_interpolation_2)
        plt.title(f'IBI interpolation – version 2 ({key})')
        plt.xlabel('IBI index')
        plt.ylabel('IBI (ms)')
        plt.tight_layout()
        plt.show()
