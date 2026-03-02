import pandas as pd
from config import Config_03_json_empathy_9, Config_03_json_empathy_18
from def_process_json_folder import process_json_folder
from pathlib import Path
import pickle





empathy_9_month_pickle = process_json_folder(Config_03_json_empathy_9)
empathy_18_month_pickle = process_json_folder(Config_03_json_empathy_18)


