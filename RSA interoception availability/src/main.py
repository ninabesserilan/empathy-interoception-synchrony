from pathlib import Path
import pandas as pd
from data_loader import data_loader

pickle_rsa = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/RSA analysis/rsa_pickle.pkl')


rsa_dict = data_loader(pickle_rsa)



ib_s = pd.read_csv(Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/RSA interoception availability/interoception data/ib_s.csv'))
ibr_s = pd.read_csv(Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/RSA interoception availability/interoception data/ibr_s.csv'))


ib_s_18mo = pd.read_csv(Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/RSA interoception availability/interoception data/ib_s_18mo.csv'))
ibr_s_18mo = pd.read_csv(Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/RSA interoception availability/interoception data/ibr_s_18mo.csv'))



def compare_ids(rsa_dict, condition, task, csv_df, csv_name):
    rsa_ids = {str(k).zfill(2) for k in rsa_dict[condition][task].keys()}

    if csv_name in {'ib_s', 'ibr_s'}:
        csv_ids = {str(i).zfill(2) for i in csv_df['id']}
    else:
        csv_ids = {str(i - 100).zfill(2) for i in csv_df['id']}

    mutual_ids = rsa_ids & csv_ids
    return mutual_ids



def compare_ids_any_condition(rsa_dict, task, csv_df, csv_name):
    """Get IDs present in csv AND in at least one condition in rsa_dict."""
    
    # Union of IDs across all conditions
    rsa_ids_any = set()
    for condition in rsa_dict.keys():
        rsa_ids_any |= {str(k).zfill(2) for k in rsa_dict[condition][task].keys()}

    if csv_name in {'ib_s', 'ibr_s'}:
        csv_ids = {str(i).zfill(2) for i in csv_df['id']}
    else:
        csv_ids = {str(i - 100).zfill(2) for i in csv_df['id']}

    return rsa_ids_any & csv_ids


# --- Usage ---
for task in ['distress', 'freeplay', 'reunion']:
    mutual_ib_s    = compare_ids_any_condition(rsa_dict, task, ib_s, 'ib_s')
    mutual_ibr_s   = compare_ids_any_condition(rsa_dict, task, ibr_s, 'ibr_s')
    mutual_ib_s_18 = compare_ids_any_condition(rsa_dict, task, ib_s_18mo, 'ib_s_18mo')
    mutual_ibr_s_18= compare_ids_any_condition(rsa_dict, task, ibr_s_18mo, 'ibr_s_18mo')

    print(f"\n{task}:")
    print(f"  ib_s:       {len(mutual_ib_s)}")
    print(f"  ibr_s:      {len(mutual_ibr_s)}")
    print(f"  ib_s_18mo:  {len(mutual_ib_s_18)}")
    print(f"  ibr_s_18mo: {len(mutual_ibr_s_18)}")

