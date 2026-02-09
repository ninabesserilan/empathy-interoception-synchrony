from pathlib import Path
import pandas as pd
from data_loader import data_loader

pickle_rsa = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/RSA analysis/rsa_pickle.pkl')


rsa_data = data_loader(pickle_rsa)

toys_rsa_data = rsa_data['toys']
notoys_rsa_data = rsa_data['no_toys']



ib_s = pd.read_csv(Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/RSA interoception availability/interoception data/ib_s.csv'))
ibr_s = pd.read_csv(Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/RSA interoception availability/interoception data/ibr_s.csv'))


ib_s_18mo = pd.read_csv(Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/RSA interoception availability/interoception data/ib_s_18mo.csv'))
ibr_s_18mo = pd.read_csv(Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/RSA interoception availability/interoception data/ibr_s_18mo.csv'))



def compare_ids(rsa_dict, csv_df, csv_name):
    rsa_ids = {str(k).zfill(2) for k in rsa_dict.keys()}

    if csv_name in {'ib_s', 'ibr_s'}:
        csv_ids = {str(i).zfill(2) for i in csv_df['id']}
    else:
        csv_ids = {str(i - 100).zfill(2) for i in csv_df['id']}

    mutual_ids = rsa_ids & csv_ids
    return mutual_ids



def compare_ids_all(rsa_dict_toys, rsa_dict_no_toys, csv_df, csv_name):
    rsa_dict_toys_ids = {str(k).zfill(2) for k in rsa_dict_toys.keys()}
    rsa_dict_no_toys_ids = {str(k).zfill(2) for k in rsa_dict_no_toys.keys()}

    if csv_name in {'ib_s', 'ibr_s'}:
        csv_ids = {str(i).zfill(2) for i in csv_df['id']}
    else:
        csv_ids = {str(i - 100).zfill(2) for i in csv_df['id']}

    mutual_ids = rsa_dict_toys_ids & rsa_dict_no_toys_ids & csv_ids
    return mutual_ids



mutual_id_toys_ib_s = compare_ids(toys_rsa_data, ib_s, 'ib_s')
mutual_id_toys_ibr_s =compare_ids(toys_rsa_data, ibr_s, 'ibr_s')

mutual_id_no_toys_ib_s = compare_ids(notoys_rsa_data, ib_s, 'ib_s')
mutual_id_no_toys_ibr_s =compare_ids(notoys_rsa_data, ibr_s, 'ibr_s')


mutual_id_toys_ib_s_18mo =compare_ids(toys_rsa_data, ib_s_18mo, 'ib_s_18mo')
mutual_id_toys_ibr_s_18mo =compare_ids(toys_rsa_data, ibr_s_18mo, 'ibr_s_18mo')

mutual_id_no_toys_ib_s_18mo =compare_ids(notoys_rsa_data, ib_s_18mo, 'ib_s_18mo')
mutual_id_no_toys_ibr_s_18mo =compare_ids(notoys_rsa_data, ibr_s_18mo, 'ibr_s_18mo')


print(len(mutual_id_toys_ib_s))
print(len(mutual_id_toys_ibr_s))
print(len(mutual_id_no_toys_ib_s))
print(len(mutual_id_no_toys_ibr_s))

print(len(mutual_id_toys_ib_s_18mo))
print(len(mutual_id_toys_ibr_s_18mo))
print(len(mutual_id_no_toys_ib_s_18mo))
print(len(mutual_id_no_toys_ibr_s_18mo))


# ib_mutual = compare_ids_all(toys_rsa_data, notoys_rsa_data, ib_s, 'ib_s')
# ibr_mutual = compare_ids_all(toys_rsa_data, notoys_rsa_data, ibr_s, 'ibr_s')