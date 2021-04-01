
import numpy as np
import ray

@ray.remote
class ParameterServer(object):
    def __init__(self, dim):
        # Alternatively, params could be a dictionary
        # mapping keys to arrays.
        self.params = np.zeros(dim)

    def get_params(self):
        return self.params
    def update_params(self, grad):
        self.params += grad

ray.init()

ps = ParameterServer.remote(10)