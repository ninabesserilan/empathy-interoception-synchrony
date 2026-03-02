import pandas as pd

def channel_stats_df(data_dict, participant, group, condition, with_all_indices= False):
    """
    Returns a DataFrame with dyad_id as index and columns like:
    ch_0_mean, ch_0_std, ch_0_min, ch_0_max, ch_0_count, ch_1_mean, ...
    """
    all_dyads = {}

    for dyad_id, dyad_data in data_dict[group].items():
        if condition not in dyad_data or participant not in dyad_data[condition]:
            continue

        participant_channels = dyad_data[condition][participant]
        dyad_stats = {}

        for channel_name, channel_dict in participant_channels.items():
            series = channel_dict['data']
            # ensure it's always treated as a pandas Series
            if not isinstance(series, pd.Series):
                series = pd.Series([series])

            dyad_stats[f"{channel_name}_mean"] = series.mean()
            dyad_stats[f"{channel_name}_std"] = series.std()
            dyad_stats[f"{channel_name}_min"] = series.min()
            dyad_stats[f"{channel_name}_max"] = series.max()
            dyad_stats[f"{channel_name}_lenght"] = len(series)
            dyad_stats[f"{channel_name}_above_1000"] = (series > 1000).sum()  # new counter

        all_dyads[dyad_id] = dyad_stats

    df = pd.DataFrame.from_dict(all_dyads, orient='index')
    df.index = df.index.astype(int)
    df = df.sort_index()

    df.index.name = f'dyad_id ({len(all_dyads)} dyads)'

    cols = df.columns
    order = (
        sorted([c for c in cols if c.endswith("lenght")]) +
        sorted([c for c in cols if c.endswith("mean")]) +
        sorted([c for c in cols if c.endswith("std")]) +
        sorted([c for c in cols if c.endswith("min")]) +
        sorted([c for c in cols if c.endswith("max")]) +
        sorted([c for c in cols if c.endswith("above_1000")])
    )
    df = df[order]
    
    if with_all_indices == True:
        df = df.reindex(range(1, 91))

    return df

