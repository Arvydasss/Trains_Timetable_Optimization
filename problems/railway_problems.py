"""
Defined railway networks

Parameters
1) Problem.dmax -- maximal secondary delay
2) Problem.p_sum -- panalty for ∑_i x_i = 1 hard constrains
3) Problem.p_pair -- penalty for ∑_i,j x_i x_j = 0 hard constrains
4) Problem.p_qubic -- weight for Rosenberg decomposition of qubic term
"""

class Problem():
    def __init__(self, taus, trains_timing, trains_routes):
        self.taus = taus
        self.trains_timing = trains_timing
        self.trains_routes = trains_routes
        self.p_sum = 2.5
        self.p_pair = 1.25
        self.p_qubic = 2.1
        self.d_max = 5

    def __str__(self):
        output = "Problem:\n"
        output += "\n"
        output += "taus:\n"
        output += self.dict_to_str(self.taus) + "\n"
        output += "trains_timing:\n"
        output += self.dict_to_str(self.trains_timing) + "\n"
        output += "trains_routes:\n"
        output += self.dict_to_str(self.trains_routes) + "\n"
        output += "p_sum: {}\n".format(self.p_sum)
        output += "p_pair: {}\n".format(self.p_pair)
        output += "p_qubic: {}\n".format(self.p_qubic)
        output += "d_max: {}\n".format(self.d_max)
        return output

    def dict_to_str(self, d, indent_level=1):
        indent = "\t" * indent_level
        return '\n'.join([f"{indent}{k}: {v}" for k, v in d.items()])