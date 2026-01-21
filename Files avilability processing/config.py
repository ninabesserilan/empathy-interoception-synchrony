
folder_paths = {
   '01_ibi_after_extraction': "Q:\\hoehl\\projects\\mibo_p\\Physiological_Synchrony\\data\\01_ibi_after_extraction_from_xdf\\ibiData - with Moritz data - WE USE THIS",
   '03_ibi_empathy_data_9_month': "Q:\\hoehl\\projects\\mibo_p\\Physiological_Synchrony\\data\\03_ibi_after_manual_coding_should_be_json\\dashboardOutputData_emp_9mo - jason",
   '03_ibi_empathy_data_18_month':"Q:\\hoehl\\projects\\mibo_p\\Physiological_Synchrony\\data\\03_ibi_after_manual_coding_should_be_json\\dashboardInputData_emp18 - jason",
   '01_ibi_empathy_data_9_month': "Q:\\hoehl\\projects\\mibo_p\\Physiological_Synchrony\\data\\01_ibi_after_extraction_from_xdf\\empathy_9mo - csv"
}

Config_01_ibi_after_extraction = {

    'analysis_stage': '01_ibi_after_extraction',

    'data_type': {
        'ibis': 'ibis',
        'peaks': 'peaks',
    },
    'group': {
        '9_months': 'wp3_0',   
        '18_months': 'wp3_1',  
    },
    'condition': {
        'toys': 'wtoys',
        'no_toys': 'wotoys',
        'book': 'book',
        'puzzle': 'puzzle',
    },
    'participant': {
        'mom': 'ECG1', # NEW 13.10.25 - switch between infant and mom
        'infant': 'ECG2',
    },
    'channel': {
        'ch_0': 'channel0',
        'ch_1': 'channel1',
        'ch_2': 'channel2',
    }
}


Config_03_jason_ibi_empathy_data = {
    
    'analysis_stage': '03_ibi_after_manual_coding',

    'data_type': {
        'ibis': 'ibis',
        'peaks': 'peaks'},


    'example_for_file_names' : 
    {'9_month_name': 'empathy_006_empathyhammer_ECG2_channel2', 
    '18_month_name': '136_empathy_chair_ecg1_reunion_ch3_ecg'},

    'group': {'9_months': '9',   
        '18_months': '18'}, 

    'condition': {
        'hammer': 'hammer',
        'chair': ['chair', 'chiar', 'knee'],
        'not play': 'nplaying',
        'no book': 'nbook',
        'neutral': 'neutral'},

    'session type': {
        'distress': 'distress',
        'freeplay': 'freeplay',
        'reunion': 'reunion'},

    'participant': { 'mom': 'ecg1','infant': 'ecg2'}, # NEW 13.10.25 - switch between infant and mom

    'channel': { 
        'ch_0': ['ch1','_channel0'], 
        'ch_1': ['ch2','_channel1'], 
        'ch_2': ['ch3','_channel2']}
}



Config_01_csv_ibi_empathy_data = {

    'analysis_stage': '01_ibi_after_extraction',

    'data_type': {
        'ibis': 'ibis',
        'peaks': 'peaks'},



    'group': {'9_months': '9_emp'}, 
        
    'condition': {
        'hammer': 'hammer',
        'chair': ['chair', 'chiar', 'knee'],
        'not play': 'nplaying',
        'no book': 'nbook',
        'neutral': 'neutral'},

    'session type': {
        'distress': 'distress',
        'freeplay': 'freeplay',
        'reunion': 'reunion'},

    'participant': { 'mom': 'ecg1','infant': 'ecg2'}, # NEW 13.10.25 - switch between infant and mom

    'channel': { 
        'ch_0': ['ch1','_channel0'], 
        'ch_1': ['ch2','_channel1'], 
        'ch_2': ['ch3','_channel2']}
    }




