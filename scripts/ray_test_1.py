import numpy as np
import ray
import gym
import time
import wandb


@ray.remote
class Agent(object):
    def __init__(self,stream):
        self.weights =  np.random.random(2).reshape((1,-1))
        self.stream = stream

    def run(self):
        t0 = time.time()
        timeout = 0
        while not timeout:
            state,timeout = ray.get(self.stream.get.remote(["state","timeout"]))
            new_action = self.weights.dot(state)[0]
            self.stream.push.remote([("action",new_action)])
            time.sleep(0.5)

@ray.remote
class StreamServer(object):
    def __init__(self):
        self.stream = {}

    def create_stream(self,data_list):
        for key,data in data_list:
            self.stream[key] = [data]

    def get(self,key_list,num_points=1):
        if num_points == -1:
            return [self.stream[key] for key in key_list]
        elif num_points == 1:
            return [self.stream[key][-1] for key in key_list]
        else:
            return [self.stream[key][-(num_points):] for key in key_list]

    def push(self,data_list):
        for key,data in data_list:
            self.stream[key].append(data)


@ray.remote
def environment(stream,time_limit=100):
    t0 = time.time()
    env = gym.make("MountainCarContinuous-v0")
    s = env.reset()
    while (time.time() - t0) < time_limit:
        a = ray.get(ps.get.remote(["action"]))
        s, r,done,info = env.step(a)
        if done:
            s = env.reset()
        stream.push.remote([("state",s),("reward",r)])
        print("Env",ray.get(ps.get.remote(["state", "action", "reward"])))
        print(time.time() - t0, "/",time_limit)
        time.sleep(0.1)
    stream.push.remote([("timeout",1)])

wandb.init(project='real_time_ml', entity='pierthodo')


ray.init()

ps = StreamServer.remote()
env = gym.make("MountainCarContinuous-v0")
s = env.reset()
ps.create_stream.remote([("state", s), ("action", 0.5), ("reward", 0),("timeout",0)])
ag = Agent.remote(ps)

environment.remote(ps,time_limit=10)
ray.get(ag.run.remote())

data = ray.get(ps.get.remote(["state","action","reward"],num_points=-1))
print(data[-1])
result = {"reward":data[-1]}
wandb.log(result)
#print(data)
#print(ps.get_stream.remote(["state","action","reward"]))