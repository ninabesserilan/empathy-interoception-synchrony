from typing import List
from sync import rsa_magnitude, rsa_per_epoch, rsa_time_series, epochs_synchrony, cross_correlation_zlc, multimodal_synchrony
import numpy as np
import pandas as pd
import neurokit2 as nk
import numpy as np
from pathlib import Path
import pickle

def validate_array(arr: List[pd.Series]):
    for val in arr:
        if np.isinf(val) or np.isnan(val):
            print("ERROROROROROR")

def clean_array(arr: List[pd.Series], sub_id, participant, ibi_value_th):
    # Flatten arr in case it contains pd.Series elements
    values = []
    for x in arr:
        if isinstance(x, pd.Series):
            values.extend(x.tolist())
        else:
            values.append(x)

    # Count values above the threshold
    num_above = sum(v >= ibi_value_th for v in values)

    if num_above > 0:
        print(f" {num_above} values >= {ibi_value_th} detected for {sub_id}, {participant}")
    
    return list(filter(lambda n: n < ibi_value_th, arr))


def calculate_rsa(valid_sample: dict, ibi_value_th: int, require_partner=True):
    excluded_summary = {}

    if require_partner:
        sample_to_analysis, excluded_summary = exclude_unmatched_pairs(valid_sample)
    else:
        sample_to_analysis = valid_sample

    rsa_dict = {}


    for condition, cond_data in sample_to_analysis.items():
        for task, task_data in cond_data.items():
            for participant, sub_dict in task_data.items():
                if condition not in rsa_dict:
                    rsa_dict[condition] = {}
                if task not in rsa_dict[condition]:
                    rsa_dict[condition][task] = {}

                for sub_id, ts in sub_dict.items():
                    if sub_id not in rsa_dict[condition][task]:
                        rsa_dict[condition][task][sub_id] = {}

                    age_type = 'infant' if participant == 'infant' else 'adult'

                    if ts is None:
                        rsa_dict[condition][task][sub_id][participant] = {}
                    else:
                        ibi_ts = list(pd.Series(ts))
                        validate_array(ibi_ts)
                        rsa_dict[condition][task][sub_id][participant] = rsa_time_series(
                            ibi_ms=ibi_ts,
                            rsa_method='abbney',
                            age_type=age_type
                        )

    return rsa_dict, excluded_summary


def exclude_unmatched_pairs(valid_sample: dict):
    sample_to_analysis = {}
    excluded_summary = {}

    for participant, part_data in valid_sample.items():
        for condition, cond_data in part_data.items():
            for task, sub_dict in cond_data.items():
                if condition not in sample_to_analysis:
                    sample_to_analysis[condition] = {}
                    excluded_summary[condition] = {}
                if task not in sample_to_analysis[condition]:
                    sample_to_analysis[condition][task] = {}
                    excluded_summary[condition][task] = {}

                sample_to_analysis[condition][task][participant] = sub_dict

    # Now find unmatched pairs per condition/task
    for condition, cond_data in sample_to_analysis.items():
        for task, task_data in cond_data.items():
            participants = list(task_data.keys())
            subj_sets = {p: set(task_data[p].keys()) for p in participants}
            common_subs = set.intersection(*subj_sets.values())
            all_subs = set.union(*subj_sets.values())
            unmatched_subs = all_subs - common_subs

            if unmatched_subs:
                excluded_summary[condition][task]['unmatched_subjects'] = list(unmatched_subs)
                for p in participants:
                    for sub in unmatched_subs:
                        task_data[p].pop(sub, None)

    return sample_to_analysis, excluded_summary
