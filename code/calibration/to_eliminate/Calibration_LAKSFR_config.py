#%% Setup

import datetime
import os
import pandas as pd

from SFRCalibration import *

#%% Definition of parameters

cwd = '\\'.join(os.getcwd().split('\\')[:-1])

# Calibration parameters
parameters_sets = {
    0: {
        'file_path': os.path.join(cwd, 'runs', 'busca_lak_data_laksfr.xlsx'),
        'modelname': 'busca_base_infittito_apr24_sfr_icalc2_lake_quotaGNSS_NP',
        'model_ws': os.path.join(cwd, 'models', 'Busca_LAK_SFR_0'),
        'seg_t': None,
        'seg_a': [1,2,3,4,5,6,7],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
            'kt': [1e-5, 5.5e-5, 1e-4, 5.5e-4, 1e-3], 
            'ka': [1e-6, 5.5e-6, 1e-5, 5.5e-5, 1e-4] 
        },
        's_dict': {
                'st': [None],
                'sa_coeff': [-0.5, 0, 0.5],
                'sa_start': [0.001592,0.000284,0.000652,0.00304,0.001778,0.001764,0.00776]
        },
        'geom': 'nSEG',
        'elev': 'GNSS',
        'icalc': 1,
        'n': [0.20, 0.030, 0.035, 0.040, 0.50],
        'reach': 1,
        'segment': 2,
        'flow_target': 0.019,  # m3/s
        'depth_target': 0.20,   # m
        'silent': True
    },
        1: {
        'file_path': os.path.join(cwd, 'runs', 'busca_lak_data_laksfr.xlsx'),
        'modelname': 'busca_base_infittito_apr24_sfr_icalc2_lake_quotaGNSS_NP',
        'model_ws': os.path.join(cwd, 'models', 'Busca_LAK_SFR_1'),
        'seg_t': None,
        'seg_a': [1,2,3,4,5,6,7],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
        'kt': [1e-5, 5.5e-5, 1e-4, 5.5e-4, 1e-3], 
        'ka': [1e-6, 5.5e-6, 1e-5, 5.5e-5, 1e-4] 
        },
        's_dict': {
                'st': [None],
                'sa_coeff': [-0.5, -0.25, 0, 0.25, 0.5],
                'sa_start': [0.001592,0.000284,0.000652,0.00304,0.001778,0.001764,0.00776]
        },
        'geom': 'nSEG',
        'elev': 'GNSS',
        'icalc': 2,
        'n': [0.20, 0.030, 0.035, 0.040, 0.50],
        'reach': 1,
        'segment': 2,
        'flow_target': 0.019,  # m3/s
        'depth_target': 0.20,   # m
        'silent': True
    }
}

laktemplate = 'lak_template.txt'

#%% Loop

i = 1
for run in parameters_sets.keys():
        start = datetime.datetime.now()
        lak = LAKSFRCalibrator(parameters_sets[run])
        lak.load()
        lak.sfr.n_runs()
        
        for kt in lak.k_dict['kt']:
                # Change LAK leakance
                lak.set_lak_leakance(k = kt, thickness=0.5)
                for ka in lak.k_dict['ka']:
                        tool = pd.DataFrame(lak.sfr.reach_data).copy()
                        tool.loc[:, 'strhc1'] = ka                
                        for sa1 in lak.sfr.s_dict['sa'][0]:
                                tool.loc[tool.iseg == lak.sfr.seg_a[0], 'slope'] = sa1
                                for sa2 in lak.sfr.s_dict['sa'][1]:
                                        tool.loc[tool.iseg == lak.sfr.seg_a[1], 'slope'] = sa2
                                        for sa3 in lak.sfr.s_dict['sa'][2]:
                                                tool.loc[tool.iseg == lak.sfr.seg_a[2], 'slope'] = sa3
                                                for sa4 in lak.sfr.s_dict['sa'][3]:
                                                        tool.loc[tool.iseg == lak.sfr.seg_a[3], 'slope'] = sa4
                                                        for sa5 in lak.sfr.s_dict['sa'][4]:
                                                                tool.loc[tool.iseg == lak.sfr.seg_a[4], 'slope'] = sa5                                    
                                                                for sa6 in lak.sfr.s_dict['sa'][5]:
                                                                        tool.loc[tool.iseg == lak.sfr.seg_a[5], 'slope'] = sa6
                                                                        for sa7 in lak.sfr.s_dict['sa'][6]:
                                                                                tool.loc[tool.iseg == lak.sfr.seg_a[6], 'slope'] = sa7
                                                                                for n in lak.sfr.n:
                                                                                        segment_data = pd.DataFrame(lak.sfr.segment_data[0]).copy()
                                                                                        segment_data.roughch = n
                                                                                        if lak.sfr.icalc == 2:
                                                                                                segment_data.roughbk = n
                                                                                
                                                                                        lak.set_packages(laktemplate, reach_data=tool, segment_data=segment_data)

                                                                                        sas = [sa1, sa2, sa3, sa4, sa5, sa6, sa7]
                                                                                        lak.sfr.store_params(params = [kt, ka, n] + sas,
                                                                                                        labels = ['kt','ka', 'n'] + [f'sa{x}' for x in range(1, len(lak.seg_a)+1)],
                                                                                                        modelcode=f'M{i}')

                                                                                        lak.sfr.run()

                                                                                        lak.sfr.load_results()

                                                                                        lak.sfr.save_results(i)
                                                                                        # Progress the counter to generate the model code
                                                                                        i += 1       
        lak.sfr.save_results(i-1, overpass = True)

        end = datetime.datetime.now()
        print('Runs terminated')
        print('Run code: ')
        print('Number of runs: ', i-1)
        elapsed = end - start
        print('Elapsed time (s): ', f'{elapsed.total_seconds():.4f}')
        print('Elapsed time (h): ', f'{elapsed.total_seconds()/3600:.6f}')
