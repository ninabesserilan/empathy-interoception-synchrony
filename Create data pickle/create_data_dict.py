import pandas as pd
from config import Config_03_json_empathy_9, Config_03_json_empathy_18
from def_extract_peaks_from_pickle import filter_and_save_pickle
from pathlib import Path
import pickle




empathy_9_month_pickle = filter_and_save_pickle(Config_03_json_empathy_9)
empathy_18_month_pickle = filter_and_save_pickle(Config_03_json_empathy_18)


