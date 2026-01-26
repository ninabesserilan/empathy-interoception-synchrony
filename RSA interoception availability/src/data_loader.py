import pickle
from pathlib import Path
from typing import Literal


def data_loader(pickle_path: Path):
    with open(pickle_path, "rb") as l_data:
        pickle_data = pickle.load(l_data)
    
    return pickle_data




