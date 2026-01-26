import argparse
import json
from pathlib import Path
import pandas as pd
import pickle
import openpyxl

from data_loader import ibis_toys_9m_infants_data, ibis_toys_9m_moms_data, ibis_no_toys_9m_infants_data, ibis_no_toys_9m_moms_data # ibis data- 9 month
from data_loader import peaks_toys_9m_infants_data, peaks_toys_9m_moms_data, peaks_no_toys_9m_infants_data, peaks_no_toys_9m_moms_data # peaks data- 9 month
from channel_selection import channel_selection
from finalyzing import create_final_data_dict
from save_all_to_pickle import save_all_final_data_pickle



# ---- best ibis channels selection  - df and dict with the statistics of the best, medium and worst channel for each subject in each group and condition---------------------------

df_ch_selection_infant_9m_toys, ch_selection_dict_infant_9m_toys = channel_selection(ibis_toys_9m_infants_data, "infant", short_channel_pct=0.80, infant_ibis_th =600, mom_ibis_th = 1000)
df_ch_selection_mom_9m_toys,ch_selection_dict_mom_9m_toys = channel_selection(ibis_toys_9m_moms_data, "mom", short_channel_pct=0.80, infant_ibis_th =600, mom_ibis_th = 1000)

df_ch_selection_infant_9m_no_toys, ch_selection_dict_infant_9m_no_toys = channel_selection(ibis_no_toys_9m_infants_data, "infant", short_channel_pct=0.80, infant_ibis_th =600, mom_ibis_th = 1000)
df_ch_selection_mom_9m_no_toys, ch_selection_dict_mom_9m_no_toys = channel_selection(ibis_no_toys_9m_moms_data, "mom", short_channel_pct=0.80,infant_ibis_th =600, mom_ibis_th = 1000)


# # # ---- Insert missing peaks for best ibis channels and creat final dict with original and improved data---------------------------

toys_infant_final_dict, toys_infant_df_new_ibis_stats, excluded_toys_infant = create_final_data_dict('infant',peaks_toys_9m_infants_data, ibis_toys_9m_infants_data, ch_selection_dict_infant_9m_toys,infant_ibis_th =600, mom_ibis_th = 1000, median_ibis_percantage_th = 1.00 )
toys_mom_final_dict, toys_mom_df_new_ibis_stats, excluded_toys_mom = create_final_data_dict('mom',peaks_toys_9m_moms_data, ibis_toys_9m_moms_data, ch_selection_dict_mom_9m_toys,infant_ibis_th =600, mom_ibis_th = 1000, median_ibis_percantage_th = 1.00 )

notoys_infant_final_dict, notoys_infant_df_new_ibis_stats, excluded_notoys_infant = create_final_data_dict('infant',peaks_no_toys_9m_infants_data, ibis_no_toys_9m_infants_data, ch_selection_dict_infant_9m_no_toys,infant_ibis_th =600, mom_ibis_th = 1000, median_ibis_percantage_th = 1.00 )
notoys_mom_final_dict, notoys_mom_df_new_ibis_stats, excluded_notoys_mom = create_final_data_dict('mom',peaks_no_toys_9m_moms_data, ibis_no_toys_9m_moms_data, ch_selection_dict_mom_9m_no_toys,infant_ibis_th =600, mom_ibis_th = 1000, median_ibis_percantage_th = 1.00 )

# # ---- save all data to a new pickle ---------------------------

parent_dir = Path(__file__).resolve().parent.parent

all_data_pickle_output_path = parent_dir / 'all data improved and original chs.pkl'
new_improved_channel_data = save_all_final_data_pickle(toys_infant_final_dict, toys_mom_final_dict, notoys_infant_final_dict, notoys_mom_final_dict, all_data_pickle_output_path)

# # # # ---- save original and new ibis+peaks ststs df  ---------------------------

### Original

output_path_original = parent_dir / "original_best_channels_stat.xlsx"

with pd.ExcelWriter(output_path_original, engine="openpyxl") as writer:
    df_ch_selection_infant_9m_toys.to_excel(writer, sheet_name="Infant_9m_Toys", index=False)
    df_ch_selection_mom_9m_toys.to_excel(writer, sheet_name="Mom_9m_Toys", index=False)
    df_ch_selection_infant_9m_no_toys.to_excel(writer, sheet_name="Infant_9m_NoToys", index=False)
    df_ch_selection_mom_9m_no_toys.to_excel(writer, sheet_name="Mom_9m_NoToys", index=False)

### New

output_path_new = parent_dir / "improved_best_channels_stat.xlsx"

# Handle excluded subs df
excluded_toys_infant['group'] = 'toys'
excluded_toys_mom['group'] =  'toys'
excluded_notoys_infant['group'] =  'no_toys'
excluded_notoys_mom['group'] = 'no_toys'

df_excluded = pd.concat([excluded_toys_infant, excluded_toys_mom, excluded_notoys_infant, excluded_notoys_mom], ignore_index=True)
df_excluded = df_excluded.set_index('sub_id')

# write all dfs to excel
with pd.ExcelWriter(output_path_new, engine="openpyxl") as writer:
    toys_infant_df_new_ibis_stats.to_excel(writer, sheet_name="Infant_9m_Toys", index=False)
    toys_mom_df_new_ibis_stats.to_excel(writer, sheet_name="Mom_9m_Toys", index=False)
    notoys_infant_df_new_ibis_stats.to_excel(writer, sheet_name="Infant_9m_NoToys", index=False)
    notoys_mom_df_new_ibis_stats.to_excel(writer, sheet_name="Mom_9m_NoToys", index=False)
    df_excluded.to_excel(writer, sheet_name= 'excluded subs', index=True)


