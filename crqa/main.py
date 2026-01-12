import pandas as pd
from pathlib import Path
import numpy as np
from scipy.stats import norm
from scipy.stats import pearsonr


result_file = Path('/Users/nina/Desktop/University of Vienna/PhD projects/phy_synch_interoception/only toys crqa results.xlsx')

data= pd.read_excel(result_file)



def bayesian_corr(x, y, prior_mean=0, prior_sd=1):
    # Drop NaNs pairwise
    mask = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[mask], y[mask]
    
    n = len(x)
    if n < 3:
        return np.nan

    # Sample Pearson correlation
    r = np.corrcoef(x, y)[0, 1]

    # Fisher z-transform
    z = np.arctanh(r)
    se = 1 / np.sqrt(n - 3)

    # Posterior (Normal-Normal conjugacy)
    post_var = 1 / (1 / prior_sd**2 + 1 / se**2)
    post_mean = post_var * (prior_mean / prior_sd**2 + z / se**2)

    # Back-transform to correlation space
    return np.tanh(post_mean)





det_col = 'det'
interoception_cols = ['ib_score_9',	'ib_maister_score_9',	'ibr_score_9',	'ibr_maister_score_9',	'ibr_score_18',	'ibr_maister_score_18',	'ib_score_18',	'ib_maister_score_18']
# corr_dict_base = {}
# corr_dict_pearson = {}



# for i in interoception_cols:
#     corr_dict_base[i] = bayesian_corr(data[det_col].to_numpy(), data[i].to_numpy())
#     corr_dict_pearson[i] = (data[det_col]).corr(data[i], method='pearson')




corr_dict_base = {}
corr_dict_pearson = {}

for col in interoception_cols:
    # Drop NaNs pairwise
    tmp = data[[det_col, col]].dropna()
    
    if len(tmp) < 2:
        corr_dict_pearson[col] = (np.nan, np.nan)
        corr_dict_base[col] = np.nan
        continue

    # Pearson r and p-value
    r, p = pearsonr(tmp[det_col], tmp[col])
    corr_dict_pearson[col] = (r, p)

    # Bayesian correlation (already NaN-safe)
    corr_dict_base[col] = bayesian_corr(
        tmp[det_col].to_numpy(),
        tmp[col].to_numpy()
    )
