import pickle
import pandas as pd



pickle_path_9m = '/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Files data/03_peaks_after_manual_coding_9_month.pkl'

with open(pickle_path_9m, "rb") as f_ibis:
    data_9 = pickle.load(f_ibis)




def check_peaks_increasing(data):
    """
    Checks if 'peaks' lists are strictly increasing for every
    participant ('infant'/'mom') > condition > subject > channel combination.
    Reports any that are NOT strictly increasing.
    """
    participants = ['infant', 'mom']
    non_increasing = []

    for participant in participants:
        if participant not in data:
            print(f"⚠️  Participant group '{participant}' not found in data, skipping.")
            continue

        for condition, subjects in data[participant].items():
            for subject, channels in subjects.items():
                for channel, channel_data in channels.items():
                    peaks = channel_data.get('peaks', None)

                    if peaks is None or len(peaks) < 2:
                        continue  # skip if no peaks or only one value

                    # Flag if ANY decrease exists
                    is_increasing = all(
                        peaks[i] < peaks[i + 1] for i in range(len(peaks) - 1)
                    )

                    if not is_increasing:
                        # Find exactly where the decrease(s) happen
                        drops = [
                            f"{peaks[i]} → {peaks[i+1]}"
                            for i in range(len(peaks) - 1)
                            if peaks[i] >= peaks[i + 1]
                        ]
                        non_increasing.append({
                            'participant': participant,
                            'condition':   condition,
                            'subject':     subject,
                            'channel':     channel,
                            'peaks':       peaks,
                            'drops_at':    ', '.join(drops)
                        })

    # --- Console output ---
    if not non_increasing:
        print("✅ All peaks are strictly increasing across all subjects/channels.")
    else:
        print(f"⚠️  Found {len(non_increasing)} case(s) where peaks are NOT strictly increasing:\n")
        for entry in non_increasing:
            print(
                f"  Participant : {entry['participant']}\n"
                f"  Condition   : {entry['condition']}\n"
                f"  Subject     : {entry['subject']}\n"
                f"  Channel     : {entry['channel']}\n"
                f"  Peaks       : {entry['peaks']}\n"
                f"  Drops at    : {entry['drops_at']}\n"
                f"  {'-'*40}"
            )

    # --- CSV output ---
    df = pd.DataFrame(non_increasing)
    output_path = "non_increasing_peaks.csv"
    df.to_csv(output_path, index=False)
    print(f"\n💾 Results saved to '{output_path}'")

    return df


# --- Run it ---
flagged_df = check_peaks_increasing(data_9)


# pickle_path_18m = '/Users/nina/Desktop/University of Vienna/PhD projects/python code/empathy-interoception-synchrony/Files data/03_json_after_manual_coding_18_month.pkl'

# with open(pickle_path_18m, "rb") as f_ibis:
#     data_18 = pickle.load(f_ibis)



# data_9_infant_chair = data_9['infant']['chair']
# data_9_infant_hammer = data_9['infant']['hammer']
# data_9_infant_neutral = data_9['infant']['neutral']
# data_9_infant_nplay = data_9['infant']['not play']
# data_9_infant_nbook = data_9['infant']['no book']

# data_9_mom_chair = data_9['mom']['chair']
# data_9_mom_hammer = data_9['mom']['hammer']
# data_9_mom_neutral = data_9['mom']['neutral']
# data_9_mom_nplay = data_9['mom']['not play']
# data_9_mom_nbook = data_9['mom']['no book']


# data_18_infant_freeplay_chair = data_18['infant']['chair']['freeplay']
# data_18_infant_freeplay_hammer = data_18['infant']['hammer']['freeplay']

# data_18_infant_distress_chair = data_18['infant']['chair']['distress']
# data_18_infant_distress_hammer = data_18['infant']['hammer']['distress']

# data_18_infant_reunion_chair = data_18['infant']['chair']['reunion']
# data_18_infant_reunion_hammer = data_18['infant']['hammer']['reunion']


# data_18_mom_freeplay_chair = data_18['mom']['chair']['freeplay']
# data_18_mom_freeplay_hammer = data_18['mom']['hammer']['freeplay']

# data_18_mom_distress_chair = data_18['mom']['chair']['distress']
# data_18_mom_distress_hammer = data_18['mom']['hammer']['distress']

# data_18_mom_reunion_chair = data_18['mom']['chair']['reunion']
# data_18_mom_reunion_hammer = data_18['mom']['hammer']['reunion']


# Print availability
# print('9 MONTHS:\n')

# print(f"Chair: {len(set(data_9_mom_chair.keys()) & set(data_9_infant_chair.keys()))} dyads\n")

# print(f"Hammer: {len(set(data_9_mom_hammer.keys()) & set(data_9_infant_hammer.keys()))} dyads\n")

# print(f"Dyads with Hammer and Chair: {len((set(data_9_mom_chair.keys()) & set(data_9_infant_chair.keys())) & (set(data_9_mom_hammer.keys()) & set(data_9_infant_hammer.keys())))}\n")

# print(f"Neutral: {len(set(data_9_mom_neutral.keys()) & set(data_9_infant_neutral.keys()))} dyads\n")

# print(f"Dyads with Hammer, Chair and Neutral: {len((set(data_9_mom_chair.keys()) & set(data_9_infant_chair.keys())) & (set(data_9_mom_hammer.keys()) & set(data_9_infant_hammer.keys())) & (set(data_9_mom_neutral.keys()) & set(data_9_infant_neutral.keys())))}\n")

# print(f"Not play: Infants: {len(data_9['infant']['not play'])}, Moms: {len(data_9['mom']['not play'])}\n")

# print(f"No book: Infants: {len(data_9['infant']['no book'])}, Moms: {len(data_9['mom']['no book'])}\n")


# print('18 MONTHS:\n')

# # Chair
# print(f"Chair Freeplay: {len(set(data_18_mom_freeplay_chair.keys()) & set(data_18_infant_freeplay_chair.keys()))} dyads\n")
# print(f"Chair Distress: {len(set(data_18_mom_distress_chair.keys()) & set(data_18_infant_distress_chair.keys()))} dyads\n")
# print(f"Chair Reunion: {len(set(data_18_mom_reunion_chair.keys()) & set(data_18_infant_reunion_chair.keys()))} dyads\n")

# # Hammer
# print(f"Hammer: Freeplay {len(set(data_18_mom_freeplay_hammer.keys()) & set(data_18_infant_freeplay_hammer.keys()))} dyads\n")
# print(f"Hammer Distress : {len(set(data_18_mom_distress_hammer.keys()) & set(data_18_infant_distress_hammer.keys()))} dyads\n")
# print(f"Reunion Hammer: {len(set(data_18_mom_reunion_hammer.keys()) & set(data_18_infant_reunion_hammer.keys()))} dyads\n")

# # Dyads with all conditions
# print(f"Freeplay - Dyads with Hammer and Chair: {len((set(data_18_mom_freeplay_chair.keys()) & set(data_18_infant_freeplay_chair.keys())) & (set(data_18_mom_freeplay_hammer.keys()) & set(data_18_infant_freeplay_hammer.keys())))}\n")
# print(f"Distress - Dyads with Hammer and Chair: {len((set(data_18_mom_distress_chair.keys()) & set(data_18_infant_distress_chair.keys())) & (set(data_18_mom_distress_hammer.keys()) & set(data_18_infant_distress_hammer.keys())))}\n")
# print(f"Reunion - Dyads with Hammer and Chair: {len((set(data_18_mom_reunion_chair.keys()) & set(data_18_infant_reunion_chair.keys())) & (set(data_18_mom_reunion_hammer.keys()) & set(data_18_infant_reunion_hammer.keys())))}\n")

# print(f"Dyads with ALL conditions (Hammer + Chair across Freeplay, Distress, Reunion): {len((set(data_18_mom_freeplay_chair.keys()) & set(data_18_infant_freeplay_chair.keys())) & (set(data_18_mom_freeplay_hammer.keys()) & set(data_18_infant_freeplay_hammer.keys())) & (set(data_18_mom_distress_chair.keys()) & set(data_18_infant_distress_chair.keys())) & (set(data_18_mom_distress_hammer.keys()) & set(data_18_infant_distress_hammer.keys())) & (set(data_18_mom_reunion_chair.keys()) & set(data_18_infant_reunion_chair.keys())) & (set(data_18_mom_reunion_hammer.keys()) & set(data_18_infant_reunion_hammer.keys())))}\n")


# len(data_18_infant_freeplay_chair)+ len(data_18_infant_freeplay_hammer) + len(data_18_infant_distress_chair) + len(data_18_infant_distress_hammer)+ len(data_18_infant_reunion_chair)+ len(data_18_infant_reunion_hammer)