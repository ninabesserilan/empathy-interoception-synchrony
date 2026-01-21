
import numpy as np
import pandas as pd
import copy
import pickle



def apply_gap_filling_to_data_dict(data_dict, factor=2, infant_ibis_th=600, 
                                   mom_ibis_th=1000, tension=0.2, save_path=None):
    """
    Applies spline-based interpolation to each subject's IBI array and stores results.
    
    This version uses Catmull-Rom spline interpolation matching the JavaScript implementation.
    
    Args:
        data_dict: Nested dictionary containing IBI data
        factor: Threshold multiplier for gap detection (default: 2)
        infant_ibis_th: Long IBI threshold for infants in ms (default: 600)
        mom_ibis_th: Long IBI threshold for mothers in ms (default: 1000)
        tension: Spline tension parameter (default: 0.2)
        save_path: Optional path to save the processed data as pickle
    
    Returns:
        Processed copy of data_dict with interpolated IBIs added
    """
    processed = copy.deepcopy(data_dict)


    for condition, condition_dict in processed.items():
        for participant, part_data in condition_dict.items():
            # Get source data
            subs_stat = part_data['refined_best_channel_data']['new_ibis_stats'] 
            subs_data = part_data['refined_best_channel_data']['new_ibis_data']['data']

            # Containers for transformed IBIs and their stats
            ibis_after_interpolation_data = {}
            ibis_after_interpolation_stats = {}

            # Process each subject
            for sub_id, ibi_arr in subs_data.items():
                # Apply spline-based gap-filling
                filled_arr = ibis_interpolation_spline(ibi_arr, factor=factor, tension=tension)
                ibis_after_interpolation_data[sub_id] = filled_arr

                # Compute statistics
                if participant == 'infant':
                    long_ibi_threshold = infant_ibis_th
                else:
                    long_ibi_threshold = mom_ibis_th

                length_best = len(filled_arr)
                median_best = np.median(filled_arr) if length_best > 0 else np.nan
                mean_best = np.mean(filled_arr) if length_best > 0 else np.nan
                sdrr_best = np.std(filled_arr, ddof=1) if length_best > 1 else np.nan
                long_ibi_count_best = (
                    np.sum(filled_arr > long_ibi_threshold) if length_best > 0 else 0
                )

                name_best = subs_stat[sub_id]['best_channel']
                session_lenght_sec = subs_stat[sub_id]['session_lenght_sec']

                ibis_after_interpolation_stats[sub_id] = {
                    'best_channel': name_best,
                    'session_lenght_sec': session_lenght_sec,
                    'length_ibis_ts': length_best,
                    'median': median_best,
                    'mean': mean_best,
                    'sdrr': sdrr_best,
                    'long_ibi_count': long_ibi_count_best
                }

            # Attach results back into the data structure
            part_data['refined_best_channel_data']['ibis_after_interpolation'] = {
                'data': ibis_after_interpolation_data,
                'stats': ibis_after_interpolation_stats
            }
    
    # Save as pickle if requested
    if save_path is not None:
        with open(save_path, "wb") as f:
            pickle.dump(processed, f)

    return processed





def catmull_rom_spline(points, tension=0.0):
    """
    Creates a Catmull-Rom spline interpolator matching the JS CurveInterpolator.
    
    Args:
        points: List of [x, y] pairs (e.g., [[0, 520], [1, 505], ...])
        tension: Spline tension (0.0 = Catmull-Rom, higher = tighter)
    
    Returns:
        Function that takes an x value and returns interpolated y value
    """
    points = np.array(points)
    
    def interpolate(t):
        """Interpolate value at position t"""
        # Find the segment
        for i in range(len(points) - 1):
            if points[i][0] <= t <= points[i+1][0]:
                # Get 4 control points (with boundary handling)
                p0 = points[max(0, i-1)]
                p1 = points[i]
                p2 = points[i+1]
                p3 = points[min(len(points)-1, i+2)]
                
                # Normalize t to [0, 1] within this segment
                x1, y1 = p1
                x2, y2 = p2
                t_norm = (t - x1) / (x2 - x1) if x2 != x1 else 0
                
                # Catmull-Rom basis functions with tension
                t2 = t_norm * t_norm
                t3 = t2 * t_norm
                
                s = (1 - tension) / 2
                
                # Catmull-Rom coefficients
                h1 = -s*t3 + 2*s*t2 - s*t_norm
                h2 = (2-s)*t3 + (s-3)*t2 + 1
                h3 = (s-2)*t3 + (3-2*s)*t2 + s*t_norm
                h4 = s*t3 - s*t2
                
                # Interpolate y value
                y = h1*p0[1] + h2*p1[1] + h3*p2[1] + h4*p3[1]
                
                return y
        
        # If t is outside range, return nearest endpoint
        if t < points[0][0]:
            return points[0][1]
        return points[-1][1]
    
    return interpolate


def ibis_interpolation_spline(ibi_arr, factor=2, tension=0.2): # Should we do factor = 1.5?
    """
    Interpolates IBIs using Catmull-Rom spline, matching the JS implementation.
    
    Args:
        ibi_arr: Array of IBI values in milliseconds
        factor: Threshold multiplier for detecting gaps (default: 2)
        tension: Spline tension parameter (default: 0.2, matching JS)
    
    Returns:
        Interpolated IBI array with gaps filled using spline interpolation
    """
    arr = np.asarray(ibi_arr, dtype=float)
    
    if len(arr) == 0:
        return arr
    
    mean_ibi = np.mean(arr)
    
    # Step 1: Create indexed real IBIs and identify gap locations
    ibi_indexed = []  # [[index, ibi_value], ...]
    interpolation_groups = []  # [[gap_start_idx, gap_indices...], ...]
    gap_durations = []  # Store original gap durations for scaling
    
    index = 0
    arr_position = 0
    
    for val in arr:
        if val > factor * mean_ibi:
            # This is a gap - calculate how many IBIs should fill it
            num_ibis_floor = int(np.floor(val / mean_ibi))
            num_ibis_ceil = int(np.ceil(val / mean_ibi))
            
            # Choose the number that makes synthetic IBIs closest to mean
            dist_floor = abs(mean_ibi - val / num_ibis_floor) if num_ibis_floor > 0 else float('inf')
            dist_ceil = abs(mean_ibi - val / num_ibis_ceil) if num_ibis_ceil > 0 else float('inf')
            
            num_ibis = num_ibis_floor if dist_floor < dist_ceil else num_ibis_ceil
            num_ibis = max(1, num_ibis)  # At least 1 IBI
            
            # Create indices for this gap
            gap_indices = list(range(index, index + num_ibis))
            interpolation_groups.append(gap_indices)
            gap_durations.append(val)
            
            index += num_ibis
        else:
            # Real IBI
            ibi_indexed.append([index, val])
            index += 1
        
        arr_position += 1
    
    # If no gaps, return original array
    if len(interpolation_groups) == 0:
        return arr
    
    # If no real IBIs, can't interpolate
    if len(ibi_indexed) == 0:
        return arr
    
    # Step 2: Handle placeholders for boundary cases
    # If interpolation regions exist before first or after last real IBI, add placeholders
    first_interpolation_index = min(interpolation_groups[0])
    last_interpolation_index = max(interpolation_groups[-1])
    first_real_ibi_index = min(x[0] for x in ibi_indexed)
    last_real_ibi_index = max(x[0] for x in ibi_indexed)
    
    placeholder_start_index = None
    placeholder_end_index = None
    
    # Add start placeholder if needed
    if first_interpolation_index < first_real_ibi_index:
        placeholder_start_index = first_interpolation_index - 1
        placeholder_value = next(x[1] for x in ibi_indexed if x[0] == first_real_ibi_index)
        ibi_indexed.insert(0, [placeholder_start_index, placeholder_value])
    
    # Add end placeholder if needed
    if last_interpolation_index > last_real_ibi_index:
        placeholder_end_index = last_interpolation_index + 1
        placeholder_value = next(x[1] for x in ibi_indexed if x[0] == last_real_ibi_index)
        ibi_indexed.append([placeholder_end_index, placeholder_value])
    
    # Step 3: Create spline interpolator
    interpolator = catmull_rom_spline(ibi_indexed, tension=tension)
    
    # Step 4: Get interpolated values for each gap
    interpolated_values_all = []
    
    for gap_idx, gap_indices in enumerate(interpolation_groups):
        # Get raw interpolated values
        group_values = [interpolator(idx) for idx in gap_indices]
        
        # Step 5: Scale to match original gap duration
        interpolated_sum = sum(group_values)
        original_gap_duration = gap_durations[gap_idx]
        
        if interpolated_sum > 0:
            scale = original_gap_duration / interpolated_sum
            scaled_values = [round(v * scale) for v in group_values]
        else:
            # Fallback: distribute duration equally
            print("spline failed")
            scaled_values = [original_gap_duration / len(gap_indices)] * len(gap_indices)
        
        # Store as [index, value] pairs
        for idx, val in zip(gap_indices, scaled_values):
            interpolated_values_all.append([idx, val])
    
    # Step 6: Merge real and interpolated IBIs (excluding placeholders)
    ibi_merged = []
    
    # Add real IBIs (excluding placeholders)
    for idx_val in ibi_indexed:
        if idx_val[0] != placeholder_start_index and idx_val[0] != placeholder_end_index:
            ibi_merged.append(idx_val)
    
    # Add interpolated IBIs
    ibi_merged.extend(interpolated_values_all)
    
    # Sort by index
    ibi_merged.sort(key=lambda x: x[0])
    
    # Extract just the IBI values
    result = np.array([round(x[1]) for x in ibi_merged], dtype=int)
    
    return result






# def basic_interpolation(ibi_arr, factor=2):
#     arr = np.asarray(ibi_arr)
#     mean_ibi = round(np.mean(ibi_arr))

#     filled = []

#     for val in arr:
#         if val > factor * mean_ibi:
#             # how many full mean intervals fit?
#             num_reps = int(val // mean_ibi)

#             # add the repeated median IBIs
#             filled.extend([mean_ibi] * num_reps)

#         else:
#             filled.append(val)

#     return np.array(filled)

