import pandas as pd
import pickle
def compare_best_channel_stats(loaded_data, participant: str, condition: str):
    """
    Compare best channel statistics between original and refined data.

    Parameters:
    - loaded_data: dict loaded from pickle
    - participant: 'infant' or 'mom'
    - condition: 'toys' or 'no_toys'

    Returns:
    - df_compare: DataFrame with original and refined metrics and differences
    """
    # --- Extract data ---
    final_dict = loaded_data[condition][participant]
    
    refined_stats = final_dict['refined_best_channel_data']['new_ibis_stats']
    original_stats = final_dict['original_data_all_channels']['ibis_stats']

    # --- Convert to DataFrames ---
    df_new = pd.DataFrame.from_dict(refined_stats, orient='index')
    df_new.index.name = 'subject_id'
    df_new.reset_index(inplace=True)

    df_orig = pd.DataFrame.from_dict(original_stats, orient='index')
    df_orig.index.name = 'subject_id'
    df_orig.reset_index(inplace=True)

    # --- Merge ---
    df_compare = df_orig.merge(df_new, on='subject_id', suffixes=('_original', '_refined'))

    # --- Compute numeric differences ---
    numeric_cols = ['median_best', 'mean_best', 'sdrr_best', 'long_ibi_count_best', 'length_best']
    for col in numeric_cols:
        df_compare[f'{col}_diff'] = df_compare[f'{col}_refined'] - df_compare[f'{col}_original']

    return df_compare



pickle_path = '/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/Best ch pipeline/all data improved and original chs.pkl'

with open(pickle_path, "rb") as f_data:
    data = pickle.load(f_data)

# df = compare_best_channel_stats(data, 'infant', 'toys')

data_best_ch_toys_infants = data['toys']['infant']['refined_best_channel_data']['new_ibis_data']['data']
data_best_ch_toys_moms = data['toys']['mom']['refined_best_channel_data']['new_ibis_data']['data']
data_best_ch_notoys_infants = data['no_toys']['infant']['refined_best_channel_data']['new_ibis_data']['data']
data_best_ch_notoys_moms = data['no_toys']['mom']['refined_best_channel_data']['new_ibis_data']['data']


