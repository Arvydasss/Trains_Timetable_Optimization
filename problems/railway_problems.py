"""
Defined railway network
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