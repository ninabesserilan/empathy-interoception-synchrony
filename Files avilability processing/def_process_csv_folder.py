import os
import pickle
import pandas as pd

def process_csv_folder(folder_path, config, output_prefix, save_pickles=True, save_path = None):
    
    """
    Process CSV files in a folder into a nested dictionary and save as pickle.

    Args:
        folder_path (str): Path to the folder containing CSV files.
        config (dict): Dictionary mapping categories to filename markers.
        output_prefix (str): Prefix for the saved pickle files.
        save_pickles (bool): Whether to save the results as pickle files.

    Returns:
        dict: Nested dictionary of processed data.
    """
 
    # List all CSV files
    all_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    total_files = len(all_files)
    print(f"Found {total_files} CSV files in {folder_path}")

    # Dictionary to store all CSV data
    data_dict = {}

    # Keep track of counts
    skipped_files = 0
    data_type_counts = {dt: 0 for dt in config.get("data_type", {}).keys()}

    for idx, file_name in enumerate(all_files, 1):
        print(f"Processing file {idx}/{total_files}: {file_name}")
        file_path = os.path.join(folder_path, file_name)

        # Load CSV safely
        try:
            csv_data = pd.read_csv(file_path, header=None).squeeze()
        except pd.errors.EmptyDataError:
            print(f"Warning: {file_name} could not be read")

        # --- Detect file attributes only for required categories ---
        file_attributes = {}

        # Required keys: always need data_type + groups + dyad_id + conditions + channels
        required_keys = ["data_type", "group", "dyad_id", "condition", "channel"]

        # Participants are optional
        has_participants = "participant" in config
        if has_participants:
            required_keys.insert(-1, "participant")  # insert before channels

        for category in required_keys:
            if category == "dyad_id":  # derived, not in config
                continue

            options_dict = config.get(category, {})
            for attribute_name, filename_marker in options_dict.items():
                if str(filename_marker) in file_name:
                    file_attributes[category] = attribute_name

                    # Extract dyad ID if category == groups
                    if category == "group":
                        start_index = file_name.find(str(filename_marker))
                        dyad_id = file_name[start_index + len(str(filename_marker)) :
                                            start_index + len(str(filename_marker)) + 2]
                        file_attributes["dyad_id"] = dyad_id
                    break

        # --- Validate required attributes ---
        if not all(file_attributes.get(k) for k in required_keys):
            print(f"Warning: Could not fully parse {file_name}, skipping.")
            skipped_files += 1
            continue

            # --- Update count for this data_type ---
        data_type_counts[file_attributes["data_type"]] += 1

        # --- Build dynamic nesting based on required keys ---
        ref = data_dict
        for key in required_keys[:-1]:  # go through all but the last
            ref = ref.setdefault(file_attributes[key], {})

        channel = file_attributes["channel"]
        ref[channel] = {"data": csv_data}

    # --- Save pickle files if requested ---
    if save_pickles:
        if save_path is not None:
            full_pickle = save_path/f"{output_prefix}.pkl"
        else:
            full_pickle = f"{output_prefix}.pkl"
        with open(full_pickle, "wb") as pickle_file:
            pickle.dump(data_dict, pickle_file)
        print(f"Saved all data to {full_pickle} ({total_files} files processed, {skipped_files} skipped).")

        # Save subsets based on config['data_type']
        if "data_type" in config:
            for subset in config["data_type"].keys():
                if subset in data_dict:
                    subset_filename = f"{config['analysis_stage']}_{subset}_data.pkl"
                    # build full path depending on save_path
                    if save_path is not None:
                        subset_pickle = save_path / subset_filename
                    else:
                        subset_pickle = subset_filename
                    with open(subset_pickle, "wb") as f_subset:
                        pickle.dump(data_dict[subset], f_subset)
                    count = data_type_counts.get(subset, 0)
                    print(f"Saved {subset} data to {subset_pickle} ({count} files).")

    return data_dict

