import pandas as pd
import xarray as xr
import numpy as np
import pyomo.environ as pe
from datetime import datetime
import os
from pyomo.opt import SolverStatus, TerminationCondition

class problem:
    # Set up the problem
    def __init__(self, folder, simulation_name):
        # Path to the folder where the input files are stored
        self.model_folder = folder 
        # Name of the simulation (used for the NetCDF output)
        self.simulation_name = simulation_name
        # Generation units
        self.gen = pd.read_csv(folder+'/gen.csv')
        # Lines
        self.lin = pd.read_csv(folder+'/lin.csv')
        # Demand time-series
        self.dem = pd.read_csv(folder+'/dem.csv')
        # Non-dispatchable renewables time-series
        self.ren = pd.read_csv(folder+'/ren.csv')
        # Non-dispatchable renewables capacity
        self.ren_pp = pd.read_csv(folder+'/ren_pp.csv')
        # Inflow time-series
        self.inflow = pd.read_csv(folder + '/inflow.csv')
        # Units' availability time-series
        self.av = pd.read_csv(folder + '/avail.csv')
        # Storage minimum
        self.stomin = pd.read_csv(folder + '/stomin.csv') 
        # Number of generating units
        self.ng = len(self.gen)
        # Number of lines
        self.nl = len(self.lin)
        # Number of zones
        self.nn = self.dem.shape[1] 
        # Number of steps
        self.nt = self.dem.shape[0]

        # CONSTANTS
        # Initial and final storage level (0-1)
        self.INITIAL_STORAGE_LEVEL = 0.45
        # Production of hydropower could ramp up/down of a factor RAMPING_FACTOR
        self.RAMPING_FACTOR = 8

    # Solve the problem
    def solve(self):

        # Define the model
        m = pe.ConcreteModel()

        # Define the sets
        m.g = pe.Set(initialize=list(range(self.ng)),ordered=True) # generators
        m.l = pe.Set(initialize=list(range(self.nl)),ordered=True) # lines
        m.n = pe.Set(initialize=list(range(self.nn)),ordered=True) # number of zones
        m.t = pe.Set(initialize=list(range(self.nt)),ordered=True) # time steps

        # Define variables
        m.system_cost   = pe.Var() # obj function
        m.prod = pe.Var(m.g, m.t, within=pe.NonNegativeReals, initialize = 0) # prod(g, t)
        m.sl  = pe.Var(m.g, m.t, within=pe.NonNegativeReals, initialize = 0) # storage_level(g, t)
        m.u = pe.Var(m.g,m.t,within=pe.NonNegativeReals, bounds=(0,1)) # commit(g,t)
        m.shd = pe.Var(m.n,m.t,within=pe.NonNegativeReals) # shed(n, t)
        m.curt = pe.Var(m.n,m.t,within=pe.NonNegativeReals) # spl(n,t)
        m.flw = pe.Var(m.l,m.t) # flow(l, t)

        # Slack variables
        m.water_slack = pe.Var(m.g, m.t, within=pe.NonNegativeReals)
        m.storage_slack = pe.Var(m.g, m.t, within=pe.NonNegativeReals)
        m.curt_slack = pe.Var(m.n, m.t, within=pe.NonNegativeReals)
          
        
        
        #Objective function
        def obj_rule(m):
            return m.system_cost
        m.obj = pe.Objective(rule=obj_rule)

        #Definition cost
        def cost_def_rule(m):
            return m.system_cost == sum(self.gen['cost'][g]*m.prod[g,t] for g in m.g for t in m.t) + \
            sum(400*m.shd[n,t] for n in m.n for t in m.t) + \
            sum(100*m.water_slack[g,t] for g in m.g for t in m.t) + \
            sum(100*m.storage_slack[g,t] for g in m.g for t in m.t) + \
            sum(100*m.curt_slack[n,t] for n in m.n for t in m.t)
        
        m.cost_def = pe.Constraint(rule=cost_def_rule)

        # Energy balance
        def bal_rule(m,n,t):
            return sum(m.prod[g,t] for g in m.g if self.gen['bus'][g] == n) + \
            self.ren.iloc[t,n] + \
            m.shd[n,t] + \
            sum(m.flw[l,t] for l in m.l if self.lin['to'][l] == n) == self.dem.iloc[t,n] + \
            m.curt[n,t] + \
            sum(m.flw[l,t] for l in m.l if self.lin['from'][l] == n)
        m.nal = pe.Constraint(m.n, m.t, rule=bal_rule)

        # Minimum generation
        def min_gen_rule(m,g,t):
            return m.prod[g,t] >= self.gen['min'][g] * self.av.iloc[t,g]
        m.min_gen = pe.Constraint(m.g, m.t, rule=min_gen_rule)

        # Maximum generation
        def max_gen_rule(m,g,t):
            return m.prod[g,t] <= m.u[g,t]*self.gen['max'][g]* self.av.iloc[t,g]
        m.max_gen = pe.Constraint(m.g, m.t, rule=max_gen_rule)
        
        # Max ramping-up hydropower
        def max_ramp_up_rule(m,g,t):
            if self.gen['stomax'][g] == 0:
                return pe.Constraint.Skip
            elif (t > 0):
                return m.prod[g,t]-m.prod[g,t-1] <= self.gen['max'][g]*self.av.iloc[t,g]/self.RAMPING_FACTOR
            else:
                return pe.Constraint.Skip
        m.max_ramp_up = pe.Constraint(m.g, m.t, rule = max_ramp_up_rule)
        
        # Max ramping-down hydropower
        def max_ramp_down_rule(m,g,t):
            if self.gen['stomax'][g] == 0:
                return pe.Constraint.Skip
            elif (t > 0):
                return m.prod[g,t]-m.prod[g,t-1] >= -1*self.gen['max'][g]*self.av.iloc[t,g]/self.RAMPING_FACTOR
            else:
                return pe.Constraint.Skip
        m.max_ramp_down = pe.Constraint(m.g, m.t, rule = max_ramp_down_rule)
        
        
        # Minimum storage level
        def min_storage_level_rule(m,g,t):
            if self.gen['stomax'][g] == 0:
                return pe.Constraint.Skip
            elif (t == self.nt-1):
                return m.sl[g,t] + m.storage_slack[g,t] >= self.gen['stomax'][g]* self.av.iloc[t,g]*self.INITIAL_STORAGE_LEVEL
            else:
                return m.sl[g,t] + m.storage_slack[g,t] >= self.stomin.iloc[t,g]* self.av.iloc[t,g]
        m.min_sl = pe.Constraint(m.g, m.t, rule = min_storage_level_rule)
        
        # Maximum storage level
        def max_storage_level_rule(m,g,t):
            if self.gen['stomax'][g] == 0:
                return pe.Constraint.Skip
            else:
                return m.sl[g,t] <= self.gen['stomax'][g]* self.av.iloc[t,g]
        m.max_sl = pe.Constraint(m.g, m.t, rule = max_storage_level_rule)
        
        # Storage balance
        def storage_bal_rule(m, g, t):
            if self.gen['stomax'][g] == 0:
                return pe.Constraint.Skip
            else:
                if (t == 0):
                    return self.gen['stomax'][g]* self.av.iloc[t,g]*self.INITIAL_STORAGE_LEVEL + self.inflow.iloc[t,g] - (m.sl[g,t] + m.prod[g,t]) - m.water_slack[g,t]== 0
                else:
                    return m.sl[g,t-1] + self.inflow.iloc[t,g] - m.sl[g,t] - m.prod[g,t] - m.water_slack[g,t] == 0
        m.sto_rul_bal = pe.Constraint(m.g, m.t, rule = storage_bal_rule)

        # Max discharge
        def max_discharge_rule(m, g, t):
            if self.gen['stomax'][g] == 0:
                return pe.Constraint.Skip
            else:
                return m.prod[g,t] - self.inflow.iloc[t,g] <= m.sl[g,t]
        m.max_discharge = pe.Constraint(m.g, m.t, rule = max_discharge_rule)

        #Maximum curtage
        def max_curt_rule(m,n,t):
            return m.curt[n,t] - m.curt_slack[n,t] <= self.ren.iloc[t,n]
        m.max_curt = pe.Constraint(m.n, m.t, rule=max_curt_rule)

        #Maximum shedding
        def max_shed_rule(m,n,t):
            return m.shd[n,t] <= self.dem.iloc[t,n]
        m.max_shed = pe.Constraint(m.n, m.t, rule=max_shed_rule)

        #Max power flow
        def max_flow_rule(m,l,t):
            return m.flw[l,t] <= self.lin['cap'][l]
        m.max_flow = pe.Constraint(m.l, m.t, rule=max_flow_rule)

        #Min power flow
        def min_flow_rule(m,l,t):
            return m.flw[l,t] >= -self.lin['cap'][l]
        m.min_flow = pe.Constraint(m.l, m.t, rule=min_flow_rule)

        # SOLVING the optimization problem using CBC
        opt = pe.SolverFactory('cbc')
        # Gettint duals
        m.dual = pe.Suffix(direction=pe.Suffix.IMPORT)
        # Get results
        res = opt.solve(m, symbolic_solver_labels=True, tee=True)
        # Print solver output
        print(res['Solver'][0])
        # Save LP problem
        m.write(filename = self.model_folder + '/model.lp', io_options={'symbolic_solver_labels': True})
        
        print ("Solver Status: ",  res.solver.status)
        if (res.solver.termination_condition == TerminationCondition.infeasible):
            # Do something when model in infeasible
            print('Problem infeasible. Results not saved')
        else:
            #We save the results
            self.output = m
            # Convert pyomo results into dataframes
            self.prod = get_dataframe(m.prod,m.g,m.t).T
            self.stat = get_dataframe(m.u,m.g,m.t).T
            self.flow = get_dataframe(m.flw,m.l,m.t).T
            self.shed = get_dataframe(m.shd,m.n,m.t).T
            self.curt = get_dataframe(m.curt,m.n,m.t).T
            self.ws   = get_dataframe(m.water_slack,m.g,m.t).T
            self.ss   = get_dataframe(m.storage_slack,m.g,m.t).T
            self.cs   = get_dataframe(m.curt_slack,m.n,m.t).T
            self.sl = get_dataframe(m.sl,m.g,m.t).T
            # Save them to CSV
            self.stat.to_csv(self.model_folder + '/stat.csv', index = False)
            self.prod.to_csv(self.model_folder + '/prod.csv',index=False, header = self.gen['Unit'].values)
            self.flow.to_csv(self.model_folder + '/flow.csv',index=False, header = self.lin['line_name'].values)
            self.shed.to_csv(self.model_folder + '/shed.csv',index=False, header = self.dem.columns)
            self.curt.to_csv(self.model_folder + '/curt.csv',index=False, header = self.dem.columns)
            self.ws.to_csv(self.model_folder + '/ws.csv',index=False, header = self.gen['Unit'].values)
            self.ss.to_csv(self.model_folder + '/ss.csv',index=False, header = self.gen['Unit'].values)
            self.cs.to_csv(self.model_folder + '/cs.csv',index=False, header = self.dem.columns)
            self.sl.to_csv(self.model_folder + '/sl.csv',index=False, header = self.gen['Unit'].values)
            
            # CREATE NETCDF
            all_ds = []
            
            all_ds.append(
                xr.DataArray(self.prod.values, 
                    coords={'day': np.arange(self.nt), 'unit': self.gen['Unit'].values},
                    dims=['day', 'unit'], 
                    attrs = {'unit': 'MWh', 'description': 'Generation for each unit'},
                    name = 'production')
            )
            all_ds.append(
                xr.DataArray(self.av.values, 
                    coords={'day': np.arange(self.nt), 'unit': self.av.columns},
                    dims=['day', 'unit'], 
                    attrs = {'availability_factor': 'percentage', 'description': 'availability for each unit'},
                    name = 'availability')
            )
            all_ds.append(
                xr.DataArray(self.inflow.values, 
                    coords={'day': np.arange(365), 'unit': self.inflow.columns},
                    dims=['day', 'unit'], 
                    attrs = {'inflow': 'MWh', 'description': 'Inflow (available energy) for each unit'},
                    name = 'inflow')
            )
            all_ds.append(
                xr.DataArray(self.stomin.values, 
                    coords={'day': np.arange(self.nt), 'unit': self.stomin.columns},
                    dims=['day', 'unit'], 
                    attrs = {'Minimum_storage_level': 'MWh', 'description': 'Minimum daily storage level for each unit'},
                    name = 'storage_min')
            )
            all_ds.append(
                xr.DataArray(self.dem.values, 
                    coords={'day': np.arange(self.nt), 'zone': self.dem.columns},
                    dims=['day', 'zone'], 
                    attrs = {'unit': 'MWh', 'description': 'Daily demand per zone'},
                    name = 'demand')
            )
            all_ds.append(
                xr.DataArray(self.ren.values, 
                    coords={'day': np.arange(self.nt), 'zone': self.ren.columns},
                    dims=['day', 'zone'], 
                    attrs = {'unit': 'MWh', 'description': 'Non-dispatchable renewables per zone'},
                    name = 'renewables')
            )
            all_ds.append(
                xr.DataArray(self.ren_pp.drop(columns = ['Technology']),
                    coords={'ren_technology': self.ren_pp['Technology'], 'zone': self.ren_pp.drop(columns = ['Technology']).columns},
                    dims=['ren_technology', 'zone'], 
                    attrs = {'unit': 'MW', 'description': 'Non-dispatchable capacity per zone'},
                    name = 'renewables_pp')
            )
            all_ds.append(
                xr.DataArray(self.flow.values, 
                    coords={'day': np.arange(365), 'line': self.lin['line_name'].values},
                    dims=['day', 'line'], 
                    attrs = {'unit': 'MWh (positive is from left to right)', 'description': 'Cross-zones electricity transfers'},
                    name = 'flow')
            )
            all_ds.append(
                xr.DataArray(self.shed.values, 
                    coords={'day': np.arange(self.nt), 'zone': self.dem.columns},
                    dims=['day', 'zone'], 
                    attrs = {'unit': 'MWh', 'description': 'Shed load'},
                    name = 'shed_load')
            )
            all_ds.append(
                xr.DataArray(self.curt.values, 
                    coords={'day': np.arange(self.nt), 'zone': self.dem.columns},
                    dims=['day', 'zone'], 
                    attrs = {'unit': 'MWh', 'description': 'Curtailment of non-dispatchable renewables'},
                    name = 'curtailed')
            )
            all_ds.append(
                xr.DataArray(self.sl.values, 
                    coords={'day': np.arange(self.nt), 'unit': self.gen['Unit'].values},
                    dims=['day', 'unit'], 
                    attrs = {'unit': 'MWh', 'description': 'Daily computed storage level for each unit'},
                    name = 'storage_level')
            )
            all_ds.append(
                xr.DataArray(self.ws.values, 
                    coords={'day': np.arange(self.nt), 'unit': self.gen['Unit'].values},
                    dims=['day', 'unit'],
                    attrs = { 'description': 'slack in the storage balance constraint'},
                    name = 'water_slack')
            )
            all_ds.append(
                xr.DataArray(self.ss.values, 
                    coords={'day': np.arange(self.nt), 'unit': self.gen['Unit'].values},
                    dims=['day', 'unit'], 
                    attrs = { 'description': 'slack in the storage level rule'},
                    name = 'storage_slack')
            )
            all_ds.append(
                xr.DataArray(self.cs.values, 
                    coords={'day': np.arange(self.nt), 'zone': self.dem.columns},
                    dims=['day', 'zone'], 
                    attrs = { 'description': 'slack in the curtailment constraint'},
                    name = 'curtailment_slack')
            )
            all_ds.append(
                self.gen.rename(columns={"Unit": "unit"}).set_index('unit').add_prefix('unit_').to_xarray()
            )
            all_ds.append(
                self.lin.rename(columns={"line_name": "line"}).set_index('line').add_prefix('line_').to_xarray()
            )
            all_ds = xr.merge(all_ds)
            all_ds.attrs = {'created': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'hostname': os.uname().nodename,
            'model_folder': self.model_folder,
            'simulation_name': self.simulation_name
            }
            all_ds.to_netcdf(f'{self.model_folder}/{self.simulation_name}.nc')
            
            # SAVE DUAL to TEXT
            for c in m.component_objects(pe.Constraint, active=True):
                #print ("   Constraint",c)
                with open(f'{self.model_folder}/dual_{c}.txt', 'w') as f:
                    for index in c:
                        f.write(str(index) + ' ' + str(m.dual[c[index]]) + '\n')
                    f.close()
 

def get_dataframe(pyomo_var,index1,index2):
    mat = []
    for i in index1:
        row = []
        for j in index2:
            row.append(pyomo_var[i,j].value)
        mat.append(row)
    return pd.DataFrame(mat)
