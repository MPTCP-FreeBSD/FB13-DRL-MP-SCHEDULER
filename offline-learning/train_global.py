import torch, csv, threading
from collections import OrderedDict
from models.dqn import Agent

# Observation space = 8
# subflow 1 - pipe, wnd, rtt, rttvar
# subflow 2 - pipe, wnd, rtt, rttvar
n_observations = 8

# Action space = 2
# 0 = select subflow 1, 1 = select subflow 2
n_actions = 2

n_rounds = 10

class Client():
    def __init__(self, n_observations, n_actions, datapath):
        self.agent = Agent(n_observations, n_actions)
        self.data = []
        self.data_idx = 0
        self.load_data(datapath)

    def load_data(self, path):
        with open(path) as data:
            datareader = csv.reader(data)
            line_count = 0
            # Iterate over training data
            for row in datareader:
                if line_count > 0:
                    self.data.append([int(x) for x in row])
                line_count += 1

    def train_local(self):
        for row in self.data:
            # Convert to tensors
            state = torch.tensor(row[0:8], dtype=torch.float32).unsqueeze(0)
            action = torch.tensor([[row[8]]], dtype=torch.long)
            next_state = torch.tensor(row[9:17], dtype=torch.float32).unsqueeze(0)
            reward = torch.tensor([row[17]])

            # Store in agent's memory
            self.agent.remember(state, action, next_state, reward)

            # Train model
            self.agent.optimize_model()
            self.agent.soft_update()


clients = []
clients.append(Client(n_observations, n_actions, "data/data1.csv"))
clients.append(Client(n_observations, n_actions, "data/data2.csv"))
clients.append(Client(n_observations, n_actions, "data/data3.csv"))

agw = 1. / len(clients)

for x in range(n_rounds):
    # Perform local training pass
    threads = []
    for client in clients:
        thread = threading.Thread(target=client.train_local())
        threads.append(thread)
        thread.start()
    
    # Wait for local training to finish
    for thread in threads:
        thread.join()

    # Aggregate local models
    global_state = OrderedDict()
    for idx, client in enumerate(clients):
        local_state = client.agent.state_dict()
        for key in local_state:
            if idx == 0:
                global_state[key] = local_state[key] * agw
            else:
                global_state[key] += local_state[key] * agw
        
    for client in clients:
        client.agent.load_state_dict(global_state)

clients[0].agent.save_model("saved-models/global.weights")