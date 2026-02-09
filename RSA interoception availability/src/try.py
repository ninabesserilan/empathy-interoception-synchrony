import pyxdf
import neurokit2 as nk
import numpy as np
import pandas as pd
from data_loader import data_loader

# load XDF
data, header = pyxdf.load_xdf(
    "011020_1219_wp3_wtoys.xdf",
    synchronize_clocks=False
)

# extract ECG stream
ecg_stream = next(
    s for s in data
    if s['info']['type'][0].lower() == 'eeg'
)

# ECG signal (first channel only)
ecg_signal = ecg_stream['time_series'][:, 0]

# timestamps
ecg_time = ecg_stream['time_stamps']

# sampling rate
fs = float(ecg_stream['info']['nominal_srate'][0])
if fs == 0:
    fs = 1 / np.median(np.diff(ecg_time))

# ECG → R-peaks → IBIs
signals, info = nk.ecg_process(
    ecg_signal,
    sampling_rate=fs
)

# ibi_ms = info["ECG_RR_Intervals"]
# ibi_time = ecg_time[info["ECG_R_Peaks"][1:]]

# # dataframe
# ibi_df = pd.DataFrame({
#     "time": ibi_time,
#     "IBI_ms": ibi_ms
# })



peaks = info['ECG_R_Peaks']
ibi_new = np.diff(peaks)


piclke_file = ('/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/Best ch pipeline/all data improved and original chs.pkl')
data = data_loader(piclke_file)
sub = data['toys']['infant']['original_data_all_channels']['ibis_data']['02']