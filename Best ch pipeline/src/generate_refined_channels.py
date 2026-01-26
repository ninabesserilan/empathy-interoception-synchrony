import numpy as np
import pandas as pd
from metrics import compute_metrics
from channel_selection import select_best_channel
from typing import Literal, List, Tuple



def fill_missing_peaks(
    participant: Literal['infant', 'mom'],
    peaks_data_dict: dict,
    ch_selection_dict: dict,
    missing_peaks_dict: dict,
    median_ibis_percantage_th:float
):
    new_best_ch_peaks = {'data': {}, 'source': {}}

    for subj, missing_data in missing_peaks_dict.items():
        #  Access best channel correctly
        best_ch = ch_selection_dict[subj]['best_channel']
        best_peaks = peaks_data_dict[subj][participant][best_ch]['data']
        best_ch_medain_ibis= ch_selection_dict[subj]['median_best']

        merge_tolerance_ms = best_ch_medain_ibis * median_ibis_percantage_th

        new_peaks = best_peaks.copy()
        new_sources = pd.Series([{ 'best': best_ch }] * len(new_peaks))

        if missing_data:
            for interval_idx, interval_data in missing_data.items():
                # --- Collect candidates from medium + worst ---
                new_peaks_candidates = []
                for ch_type in ['medium', 'worst']:
                    ch_type_peaks_dict = interval_data['other_channels'].get(ch_type, {})
                    for ch_name, ch_peaks in ch_type_peaks_dict.items():
                        for p in ch_peaks:
                            new_peaks_candidates.append((p, ch_type, ch_name))

                # --- Merge close ones ---
                merged_candidates = merge_close_peaks(new_peaks_candidates, merge_tolerance_ms)

                # --- Add merged peaks ---
                for p, ch_type, ch_name in merged_candidates:
                    # Only add the peak if it’s not already in new_peaks
                    if p not in new_peaks.values:
                        # Append the peak time to new_peaks
                        new_peaks = pd.concat([new_peaks, pd.Series([p])], ignore_index=True)
                        # Append a dict recording the source (channel type & name) to new_sources
                        new_sources = pd.concat(
                            [new_sources, pd.Series([{ch_type: ch_name}])],
                            ignore_index=True
                        )


        # --- Sort peaks and reorder sources to match chronological order ---
        # Get the indices that would sort new_peaks by time
        sorted_idx = np.argsort(new_peaks.values)

        # Reorder new_peaks and store in results for this subject
        new_best_ch_peaks['data'][subj] = new_peaks.iloc[sorted_idx].reset_index(drop=True)

        # Reorder the corresponding sources so they stay aligned with the peaks
        new_best_ch_peaks['source'][subj] = new_sources.iloc[sorted_idx].reset_index(drop=True)

    return new_best_ch_peaks


def merge_close_peaks(
    candidates: List[Tuple[int, str, str]],
    merge_tolerance_ms: float
) -> List[Tuple[int, str, str]]:
    """
    Merge peaks that occur within a given time tolerance, keeping the one
    from the higher-quality channel.

    Parameters
    ----------
    candidates : list of tuples
        Each element is peak_time, quality_label (channel type), channel_name
        Example: [(2626, 'medium', 'ch_0'), (2635, 'worst', 'ch_1')]
    merge_tolerance_ms : int
        Maximum time difference (in ms) between peaks to consider them duplicates.

    Returns
    -------
    merged_peaks : list of tuples
        Same format as input but with merged nearby peaks.
    """

    # Define priority (lower is better)
    QUALITY_PRIORITY = {'best': 0, 'medium': 1, 'worst': 2}

    # Sort by peak time
    candidates = sorted(candidates, key=lambda x: x[0])

    merged = []
    for p, ch_type, ch_name in candidates:
        if not merged:
            merged.append((p, ch_type, ch_name))
        else:
            last_p, last_quality, last_ch = merged[-1]
            # If close enough, keep the better one
            if abs(p - last_p) <= merge_tolerance_ms:
                if QUALITY_PRIORITY[ch_type] < QUALITY_PRIORITY[last_quality]:
                    merged[-1] = (p, ch_type, ch_name)
            else:
                merged.append((p, ch_type, ch_name))

    return merged
