import os
import pandas as pd


def build_empathy_dict(folder:str, age_group:str, config:dict, with_all_indices:bool= False, is_saving:bool = False):
    # Initialize the outer dictionary
    outer_dict = {
        f'infant {age_group} month empathy': {},
        f'mom {age_group} month empathy': {}
    }
    
    # Helper to get dyad id
    def get_dyad_id(filename, age_group):

        if age_group == '9_emp':
            parts = filename.split("_")
            return parts[2][-2:]
        
        else:

            if age_group == '9':
                parts = filename.split("_")
                return parts[1][-2:]
            else:
                parts = filename.split("_")
                return parts[0][-2:] 
    
    # Helper to get participant
    def get_participant(filename):
        for key, value in config['participant'].items():
            if value.lower() in filename.lower():
                return key

    # Helper to get condition
    def get_condition(filename):
        for key, values in config['condition'].items():
            if isinstance(values, list):
                if any(v.lower() in filename.lower() for v in values):
                    return key
            else:
                if values.lower() in filename.lower():
                    return key

    # Helper to get empathy session
    def get_session_type(filename, age_group):
        if age_group == '18':
            for key, val in config['session type'].items():
                if val.lower() in filename.lower():
                    return key
    
    # Helper to get channel
    def get_channel(filename):
        for key, values in config['channel'].items():
            if any(v in filename for v in values):
                return key

  
    def init_hierarchy(age_group):
        """Condition -> session type -> list of channels"""
        hierarchy = {}
        for cond in config['condition'].keys():
            if age_group == '18':
                hierarchy[cond] = {}
                for sess in config['session type'].keys():
                    hierarchy[cond][sess] = []     
            else:
                hierarchy[cond] = []
          
        return hierarchy

    
    def prune_empty_lists(dic):
        for key in list(dic.keys()):
            value = dic[key]
            if isinstance(value, dict):
                prune_empty_lists(value)
                if not value:
                    del dic[key]
            elif isinstance(value, list) and not value:
                del dic[key]
        return dic
    
    def dict_to_str(d):
        s = str(d)
        # remove the first and last curly braces
        if s.startswith("{") and s.endswith("}"):
            s = s[1:-1]
        return s

    
    for file in os.listdir(folder):
        dyad_id = get_dyad_id(file, age_group)
        participant = get_participant(file)
        condition = get_condition(file)
        session_type = get_session_type(file, age_group)
        channel = get_channel(file)

        outer_key = f"{participant} {age_group} month empathy"
        print(dyad_id)
        print(participant)
        print(condition)
        print(session_type)
        print(channel)
        print(outer_key)

        
        if dyad_id not in outer_dict[outer_key]:
            outer_dict[outer_key][dyad_id] = init_hierarchy(age_group)
        
        # Append channel only if valid
        if age_group == '18':
            if channel not in outer_dict[outer_key][dyad_id][condition][session_type]:
                outer_dict[outer_key][dyad_id][condition][session_type].append(channel)

        else:
            if channel not in outer_dict[outer_key][dyad_id][condition]:
                outer_dict[outer_key][dyad_id][condition].append(channel)

            
    dic = prune_empty_lists(outer_dict)

    #  Build a DataFrame where rows = dyad_id, columns = participants


    rows = {}
    for participant_col, dyads in dic.items():
        for dyad_id, content in dyads.items():
            if dyad_id not in rows:
                rows[dyad_id] = {}
            rows[dyad_id][participant_col] = content

    out_df = pd.DataFrame.from_dict(rows, orient="index")
    out_df.index.name = "dyad_id"
    out_df.index = out_df.index.astype(int)
    out_df = out_df.sort_index()

    if with_all_indices:
        out_df = out_df.reindex(range(1, 91))
    
    if is_saving:

        out_df_str = out_df.applymap(lambda x: dict_to_str(x) if isinstance(x, dict) else x)

        file_name = f'Empathy Availability {age_group} month.xlsx'
        with pd.ExcelWriter(file_name) as writer:
            out_df_str.to_excel(writer, sheet_name=config['analysis_stage'])

    return dic, out_df_str


