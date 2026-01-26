import numpy as np
import numpy as np

def prepare_sample_for_analysis(data: dict, min_session_length_sec, min_sdrr, is_interpolation: bool, missing_ibis_prop=0.20 
):

    sample_for_calculation = {}
    excluded_summary = {}

    

    for condition, condition_dict in data.items():
        sample_for_calculation[condition] = {}
        excluded_summary[condition] = {}


        for participant, part_data in condition_dict.items():    
            refined = part_data['refined_best_channel_data']

            if is_interpolation:
                subs_stat = refined['ibis_after_interpolation']['stats']
                subs_data = refined['ibis_after_interpolation']['data']
                subs_data_before_interpolation = refined['new_ibis_data']['data']
            else:
                subs_stat = refined['new_ibis_stats']
                subs_data = refined['new_ibis_data']['data']
                subs_data_before_interpolation = subs_data

            # Exclude invalid subjects
            excluded_subs = exclude_invalid_subs(subs_data,
                subs_data_before_interpolation, 
                subs_stat,
                missing_ibis_prop,
                is_interpolation,
                min_session_length_sec,
                min_sdrr
                
            )

            # Filter out excluded subjects and extract only ibi_samples
            valid_subs_data = {
                sub_id: data['ibi_samples']
                for sub_id, data in subs_data.items()
                if sub_id not in excluded_subs
            }

            # Store valid data for further analysis
            sample_for_calculation[condition][participant] = valid_subs_data

            # Keep track of excluded ones
            excluded_summary[condition][participant] = excluded_subs

    return sample_for_calculation, excluded_summary

    
    


def exclude_invalid_subs(
        subs_data:dict,
        subs_data_before_interpolation:dict,
        subs_stat: dict, 
        missing_ibis_prop: float, 
        is_interpolation :bool,
        min_session_length_sec: None,
        sdrr_threshold=None    ):
        
    excluded_subs = {}

    # -------- Session length exclusion --------
    if min_session_length_sec is None:
        mean_session_length = np.mean([v['session_lenght_sec'] for v in subs_stat.values()])
        min_session_length = 0.50 * mean_session_length
        min_length_criteria = f"half the mean length ({min_session_length:.2f}s)"
    else:
        min_session_length = min_session_length_sec
        min_length_criteria = f'{min_session_length_sec} sec'

    for sub, stat_data in subs_stat.items():
        if stat_data['session_lenght_sec'] < min_session_length:
            reason = (
                f"Session length ({stat_data['session_lenght_sec']:.2f}s) is shorter "
                f"than {min_length_criteria}"
            )
            excluded_subs[sub] = reason
    
    # -------- Missing IBI exclusion --------
        if is_interpolation:
            for sub, sub_data in subs_data.items():
                if sub in excluded_subs:
                    continue
                ibis_length_before_interpolation = len(subs_data_before_interpolation[sub])
                ibis_lenght_with_interpolation = len(sub_data['ibi_samples'])
                interpolated_ibis_count = ibis_lenght_with_interpolation - ibis_length_before_interpolation

                if interpolated_ibis_count >=missing_ibis_prop * ibis_lenght_with_interpolation:
                    reason = (
                                f"Interpolated ibis count ({interpolated_ibis_count}) exceeds "
                                f"{missing_ibis_prop*100:.0f}% of series length after interpolation({ibis_lenght_with_interpolation})"
                            )
                    excluded_subs[sub] = reason

        else:
            for sub, stat_data in subs_stat.items():
                if sub in excluded_subs:
                    continue

                if stat_data['long_ibi_count'] >= missing_ibis_prop * stat_data['length_ibis_ts']:
                    reason = (
                        f"Long IBI count ({stat_data['long_ibi_count']}) exceeds "
                        f"{missing_ibis_prop*100:.0f}% of series length ({stat_data['length_ibis_ts']})"
                    )
                    excluded_subs[sub] = reason

    # -------- SDRR exclusion (NEW) --------
    if sdrr_threshold is not None:
        for sub, stat_data in subs_stat.items():
            if sub in excluded_subs:
                continue
            if stat_data['sdrr'] > sdrr_threshold:
                reason = (
                    f"SDRR ({stat_data['sdrr']:.2f}) exceeds threshold "
                    f"({sdrr_threshold})"
                )
                excluded_subs[sub] = reason

    return excluded_subs

                  

             
             
        
