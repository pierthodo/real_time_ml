
import numpy as np
import ray
import gym
import time

@ray.remote
class StreamServer(object):
    def __init__(self):
        self.stream = {}

    def create_stream(self,data_list):
        for key,data in data_list:
            self.stream[key] = [data]

    def get(self,key_list):
        return [self.stream[key][-1] for key in key_list]

    def push(self,data_list):
        for key,data in data_list:
            self.stream[key].append(data)

@ray.remote
def environment(stream):
    print("A")
    env = gym.make("MountainCarContinuous-v0")
    s = env.reset()
    for i in range(1000):
        a = ray.get(ps.get.remote(["action"]))
        s, r,done,info = env.step(a)
        if done:
            s = env.reset()
        stream.push.remote([("state",s),("reward",r)])
        time.sleep(1)


ray.init()

ps = StreamServer.remote()
ps.create_stream.remote([("state",0),("action",0.5),("reward",0)])
environment.remote(ps)

for i in range(100):
    ps.push.remote([("action",np.random.random())])
    print(ray.get(ps.get.remote(["state","action","reward"])))
    time.sleep(1)
#data = ps.get_stream.remote(["state","action","reward"])
#print(data)
#print(ps.get_stream.remote(["state","action","reward"]))