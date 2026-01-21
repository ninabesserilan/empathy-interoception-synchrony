
from defs_empathy_availability import build_empathy_dict
from config import folder_paths, Config_01_csv_ibi_empathy_data

folder = folder_paths['01_ibi_empathy_data_9_month']

empathy_dic_9, df_9 = build_empathy_dict(folder, '9_emp', Config_01_csv_ibi_empathy_data, with_all_indices= True, is_saving = True)

