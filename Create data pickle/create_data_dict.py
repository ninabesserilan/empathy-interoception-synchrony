import pandas as pd
from config import Config_03_json_empathy_9, Config_03_json_empathy_18
from def_extract_peaks_from_pickle import filter_and_save_pickle
from pathlib import Path
import pickle


pickle_path_9m = '/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Files data/03_json_after_manual_coding_9_month.pkl'

pickle_path_18m = '/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Files data/03_json_after_manual_coding_18_month.pkl'




empathy_9_month_pickle = filter_and_save_pickle(Config_03_json_empathy_9)
empathy_18_month_pickle = filter_and_save_pickle(Config_03_json_empathy_18)


