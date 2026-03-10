from metrics import compute_metrics
from ranking import rank_channels
from typing import Literal
import numpy as np
import pandas as pd


def _validate_ibi_channel(subj_id, ch_key, ibis, peaks_raw):
    """Validate IBIs: check for negatives and verify against peak differences."""
    neg_mask = ibis < 0
    if neg_mask.any():
        print(f"  WARNING: Subject '{subj_id}', channel '{ch_key}' — "
              f"{neg_mask.sum()} negative IBI value(s) found: {ibis[neg_mask]}")

    if peaks_raw is not None:
        computed = np.diff(np.array(peaks_raw, dtype=float))
        if len(computed) != len(ibis):
            print(f"  WARNING: Subject '{subj_id}', channel '{ch_key}' — "
                  f"length mismatch: np.diff(peaks)={len(computed)}, ibi={len(ibis)}")
        elif not np.allclose(computed, ibis, atol=1):
            diff = np.abs(computed - ibis)
            print(f"  WARNING: Subject '{subj_id}', channel '{ch_key}' — "
                  f"ibi != np.diff(peaks), max diff={diff.max():.2f}")
    else:
        print(f"  WARNING: Subject '{subj_id}', channel '{ch_key}' — "
              f"no peaks found to verify ibi")


def extract_ibis_channels(data: dict,
                           age: Literal['9', '18', '9_csv'],
                           participant: Literal['mom', 'infant'],
                           condition: Literal['chair', 'hammer', 'neutral'],
                           task: Literal['freeplay', 'distress', 'reunion'] = None) -> tuple[dict, dict]:
    """
    Extract IBI channels into the format expected by channel_selection:
        { subj_id: { participant: { ch_key: { 'data': np.ndarray } } } }

    Age 18: data[participant][condition][task][subj_id][ch_key]['ibi']       → ndarray
    Age 9:  data[participant][condition][subj_id][ch_key]['ibi']['samples']  → list

    Note: 'neutral' condition is only available for age 9.

    Returns: (data_dict, exclude_subs)
    """
    if age == '18' and condition == 'neutral':
        raise ValueError("Condition 'neutral' is only available for age 9.")

    if age == '18':
        if task is None:
            raise ValueError("task must be specified for age 18 data.")
        subj_level = data[participant][condition][task]
    else:
        subj_level = data[participant][condition]

    data_dict = {}
    exclude_subs = {}

    for subj_id, subj_data in subj_level.items():
        ch_dict = {}

        if age == '9_csv':
            ibi_channels = subj_data.get('ibi', {})
            peaks_channels = subj_data.get('peaks', {})

            if not ibi_channels:
                print(f"  WARNING: Subject '{subj_id}' — no IBI data found, skipping subject.")
                exclude_subs[subj_id] = "No IBI data in source — subject skipped at extraction"
                continue

            for ch_key, raw in ibi_channels.items():
                if not ch_key.startswith('ch'):
                    continue
                ibis = np.atleast_1d(np.array(raw, dtype=int))
                peaks_raw = peaks_channels.get(ch_key, None)
                _validate_ibi_channel(subj_id, ch_key, ibis, peaks_raw)
                ch_dict[ch_key] = {'data': ibis}

        else:  # age '9' and '18'
            for ch_key, ch_data in subj_data.items():
                if not ch_key.startswith('ch'):
                    continue
                raw = ch_data.get('ibi', {}).get('samples', None) if age == '9' else ch_data.get('ibi', None)
                if raw is None:
                    print(f"  WARNING: Subject '{subj_id}', channel '{ch_key}' — IBI data missing, skipping channel.")
                    continue
                ibis = np.atleast_1d(np.array(raw, dtype=int))
                
                # ← fix here: peaks are inside ch_data, not at subj_data level
                peaks_raw = ch_data.get('peaks', None) if age == '18' else subj_data.get('peaks', {}).get(ch_key, None)
                
                _validate_ibi_channel(subj_id, ch_key, ibis, peaks_raw)
                ch_dict[ch_key] = {'data': ibis}

        data_dict[subj_id] = {participant: ch_dict}

    return data_dict, exclude_subs


def select_best_channel(ibis_channels, participant: Literal['mom', 'infant'],
                        short_channel_pct: float, weights=None,
                        infant_ibis_th=600, mom_ibis_th=1000):
    """
    Select the best channel for a participant, keeping invalid (too short) channels
    but ranking them automatically as the worst.
    """
    n_ibis = {ch: len(np.atleast_1d(ibis)) for ch, ibis in ibis_channels.items()}
    max_len = max(n_ibis.values()) if n_ibis else 0
    valid_flags = {ch: (n_ibis[ch] >= short_channel_pct * max_len) for ch in n_ibis}

    metrics_per_ch = {}
    for ch in ibis_channels:
        metrics = compute_metrics(ibis_channels[ch], participant, infant_ibis_th, mom_ibis_th)
        metrics['length'] = n_ibis[ch]
        metrics['invalid'] = not valid_flags[ch]
        metrics_per_ch[ch] = metrics

    invalid_channels = [ch for ch, m in metrics_per_ch.items() if m.get('invalid', False)]
    valid_channels = [ch for ch in metrics_per_ch.keys() if ch not in invalid_channels]

    best_ch, weighted_ranks, total_ranks = rank_channels(
        metrics_per_ch, invalid_channels, valid_channels, weights
    )

    return best_ch, {
        "metrics": metrics_per_ch,
        "ranks": weighted_ranks,
        "total_ranks": total_ranks
    }


def channel_selection(data_dict: dict, participant: Literal['mom', 'infant'],
                      age: Literal['9', '18', '9_csv'], short_channel_pct: float,
                      weights=None, infant_ibis_th=600, mom_ibis_th=1000):
    """
    Build a summary DataFrame with channels ordered by rank (best → medium → worst),
    and columns ordered by parameter type: length → median → sdrr → long_ibi_count → mean.
    """
    data_dic = {}

    for subj_id, subj_data in data_dict.items():
        sub_data = subj_data.get(participant, {})

        ibis_channels = {}
        for ch_key in sub_data.keys():
            if 'ch' in ch_key and 'data' in sub_data[ch_key]:
                ibis_channels[ch_key] = sub_data[ch_key]['data']

        best_ch, results = select_best_channel(
            ibis_channels, participant, short_channel_pct, weights, infant_ibis_th, mom_ibis_th
        )
        row = {"subject_id": subj_id}

        if results is None:
            row.update({"best_channel": None, "medium_channel": None, "worst_channel": None})
            data_dic[subj_id] = row
            continue

        sorted_channels = sorted(results["total_ranks"].items(), key=lambda x: x[1])
        channel_order = [ch for ch, _ in sorted_channels]

        labels = ["best", "medium", "worst"]
        for i, label in enumerate(labels):
            row[f"{label}_channel"] = channel_order[i] if i < len(channel_order) else None

        for i, label in enumerate(labels):
            if i >= len(channel_order):
                continue
            ch = channel_order[i]
            metrics = results["metrics"][ch]
            ibis_vals = np.atleast_1d(ibis_channels[ch]).astype(int)
            row[f"length_{label}"] = int(len(ibis_vals))
            row[f"median_{label}"] = np.nanmedian(ibis_vals)
            row[f"sdrr_{label}"] = metrics.get("sdrr", np.nan)
            long_ibi = metrics.get("long_ibi_count")
            row[f"long_ibi_count_{label}"] = int(long_ibi) if (long_ibi is not None and not np.isnan(long_ibi)) else None
            row[f"mean_{label}"] = np.nanmean(ibis_vals)

        data_dic[subj_id] = row

    data_dic = dict(sorted(data_dic.items()))

    df = pd.DataFrame(list(data_dic.values()))

    column_order = ["subject_id",
                    "best_channel", "medium_channel", "worst_channel",
                    "length_best", "length_medium", "length_worst",
                    "long_ibi_count_best", "long_ibi_count_medium", "long_ibi_count_worst",
                    "sdrr_best", "sdrr_medium", "sdrr_worst",
                    "mean_best", "mean_medium", "mean_worst",
                    "median_best", "median_medium", "median_worst"]

    extra_cols = [c for c in df.columns if c not in column_order]
    df = df[column_order + extra_cols]
    int_cols = [c for c in df.columns if c.startswith('length_') or c.startswith('long_ibi_count_')]
    df[int_cols] = df[int_cols].astype('Int64')
    df.set_index('subject_id', inplace=True)

    return df, data_dic


def run_channel_selection(data: dict,
                           age: Literal['9', '18', '9_csv'],
                           participant: Literal['mom', 'infant'],
                           condition: Literal['chair', 'hammer', 'neutral'],
                           short_channel_pct: float,
                           weights=None,
                           infant_ibis_th: int = 600,
                           mom_ibis_th: int = 1000,
                           tasks: list[Literal['freeplay', 'distress', 'reunion']] = None):
    """
    Main entry point for channel selection across both age groups.

    Age 9:  no task level → returns { condition: {'df': df, 'dict': data_dic, 'excluded_subs': exclude_subs} }
    Age 18: has task level → returns { task: {'df': df, 'dict': data_dic, 'excluded_subs': exclude_subs}, ... }

    Note: 'neutral' condition is only available for age 9.
    """
    if age == '18' and condition == 'neutral':
        raise ValueError("Condition 'neutral' is only available for age 9.")

    results = {}

    if age == '18':
        if tasks is None:
            tasks = ['freeplay', 'distress', 'reunion']
            print(f"No tasks specified, defaulting to all tasks: {tasks}")

        for task in tasks:
            print(f"\n--- Processing task: '{task}' ---")
            data_dict, exclude_subs = extract_ibis_channels(data, age, participant, condition, task=task)
            df, data_dic = channel_selection(
                data_dict, participant, age, short_channel_pct,
                weights, infant_ibis_th, mom_ibis_th
            )
            results[task] = {'df': df, 'dict': data_dic, 'excluded_subs': exclude_subs}

    else:
        data_dict, exclude_subs = extract_ibis_channels(data, age, participant, condition)
        df, data_dic = channel_selection(
            data_dict, participant, age, short_channel_pct,
            weights, infant_ibis_th, mom_ibis_th
        )
        results[condition] = {'df': df, 'dict': data_dic, 'excluded_subs': exclude_subs}

    return results