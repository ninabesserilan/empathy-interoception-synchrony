import pandas as pd
from config import Config_03_json_empathy_9, Config_03_json_empathy_18, Config_01_csv_empathy_9
from def_extract_peaks_from_pickle import filter_and_save_pickle
from def_process_9month_csv_folder import process_csv_folder
from pathlib import Path
import pickle




# empathy_9_month_pickle = filter_and_save_pickle(Config_03_json_empathy_9)
# empathy_18_month_pickle = filter_and_save_pickle(Config_03_json_empathy_18)
empathy_9_month_pickle_csv = process_csv_folder(Config_01_csv_empathy_9)

