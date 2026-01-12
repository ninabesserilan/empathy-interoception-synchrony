from pathlib import Path
import pickle
from data_loader import data_loader

pickle_rsa = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/RSA analysis/rsa_pickle.pkl')


rsa_data = data_loader(pickle_rsa)

toys_rsa_data = rsa_data['toys']
notoys_rsa_data = rsa_data['no_toys']