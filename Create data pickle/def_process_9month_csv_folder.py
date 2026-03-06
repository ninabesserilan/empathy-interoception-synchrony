from pathlib import Path
import os
import json
import pickle
import pandas as pd
import re

def process_csv_folder(config, save_pickles=True):
    """
    Process SV files in a folder into a nested dictionary and save as pickle.

    Args:
        folder_path (str): Path to the folder containing files.
        config (dict): Dictionary mapping categories to filename markers.
        output_prefix (str): Prefix for the saved pickle files.
        save_pickles (bool): Whether to save the results as pickle files.

    Returns:
        dict: Nested dictionary of processed data.
    """

    # List all files (csv)
    folder_path = config['folder_path']
    all_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    total_files = len(all_files)
    print(f"Found {total_files} files in {folder_path}")

    data_dict = {}
    skipped_files = 0      # for unreadable/unparseable files
    excluded_files = 0     # for intentionally excluded dyads

    # Build the nesting order dynamically from config
    # Fixed order: participant (optional) > dyad_id > condition (optional) > setting (optional) > file_type > channel
    possible_keys = ["participant",  "condition", "task", "dyad_id", "file_type", "channel"]
    required_keys = [k for k in possible_keys if k == "dyad_id" or k in config]
    stored_files = 0
    for idx, file_name in enumerate(all_files, 1):
        print(f"Processing file {idx}/{total_files}: {file_name}")
        file_path = os.path.join(folder_path, file_name)

        # Load file
        try:
            file_data = pd.read_csv(file_path, header=None).squeeze()
        except Exception as e:
            print(f"Warning: {file_name} could not be read: {e}")
            skipped_files += 1  # ← add this
            continue
        # Detect file attributes
        file_attributes = {}

        for category in required_keys:
            if category == "dyad_id":
                continue  # derived from group/participant marker

            options_dict = config.get(category, {})
            for attribute_name, filename_marker in options_dict.items():
                # filename_marker can be a string or a list of strings
                markers = filename_marker if isinstance(filename_marker, list) else [filename_marker]
                for marker in markers:
                    if str(marker).lower() in file_name.lower():
                        file_attributes[category] = attribute_name

                        # Extract dyad_id from participant marker
                        if category == "participant":
                            match = re.search(r'\d{2,3}', file_name)
                            if match:
                                file_attributes["dyad_id"] = (match.group())[-2:]
                        break
                if category in file_attributes:
                    break

        # Validate all required keys are found
        if not all(file_attributes.get(k) for k in required_keys):
            missing = [k for k in required_keys if not file_attributes.get(k)]
            print(f"Warning: Could not parse {file_name} (missing: {missing}), skipping.")
            skipped_files += 1
            continue

        if file_attributes.get("dyad_id") in config.get("exclude_dyads", set()):
            print(f"Skipping excluded dyad: {file_name}")
            excluded_files += 1
            continue


        # Build nested dict according to required_keys order (excluding channel)
        ref = data_dict
        for key in required_keys[:-1]:  # all except channel
            ref = ref.setdefault(file_attributes[key], {})

        # Store data at channel level
        channel = file_attributes["channel"]

        if channel in ref:
            print(f"OVERWRITE DETECTED: {file_name} is overwriting existing data at path {file_attributes}")
        ref[channel] = file_data
        stored_files += 1
    print(f"Total files found: {total_files}")
    print(f"Stored files: {stored_files}")
    print(f"Skipped files: {skipped_files}")

    if stored_files + skipped_files + excluded_files != total_files:
        print(f"WARNING: File count mismatch! {stored_files} stored + {skipped_files} skipped + {excluded_files} excluded = {stored_files + skipped_files + excluded_files} ≠ {total_files}")
    if skipped_files > 0:
        print(f"Warning: {skipped_files} files could not be read and were skipped.")  # ← just a warning, no raise
    if excluded_files > 0:
        print(f"Excluded {excluded_files} files from dyads: {config.get('exclude_dyads')}")
            # Save pickles
    if save_pickles:
        save_path = Path(config['save_path'])
        output_prefix = config['peaks_prefix']
        full_pickle = save_path / f"{output_prefix}.pkl"
        with open(full_pickle, "wb") as pickle_file:
            pickle.dump(data_dict, pickle_file)
        print(f"Saved all data to {full_pickle} ({total_files} files, {skipped_files} skipped).")

    return data_dict
