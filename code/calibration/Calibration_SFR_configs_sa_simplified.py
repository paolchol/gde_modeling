#%% Setup

import datetime
import os
import pandas as pd

from SFRCalibration import *

#%% Definition of parameters

cwd = '\\'.join(os.getcwd().split('\\')[:-2])

# Calibration parameters
parameters_sets = {
    0: {
        'file_path': os.path.join(cwd, 'code', 'calibration', 'busca_sfr_data_2seg.xlsx'),
        'modelname': 'busca_base_infittito_apr24_sfr_icalc1',
        'model_ws': os.path.join(cwd, 'models', 'Busca_SFR_S'),
        'seg_t': 1,
        'seg_a': [2],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
            'kt': [1e-5, 5.5e-5, 1e-4, 5.5e-4, 1e-3], 
            'ka': [1e-6, 5.5e-6, 1e-5, 5.5e-5, 1e-4]
        },
        's_dict': {
                'st_start': [0.0022],
                'sa_start': [0.0022],
                's_coeff': [-0.5, -0.25, 0, 0.25, 0.5]
        },
        'geom': '2SEG',
        'icalc': 1,
        'elev': 'GNSS',
        'reach': 62,
        'segment': 2,
        'flow_target': 0.019,  # m3/s
        'depth_target': 0.20,   # m
        'silent': True,
        'n': [0.030, 0.035, 0.040, 0.050, 0.080],
    },
    1: {
        'file_path': os.path.join(cwd, 'code', 'calibration', 'busca_sfr_data_2seg.xlsx'),
        'modelname': 'busca_base_infittito_apr24_sfr_icalc1',
        'model_ws': os.path.join(cwd, 'models', 'Busca_SFR_S'),
        'seg_t': 1,
        'seg_a': [2],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
            'kt': [1e-5, 5.5e-5, 1e-4, 5.5e-4, 1e-3], 
            'ka': [1e-6, 5.5e-6, 1e-5, 5.5e-5, 1e-4] 
        },
        's_dict': {
                'st_start': [0.0022],
                'sa_start': [0.0022],
                's_coeff': [-0.5, -0.25, 0, 0.25, 0.5]
        },
        'geom': '2SEG',
        'icalc': 1,
        'elev': 'LIDAR',
        'reach': 62,
        'segment': 2,
        'flow_target': 0.019,  # m3/s
        'depth_target': 0.20,   # m
        'silent': True,
        'n': [0.030, 0.035, 0.040, 0.050, 0.080],
    },
    2: {
        'file_path': os.path.join(cwd, 'code', 'calibration', 'busca_sfr_data_nseg.xlsx'),
        'modelname': 'busca_base_infittito_apr24_sfr_icalc1',
        'model_ws': os.path.join(cwd, 'models', 'Busca_SFR_S'),
        'seg_t': 1,
        'seg_a': [2,3,4,5,6,7,8],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
            'kt': [1e-5, 5.5e-5, 1e-4, 5.5e-4, 1e-3], 
            'ka': [1e-6, 5.5e-6, 1e-5, 5.5e-5, 1e-4] 
        },
        's_dict': {
                'st_start': [0.001592],
                'sa_start': [0.001592,0.000284,0.000652,0.00304,0.001778,0.001764,0.00776],
                's_coeff': [-0.5, -0.25, 0, 0.25, 0.5]
        },
        'geom': 'nSEG',
        'elev': 'LIDAR',
        'icalc': 1,
        'reach': 1,
        'segment': 3,
        'flow_target': 0.019,  # m3/s
        'depth_target': 0.20,   # m
        'silent': True,
        'n': [0.030, 0.035, 0.040, 0.050, 0.080],
    },
    3: {
        'file_path': os.path.join(cwd, 'code', 'calibration', 'busca_sfr_data_nseg.xlsx'),
        'modelname': 'busca_base_infittito_apr24_sfr_icalc1',
        'model_ws': os.path.join(cwd, 'models', 'Busca_SFR_S'),
        'seg_t': 1,
        'seg_a': [2,3,4,5,6,7,8],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
            'kt': [1e-5, 5.5e-5, 1e-4, 5.5e-4, 1e-3], 
            'ka': [1e-6, 5.5e-6, 1e-5, 5.5e-5, 1e-4] 
        },
        's_dict': {
                'st_start': [0.001592],
                'sa_start': [0.001592,0.000284,0.000652,0.00304,0.001778,0.001764,0.00776],
                's_coeff': [-0.5, -0.25, 0, 0.25, 0.5]
        },
        'geom': 'nSEG',
        'elev': 'LIDAR',
        'icalc': 2,
        'n': [0.030, 0.035, 0.040, 0.050, 0.080],
        'reach': 1,
        'segment': 3,
        'flow_target': 0.019,  # m3/s
        'depth_target': 0.20,   # m
        'silent': True
    },
}

#%% Loop

i = 1
for run in parameters_sets.keys():
        start = datetime.datetime.now()
        sfr = SFRCalibrator(parameters_sets[run])
        # sfr.n_runs()
        sfr.n_runs_modified()
        sfr.load()
        
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

                                                        sfr.save_results(i)
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

                                                        sfr.save_results(i)
                                                        # Progress the counter to generate the model code
                                                        i += 1
        
        sfr.save_results(i, overpass = True)

        end = datetime.datetime.now()
        print('Runs terminated')
        print('Run code: ')
        print('Number of runs: ', i)
        elapsed = end - start
        print('Elapsed time (s): ', f'{elapsed.total_seconds():.4f}')
        print('Elapsed time (h): ', f'{elapsed.total_seconds()/3600:.6f}')

# %%
