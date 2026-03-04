import pickle





pickle_path_9m = '/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Files data/03_peaks_after_manual_coding_9_month.pkl'

with open(pickle_path_9m, "rb") as f_ibis:
    data_9 = pickle.load(f_ibis)


pickle_path_18m = '/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Files data/03_peaks_after_manual_coding_18_month.pkl'

with open(pickle_path_18m, "rb") as f_ibis:
    data_18 = pickle.load(f_ibis)





