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
        'file_path': os.path.join(cwd, 'runs', 'busca_sfr_data_2seg.xlsx'),
        'modelname': 'busca_base_infittito_apr24_sfr_icalc1',
        'model_ws': os.path.join(cwd, 'models', 'Busca_SFR_0'),
        'seg_t': 1,
        'seg_a': [2],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
            'kt': [1e-5, 5.5e-5, 1e-4, 5.5e-4, 1e-3], 
            'ka': [1e-6, 5.5e-6, 1e-5, 5.5e-5, 1e-4] 
        },
        's_dict': {
                'st': [0.0033, 0.0022,	0.0011],
                'sa': [0.0033, 0.0022,	0.0011]
        },
        'geom': '2SEG',
        'icalc': 1,
        'elev': 'GNSS',
        'reach': 62,
        'segment': 2,
        'flow_target': 0.019,  # m3/s
        'depth_target': 0.20,   # m
        'silent': True,
        'n': [0.030, 0.035, 0.040]
    },
    1: {
        'file_path': os.path.join(cwd, 'runs', 'busca_sfr_data_2seg.xlsx'),
        'modelname': 'busca_base_infittito_apr24_sfr_icalc1',
        'model_ws': os.path.join(cwd, 'models', 'Busca_SFR_1'),
        'seg_t': 1,
        'seg_a': [2],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
            'kt': [1e-5, 5.5e-5, 1e-4, 5.5e-4, 1e-3], 
            'ka': [1e-6, 5.5e-6, 1e-5, 5.5e-5, 1e-4] 
        },
        's_dict': {
                'st': [0.0033, 0.0022,	0.0011],
                'sa': [0.0033, 0.0022,	0.0011]
        },
        'geom': '2SEG',
        'icalc': 1,
        'elev': 'LIDAR',
        'reach': 62,
        'segment': 2,
        'flow_target': 0.019,  # m3/s
        'depth_target': 0.20,   # m
        'silent': True,
        'n': [0.030, 0.035, 0.040]
    },
    2: {
        'file_path': os.path.join(cwd, 'runs', 'busca_sfr_data_nseg.xlsx'),
        'modelname': 'busca_base_infittito_apr24_sfr_icalc1',
        'model_ws': os.path.join(cwd, 'models', 'Busca_SFR_2'),
        'seg_t': 1,
        'seg_a': [2,3,4,5,6,7,8],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
            'kt': [1e-5, 5.5e-5, 1e-4, 5.5e-4, 1e-3], 
            'ka': [1e-6, 5.5e-6, 1e-5, 5.5e-5, 1e-4] 
        },
        's_dict': {
                'st': [0.002388,	0.001592,	7.96E-04],
                'sa': [
                    [0.002388,	0.001592,	7.96E-04],
                    [0.000426,	0.000284,	1.42E-04],
                    [0.000978,	0.000652,	3.26E-04],
                    [0.00456,	0.00304,	1.52E-03],
                    [0.002667,	0.001778,	8.89E-04],
                    [0.002646,	0.001764,	8.82E-04],
                    [0.01164,	0.00776,	3.88E-03]]
        },
        'geom': 'nSEG',
        'elev': 'LIDAR',
        'icalc': 1,
        'reach': 1,
        'segment': 3,
        'flow_target': 0.019,  # m3/s
        'depth_target': 0.20,   # m
        'silent': True,
        'n': [0.030, 0.035, 0.040]
    },
    3: {
        'file_path': os.path.join(cwd, 'runs', 'busca_sfr_data_nseg.xlsx'),
        'modelname': 'busca_base_infittito_apr24_sfr_icalc1',
        'model_ws': os.path.join(cwd, 'models', 'Busca_SFR_3'),
        'seg_t': 1,
        'seg_a': [2,3,4,5,6,7,8],
        'tseg': True,
        'reach_t': 9,
        'k_dict': {
            'kt': [1e-5, 5.5e-5, 1e-4, 5.5e-4, 1e-3], 
            'ka': [1e-6, 5.5e-6, 1e-5, 5.5e-5, 1e-4] 
        },
        's_dict': {
                'st': [0.002388,	0.001592,	7.96E-04],
                'sa': [
                    [0.002388,	0.001592,	7.96E-04],
                    [0.000426,	0.000284,	1.42E-04],
                    [0.000978,	0.000652,	3.26E-04],
                    [0.00456,	0.00304,	1.52E-03],
                    [0.002667,	0.001778,	8.89E-04],
                    [0.002646,	0.001764,	8.82E-04],
                    [0.01164,	0.00776,	3.88E-03]]
        },
        'geom': 'nSEG',
        'elev': 'LIDAR',
        'icalc': 2,
        'n': [0.030, 0.035, 0.040],
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
        sfr.n_runs()
        sfr.load()
        
        if sfr.geom == '2SEG':
                for kt in sfr.k_dict['kt']:
                        tool = pd.DataFrame(sfr.reach_data).copy()
                        tool.loc[sfr.find_cond(True), 'strhc1'] = kt
                        for ka in sfr.k_dict['ka']:
                                tool.loc[sfr.find_cond(False), 'strhc1'] = ka
                                for st in sfr.s_dict['st']:
                                        tool.loc[sfr.find_cond(True), 'slope'] = st
                                        for sa in sfr.s_dict['sa']:
                                                tool.loc[sfr.find_cond(False), 'slope'] = sa
                                                for n in sfr.n:
                                                        segment_data = pd.DataFrame(sfr.segment_data[0]).copy()
                                                        segment_data.roughch = n
                                                        if sfr.icalc == 2:
                                                                segment_data.roughbk = n
                                                        
                                                        sfr.set_package(reach_data=tool, segment_data=segment_data)

                                                        sfr.store_params(params = [kt, ka, st, sa, n],
                                                                        labels = ['kt','ka', 'st', 'sa', 'n'],
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
                                for st in sfr.s_dict['st']:
                                        if not sfr.tseg:
                                                tool.loc[(tool.iseg == sfr.seg_t) & (tool.ireach <= sfr.reach_t), 'slope'] = st
                                        else:
                                                tool.loc[tool.iseg == sfr.seg_t, 'slope'] = st
                                        for sa1 in sfr.s_dict['sa'][0]:
                                                if sfr.seg_a[0] == sfr.seg_t and not sfr.tseg:
                                                        tool.loc[(tool.iseg == sfr.seg_a[0]) & (tool.ireach > sfr.reach_t), 'slope'] = sa1
                                                else:
                                                        tool.loc[tool.iseg == sfr.seg_a[0], 'slope'] = sa1
                                                for sa2 in sfr.s_dict['sa'][1]:
                                                        tool.loc[tool.iseg == sfr.seg_a[1], 'slope'] = sa2
                                                        for sa3 in sfr.s_dict['sa'][2]:
                                                                tool.loc[tool.iseg == sfr.seg_a[2], 'slope'] = sa3
                                                                for sa4 in sfr.s_dict['sa'][3]:
                                                                        tool.loc[tool.iseg == sfr.seg_a[3], 'slope'] = sa4
                                                                        for sa5 in sfr.s_dict['sa'][4]:
                                                                                tool.loc[tool.iseg == sfr.seg_a[4], 'slope'] = sa5                                    
                                                                                for sa6 in sfr.s_dict['sa'][5]:
                                                                                        tool.loc[tool.iseg == sfr.seg_a[5], 'slope'] = sa6
                                                                                        for sa7 in sfr.s_dict['sa'][6]:
                                                                                                tool.loc[tool.iseg == sfr.seg_a[6], 'slope'] = sa7
                                                                                                for n in sfr.n:
                                                                                                        segment_data = pd.DataFrame(sfr.segment_data[0]).copy()
                                                                                                        segment_data.roughch = n
                                                                                                        if sfr.icalc == 2:
                                                                                                                segment_data.roughbk = n

                                                                                                        sfr.set_package(reach_data=tool, segment_data=segment_data)

                                                                                                        sas = [st, sa1, sa2, sa3, sa4, sa5, sa6, sa7]
                                                                                                        sfr.store_params(params = [kt, ka, n] + sas,
                                                                                                                        labels = ['kt','ka', 'n', 'st'] + [f'sa{x}' for x in range(1, len(sfr.seg_a)+1)],
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
