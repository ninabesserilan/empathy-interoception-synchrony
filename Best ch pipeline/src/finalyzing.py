import numpy as np
import pandas as pd
from typing import Literal
from generate_refined_channels import fill_missing_peaks
from identifying_missing_peaks import analyze_missing_peaks


def create_final_data_dict(data :dict, ch_selection_dict: dict,
                            age: Literal['9', '18'],
                            participant: Literal['mom', 'infant'],
                           condition: Literal['chair', 'hammer', 'neutral'],
                           infant_ibis_th: int = 600,
                           mom_ibis_th: int = 1000, 
                           median_ibis_percantage_th: float = 1.0, 
                           tasks: list[Literal['freeplay', 'distress', 'reunion']] = None):
    """
    Create a unified dictionary with refined best channel data and original data.
    Loops over all tasks (distress/freeplay/reunion) for one participant × condition.
    Output structure: final_dict[task] → refined + original data
    """
    if age == '18' and condition == 'neutral':
        raise ValueError("Condition 'neutral' is only available for age 9.")

    long_ibi_threshold = infant_ibis_th if participant == 'infant' else mom_ibis_th
    final_dict = {}

    if age == '18':
        if tasks is None:
            tasks = ['freeplay', 'distress', 'reunion']
            print(f"No tasks specified, defaulting to all tasks: {tasks}")

        for task in tasks:
            print(f"\n--- Processing task: '{task}' ---")
            data_slice       = data[participant][condition][task]
            ch_selection     = ch_selection_dict[task]['dict']
            exclude_subs = ch_selection_dict[task]['excluded_subs']
            final_dict[task] = _process_single_slice(
                participant, data_slice, ch_selection,exclude_subs,
                long_ibi_threshold, median_ibis_percantage_th
            )

    else:  # age == '9'
        data_slice            = data[participant][condition]
        ch_selection          = ch_selection_dict[condition]['dict']
        exclude_subs = ch_selection_dict[condition]['excluded_subs']

        final_dict[condition] = _process_single_slice(
            participant, data_slice, ch_selection,exclude_subs,
            long_ibi_threshold, median_ibis_percantage_th
        )

    return final_dict
    

def _process_single_slice(
    participant: Literal['infant', 'mom'],
    data_slice: dict,
    ch_selection: dict,
    exclude_subs: dict,
    long_ibi_threshold: int,
    median_ibis_percantage_th: float
) -> dict:
    """
    Core processing for a single data slice (task for age 18, condition for age 9).
    Expects:
        data_slice   : {subj_id: {ch_name: {'peaks': ..., 'ibi': ...}}}
        ch_selection : {subj_id: {best_channel, ...}}
    """
    # --- Build peaks/ibis dicts ---
    peaks_data_dict = {}
    ibis_data_dict  = {}
    for subj_id, subj_data in data_slice.items():
        peaks_data_dict[subj_id] = {participant: {}}
        ibis_data_dict[subj_id]  = {participant: {}}
        for ch_name, ch_data in subj_data.items():
            peaks_data_dict[subj_id][participant][ch_name] = {'data': ch_data['peaks']}
            ibis_data_dict[subj_id][participant][ch_name]  = {'data': ch_data['ibi']}

    refined_dict = {}
    # --- 1. Analyze & fill missing peaks ---
    missing_peaks_dict, exclude_subs_dict = analyze_missing_peaks(
        participant, peaks_data_dict, ibis_data_dict, ch_selection,
        median_ibis_percantage_th, exclude_subs, refined_best_ch=True)
    
    new_best_ch_peaks_dict = fill_missing_peaks(
        participant, peaks_data_dict, ch_selection,
        missing_peaks_dict, median_ibis_percantage_th
    )
    refined_dict['new_peaks_data'] = new_best_ch_peaks_dict

    # --- 2. New IBIs ---
    new_best_ch_ibis_data = {'data': {}}
    for subj, peaks_series in new_best_ch_peaks_dict['data'].items():
        new_best_ch_ibis_data['data'][subj] = np.diff(peaks_series.values)
    refined_dict['new_ibis_data'] = new_best_ch_ibis_data

    # --- 3. New IBI stats ---
    new_best_ch_ibis_stats = {}
    for subj, ibis in new_best_ch_ibis_data['data'].items():
        length_best         = len(ibis)
        peaks_best          = new_best_ch_peaks_dict['data'][subj]
        last_peak_time_best = peaks_best.iloc[-1] if length_best > 0 else np.nan

        new_best_ch_ibis_stats[subj] = {
            'best_channel':       ch_selection[subj]['best_channel'],
            'last_peak_ts':       last_peak_time_best,
            'session_length_sec': last_peak_time_best / 500,
            'length_ibis_ts':     length_best,
            'median':             np.median(ibis) if length_best > 0 else np.nan,
            'mean':               np.mean(ibis)   if length_best > 0 else np.nan,
            'sdrr':               np.std(ibis, ddof=1) if length_best > 1 else np.nan,
            'long_ibi_count':     int(np.sum(ibis > long_ibi_threshold)) if length_best > 0 else 0
        }

    refined_dict['new_ibis_stats']            = new_best_ch_ibis_stats
    refined_dict['excluded_subs']             = exclude_subs_dict
    refined_dict['original_data_all_channels'] = {
        'peaks_data': peaks_data_dict,
        'ibis_data':  ibis_data_dict,
        'ibis_stats': ch_selection
    }

    return refined_dict
