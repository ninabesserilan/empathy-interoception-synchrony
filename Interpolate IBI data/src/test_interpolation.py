
from pathlib import Path
from data_loader import data_loader
import numpy as np


data_after_interpolation = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/Interpolate IBI data/after interpolation_Moritz.pkl')

data = data_loader(data_after_interpolation)



example_original_ibi = data['no_toys']['mom']['refined_best_channel_data']['new_ibis_data']['data']['85']
example_original_peaks = np.array(data['no_toys']['mom']['refined_best_channel_data']['new_peaks_data']['data']['85'])
prepared_for_interpolation = data['no_toys']['mom']['refined_best_channel_data']['data_for_interpolation']['85']

after_interpoltion = data['no_toys']['mom']['refined_best_channel_data']['ibis_after_interpolation']['data']['85']


example_original_ibi2 = data['no_toys']['infant']['refined_best_channel_data']['new_ibis_data']['data']['43']
example_original_peaks2 = np.array(data['no_toys']['infant']['refined_best_channel_data']['new_peaks_data']['data']['43'])
prepared_for_interpolation2 = data['no_toys']['infant']['refined_best_channel_data']['data_for_interpolation']['43']

after_interpoltion2 = data['no_toys']['infant']['refined_best_channel_data']['ibis_after_interpolation']['data']['43']


example_original_ibi3 = data['toys']['infant']['refined_best_channel_data']['new_ibis_data']['data']['78']
example_original_peaks3 = np.array(data['toys']['infant']['refined_best_channel_data']['new_peaks_data']['data']['78'])
prepared_for_interpolation3 = data['toys']['infant']['refined_best_channel_data']['data_for_interpolation']['78']

after_interpoltion3 = data['toys']['infant']['refined_best_channel_data']['ibis_after_interpolation']['data']['78']



example_original_ibi4 = data['no_toys']['infant']['refined_best_channel_data']['new_ibis_data']['data']['87']
example_original_peaks4= np.array(data['no_toys']['infant']['refined_best_channel_data']['new_peaks_data']['data']['87'])
prepared_for_interpolation4 = data['no_toys']['infant']['refined_best_channel_data']['data_for_interpolation']['87']

after_interpoltion4= data['no_toys']['infant']['refined_best_channel_data']['ibis_after_interpolation']['data']['87']

