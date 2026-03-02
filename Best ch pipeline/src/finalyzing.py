import numpy as np
import pandas as pd
from typing import Literal
from generate_refined_channels import fill_missing_peaks
from identifying_missing_peaks import analyze_missing_peaks


def create_final_data_dict(
    participant: Literal['infant', 'mom'],
    data_dict: dict,            # data_18[participant][condition]
    ch_selection_dict: dict,    # results_18_chair_infant  → {task: {sub_id: ...}}
    infant_ibis_th=600, mom_ibis_th=1000, median_ibis_percantage_th=1.00
):
    """
    Create a unified dictionary with refined best channel data and original data.
    Loops over all tasks (distress/freeplay/reunion) for one participant × condition.
    Output structure: final_dict[task] → refined + original data
    """
    final_dict = {}
    long_ibi_threshold = infant_ibis_th if participant == 'infant' else mom_ibis_th

    for task, task_data in data_dict.items():

        # --- Build peaks/ibis dicts in the format expected by analyze_missing_peaks ---
        # Shape: {subj_id: {participant: {ch_name: {'data': ...}}}}
        peaks_data_dict = {}
        ibis_data_dict = {}
        for subj_id, subj_data in task_data.items():
            peaks_data_dict[subj_id] = {participant: {}}
            ibis_data_dict[subj_id]  = {participant: {}}
            for ch_name, ch_data in subj_data.items():
                peaks_data_dict[subj_id][participant][ch_name] = {'data': ch_data['peaks']}
                ibis_data_dict[subj_id][participant][ch_name]  = {'data': ch_data['ibi']}

        # print(peaks_data_dict)

        task_ch_selection = ch_selection_dict[task]['dict']  # {sub_id: {best_channel, median_best, ...}}
        refined_dict = {}
        # --- 1. Analyze & fill missing peaks ---
        missing_peaks_dict, exclude_subs_dict = analyze_missing_peaks(
            participant, peaks_data_dict, ibis_data_dict, task_ch_selection,
            median_ibis_percantage_th, refined_best_ch=True
        )

        new_best_ch_peaks_dict = fill_missing_peaks(
            participant, peaks_data_dict, task_ch_selection,
            missing_peaks_dict, median_ibis_percantage_th
        )
        refined_dict['new_peaks_data'] = new_best_ch_peaks_dict

        # --- 2. New IBIs ---
        new_best_ch_ibis_data = {'data': {}}
        for subj, peaks_series in new_best_ch_peaks_dict['data'].items():
            peaks_array = peaks_series.values
            new_best_ch_ibis_data['data'][subj] = np.diff(peaks_array)
        refined_dict['new_ibis_data'] = new_best_ch_ibis_data

        # --- 3. New IBI stats ---
        new_best_ch_ibis_stats = {}
        for subj, ibis in new_best_ch_ibis_data['data'].items():
            name_best           = task_ch_selection[subj]['best_channel']
            length_best         = len(ibis)
            median_best         = np.median(ibis) if length_best > 0 else np.nan
            mean_best           = np.mean(ibis)   if length_best > 0 else np.nan
            sdrr_best           = np.std(ibis, ddof=1) if length_best > 1 else np.nan
            long_ibi_count_best = int(np.sum(ibis > long_ibi_threshold) if length_best > 0 else 0)
            peaks_best          = new_best_ch_peaks_dict['data'][subj]
            last_peak_time_best   = peaks_best.iloc[-1] if len(peaks_best) > 0 else np.nan
            session_length_sec  = last_peak_time_best / 500

            new_best_ch_ibis_stats[subj] = {
                'best_channel':       name_best,
                'last_peak_ts':       last_peak_time_best,
                'session_length_sec': session_length_sec,
                'length_ibis_ts':     length_best,
                'median':             median_best,
                'mean':               mean_best,
                'sdrr':               sdrr_best,
                'long_ibi_count':     long_ibi_count_best
            }

        refined_dict['new_ibis_stats'] = new_best_ch_ibis_stats
        refined_dict['excluded_subs']  = exclude_subs_dict

        # --- 4. Original data (all channels) ---
        refined_dict['original_data_all_channels'] = {
            'peaks_data': peaks_data_dict,
            'ibis_data':  ibis_data_dict,
            'ibis_stats': task_ch_selection
        }

        final_dict[task] = refined_dict

    return final_dict