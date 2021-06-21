import numpy as np
from copy import deepcopy
from math import ceil, modf
from scipy.integrate import odeint

dWdN = 1e6 * 24 * 3600 / (1.23 / 235)

class Calculate():

    def __init__(self, data, settings):
        self.DATA = data

        self.FUEL = {}
        for nuclide, weight_ratio in settings['Initial'].items():
            self.FUEL[nuclide] = weight_ratio / (int(nuclide[0:3]) * 1e-3)
        self.DT = settings['DT'] * 24 * 60 * 60
        self.METHOD = settings['Method']
        if self.METHOD == 'Flux':
            self.phi = settings['Flux'] * 1e-24
        else:
            self.POWER = settings['Power'] * 1e6
            self.POWER_MAX = self.POWER * 100

        self.GENEALOGY = {}

        def find_parents(row):
            if row[2] == 0:
                self.GENEALOGY[row[1]] = []
            elif row[1] not in self.GENEALOGY.keys():
                parent_row = self.DATA[self.DATA[:, 0].tolist().index(row[2])]
                if parent_row[1] in self.GENEALOGY.keys():
                    self.GENEALOGY[row[1]] = self.GENEALOGY[parent_row[1]] + [parent_row[1]]
                else:
                    self.GENEALOGY[row[1]] = find_parents(parent_row) + [parent_row[1]]
            return self.GENEALOGY[row[1]]
            
        for nuclide in self.FUEL.keys():
            find_parents(self.DATA[self.DATA[:, 1].tolist().index(nuclide)])

    def Cal_A(self, row):
        if row[4] == 'Neutron Absorbtion':
            return -self.phi*(float(row[5]) + float(row[6]))
        elif row[4] == 'Neutron Absorbtion and Beta Decay':
            return -self.phi*(float(row[5]) + float(row[6])) - float(row[7])

    def Cal_A_(self, parent_row, tf_type):
        if tf_type == 'Neutron Absorbtion':
            return self.phi*float(parent_row[6])
        elif tf_type == 'Beta Decay':
            return float(parent_row[7])

    def power2phi(self, fuel_current):
        SUM_N = 0
        for nuclide in self.DATA:
            SUM_N += nuclide[5] * fuel_current[nuclide[1]]
        if SUM_N == 0:
            return None
        else:
            power = self.POWER / (SUM_N * dWdN)
            return power if power < self.POWER_MAX else None

class Analytic(Calculate):
    
    def __init__(self, data, setting):
        super().__init__(data, setting)

    def main(self, t, precision=1e-3):
        self.numerical_result = {}
        self.analytic_result = []
        self.t_result = None
        self.time_sequence = np.array([])
        fuel_current = deepcopy(self.FUEL)

        if self.METHOD == 'Power':
            self.numerical_result['Power'] = self.POWER * 1e-6
            
        steps = int(t / self.DT) + 1
        t = modf(t / self.DT)[0]
        time_sequence_DT = np.linspace(
            0, self.DT, num=ceil(1/precision), endpoint=True)
            
        for index in range(steps):
            self.phi = self.power2phi(fuel_current) if self.METHOD == 'Power' else self.phi
            if self.phi is None:
                break
            result_A, result_C, fuel_current = self.step(fuel_current, time_sequence_DT)
            self.analytic_result.append({
                'time': {
                    'start': index * self.DT,
                    'end': index * self.DT
                },
                'A_ii': result_A,
                'C_ij': result_C
            })
            self.time_sequence = np.hstack((self.time_sequence, time_sequence_DT + index * self.DT))

    def step(self, fuel_current, time_sequence):
        result_A = {}
        result_C = {}
        fuel_new = {}

        def Calculate_A_and_C(row):
            if row[1] in result_A.keys() and row[1] in result_C.keys():
                pass
            elif row[2] == 0:
                result_A[row[1]] = self.Cal_A(row)
                result_C[row[1]] = {
                    row[1]: fuel_current[row[1]]
                }
            else:
                parent_row = self.DATA[self.DATA[:, 0].tolist().index(row[2])]
                Calculate_A_and_C(parent_row)
                result_A[row[1]] = self.Cal_A(row)
                A_ = self.Cal_A_(parent_row, row[3])
                result_C[row[1]] = {
                    row[1]: fuel_current[row[1]]
                }
                for nuclide in self.GENEALOGY[row[1]]:
                    result_C[row[1]][nuclide] = A_ * result_C[parent_row[1]][nuclide] / (result_A[nuclide] - result_A[row[1]])
                    result_C[row[1]][row[1]] -= result_C[row[1]][nuclide]

        for row in self.DATA:
            N_sequence = np.zeros(len(time_sequence))
            fuel_new[row[1]] = 0
            Calculate_A_and_C(row)
            for nuclide, C_ij in result_C[row[1]].items():
                N_sequence += C_ij * np.exp(result_A[nuclide] * time_sequence)
                fuel_new[row[1]] += C_ij * np.exp(result_A[nuclide] * self.DT)
            if row[1] in self.numerical_result.keys():
                self.numerical_result[row[1]] = np.hstack((self.numerical_result[row[1]], N_sequence))
            else:
                self.numerical_result[row[1]] = N_sequence

        return result_A, result_C, fuel_new

class Numerical(Calculate):
    
    def __init__(self, data, setting):
        super().__init__(data, setting)

    def main(self, t, precision=1e-3):
        self.numerical_result = {}
        self.analytic_result = []
        self.t_result = None
        self.time_sequence = np.array([])
        fuel_current = deepcopy(self.FUEL)

        if self.METHOD == 'Power':
            self.numerical_result['Power'] = self.POWER * 1e-6
            
        steps = int(t / self.DT) + 1
        t = modf(t / self.DT)[0]
        time_sequence_DT = np.linspace(
            0, self.DT, num=ceil(1/precision), endpoint=True)
            
        for index in range(steps):
            self.phi = self.power2phi(fuel_current) if self.METHOD == 'Power' else self.phi
            if self.phi is None:
                break
            fuel_current = self.step(fuel_current, time_sequence_DT)
            self.time_sequence = np.hstack((self.time_sequence, time_sequence_DT + index * self.DT))

    def step(self, fuel_current, time_sequence):
        fuel_new = {}
        fuel_current = [fuel_current[nuclide] for nuclide in self.DATA[:, 1]]

        def Calculate(N, t):
            dNdt = []
            for n_id, n in enumerate(N):
                row = self.DATA[n_id]
                if row[2] == 0:
                    dNdt.append(self.Cal_A(row) * n)
                else:
                    parent_row_id = self.DATA[:, 0].tolist().index(row[2])
                    parent_row = self.DATA[parent_row_id]
                    parent_n = N[parent_row_id]
                    dNdt.append(self.Cal_A_(parent_row, row[3]) * parent_n + self.Cal_A(row) * n)
            return dNdt
        
        sol = odeint(Calculate, fuel_current, time_sequence)
        for nuclide_id, nuclide in enumerate(self.DATA[:, 1]):
            N_sequence = sol[:, nuclide_id]
            if nuclide in self.numerical_result.keys():
                self.numerical_result[nuclide] = np.hstack((self.numerical_result[nuclide], N_sequence))
            else:
                self.numerical_result[nuclide] = N_sequence
            fuel_new[nuclide] = N_sequence[-1]

        return fuel_new
