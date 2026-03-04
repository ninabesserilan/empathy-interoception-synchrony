import copy
import pickle
import numpy as np
from pathlib import Path


def filter_and_save_pickle(config):
    """
    Recursively filters a nested dictionary, keeping only:
    'peaks', 'startIndex', 'endIndex', 'removedRegions', 
    'samplingRate', and 'ibi' (if it exists).

    Saves the filtered dictionary as a new pickle file.
    """
    
    keys_to_keep = {
        'peaks',
        'startIndex',
        'endIndex',
        'removedRegions',
        'samplingRate',
        'ibi'
    }

    def recursive_filter(d):
        if isinstance(d, dict):
            new_dict = {}
            for key, value in d.items():

                # Channel-level dict detection
                if isinstance(value, dict) and 'peaks' in value:
                    
                    filtered = {
                        k: copy.deepcopy(value[k])
                        for k in keys_to_keep
                        if k in value and k != 'ibi'
                    }

                    # Create ibi if missing
                    if 'ibi' in value:
                        filtered['ibi'] = copy.deepcopy(value['ibi'])
                    else:
                        peaks = np.asarray(value['peaks'])
                        if len(peaks) > 1:
                            filtered['ibi'] = np.diff(peaks)
                        else:
                            filtered['ibi'] = np.array([])

                    new_dict[key] = filtered

                else:
                    new_dict[key] = recursive_filter(value)

            return new_dict


    folder_path = Path(config['save_path'])

    json_prefix = config['json_prefix']
    path = folder_path / f"{json_prefix}.pkl"

    with open(path, "rb") as f_ibis:
        data = pickle.load(f_ibis)

    filtered_data = recursive_filter(data)

    # Save to pickle
    save_prefix = config['peaks_prefix']
    output_filename = folder_path /f"{save_prefix}.pkl"

    with open(output_filename, 'wb') as f:
        pickle.dump(filtered_data, f)

    return filtered_data

