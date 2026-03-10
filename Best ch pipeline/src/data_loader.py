import pickle
from config import Config_03_json_empathy_18, Config_01_csv_empathy_9
from pathlib import Path



pickle_path_18m = Path(Config_03_json_empathy_18['save_path']) / f"{Config_03_json_empathy_18['peaks_prefix']}.pkl"

pickle_path_9m = Path(Config_01_csv_empathy_9['save_path']) / f"{Config_01_csv_empathy_9['peaks_prefix']}.pkl"



with open(pickle_path_9m, "rb") as f_ibis:
    data_9 = pickle.load(f_ibis)


with open(pickle_path_18m, "rb") as f_ibis:
    data_18 = pickle.load(f_ibis)
