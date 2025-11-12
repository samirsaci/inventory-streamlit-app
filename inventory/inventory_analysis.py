import pandas as pd
from inventory.inventory_models import InventoryParams
from typing import Optional
import traceback
import numpy as np

class InventorySimulation:
    def __init__(self, 
                 params: InventoryParams):

        self.type = type
        self.D = params.D
        self.T_total = params.T_total
        self.LD = params.LD
        self.T = params.T
        self.Q = params.Q
        self.initial_ioh = params.initial_ioh
        self.sigma = params.sigma
        
        # # Demand per day (unit/day)
        self.D_day = self.D / self.T_total
        
        # Simulation dataframe
        self.sim = pd.DataFrame({'time': np.array(range(1, self.T_total+1))})

    def order(self, t, T, Q, start_day=1):
        """Order Q starting at `start_day`, then every T days."""
        return Q if (t > start_day and ((t-start_day) % T) == 0) else 0
    
    def simulation_1(self):
        """Fixed-cycle ordering; lead time NOT compensated."""
        sim_1 = self.sim.copy()

        # constant daily demand
        # sim_1['demand'] = self.D_day
        sim_1['demand'] = np.random.normal(self.D_day, self.sigma, self.T_total)

        # place orders at t = 1 + k*T
        T = int(self.T)
        Q = float(self.Q)
        sim_1['order'] = sim_1['time'].apply(lambda t: self.order(t, T, Q))

        # receipts arrive after LD days
        LD = int(self.LD)
        sim_1['receipt'] = sim_1['order'].shift(LD, fill_value=0.0)

        # Inventory: iterative update to respect lead time
        ioh = [self.initial_ioh]
        for t in range(1, len(sim_1)):
            # subtract demand of day t
            new_ioh = ioh[-1] - sim_1.loc[t, 'demand']
            # add receipt of day t (if any arrives today)
            new_ioh += sim_1.loc[t, 'receipt']
            ioh.append(new_ioh)
        sim_1['ioh'] = ioh

        for col in ['order', 'ioh', 'receipt']:
            sim_1[col] = np.rint(sim_1[col]).astype(int)

        return sim_1 
    
    def order_leadtime(self, t, T, Q, LD, start_day=1):
        """Order Q starting at `start_day`, then every T days."""
        return Q if (t > start_day and ((t-start_day + (LD-1)) % T) == 0) else 0

    def simulation_2(self, 
                     method: Optional[str] = "order_leadtime"):
        """Fixed-cycle ordering; lead time NOT compensated."""
        sim_1 = self.sim.copy()
        LD = int(self.LD)

        # constant daily demand
        sim_1['demand'] = self.D_day
        sim_1['demand'] = np.maximum(np.random.normal(self.D_day, self.sigma, self.T_total), 0)

        # place orders at t = 1 + k*T
        T = int(self.T)
        Q = float(self.Q)
        if method == "order_leadtime":
            sim_1['order'] = sim_1['time'].apply(lambda t: self.order_leadtime(t, T, Q, LD))
        else:
            sim_1['order'] = sim_1['time'].apply(lambda t: self.order(t, T, Q))

        # receipts arrive after LD days
        sim_1['receipt'] = sim_1['order'].shift(LD, fill_value=0.0)

        # Inventory: iterative update to respect lead time
        ioh = [self.initial_ioh]
        for t in range(1, len(sim_1)):
            # subtract demand of day t
            new_ioh = ioh[-1] - sim_1.loc[t, 'demand']
            # add receipt of day t (if any arrives today)
            new_ioh += sim_1.loc[t, 'receipt']
            ioh.append(new_ioh)
        sim_1['ioh'] = ioh

        for col in ['order', 'ioh', 'receipt']:
            sim_1[col] = np.rint(sim_1[col]).astype(int)

        return sim_1   
    