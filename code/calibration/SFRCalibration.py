#%% Setup

# Import necessary packages
import flopy
import math
import numpy as np
import os
import pandas as pd
import re

#%% Functions
def change_type(df, cols, t):
    """
    Change the dtype of selected columns to a given type

    df: pandas.DataFrame
        the dataframe
    cols: str, list of str
        the columns to be changed
    t: str
        the dtype wanted

    Returns:
    df: pandas.DataFrame
    """
    for col in cols:
        df[col] = df[col].astype(t)
    return df

def load_streamflow_dat(f, nsp = 1):
    """
    Load the streamflow.dat file generated as output by MODFLOW

    f: str
        path to the streamflow.dat file
    nsp: int, optional
        number of stress periods of the simulation. 1 works also with stationary models.
        Default is 1
        The option is not yet developed
    
    Returns:
    df: pandas.DataFrame
        dataframe containing the information stored inside streamflow.dat file
    """
    if nsp == 1:
        df = pd.DataFrame()
        with open(f, 'r') as file:
            for row in file.readlines()[8:]:
                r = list(filter(None, row.split(' ')))
                df = pd.concat([df, pd.DataFrame(r).transpose()])
            df.columns = ['l', 'r', 'c', 'iseg', 'ireach', 'flow_into_reach', 'flow_to_aquifer', 'flow_out_reach', 'overlnd_runoff',
                        'direct_precip', 'stream_et', 'stream_head', 'stream_depth', 'stream_width', 'streambed_cond', 'streambed_gradient']
            df.streambed_gradient = df.streambed_gradient.str.removesuffix('\n')
            df = change_type(df, ['l', 'r', 'c', 'iseg', 'ireach'], 'int') 
            df = change_type(df, ['flow_into_reach', 'flow_to_aquifer', 'flow_out_reach', 'overlnd_runoff',
                                    'direct_precip', 'stream_et', 'stream_head', 'stream_depth', 'stream_width',
                                    'streambed_cond', 'streambed_gradient'], 'float')
            df.reset_index(inplace = True, drop= True)
    else:
        for sp in range(nsp):
            pass
    return df

#%% Class

class SFRCalibrator:
    def __init__(self, params):
        for key, value in params.items():
            setattr(self, key, value)
    
    def n_runs(self):
        if self.geom == 'nSEG':
            n = len(self.k_dict['kt'])*len(self.k_dict['ka'])*len(self.s_dict['st'])*math.prod([len(self.s_dict['sa'][x]) for x in range(len(self.s_dict['sa']))])
        elif self.geom == '2SEG':
                n = len(self.k_dict['kt'])*len(self.k_dict['ka'])*len(self.s_dict['st'])*len(self.s_dict['sa'])
        if hasattr(self, "n"):
            n = n*len(self.n)
        print('Based on the parameters set:\n')
        print('- ' + str(n) + ' runs will be executed')
        print(f'- Approximately {n*0.5} s will be needed ({n*0.5/(60*60*24)} days)')
    
    def n_runs_modified(self, lak = False):
        n = len(self.k_dict['kt'])*len(self.k_dict['ka'])*len(self.s_dict['s_coeff'])
        if not lak:
            n = n*len(self.s_dict['s_coeff'])
        if hasattr(self, "n"):
            n = n*len(self.n)
        print('Based on the parameters set:\n')
        print('- ' + str(n) + ' runs will be executed')
        print(f'- Approximately {n*0.5} s will be needed ({round(n*0.5/(60*60), 2)} hours, {round(n*0.5/(60*60*24), 3)} days)')
       
    def load(self):

        # Load general parameters (item 1)
        self.it1 = pd.read_excel(self.file_path, sheet_name = 'ITEM1')

        # Load reach data (item 2)
        if self.geom == '2SEG':
            if self.elev == 'LIDAR':
                sheet_name = 'ITEM2_LIDAR'
            else:
                sheet_name = 'ITEM2_GNSS'
        else:
            sheet_name = 'ITEM2'
        reach_data = pd.read_excel(self.file_path, sheet_name = sheet_name)
        reach_data = reach_data.apply(pd.to_numeric)
        reach_data.columns = ['k', 'i', 'j', 'iseg', 'ireach', 'rchlen', 'strtop', 'slope',  'strthick',  'strhc1']
        reach_data = reach_data.loc[:,:].to_records(index = False)
        # flopy adds 1 to layer, row and column, so remove 1 here
        reach_data.k = reach_data.k - 1
        reach_data.i = reach_data.i - 1
        reach_data.j = reach_data.j - 1
        self.reach_data = reach_data

        # Load item 5
        self.it5 = pd.read_excel(self.file_path, sheet_name = 'ITEM5')

        # Load segment data (item 6a)
        if self.geom == 'nSEG':
            if self.icalc == 1:
                sheet_name = 'ITEM6abc_icalc1'
            else:
                sheet_name = 'ITEM6abc_icalc2'
        else:
            sheet_name = 'ITEM6abc'
        segment_data = pd.read_excel(self.file_path, sheet_name = sheet_name)
        segment_data.columns = [x.lower() for x in segment_data.columns]
        segment_data = segment_data.loc[:,:].to_records(index = False)
        segment_data = {0: segment_data}
        self.segment_data = segment_data

        if self.icalc == 2:
            # load channel geometry data (item 6d)
            it6d = pd.read_excel(self.file_path, sheet_name = 'ITEM6d')
            geom_data = {}
            for seg in it6d.segment.unique():
                tool = it6d.loc[it6d.segment == seg, [f'v{i}' for i in range(1,9)]].to_numpy().copy()
                geom_data[int(seg)] = [tool[0].tolist(), tool[1].tolist()]
            geom_data = {0: geom_data}
            self.geom_data = geom_data
    
    def find_cond(self, t):
        """
        tool:
            the tool variable defined in this if structure
        t: bool
            if True, the condition found refers to the "testa"
            if False, the condition found refers to the "asta"
        tseg:
            the tseg variable defined before
        """
        tool = pd.DataFrame(self.reach_data)
        if self.tseg:
            if t:
                cond = tool.iseg == self.seg_t
            else:
                cond = tool.iseg != self.seg_t
        else:
            if t:
                cond = (tool.iseg == self.seg_t) & (tool.ireach <= self.reach_t)
            else:
                cond = (tool.iseg == self.seg_t) & (tool.ireach > self.reach_t)
        return cond

    def set_package(self, reach_data = None, segment_data = None):
        if reach_data is not None:
            # Write the new .sfr file transforming tool to reach_data
            reach_data = reach_data.loc[:,:].to_records(index = False)
            self.reach_data = reach_data
        if segment_data is not None:
            segment_data = segment_data.loc[:,:].to_records(index = False)
            segment_data = {0: segment_data}
            self.segment_data = segment_data
        
        # Generate the SFR package through flopy
        unit_number = 27 # define this based on the model

        m = flopy.modflow.Modflow(self.modelname, model_ws = self.model_ws)
        if self.icalc == 2:
            sfrpackage = flopy.modflow.ModflowSfr2(
                m,
                nstrm = self.it1.NSTRM.values[0],              # number of reaches
                nss = self.it1.NSS.values[0],                  # number of segments
                const = self.it1.CONST.values[0],              # constant for manning's equation: 1 for m/s
                dleak = self.it1.DLEAK.values[0],              # closure tolerance for stream stage computation
                ipakcb = self.it1.ISTCB1.values[0],            # flag for writing SFR output to cell-by-cell budget (on unit 50)
                istcb2 = self.it1.ISTCB2.values[0],            # flag for writing SFR output to text file
                dataset_5 = {0: self.it5.values[0].tolist()},
                unit_number = unit_number,
                isfropt = self.it1.ISFROPT.values[0],
                segment_data = self.segment_data,
                reach_data = self.reach_data,
                channel_geometry_data = self.geom_data
            )
        else:
            sfrpackage = flopy.modflow.ModflowSfr2(
            m,
            nstrm = self.it1.NSTRM.values[0],              # number of reaches
            nss = self.it1.NSS.values[0],                  # number of segments
            const = self.it1.CONST.values[0],              # constant for manning's equation: 1 for m/s
            dleak = self.it1.DLEAK.values[0],              # closure tolerance for stream stage computation
            ipakcb = self.it1.ISTCB1.values[0],            # flag for writing SFR output to cell-by-cell budget (on unit 50)
            istcb2 = self.it1.ISTCB2.values[0],            # flag for writing SFR output to text file
            dataset_5 = {0: self.it5.values[0].tolist()},
            unit_number = unit_number,
            isfropt = self.it1.ISFROPT.values[0],
            segment_data = self.segment_data,
            reach_data = self.reach_data
        )
        sfrpackage.write_file()
        
    def store_params(self, params, labels, modelcode = 'M'):
        if not hasattr(self, "params"):
            self.params = {}
        self.modelcode = modelcode
        self.params[modelcode] = dict(zip(labels, params))

    def run(self):
        success, buff = flopy.mbase.run_model(
                exe_name = os.path.join(self.model_ws, 'MF2005.exe'),
                namefile = f'{self.modelname}.nam',
                model_ws = self.model_ws,
                silent = self.silent #False to test the code, then switch to True
                )
        if not success:
            print(self.params)
            raise Exception("MODFLOW did not terminate normally.")

    def load_results(self):
        # Load the streamflow.dat file
        df = load_streamflow_dat(os.path.join(self.model_ws, f'{self.modelname}_streamflow.dat'))

        # Extract flow and depth in the target reach
        f = df.loc[(df.ireach == self.reach) & (df.iseg == self.segment), 'flow_out_reach'].values[0]
        d = df.loc[(df.ireach == self.reach) & (df.iseg == self.segment), 'stream_depth'].values[0]
        
        # Update the output structures
        # params_save.append(params + [f,d])
        self.params[self.modelcode]['flow_out_reach'] = f
        self.params[self.modelcode]['stream_depth'] = d

        # Extract flow and depth in all reaches and add them to the output structures
        if hasattr(self, "flow_save"):
            self.flow_save = pd.concat([self.flow_save, df.flow_out_reach], axis=1)
            self.depth_save = pd.concat([self.depth_save, df.stream_depth], axis=1)
            self.flowaq_save = pd.concat([self.flowaq_save, df.flow_to_aquifer], axis=1)
            self.flow_save.columns = self.depth_save.columns = self.flowaq_save.columns = self.flow_save.columns.to_list()[:-1] + [self.modelcode]
        else:
            self.flow_save = self.depth_save = self.flowaq_save = pd.DataFrame()
            self.flow_save = pd.concat([self.flow_save, df.flow_out_reach], axis=1)
            self.depth_save = pd.concat([self.depth_save, df.stream_depth], axis=1)
            self.flowaq_save = pd.concat([self.flowaq_save, df.flow_to_aquifer], axis=1)
            self.flow_save.columns = self.depth_save.columns = self.flowaq_save.columns = [self.modelcode]

    def save_results(self, i, overpass = False, threshold = 100000, threshold2 = 10000, w1 = 0.5, foldername = 'run_output'):
        # Create the output folder
        if not os.path.exists(os.path.join(self.model_ws, foldername)):
            os.makedirs(os.path.join(self.model_ws, foldername))
        
        if overpass or i % threshold == 0:
            # Define column labels
            params_save = pd.DataFrame(self.params).transpose()
            # Add columns to params_save
            params_save['geom'] = self.geom
            params_save['icalc'] = self.icalc
            params_save['elev'] = self.elev
            # Compute indexes
            params_save['flow_diff'] = self.flow_target - abs(params_save.flow_out_reach)
            params_save['depth_diff'] = self.depth_target - params_save.stream_depth
            params_save['flow_perc_err'] = abs(self.flow_target - params_save.flow_out_reach)/self.flow_target
            params_save['depth_perc_err'] = abs(self.depth_target - params_save.stream_depth)/self.depth_target
            w2 = 1 - w1 # set the weights
            params_save['combined_perc_err'] = w1*params_save.flow_perc_err + w2*params_save.depth_perc_err
            # Save as CSV
            params_save.index.name = 'model'
            params_save.to_csv(os.path.join(self.model_ws, foldername, f'sfr_results_{self.geom}_ICALC{self.icalc}_{self.elev}_M{i-1}.csv'))
        
        if overpass or i % threshold2 == 0:
            if not hasattr(self, "j"):
                self.j = 1
            self.flow_save['ireach'] = self.depth_save['ireach'] = self.flowaq_save['ireach'] = self.reach_data.ireach
            self.flow_save['iseg'] = self.depth_save['iseg'] = self.flowaq_save['iseg'] = self.reach_data.iseg
            # Save as CSV
            self.flow_save.to_csv(os.path.join(self.model_ws, foldername, f'sfr_reach_flow_out_reach_{self.geom}_ICALC{self.icalc}_{self.elev}_M{i-1}.csv'), index = False)
            self.depth_save.to_csv(os.path.join(self.model_ws, foldername, f'sfr_reach_depth_{self.geom}_ICALC{self.icalc}_{self.elev}_M{i-1}.csv'), index = False)
            self.flowaq_save.to_csv(os.path.join(self.model_ws, foldername, f'sfr_reach_flow_to_aquifer_{self.geom}_ICALC{self.icalc}_{self.elev}_M{i-1}.csv'), index = False)
            
            self.j = i
            if not overpass:
                # Clear the output structures
                del self.flow_save, self.depth_save, self.flowaq_save
    

class LAKSFRCalibrator:
    def __init__(self, params, gensfr = True):
        for key, value in params.items():
            setattr(self, key, value)
        if gensfr:
            self.sfr = SFRCalibrator(params)

    def load(self):
        # ------
        # LAK parameters
        # ------
        self.lak = {}
        # Model pars
        modpars = pd.read_excel(self.file_path, sheet_name='MODELPARS')
        self.lak['nlay'] = modpars.NLAY.item()
        self.lak['nrow'] = modpars.NROW.item()
        self.lak['ncol'] = modpars.NCOL.item()

        # LAK pars
        lakpars = pd.read_excel(self.file_path, sheet_name='LAKPARS')
        
        self.lak['lak_id'] = lakpars.LAK_ID.item()
        self.lak['k'] = lakpars.BED_K.item()
        self.lak['thickness'] = lakpars.BED_THICKNESS.item()
        self.lak['ipakcb'] = lakpars.IPAKCB.item()
        self.lak['theta'] = lakpars.THETA.item()
        self.lak['nssitr'] = lakpars.NSSITR.item()
        self.lak['sscncr'] = lakpars.SSCNCR.item()
        self.lak['surfdep'] = lakpars.SURFDEP.item()
        self.lak['stages'] = [lakpars.INITIAL_STAGE.item()]
        self.lak['stage_range'] = [[lakpars.MIN_STAGE.item(), lakpars.MAX_STAGE.item()]]
        self.lak['unitnumber'] = lakpars.UNITNO.item()

        # Create structures
        # Generate an inner object to store the parameters
        self.lak = LAKSFRCalibrator(self.lak, gensfr=False)
        self.lak.lakarr = np.zeros((self.lak.nlay, self.lak.nrow, self.lak.ncol), dtype=int)
        self.lak.lak_spd = {
            0: [
                (0, "STATUS", "ACTIVE")
                # (0, 0, 0, 0, lakpars.MIN_STAGE.item(), lakpars.MAX_STAGE.item())
            ]
        }

        #Set lake cells
        self.lak.lakcells = pd.read_excel(self.file_path, sheet_name='LAKCELLS')
        for r, c in zip(self.lak.lakcells.row, self.lak.lakcells.column):
            self.lak.lakarr[0, r, c] = self.lak.lak_id #0: only in top layer

        #Set leakance
        self.set_lak_leakance()

        # ------
        # SFR parameters
        # ------
        self.sfr.load()
    
    def set_lak_leakance(self, k = None, thickness = None):
        if k is None:
            k = self.lak.k
        if thickness is None:
            thickness = self.lak.thickness
        self.lak.bdlknc_val = k/thickness
        
        self.lak.bdlknc = np.zeros((self.lak.nlay, self.lak.nrow, self.lak.ncol), dtype=int)
        for r, c in zip(self.lak.lakcells.row, self.lak.lakcells.column):
            self.lak.bdlknc[0, r, c] = self.lak.bdlknc_val #0: only in top layer
    
    def replace_bdlknc(self, input_file):
        """
        Replace '2.6000e-05' with new_value while preserving formatting exactly.
        
        Parameters:
            input_file (str): path to input file
            output_file (str): path to output file
            new_value (float or str): new numeric value
        """
        input_file = os.path.join(self.model_ws, input_file)
        output_file = os.path.join(self.model_ws, f'{self.modelname}.lak')
        new_value = self.lak.bdlknc_val

        # Ensure Fortran-like scientific notation: x.xxxxE±xx but lowercase 'e'
        if isinstance(new_value, float):
            formatted_value = f"{new_value:.4e}"
        else:
            formatted_value = new_value  # assume already correctly formatted

        # IMPORTANT: match exact width if needed
        if len(formatted_value) != len("2.6000e-05"):
            raise ValueError(
                f"Formatted value '{formatted_value}' does not match expected width (10 chars)"
            )

        with open(input_file, "r") as f:
            content = f.read()

        # Exact substitution (no whitespace change!)
        content = content.replace("2.6000e-05", formatted_value)

        with open(output_file, "w") as f:
            f.write(content)

    def set_packages(self, laktemplatefile = None, reach_data = None, segment_data = None):
        # -----
        # LAK
        # -----
        
        self.replace_bdlknc(laktemplatefile)
        
        # -----
        # SFR
        # -----
        
        self.sfr.set_package(reach_data, segment_data)

    def store_params(self, params, labels, modelcode = 'M'):
        self.sfr.store_params(params, labels, modelcode = modelcode)

    def run(self):
        success, buff = flopy.mbase.run_model(
                exe_name = os.path.join(self.model_ws, 'MF2005.exe'),
                namefile = f'{self.modelname}.nam',
                model_ws = self.model_ws,
                silent = self.silent #False to test the code, then switch to True
                )
        if not success:
            # print(self.params)
            raise Exception("MODFLOW did not terminate normally.")
    
    def load_results(self):
        self.sfr.load_results()
    
    def save_results(self, i, overpass = False, threshold = 100000,
                     threshold2 = 10000, w1 = 0.5, foldername = 'run_output'):
        self.sfr.save_results(i, overpass = overpass, threshold = threshold,
                              threshold2 = threshold2, w1 = w1, foldername=foldername)
