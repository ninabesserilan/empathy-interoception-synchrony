
import copy
import pickle



def build_dic_for_interpolation(data_dict, factor=2, save_path=None):
    """
    Build interpolation dictionary for all participants and store it inside 
    each participant's 'refined_best_channel_data', alongside 'new_ibis_stats'.
    
    Args:
        data_dict: Original nested dictionary with all participants.
        factor: Threshold multiplier for detecting problematic peaks.
        save_path: Optional file path to save the updated data_dict as pickle.
        
    Returns:
        Updated data_dict with interpolation data added inside each participant.
    """
    
    # Deepcopy to avoid mutating original
    processed = copy.deepcopy(data_dict)

    for condition, condition_dict in processed.items():

        for participant, part_data in condition_dict.items():

            # Get source data
            subs_stat = part_data['refined_best_channel_data']['new_ibis_stats'] 
            subs_peak = part_data['refined_best_channel_data']['new_peaks_data']['data']

            interpolation_sub_dic = {}

            # Process each subject
            for sub_id, peaks_arr in subs_peak.items():
                sub_dic = {}

                median_sub = subs_stat[sub_id]['median']
                miss_peak_th = median_sub * factor

                # First/last valid peaks
                first_valid_peak = find_first_idx(peaks_arr, miss_peak_th)
                last_valid_peak = find_last_idx(peaks_arr, miss_peak_th)

                # Detect problematic gaps
                problematic_peak_gaps = []
                for i in range(1, len(peaks_arr)):
                    interval_start = peaks_arr[i - 1]
                    interval_end = peaks_arr[i]

                    if interval_end - interval_start > miss_peak_th:
                        problematic_peak_gaps.append({
                            'start': interval_start,
                            'end': interval_end
                        })

                # Store sub-dictionary
                sub_dic['peaks'] = peaks_arr
                sub_dic['startPeak'] = first_valid_peak
                sub_dic['endPeak'] = last_valid_peak
                sub_dic['removedRegions'] = problematic_peak_gaps
                sub_dic['ibiTH'] = miss_peak_th

                interpolation_sub_dic[sub_id] = sub_dic

            # Save the interpolation dict inside the participant's refined_best_channel_data
            part_data['refined_best_channel_data']['data_for_interpolation'] = interpolation_sub_dic

    # Save the whole updated data_dict if requested
    if save_path is not None:
        with open(save_path, "wb") as f:
            pickle.dump(processed, f)

    return processed


def find_first_idx(arr, threshold):
    # Case 1: first value itself is smaller than the threshold
    if arr[0] < threshold:
        return arr[0]

    # Case 2: first valid difference
    for i in range(1, len(arr)):
        if arr[i] - arr[i - 1] < threshold:
            return arr[i-1]

    return None



def find_last_idx(arr, threshold):

    for i in range(len(arr) - 1, 0, -1):
        if arr[i] - arr[i - 1] < threshold:
            return arr[i]

    return None





