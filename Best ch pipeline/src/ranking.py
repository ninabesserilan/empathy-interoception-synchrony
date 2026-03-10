import numpy as np
import pandas as pd

# -----------------------------
# Rank channels using dicts with tie handling
# -----------------------------
def rank_channels(metrics_per_ch:dict, invalid_channels:list, valid_channels:list, weights = None,):
    """
    Rank channels using weights in a dict-based approach.
    Lower total score = better channel.
    Ties in metric receive equal rank.
    """

    ch_auto_rank = None # Channel that are automatically ranked, without the ranking pipeline
    best_ch = None
    worst_ch = None

    channels_to_rank = metrics_per_ch

    if len(invalid_channels) == 1:
        # One invalid → it's automatically worst
        ch_auto_rank = invalid_channels[0]
        worst_ch = ch_auto_rank
        # channels_to_rank = {ch: metrics_per_ch[ch] for ch in valid_channels if ch in metrics_per_ch}
        channels_to_rank = {
        ch: metrics_per_ch[ch]
        for ch in metrics_per_ch
        if not metrics_per_ch[ch].get('invalid', False)
    }


    elif len(invalid_channels) == 2:
        # Two invalid → valid is automatically best
        ch_auto_rank = valid_channels[0]
        best_ch = ch_auto_rank
        # channels_to_rank = {ch: metrics_per_ch[ch] for ch in invalid_channels if ch in metrics_per_ch}
        channels_to_rank = {
        ch: metrics_per_ch[ch]
        for ch in metrics_per_ch
        if metrics_per_ch[ch].get('invalid', False)}


    directions = {
        'sdrr': False,           # lower is better
        'long_ibi_count': False, # lower is better
    }

    ranks = {ch: {} for ch in channels_to_rank}

    for metric, higher_is_better in directions.items():
        # Sort channels by metric
        ch_vals = [(ch, channels_to_rank[ch][metric]) for ch in channels_to_rank if not np.isnan(channels_to_rank[ch][metric])] 
        sorted_chs = sorted(ch_vals, key=lambda x: x[1], reverse=higher_is_better)

        # Tie-aware ranking
        rank_val = 1
        last_val = None
        for idx, (ch, val) in enumerate(sorted_chs):
            if last_val is not None and val != last_val:
                rank_val = idx + 1
            ranks[ch][metric + '_rank'] = rank_val 
            last_val = val

        # Assign worst rank to channels missing metric or nan
        ranked_chs = {ch for ch, _ in sorted_chs}
        worst_rank = len(sorted_chs) + 1
        for ch in channels_to_rank:
            if ch not in ranked_chs:
                ranks[ch][metric + '_rank'] = worst_rank 

    new_ranks = None
    if ch_auto_rank is not None:
        if best_ch is not None:
            new_ranks = {'sdrr_rank': 1, 'long_ibi_count_rank': 1}
            for ch, metrics in ranks.items():
                for key in metrics:
                    metrics[key] += 1
        elif worst_ch is not None:
            new_ranks = {'sdrr_rank': 3, 'long_ibi_count_rank': 3}
    

    weights_for_rank = weights_calculation(channels_to_rank, weights)
    if ch_auto_rank is not None:
        ranks[ch_auto_rank] = new_ranks

    # Apply weights
    weighted_ranks = {
        ch: {k: v * weights_for_rank.get(k, 1) for k, v in metrics.items()}
        for ch, metrics in ranks.items()
}
    # Compute sum rank per channel
    sum_ranks = {ch: sum(v.values()) for ch, v in weighted_ranks.items()}

    # sort channels by sum_rank (ascending = better)
    sorted_chs = sorted(sum_ranks.keys(), key=lambda ch: sum_ranks[ch])

    # tie-aware sorting within each rank
    final_order = []
    i = 0
    while i < len(sorted_chs):
        ch = sorted_chs[i]
        rank_val = sum_ranks[ch]
        
        # find all channels with the same rank
        tied = [ch]
        j = i + 1
        while j < len(sorted_chs) and sum_ranks[sorted_chs[j]] == rank_val:
            tied.append(sorted_chs[j])
            j += 1
        
        # break tie by length
        tied_sorted = sorted(tied, key=lambda ch: metrics_per_ch[ch].get('length', 0), reverse=True)
        final_order.extend(tied_sorted)
        
        i = j
        # Assign ordinal ranks: 1, 2, 3, ...
    print(final_order)
    best_ch = final_order[0]
    total_ranks = {ch: i + 1 for i, ch in enumerate(final_order)}


    return best_ch, weighted_ranks, total_ranks




def weights_calculation(metrics_per_ch:dict, weights):

    if weights == None:
        weights = {'sdrr_rank': 1.0, 'long_ibi_count_rank': 2.0}


    # Collect all non-NaN long_ibi_count values
    long_ibi_counts = [
        metrics_per_ch[ch]['long_ibi_count']
        for ch in metrics_per_ch
        if not np.isnan(metrics_per_ch[ch]['long_ibi_count'])]


    # If there are at least 2 valid counts, compute relative variability
    if len(long_ibi_counts) >= 2:
        cv = np.std(long_ibi_counts) / np.mean(long_ibi_counts)  # coefficient of variation

        # If long_ibi_count values are similar (<10% variability), give more weight to SDRR and less to long_ibi_count
        if cv < 0.10:
            weights = {'sdrr_rank': 2.0, 'long_ibi_count_rank': 1.0}        

        # else keep current weights
    
    return weights
