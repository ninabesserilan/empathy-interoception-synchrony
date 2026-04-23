from pathlib import Path
import pandas as pd
import pickle

from data_loader import  data_18
from channel_selection import run_channel_selection
from finalyzing import create_final_data_dict



# ---- best ibis channels selection  - df and dict with the statistics of the best, medium and worst channel for each subject in each group and condition---------------------------

# 18 months

#  infant

# Chair condition — all tasks 
results_18_chair_infant = run_channel_selection(
    data_18, age='18', participant='infant', condition='chair', short_channel_pct=0.80
)

# Hammer condition — all tasks 
results_18_hammer_infant = run_channel_selection(
    data_18, age='18', participant='infant', condition='hammer', short_channel_pct=0.80
)

# mom

# Chair condition — all tasks 
results_18_chair_mom = run_channel_selection(
    data_18, age='18', participant='mom', condition='chair', short_channel_pct=0.80
)

# Hammer condition — all tasks 
results_18_hammer_mom = run_channel_selection(
    data_18, age='18', participant='mom', condition='hammer', short_channel_pct=0.80
)


# # ---- Insert missing peaks for best ibis channels and creat final dict with original and improved data---------------------------




chair_infant_final_dict = create_final_data_dict(
    data=data_18, ch_selection_dict=results_18_chair_infant,
    age='18', participant='infant', condition='chair', infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
)
hammer_infant_final_dict = create_final_data_dict(
    data=data_18, ch_selection_dict=results_18_hammer_infant,
    age='18', participant='infant', condition='hammer', infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
)
chair_mom_final_dict = create_final_data_dict(
    data=data_18, ch_selection_dict=results_18_chair_mom,
    age='18', participant='mom', condition='chair', infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
)
hammer_mom_final_dict = create_final_data_dict(
    data=data_18, ch_selection_dict=results_18_hammer_mom,
    age='18', participant='mom', condition='hammer', infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
)

# ---- save all data to a new pickle ---------------------------

all_final_data = {
    'infant': {
        'chair':  chair_infant_final_dict,
        'hammer': hammer_infant_final_dict,
    },
    'mom': {
        'chair':  chair_mom_final_dict,
        'hammer': hammer_mom_final_dict,
    }
}

# ---- Save pickle ----
parent_dir = Path(__file__).resolve().parent.parent
output_path = parent_dir / 'all_final_data_18m.pkl'
with open(output_path, "wb") as f:
    pickle.dump(all_final_data, f)
print(f"Saved to {output_path}")

# ---- Build stats DataFrames (one row per subject, tagged by condition + task) ----
stats_rows = []
original_stats_rows = []
excluded_rows = []

for part, part_data in all_final_data.items():
    for condition, cond_data in part_data.items():
        for task, task_data in cond_data.items():
            for subj, stats in task_data['new_ibis_stats'].items():
                stats_rows.append({
                    'participant': part, 'condition': condition, 'task': task,
                    'subject_id': subj, **stats
                })
            for subj, stats in task_data['original_data_all_channels']['ibis_stats'].items():
                original_stats_rows.append({
                    'participant': part, 'condition': condition, 'task': task,
                    'subject_id': subj, **stats
                })
            for subj, reason in task_data['excluded_subs'].items():
                excluded_rows.append({
                    'participant': part, 'condition': condition, 'task': task,
                    'sub_id': subj, 'reason': reason
                })

df_all_stats      = pd.DataFrame(stats_rows)
df_original_stats = pd.DataFrame(original_stats_rows)
df_excluded       = pd.DataFrame(excluded_rows)
column_order_improved_ch = ['subject_id', 'participant', 'condition', 'task', 'best_channel',
                'session_length_sec', 'last_peak_ts', 'length_ibis_ts',
                'long_ibi_count', 'sdrr', 'mean', 'median']


original_column_order = ['subject_id', 'participant', 'condition', 'task',
                         'best_channel', 'medium_channel', 'worst_channel',
                         'length_best', 'length_medium', 'length_worst',
                         'long_ibi_count_best', 'long_ibi_count_medium', 'long_ibi_count_worst',
                         'sdrr_best', 'sdrr_medium', 'sdrr_worst',
                         'mean_best', 'mean_medium', 'mean_worst',
                         'median_best', 'median_medium', 'median_worst']


df_all_stats = df_all_stats[column_order_improved_ch].sort_values('subject_id')


df_original_stats = df_original_stats[original_column_order].sort_values('subject_id')


# ---- Save Excel ----
for condition in ['chair', 'hammer']:
    for prefix, df in [('improved', df_all_stats), ('original', df_original_stats)]:
        output_path = parent_dir / f'{prefix}_best_channels_stat_18m_{condition}.xlsx'
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for task in ['distress', 'freeplay', 'reunion']:
                for part in ['infant', 'mom']:
                    sheet_name = f"{task}_{part}"
                    mask = (
                        (df['participant'] == part) &
                        (df['condition'] == condition) &
                        (df['task'] == task)
                    )
                    df[mask].to_excel(writer, sheet_name=sheet_name, index=False)

            mask_excluded = df_excluded['condition'] == condition
            df_excluded[mask_excluded].to_excel(writer, sheet_name='excluded_subs', index=False)

        print(f"Saved {output_path}")
