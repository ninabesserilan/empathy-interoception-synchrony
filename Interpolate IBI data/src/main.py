import pandas as pd
from pathlib import Path
import pickle

from data_loader import data_loader
from moritz_interpolation_pipeline import interpolation_process
from use_js_interpolator import js_spline_lookup


import matplotlib.pyplot as plt
import numpy as np



dic_for_interpolation_9m = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Prepare data for interpolation/data_for_interpolation_9m.pkl')
dic_for_interpolation_18m = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Prepare data for interpolation/data_for_interpolation_18m.pkl')

parent_dir = Path(__file__).resolve().parent.parent

interpolation_pickle_output_9m = parent_dir / 'after interpolation_9m.pkl'
interpolation_pickle_output_18m = parent_dir / 'after interpolation_18m.pkl'

# data_dict_9m = data_loader(dic_for_interpolation_9m)
data_dict_18m = data_loader(dic_for_interpolation_18m)

# intrpolat_ibi_9m= interpolation_process(data_dict_9m, '9',500, js_spline_lookup, infant_ibis_th=600, mom_ibis_th=1000, tension=0.2, save_path= interpolation_pickle_output_9m)
intrpolat_ibi_18m= interpolation_process(data_dict_18m, '18', 500, js_spline_lookup, infant_ibis_th=600, mom_ibis_th=1000, tension=0.2, save_path= interpolation_pickle_output_18m)

