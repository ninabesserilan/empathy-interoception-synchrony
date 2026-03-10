from pathlib import Path
import pandas as pd
import pickle

from data_loader import data_9
from channel_selection import run_channel_selection
from finalyzing import create_final_data_dict



# ---- best ibis channels selection  - df and dict with the statistics of the best, medium and worst channel for each subject in each group and condition---------------------------

# 9 months

#  infant

# Chair condition 
results_9_chair_infant = run_channel_selection(
    data_9, age='9_csv', participant='infant', condition='chair', short_channel_pct=0.75
)

# Hammer condition 
results_9_hammer_infant = run_channel_selection(
    data_9, age='9_csv', participant='infant', condition='hammer', short_channel_pct=0.75
)

# Neutral condition 
results_9_neutral_infant = run_channel_selection(
    data_9, age='9_csv', participant='infant', condition='neutral', short_channel_pct=0.75
)



# mom

# Chair condition 
results_9_chair_mom = run_channel_selection(
    data_9, age='9_csv', participant='mom', condition='chair', short_channel_pct=0.75
)

# Hammer condition 
results_9_hammer_mom = run_channel_selection(
    data_9, age='9_csv', participant='mom', condition='hammer', short_channel_pct=0.75
)


# Neutral condition 
results_9_neutral_mom = run_channel_selection(
    data_9, age='9_csv', participant='mom', condition='neutral', short_channel_pct=0.75
)


# # # # ---- Insert missing peaks for best ibis channels and creat final dict with original and improved data---------------------------


# chair_infant_final_dict = create_final_data_dict(
#     'infant',data_9['infant']['chair'],
#     results_18_chair_infant,
#     infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
# )
# hammer_infant_final_dict = create_final_data_dict(
#     'infant', data_9['infant']['hammer'],
#     results_18_hammer_infant,
#     infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
# )
# chair_mom_final_dict = create_final_data_dict(
#     'mom', data_9['mom']['chair'],
#     results_18_chair_mom,
#     infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
# )
# hammer_mom_final_dict = create_final_data_dict(
#     'mom', data_9['mom']['hammer'],
#     results_18_hammer_mom,
#     infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
# )

# # # ---- save all data to a new pickle ---------------------------

# all_final_data = {
#     'infant': {
#         'chair':  chair_infant_final_dict,
#         'hammer': hammer_infant_final_dict,
#     },
#     'mom': {
#         'chair':  chair_mom_final_dict,
#         'hammer': hammer_mom_final_dict,
#     }
# }

# # ---- Save pickle ----
# parent_dir = Path(__file__).resolve().parent.parent
# output_path = parent_dir / 'all_final_data_18m.pkl'
# with open(output_path, "wb") as f:
#     pickle.dump(all_final_data, f)
# print(f"Saved to {output_path}")

# # ---- Build stats DataFrames (one row per subject, tagged by condition + task) ----
# stats_rows = []
# excluded_rows = []

# for part, part_data in all_final_data.items():
#     for condition, cond_data in part_data.items():
#         for task, task_data in cond_data.items():
#             for subj, stats in task_data['new_ibis_stats'].items():
#                 stats_rows.append({
#                     'participant': part, 'condition': condition, 'task': task,
#                     'subject_id': subj, **stats
#                 })
#             for subj, reason in task_data['excluded_subs'].items():
#                 excluded_rows.append({
#                     'participant': part, 'condition': condition, 'task': task,
#                     'sub_id': subj, 'reason': reason
#                 })

# df_all_stats = pd.DataFrame(stats_rows)
# df_excluded  = pd.DataFrame(excluded_rows)

# column_order = ['participant', 'condition', 'task', 'subject_id', 'best_channel',
#                 'session_length_sec', 'last_peak_ts', 'length_ibis_ts',
#                 'long_ibi_count', 'sdrr', 'mean', 'median']
# df_all_stats = df_all_stats[column_order]

# # ---- Save Excel ----
# for condition in ['chair', 'hammer']:
#     output_path_new = parent_dir / f'improved_best_channels_stat_18m_{condition}.xlsx'
#     with pd.ExcelWriter(output_path_new, engine='openpyxl') as writer:
#         for task in ['distress', 'freeplay', 'reunion']:
#             for part in ['infant', 'mom']:
#                 sheet_name = f"{task}_{part}"
#                 mask = (df_all_stats['participant'] == part) & (df_all_stats['condition'] == condition) & (df_all_stats['task'] == task)
#                 df_all_stats[mask].to_excel(writer, sheet_name=sheet_name, index=False)
        
#         mask_excluded = df_excluded['condition'] == condition
#         df_excluded[mask_excluded].to_excel(writer, sheet_name='excluded_subs', index=False)
    
#     print(f"Saved {output_path_new}")
