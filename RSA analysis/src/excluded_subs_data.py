import pandas as pd

def excluded_subs_data(excluded_subs: dict, unmatched_subs: dict, data_dict: dict):
    """
    Merge original excluded subjects with excluded_subs + unmatched_subs.
    Returns a nested dict: merged[participant][condition][task] -> DataFrame
    """

    def dict_to_df(sub_dict):
        num_subs = len(sub_dict)
        col_name = f"sub_id ({num_subs} subs)"
        rows = [{'sub_id': sub_id, "reason": reason} for sub_id, reason in sub_dict.items()]
        df = pd.DataFrame(rows).set_index('sub_id')
        df.index.name = col_name
        return df

    merged = {}

    for participant, part_data in excluded_subs.items():
        merged[participant] = {}

        for condition, cond_data in part_data.items():
            merged[participant][condition] = {}

            for task, task_excluded in cond_data.items():
                # Get original excluded from data_dict
                original_excluded = data_dict[participant][condition][task]['excluded_subs']

                # Merge original + pipeline excluded
                combined = {**original_excluded, **task_excluded}

                # Add unmatched subjects
                unmatched_list = unmatched_subs.get(condition, {}).get(task, {}).get('unmatched_subjects', [])
                for sub_id in unmatched_list:
                    if sub_id not in combined:
                        combined[sub_id] = "Unmatched subject"

                merged[participant][condition][task] = dict_to_df(combined)

    return merged