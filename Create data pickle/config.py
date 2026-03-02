Config_03_json_empathy_9 = { 

'folder_path': '/Users/nina/Desktop/University of Vienna/PhD projects/Interoception and physiological synchrony/Empathy data/03_ibi_after_manual_coding_should_be_json/dashboardOutputData_emp_9mo - jason', 
 
 'save_path': '/Users/nina/Desktop/University of Vienna/PhD projects/python code/Empathy-interoception-synchrony/Files data',

 'json_prefix': '03_json_after_manual_coding_9_month',

 'peaks_prefix': '03_peaks_after_manual_coding_9_month',
 
 'participant': { 'mom': 'ecg1','infant': 'ecg2'},
 
 'condition': { 
 'hammer': ['hammer','empathyhammer'], 
 'chair': ['chair','chiar', 'knee', 'empathychair', 'empathyknee'], 
 'not play': 'nplaying', 
 'no book': 'nbook', 
 'neutral': ['neutral', 'empathyneutral']},

 'channel': { 
     'ch_0': ['ch1','_channel0'], 
     'ch_1': ['ch2','_channel1'], 
     'ch_2': ['ch3','_channel2']}
     }


Config_03_json_empathy_18 = { 

'folder_path': '/Users/nina/Desktop/University of Vienna/PhD projects/Interoception and physiological synchrony/Empathy data/03_ibi_after_manual_coding_should_be_json/dashboardInputData_emp18 - jason', 
'save_path': '/Users/nina/Desktop/University of Vienna/PhD projects/python code/Empathy-interoception-synchrony/Files data',

 'json_prefix': '03_json_after_manual_coding_18_month',

 'peaks_prefix': '03_peaks_after_manual_coding_18_month',
 
 'participant': { 'mom': 
                 ['ecg1', 'ECG1'],
                 'infant': ['ecg2', 'ECG2']},
 
    
 'condition': { 
    'hammer': ['hammer','empathyhammer'], 
    'chair': ['chair','chiar', 'empathychair', 'empathyknee' ]},

'task': {
    'distress': 'distress',
    'freeplay': 'freeplay',
    'reunion': 'reunion'},


 'channel': { 
     'ch_0': ['ch1','_channel0'], 
     'ch_1': ['ch2','_channel1'], 
     'ch_2': ['ch3','_channel2']}
     }
