#%% Description

"""
C6 under July 2024 conditions

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

foldername = 'C6_validation'
parameters_set = {
        'file_path': os.path.join(cwd, 'code', 'calibration', 'busca_sfr_data_nseg.xlsx'),
        'modelname': 'busca_base_infittito_luglio_DRN',
        'model_ws': os.path.join(cwd, 'models', 'Busca_SFR_luglio'),
        'seg_t': 1,
        'seg_a': [2,3,4,5,6,7,8],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
            'kt': [5.5e-5], 
            'ka': [5.5e-6] 
        },
        's_dict': {
                'st_start': [0.001592],
                'sa_start': [0.001592,0.000284,0.000652,0.00304,0.001778,0.001764,0.00776],
                's_coeff': [-0.5]
        },
        'geom': 'nSEG',
        'elev': 'LIDAR',
        'icalc': 2,
        'n': [0.080],
        'reach': 1,
        'segment': 3,
        'flow_target': 0.0541,  # m3/s
        'depth_target': 0.40,   # m
        'silent': True
}

#%% Run

sfr = SFRCalibrator(parameters_set)
sfr.n_runs_modified()
sfr.load()

i=0
if sfr.geom == '2SEG':
        for kt in sfr.k_dict['kt']:
                tool = pd.DataFrame(sfr.reach_data).copy()
                tool.loc[sfr.find_cond(True), 'strhc1'] = kt
                for ka in sfr.k_dict['ka']:
                        tool.loc[sfr.find_cond(False), 'strhc1'] = ka
                        for st_coeff in sfr.s_dict['s_coeff']:
                                st = sfr.s_dict['st_start'][0]
                                tool.loc[sfr.find_cond(True), 'slope'] = st+st*st_coeff
                                for coeff in sfr.s_dict['s_coeff']:
                                        sa = sfr.s_dict['sa_start'][0]
                                        tool.loc[sfr.find_cond(False), 'slope'] = sa+sa*coeff
                                        for n in sfr.n:
                                                segment_data = pd.DataFrame(sfr.segment_data[0]).copy()
                                                segment_data.roughch = n
                                                if sfr.icalc == 2:
                                                        segment_data.roughbk = n
                                                
                                                sfr.set_package(reach_data=tool, segment_data=segment_data)

                                                sfr.store_params(params = [kt, ka, st_coeff, coeff, n],
                                                                labels = ['kt', 'ka', 'st_coeff', 'sa_coeff', 'n'],
                                                                modelcode = f'M{i}')
                                                
                                                sfr.run()

                                                sfr.load_results()

                                                sfr.save_results(i, foldername = foldername)
                                                # Progress the counter to generate the model code
                                                i += 1
elif sfr.geom == 'nSEG':
        columns = ['m_code', 'kt','ka', 'st', 'n'] + [f'sa{x}' for x in range(1, len(sfr.seg_a)+1)] + ['flow_out_reach', 'stream_depth']
        for kt in sfr.k_dict['kt']:
                # Transform reach_data to a pandas.DataFrame
                tool = pd.DataFrame(sfr.reach_data).copy()
                # Change hydraulic conductivity and slope in the segments
                if not sfr.tseg:
                        tool.loc[(tool.iseg == sfr.seg_t) & (tool.ireach <= sfr.reach_t), 'strhc1'] = kt
                else:
                        tool.loc[tool.iseg == sfr.seg_t, 'strhc1'] = kt
                for ka in sfr.k_dict['ka']:
                        tool.loc[tool.iseg != sfr.seg_t, 'strhc1'] = ka
                        if not sfr.tseg:
                                tool.loc[(tool.iseg == sfr.seg_t) & (tool.ireach > sfr.reach_t), 'strhc1'] = ka
                        for st_coeff in sfr.s_dict['s_coeff']:
                                st = sfr.s_dict['st_start'][0]
                                if not sfr.tseg:
                                        tool.loc[(tool.iseg == sfr.seg_t) & (tool.ireach <= sfr.reach_t), 'slope'] = st+st*st_coeff
                                else:
                                        tool.loc[tool.iseg == sfr.seg_t, 'slope'] = st+st*st_coeff
                                for coeff in sfr.s_dict['s_coeff']:
                                        for j, s in enumerate(sfr.seg_a):
                                                if s == sfr.seg_t and not sfr.tseg:
                                                        tool.loc[(tool.iseg == s) & (tool.ireach > sfr.reach_t), 'slope'] = sfr.s_dict['sa_start'][j]+sfr.s_dict['sa_start'][j]*coeff
                                                else:
                                                        tool.loc[tool.iseg == s, 'slope'] = sfr.s_dict['sa_start'][j]+sfr.s_dict['sa_start'][j]*coeff
                                        for n in sfr.n:
                                                segment_data = pd.DataFrame(sfr.segment_data[0]).copy()
                                                segment_data.roughch = n
                                                if sfr.icalc == 2:
                                                        segment_data.roughbk = n

                                                sfr.set_package(reach_data=tool, segment_data=segment_data)

                                                sfr.store_params(params = [kt, ka, st_coeff, coeff,  n],
                                                                labels = ['kt', 'ka', 'st_coeff', 'sa_coeff', 'n'],
                                                                modelcode=f'M{i}')

                                                sfr.run()

                                                sfr.load_results()

                                                sfr.save_results(i, foldername = foldername)
                                                # Progress the counter to generate the model code
                                                i += 1

# sfr.save_results(i, overpass = True, foldername = foldername)