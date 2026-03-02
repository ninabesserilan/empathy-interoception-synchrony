import copy
import pickle
import numpy as np
import math


def interpolation_process(data_dict, sampling_rate, js_spline_lookup, infant_ibis_th=600, 
                          mom_ibis_th=1000, tension=0.2, save_path=None):
    """
    Applies spline-based interpolation to each subject's IBI array and stores results.
    
    This version uses Catmull-Rom spline interpolation matching the JavaScript implementation.
    
    Args:
        data_dict: Nested dictionary containing IBI data
        sampling_rate: Sampling rate in Hz
        js_spline_lookup: Function to call JavaScript interpolation
        infant_ibis_th: Long IBI threshold for infants in ms (default: 600)
        mom_ibis_th: Long IBI threshold for mothers in ms (default: 1000)
        tension: Spline tension parameter (default: 0.2)
        save_path: Optional path to save the processed data as pickle
    
    Returns:
        Processed copy of data_dict with interpolated IBIs added
    """
    processed = copy.deepcopy(data_dict)


    for participant, participant_dict in processed.items():

        for condition, condition_dict in participant_dict.items():
                
            for task, part_data in condition_dict.items():

                # Get source data
                subs_stat = part_data['new_ibis_stats'] 
                subs_data = part_data['data_for_interpolation']

                # Containers for transformed IBIs and their stats
                ibis_after_interpolation_data = {}
                ibis_after_interpolation_stats = {}

                # Process each subject
                for sub_id, peak_data in subs_data.items():
                    # Apply spline-based gap-filling
                    filled_result = process_ibi_data(sub_id, peak_data, sampling_rate, js_spline_lookup, tension )
                    ibis_after_interpolation_data[sub_id] = filled_result

                    # Compute statistics
                    if participant == 'infant':
                        long_ibi_threshold = infant_ibis_th
                    else:
                        long_ibi_threshold = mom_ibis_th

                    # Compute statistics using ibi_ms
                    ibi_ms_array = np.array(filled_result['ibi_ms'])
                    ibi_sample_array = np.array(filled_result['ibi_samples'])
                    length_ibis = len(ibi_ms_array)
                    median_ibis = np.median(ibi_ms_array) if length_ibis > 0 else np.nan
                    mean_ibis = np.mean(ibi_ms_array) if length_ibis > 0 else np.nan
                    sdrr_ibis = np.std(ibi_ms_array, ddof=1) if length_ibis > 1 else np.nan
                    long_ibi_count = np.sum(ibi_sample_array > long_ibi_threshold) if length_ibis > 0 else 0


                    # Copy metadata
                    name_best = subs_stat[sub_id]['best_channel']
                    session_length = subs_stat[sub_id]['session_length_sec']  
                    session_length_sec = session_length * (1000/sampling_rate)

                    ibis_after_interpolation_stats[sub_id] = {
                        'best_channel': name_best,
                        'session_length_sec': session_length_sec,
                        'length_ibis_ts': length_ibis,
                        'median': median_ibis,
                        'mean': mean_ibis,
                        'sdrr': sdrr_ibis,
                        'long_ibi_count': long_ibi_count
                    }

                # Attach results back
                part_data['ibis_after_interpolation'] = {
                    'data': ibis_after_interpolation_data,
                    'stats': ibis_after_interpolation_stats
                }
        
    # Save as pickle if requested
    if save_path is not None:
        with open(save_path, "wb") as f:
            pickle.dump(processed, f)

    return processed


def process_ibi_data(sub_id, data, sampling_rate, js_spline_lookup, tension=0.2):
    """
    Process inter-beat interval (IBI) data with interpolation for removed regions.
    
    Args:
        data: Dictionary containing:
            - peaks: List of peak indices
            - startPeak: Start index of valid data
            - endPeak: End index of valid data
            - removedRegions: List of dicts with 'start' and 'end' keys
        sampling_rate: Sampling rate of the data
        js_spline_lookup: Function to call JavaScript interpolation
        tension: Tension parameter for curve interpolation (default 0.2)
    
    Returns:
        Dictionary containing:
            - ibi_samples: List of IBI values in samples
             - ibi_ms: List of IBIs in milliseconds
            - interpolated_indices: List of indices that were interpolated
    """
    # Sort peaks and create a copy
    peaks = sorted(data['peaks'])
    start_peak = data['startPeak']
    end_peak = data['endPeak']
    
    # Ensure all removed regions have start < end
    removed_regions = [
        invalid_gap if invalid_gap['start'] < invalid_gap['end'] else {'start': invalid_gap['end'], 'end': invalid_gap['start']}
        for invalid_gap in data['removedRegions']
    ]
    
    # Create located ibi list: [ {'t': ..., 'duration': ..., 'type': 'ibi'} ]
    ibi_located = []
    for i in range(1, len(peaks)):
        interval_start = peaks[i - 1]
        interval_end = peaks[i]
        
        # FIXED: Skip peaks outside valid range (but include boundaries)
        # Changed from <= and >= to < and >
        if interval_start < start_peak or interval_end > end_peak:
            continue
                
        if any(
            interval_start == invalid_gap['start'] and interval_end == invalid_gap['end']
            for invalid_gap in removed_regions
        ):
            continue

        
        ibi_located.append({'t': interval_start, 'duration': interval_end - interval_start, 'type': 'ibi'})
    
    # Handle edge case: no valid IBIs found
    if len(ibi_located) == 0:
        return {
            'ibi_samples': [],
            'ibi_ms': [],
            'interpolated_indices': []
        }
    
    # Calculate average ibi
    avg_ibi = sum(ibi['duration'] for ibi in ibi_located) / len(ibi_located)

    # Create list of removed regions with their durations
    gap_located = []
    for invalid_gap in removed_regions:
        # The duration is simply the span of the removed region
        duration = invalid_gap['end'] - invalid_gap['start']
        gap_located.append({
            't': invalid_gap['start'], 
            'duration': duration,  # ms
            'type': 'removed_regions'
        })
    
    
    # Calculate number of ibis for each removed region
    gap_located_processed = []
    for invalid_gap in gap_located:
        num_ibis_floor = math.floor(invalid_gap['duration'] / avg_ibi)
        num_ibis_ceil = math.ceil(invalid_gap['duration'] / avg_ibi)
        dist_floor = abs(avg_ibi - invalid_gap['duration'] / num_ibis_floor) if num_ibis_floor > 0 else float('inf')
        dist_ceil = abs(avg_ibi - invalid_gap['duration'] / num_ibis_ceil) if num_ibis_ceil > 0 else float('inf')
        
        gap_located_processed.append({
            **invalid_gap,
            'numIbis': num_ibis_floor if dist_floor < dist_ceil else num_ibis_ceil
        })
    
    
    # Merge ibi and gap lists, sorted by time
    ibi_gap_located = sorted(ibi_located + gap_located_processed, key=lambda x: x['t'])

    # Create index structure
    interpolation_indices = []
    ibi_indexed = []
    index = 0
    
    for item in ibi_gap_located:
        # Collect real ibis as [index, ibi] pairs
        if item['type'] == 'ibi':
            ibi_indexed.append([index, item['duration']])
            index += 1
            continue
        
        # Create indices for values to be interpolated
        if item['type'] == 'removed_regions':
            index_group = []
            for j in range(item['numIbis']):
                index_group.append(index)
                index += 1
            interpolation_indices.append(index_group)
            continue
    
    # Handle edge case: no interpolation needed
    if len(interpolation_indices) == 0:
        ibi_samples = [el[1] for el in ibi_indexed]
        ibi_ms = [int(s / sampling_rate * 1000) for s in ibi_samples]

        return {
            'ibi_samples': ibi_samples,
            'ibi_ms' : ibi_ms,
            'interpolated_indices': []
        }
    
    # Add placeholders if needed
    placeholder_start_index = None
    placeholder_end_index = None
    
    first_interpolation_index = min(interpolation_indices[0])
    last_interpolation_index = max(interpolation_indices[-1])
    first_real_ibi_index = min(el[0] for el in ibi_indexed)
    last_real_ibi_index = max(el[0] for el in ibi_indexed)
    
    # Create start placeholder
    if first_interpolation_index < first_real_ibi_index:
        placeholder_start_index = first_interpolation_index - 1
        placeholder_value = next(el[1] for el in ibi_indexed if el[0] == first_real_ibi_index)
        ibi_indexed.insert(0, [placeholder_start_index, placeholder_value])

    # Create end placeholder
    if last_interpolation_index > last_real_ibi_index:
        placeholder_end_index = last_interpolation_index + 1
        placeholder_value = next(el[1] for el in ibi_indexed if el[0] == last_real_ibi_index)
        ibi_indexed.append([placeholder_end_index, placeholder_value])
    
    # Apply interpolation using JavaScript spline lookup
    interpolated_values_grouped = js_spline_lookup(
        ibi_indexed=ibi_indexed,
        interpolation_groups=interpolation_indices,
        tension=tension
    )
    
    # Scale interpolated values to match removed region durations
    interpolated_values_scaled = []
    for group_index, group in enumerate(interpolated_values_grouped):
        interpolated_duration = sum(v[1] for v in group)
        removed_region_duration = gap_located[group_index]['duration']
        scale = removed_region_duration / interpolated_duration
        scaled_group = [[v[0], round(v[1] * scale)] for v in group]
        interpolated_values_scaled.append(scaled_group)
    
    # Flatten interpolated values
    ibi_interpolated = [item for group in interpolated_values_scaled for item in group]
    
    # Merge real and interpolated ibis (excluding placeholders)
    ibi_merged = sorted(
        [el for el in ibi_indexed if el[0] != placeholder_start_index and el[0] != placeholder_end_index] +
        ibi_interpolated,
        key=lambda x: x[0]
    )
    # Create output data
    ibi_samples = [x[1] for x in ibi_merged]
    ibi_ms = [int(s / sampling_rate * 1000) for s in ibi_samples]
    interpolated_indices_out = [x[0] for x in ibi_interpolated]

    
    return {
        'ibi_samples': ibi_samples,
        'ibi_ms': ibi_ms,
        'interpolated_indices': interpolated_indices_out
    }
