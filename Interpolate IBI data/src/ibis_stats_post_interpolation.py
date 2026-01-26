from data_loader import data_loader
from pathlib import Path
import pandas as pd
import openpyxl

parent_dir = Path(__file__).resolve().parent.parent


new_interpolation = Path('/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/Interpolate IBI data/after interpolation_Moritz.pkl')
save_stats_path = parent_dir /'IBIS statistics post interpolation_Moritz.xlsx'

ibis_post_interpolation = data_loader(new_interpolation)

# ### Statistics
infant_toys_stats = pd.DataFrame.from_dict(ibis_post_interpolation['toys']['infant']['refined_best_channel_data']['ibis_after_interpolation']['stats'], orient='index')
mom_toys_stats = pd.DataFrame.from_dict(ibis_post_interpolation['toys']['mom']['refined_best_channel_data']['ibis_after_interpolation']['stats'], orient='index')
infant_notoys_stats = pd.DataFrame.from_dict(ibis_post_interpolation['no_toys']['infant']['refined_best_channel_data']['ibis_after_interpolation']['stats'], orient='index')
mom_notoys_stats = pd.DataFrame.from_dict(ibis_post_interpolation['no_toys']['mom']['refined_best_channel_data']['ibis_after_interpolation']['stats'], orient='index')


with pd.ExcelWriter(save_stats_path, engine="openpyxl") as writer:
    infant_toys_stats.to_excel(writer, sheet_name="Infant_9m_Toys", index=True)
    mom_toys_stats.to_excel(writer, sheet_name="Mom_9m_Toys", index=True)
    infant_notoys_stats.to_excel(writer, sheet_name="Infant_9m_NoToys", index=True)
    mom_notoys_stats.to_excel(writer, sheet_name="Mom_9m_NoToys", index=True)

