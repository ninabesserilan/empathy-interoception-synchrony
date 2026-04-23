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
    data_9, age='9', participant='infant', condition='chair', short_channel_pct=0.80
)

# Hammer condition —
results_9_hammer_infant = run_channel_selection(
    data_9, age='9', participant='infant', condition='hammer', short_channel_pct=0.80
)


results_9_neutral_infant = run_channel_selection(
    data_9, age='9', participant='infant', condition='neutral', short_channel_pct=0.80
)

# mom

# Chair condition 
results_9_chair_mom = run_channel_selection(
    data_9, age='9', participant='mom', condition='chair', short_channel_pct=0.80
)

# Hammer condition —
results_9_hammer_mom = run_channel_selection(
    data_9, age='9', participant='mom', condition='hammer', short_channel_pct=0.80
)


results_9_neutral_mom = run_channel_selection(
    data_9, age='9', participant='mom', condition='neutral', short_channel_pct=0.80
)

# # # ---- Insert missing peaks for best ibis channels and creat final dict with original and improved data---------------------------



chair_infant_final_dict = create_final_data_dict(
    data=data_9, ch_selection_dict=results_9_chair_infant,
    age='9', participant='infant', condition='chair', infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
)
hammer_infant_final_dict = create_final_data_dict(
    data=data_9, ch_selection_dict=results_9_hammer_infant,
    age='9', participant='infant', condition='hammer', infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
)

neutral_infant_final_dict = create_final_data_dict(
    data=data_9, ch_selection_dict=results_9_neutral_infant,
    age='9', participant='infant', condition='neutral', infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
)

chair_mom_final_dict = create_final_data_dict(
    data=data_9, ch_selection_dict=results_9_chair_mom,
    age='9', participant='mom', condition='chair', infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
)
hammer_mom_final_dict = create_final_data_dict(
    data=data_9, ch_selection_dict=results_9_hammer_mom,
    age='9', participant='mom', condition='hammer', infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
)

neutral_mom_final_dict = create_final_data_dict(
    data=data_9, ch_selection_dict=results_9_neutral_mom,
    age='9', participant='mom', condition='neutral', infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
)

# # # ---- save all data to a new pickle ---------------------------

all_final_data = {
    'infant': {
        'chair':  chair_infant_final_dict,
        'hammer': hammer_infant_final_dict,
        'neutral': neutral_infant_final_dict
    },
    'mom': {
        'chair':  chair_mom_final_dict,
        'hammer': hammer_mom_final_dict,
        'neutral': neutral_mom_final_dict
    }
}

# # ---- save all data to a new pickle ---------------------------


# ---- Save pickle ----
parent_dir = Path(__file__).resolve().parent.parent
output_path = parent_dir / 'all_final_data_9m.pkl'
with open(output_path, "wb") as f:
    pickle.dump(all_final_data, f)
print(f"Saved to {output_path}")

# ---- Build stats DataFrames ----
stats_rows          = []
original_stats_rows = []
excluded_rows       = []

for part, part_data in all_final_data.items():
    for condition, cond_data in part_data.items():
        # age 9: no task level — cond_data is {condition: refined_dict}
        slice_data = cond_data[condition]
        for subj, stats in slice_data['new_ibis_stats'].items():
            stats_rows.append({
                'participant': part, 'condition': condition,
                'subject_id': subj, **stats
            })
        for subj, stats in slice_data['original_data_all_channels']['ibis_stats'].items():
            original_stats_rows.append({
                'participant': part, 'condition': condition,
                'subject_id': subj, **stats
            })
        for subj, reason in slice_data['excluded_subs'].items():
            excluded_rows.append({
                'participant': part, 'condition': condition,
                'sub_id': subj, 'reason': reason
            })

df_all_stats      = pd.DataFrame(stats_rows)
df_original_stats = pd.DataFrame(original_stats_rows)
df_excluded       = pd.DataFrame(excluded_rows)

column_order_improved_ch = ['subject_id', 'participant', 'condition', 'best_channel',
                'session_length_sec', 'last_peak_ts', 'length_ibis_ts',
                'long_ibi_count', 'sdrr', 'mean', 'median']

df_all_stats = df_all_stats[column_order_improved_ch].sort_values('subject_id')


original_column_order = ['subject_id', 'participant', 'condition',
                         'best_channel', 'medium_channel', 'worst_channel',
                         'length_best', 'length_medium', 'length_worst',
                         'long_ibi_count_best', 'long_ibi_count_medium', 'long_ibi_count_worst',
                         'sdrr_best', 'sdrr_medium', 'sdrr_worst',
                         'mean_best', 'mean_medium', 'mean_worst',
                         'median_best', 'median_medium', 'median_worst']

df_original_stats = df_original_stats.reindex(columns=original_column_order).sort_values('subject_id')


# ---- Save Excel ----
for prefix, df in [('improved', df_all_stats), ('original', df_original_stats)]:
    output_path = parent_dir / f'{prefix}_best_channels_stat_9m.xlsx'
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for condition in ['chair', 'hammer', 'neutral']:
            for part in ['infant', 'mom']:
                sheet_name = f"{condition}_{part}"
                mask = (df['participant'] == part) & (df['condition'] == condition)
                df[mask].to_excel(writer, sheet_name=sheet_name, index=False)

        df_excluded.to_excel(writer, sheet_name='excluded_subs', index=False)

    print(f"Saved {output_path}")
