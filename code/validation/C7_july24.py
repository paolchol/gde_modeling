#%% Description

"""
C7 under July 2024 conditions

"""

#%% Setup

import datetime
import os
import pandas as pd
import sys

cwd = '\\'.join(os.getcwd().split('\\')[:-2])
sys.path.insert(1, os.path.join(cwd, 'code', 'calibration'))
from SFRCalibration import *

#%% Define parameters

foldername = 'C7_validation'
parameters_set = {
        'file_path': os.path.join(cwd, 'code', 'calibration', 'busca_lak_data_laksfr.xlsx'),
        'modelname': 'busca_base_infittito_lug24_sfr_icalc2_lake_quotaGNSS_NP',
        'model_ws': os.path.join(cwd, 'models', 'Busca_LAK_SFR_luglio'),
        'seg_t': None,
        'seg_a': [1,2,3,4,5,6,7],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
            'kt': [1e-5], 
            'ka': [1e-5] 
        },
        's_dict': {
                'st_start': [None],
                'sa_start': [0.001592,0.000284,0.000652,0.00304,0.001778,0.001764,0.00776],
                's_coeff': [-0.5]
        },
        'geom': 'nSEG',
        'elev': 'GNSS',
        'icalc': 1,
        'n': [0.080],
        'reach': 1,
        'segment': 2,
        'flow_target': 0.0541,  # m3/s
        'depth_target': 0.40,   # m
        'silent': True
}

laktemplate = 'lak_template.txt'

#%% Run

i = 0
start = datetime.datetime.now()
lak = LAKSFRCalibrator(parameters_set)
lak.load()
lak.sfr.n_runs_modified(lak = True)

for kt in lak.k_dict['kt']:
        # Change LAK leakance
        lak.set_lak_leakance(k = kt, thickness=0.5)
        for ka in lak.k_dict['ka']:
                tool = pd.DataFrame(lak.sfr.reach_data).copy()
                tool.loc[:, 'strhc1'] = ka
                for coeff in lak.sfr.s_dict['s_coeff']:
                        for j, s in enumerate(lak.sfr.seg_a):
                                tool.loc[tool.iseg == s, 'slope'] = lak.sfr.s_dict['sa_start'][j]+lak.sfr.s_dict['sa_start'][j]*coeff
                        for n in lak.sfr.n:
                                segment_data = pd.DataFrame(lak.sfr.segment_data[0]).copy()
                                segment_data.roughch = n
                                if lak.sfr.icalc == 2:
                                        segment_data.roughbk = n

                                lak.set_packages(laktemplate, reach_data=tool, segment_data=segment_data)

                                lak.sfr.store_params(params = [kt, ka, coeff, n],
                                                labels = ['kt','ka', 'sa_coeff', 'n'],
                                                modelcode=f'M{i}')

                                lak.sfr.run()

                                lak.sfr.load_results()

                                lak.sfr.save_results(i, foldername=foldername)
                                # Progress the counter to generate the model code
                                i += 1
# lak.sfr.save_results(i-1, overpass = True)

end = datetime.datetime.now()
print('Runs terminated')
print('Run code: ')
print('Number of runs: ', i-1)
elapsed = end - start
print('Elapsed time (s): ', f'{elapsed.total_seconds():.4f}')
print('Elapsed time (h): ', f'{elapsed.total_seconds()/3600:.6f}')