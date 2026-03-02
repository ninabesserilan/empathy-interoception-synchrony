import numpy as np
from typing import Literal



# -----------------------------
# Analyze missing peaks of the best ibis ch
# -----------------------------

def analyze_missing_peaks(participant: Literal['infant', 'mom'], peaks_data_dict, ibis_sub_data, ch_selection_dict: dict, 
                          median_ibis_percantage_th:float, refined_best_ch:bool =True):
    """
    Analyze missing peaks in the best IBI channel per subject compared to other channels.

    Returns:
    - report: dict keyed by subject, with missing peak info per subject
    """
    exclude_subs = {}
    report = {}
    
    for subj_id, sub_data in ibis_sub_data.items():
        sub_peak_data = (peaks_data_dict[subj_id]).get(participant, {})
        sub_ibi_data = (ibis_sub_data[subj_id]).get(participant, {})

        best_ch = ch_selection_dict[subj_id]['best_channel']
        if not best_ch:
            print(f"No best_channel for {subj_id}, skipping.")
            continue

        best_ch_ibi_data = sub_ibi_data.get(best_ch, {}).get('data', [])
        best_ch_peak_data = sub_peak_data.get(best_ch, {}).get('data', [])


        if best_ch_peak_data is None or  len(best_ch_peak_data)<2:
            excluding_reason = f"No peak data for best channel {best_ch}"
            print(f"Warning: {excluding_reason}")
            exclude_subs[subj_id] = excluding_reason
            continue   # skip if no data for best channel

        # Validate IBI matches difference of peaks
        inferred_ibi = np.diff(best_ch_peak_data)
        min_len = min(len(best_ch_ibi_data), len(inferred_ibi))
        if not np.allclose(best_ch_ibi_data[:min_len], inferred_ibi[:min_len], atol=1e-3):
            excluding_reason = f'IBI data for best channel {best_ch} does not match peak differences'
            print(f"Warning: {excluding_reason}")
            exclude_subs[subj_id] = excluding_reason
            continue

        missing_peaks = analyze_missing_peaks_intervals(ch_selection_dict[subj_id], subj_id, sub_peak_data, median_ibis_percantage_th, refined_best_ch)
        
        report[subj_id] = missing_peaks
    
    return report, exclude_subs

def analyze_missing_peaks_intervals(sub_ch_selection_dict: dict, subj_id, peaks_channels: dict, median_ibis_percantage_th: float, refined_best_ch: bool):
    """
    Identify missing peaks in other channels relative to the best channel.

    Parameters:
    - best_ch_peak_data: list/array of peaks of the best channel
    - peaks_channels: dict of other channels' peaks
    - best_ch: name of best channel
    - refined_best_ch: bool
        If True, only use core peaks (before_start, after_end, important_peaks) without extensions.

    Returns:
    - missing_peaks_report: dict keyed by interval or 'before_start'/'after_end'
    """
    best_ch = sub_ch_selection_dict['best_channel']
    medium_ch = sub_ch_selection_dict['medium_channel']
    worst_ch = sub_ch_selection_dict['worst_channel']

    missing_peaks_report = {}

    best_peaks = np.array(peaks_channels[best_ch]['data'])

    if len(best_peaks) == 0:
        print(f"DEBUG: best_peaks is empty for {subj_id}!")
        print(f"  best_ch: {best_ch}")
        print(f"  peaks_channels keys: {list(peaks_channels.keys())}")
        print(f"  peaks_channels[best_ch]: {peaks_channels.get(best_ch)}")
        return {}

    best_ibis = np.diff(best_peaks)

    median_ibi = sub_ch_selection_dict['median_best']
    threshold = median_ibi * median_ibis_percantage_th

    # Prepare dicts for medium & worst

    other_channels = {
    'medium': {medium_ch: np.array(peaks_channels.get(medium_ch, {}).get('data', []))},
    'worst': {worst_ch: np.array(peaks_channels.get(worst_ch, {}).get('data', []))},
}

    # --- Peaks before the first peak ---

    start_time = best_peaks[0]
    for ch_type, ch_dict in other_channels.items():
        for ch_name, ch_peaks in ch_dict.items():
            before_start_peaks = ch_peaks[ch_peaks <= start_time - threshold]
            if len(before_start_peaks) > 0: # For debuging, if refined_best_ch = False, the code expands each early peak to include its neighboring peak
                peaks_to_add = before_start_peaks if refined_best_ch else sorted(
                    list(set(np.concatenate([
                        [p, ch_peaks[np.where(ch_peaks == p)[0][0] + 1]]
                        if np.where(ch_peaks == p)[0][0] < len(ch_peaks) - 1 else [p]
                        for p in before_start_peaks
                    ])))
                )
                missing_peaks_report.setdefault('before_start', {
                    'best_channel_peaks': [int(start_time)],
                    'other_channels': {'medium': {}, 'worst': {}}
                })
                missing_peaks_report['before_start']['other_channels'][ch_type][ch_name] = list(map(int, peaks_to_add))

    # --- Peaks after the last peak ---
    end_time = best_peaks[-1]
    for ch_type, ch_dict in other_channels.items():
        for ch_name, ch_peaks in ch_dict.items():
            after_end_peaks = ch_peaks[ch_peaks >= end_time + threshold]
            if len(after_end_peaks) > 0:
                peaks_to_add = after_end_peaks if refined_best_ch else sorted( # For debuging, if refined_best_ch = False, the code expands each early peak to include its neighboring peak
                    list(set(np.concatenate([
                        [ch_peaks[np.where(ch_peaks == p)[0][0] - 1], p]
                        if np.where(ch_peaks == p)[0][0] > 0 else [p]
                        for p in after_end_peaks
                    ])))
                )
                missing_peaks_report.setdefault('after_end', {
                    'best_channel_peaks': [int(end_time)],
                    'other_channels': {'medium': {}, 'worst': {}}
                })
                missing_peaks_report['after_end']['other_channels'][ch_type][ch_name] = list(map(int, peaks_to_add))

    # --- Missing peaks inside intervals ---
    for ibi_idx in range(len(best_ibis)):
        interval_start = best_peaks[ibi_idx]
        interval_end = best_peaks[ibi_idx + 1]
        missing_per_type = {'medium': {}, 'worst': {}}

        for ch_type, ch_dict in other_channels.items():
            for ch_name, ch_peaks in ch_dict.items():
                peaks_in_interval = ch_peaks[(ch_peaks > interval_start) & (ch_peaks < interval_end)]
                important_peaks = [
                    pt for pt in peaks_in_interval
                    if (pt - interval_start) > threshold and (interval_end - pt) > threshold
                ]

                if important_peaks:
                    if refined_best_ch:
                        extended_peaks = important_peaks
                    else:
                        extended_peaks = sorted(list(set( # For debuging, if refined_best_ch = False, the code expands each early peak to include its neighboring peak
                            np.concatenate([
                                [ch_peaks[np.where(ch_peaks == pt)[0][0] - 1], pt, ch_peaks[np.where(ch_peaks == pt)[0][0] + 1]]
                                if 0 < np.where(ch_peaks == pt)[0][0] < len(ch_peaks) - 1 else [pt]
                                for pt in important_peaks
                            ])
                        )))
                    missing_per_type[ch_type][ch_name] = list(map(int, extended_peaks))

        if any(missing_per_type[ch_type] for ch_type in missing_per_type):
            best_peaks_in_interval = [int(p) for p in best_peaks if interval_start <= p <= interval_end]
            missing_peaks_report[ibi_idx] = {
                'best_channel_peaks': best_peaks_in_interval,
                'other_channels': missing_per_type
            }

    return missing_peaks_report


