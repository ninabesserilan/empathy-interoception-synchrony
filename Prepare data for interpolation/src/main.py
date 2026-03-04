
from pathlib import Path
from  data_loader import data_loader
from build_dic_for_interpolation import build_dic_for_interpolation



ibis_pickle_path = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Best ch pipeline/all_final_data_18m.pkl')

data_dict = data_loader(ibis_pickle_path)


parent_dir = Path(__file__).resolve().parent.parent


save_path = parent_dir / "data_for_interpolation.pkl"


data_for_interpolation = build_dic_for_interpolation(data_dict=data_dict, factor=2, save_path=save_path)
