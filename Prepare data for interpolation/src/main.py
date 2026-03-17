
from pathlib import Path
from  data_loader import data_loader
from build_dic_for_interpolation import build_dic_for_interpolation


ibis_pickle_path_9m = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Best ch pipeline/all_final_data_9m.pkl')
ibis_pickle_path_18m = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Best ch pipeline/all_final_data_18m.pkl')


data_dict_9m = data_loader(ibis_pickle_path_9m)
data_dict_18m = data_loader(ibis_pickle_path_18m)


parent_dir = Path(__file__).resolve().parent.parent


save_path_9m = parent_dir / "data_for_interpolation_9m.pkl"
save_path_18m = parent_dir / "data_for_interpolation_18m.pkl"


data_for_interpolation_9m = build_dic_for_interpolation(data_dict=data_dict_9m, factor=2, save_path=save_path_9m)
data_for_interpolation_18m = build_dic_for_interpolation(data_dict=data_dict_18m, factor=2, save_path=save_path_18m)
