import numpy as np
import pandas as pd
from typing import Literal
from generate_refined_channels import fill_missing_peaks
from identifying_missing_peaks import analyze_missing_peaks
import pickle


def create_final_data_dict(
    participant: Literal['infant', 'mom'],
    peaks_data_dict: dict,
    ibis_data_dict: dict,
    ch_selection_dict: dict,
    infant_ibis_th =600, mom_ibis_th = 1000, mean_ibis_percantage_th = 0.80
):
    """
    Create a unified dictionary with refined best channel data and original data.
    """
    final_dict = {}

    # --- 1. Refined best channel data ---
    refined_dict = {}


    missing_peaks_dict, exclude_subs_dict = analyze_missing_peaks(participant, peaks_data_dict, ibis_data_dict, ch_selection_dict, mean_ibis_percantage_th, refined_best_ch= True)
    # 1.1 New peaks data
    new_best_ch_peaks_dict = fill_missing_peaks(
        participant,
        peaks_data_dict,
        ch_selection_dict,
        missing_peaks_dict,mean_ibis_percantage_th)


    refined_dict['new_peaks_data'] = new_best_ch_peaks_dict
    # Thresholds per participant type

    if participant == 'infant':
        long_ibi_threshold = infant_ibis_th
    else:
        long_ibi_threshold = mom_ibis_th

    # 1.2 New IBIs data
    new_best_ch_ibis_data = {'data': {}}
    for subj, peaks_series in new_best_ch_peaks_dict['data'].items():
        peaks_array = peaks_series.values  # convert Series to array
        ibis_array = np.diff(peaks_array)
        new_best_ch_ibis_data['data'][subj] = ibis_array
    refined_dict['new_ibis_data'] = new_best_ch_ibis_data

    # 1.3 New IBIs statistics
    new_best_ch_ibis_stats = {}
    for subj, ibis in new_best_ch_ibis_data['data'].items():

        name_best = ch_selection_dict[subj]['best_channel']
        length_best = len(ibis)
        median_best = np.median(ibis) if length_best > 0 else np.nan
        mean_best = np.mean(ibis) if length_best > 0 else np.nan
        sdrr_best = np.std(ibis, ddof=1) if length_best > 1 else np.nan
        long_ibi_count_best = np.sum(ibis > long_ibi_threshold) if length_best > 0 else 0
        peaks_best = new_best_ch_peaks_dict['data'][subj]
        last_peak_ms_best = peaks_best.iloc[-1] if len(peaks_best) > 0 else np.nan
        session_lenght_sec = last_peak_ms_best/1000

        new_best_ch_ibis_stats[subj] = {
            'best_channel': name_best,
            'last_peak_ms':last_peak_ms_best,
            'session_lenght_sec': session_lenght_sec,
            'length_ibis_ts': length_best,
            'median': median_best,
            'mean': mean_best,
            'sdrr': sdrr_best,
            'long_ibi_count': long_ibi_count_best
        }

    refined_dict['new_ibis_stats'] = new_best_ch_ibis_stats
    refined_dict['excluded_subs'] = exclude_subs_dict

    final_dict['refined_best_channel_data'] = refined_dict



    # 1.4 Create dfs from dicts 

    # 1.4.1 New stat df
    df_new_ibis_stats = pd.DataFrame.from_dict(
        refined_dict['new_ibis_stats'], orient='index'
    ).reset_index().rename(columns={'index': 'subject_id'})

    # Reorder columns as desired
    column_order = ["subject_id", "best_channel", "session_lenght_sec", "last_peak_ms", "length_ibis_ts", "long_ibi_count", 
                    "sdrr",  "mean", "median"]

    # Keep any extra columns at the end
    extra_cols = [c for c in df_new_ibis_stats.columns if c not in column_order]
    df_new_ibis_stats = df_new_ibis_stats[column_order + extra_cols]

    # # 1.4.2 New ecluded subjects df
    df_excluded_subs = pd.DataFrame(list(exclude_subs_dict.items()), columns=['sub_id', 'reason'])
    df_excluded_subs['participant'] = participant

    # --- 2. Original data all channels ---
    final_dict['original_data_all_channels'] = {
        'peaks_data': peaks_data_dict,
        'ibis_data': ibis_data_dict,
        'ibis_stats': ch_selection_dict
    }



    return final_dict, df_new_ibis_stats, df_excluded_subs






