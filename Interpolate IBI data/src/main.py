import pandas as pd
from pathlib import Path
import pickle

from data_loader import data_loader
from moritz_interpolation_pipeline import interpolation_process
from use_js_interpolator import js_spline_lookup


import matplotlib.pyplot as plt
import numpy as np



dic_for_interpolation = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Prepare data for interpolation/data_for_interpolation.pkl')

parent_dir = Path(__file__).resolve().parent.parent

interpolation_pickle_output = parent_dir / 'after interpolation_Moritz.pkl'

data_dict = data_loader(dic_for_interpolation)


intrpolat_ibi= interpolation_process(data_dict, 500, js_spline_lookup, infant_ibis_th=600, mom_ibis_th=1000, tension=0.2, save_path= interpolation_pickle_output)

        
