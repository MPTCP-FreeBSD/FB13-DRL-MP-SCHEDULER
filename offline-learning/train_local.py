import os, sys, csv, torch
from models.dqn import Agent

if len(sys.argv) < 2:
    print("Usage is train_offline.py datafile modelname")
    sys.exit(0)

datafile = "data/{}".format(sys.argv[1])
modelname = sys.argv[2]

if not os.path.isfile(datafile):
    print("{} not found.".format(datafile))
    sys.exit(0)

# Observation space = 8
# subflow 1 - pipe, wnd, rtt, rttvar
# subflow 2 - pipe, wnd, rtt, rttvar
n_observation = 8

# Action space = 2
# 0 = select subflow 1, 1 = select subflow 2
n_actions = 2

n_rounds = 5

# Init DQN agent
agent = Agent(n_observation, n_actions)

for i in range (n_rounds):
    # Load training data
    with open(datafile) as data:
        datareader = csv.reader(data)
        # Iterate over training data
        for row in datareader:
            # Read data from row
            state = [int(x) for x in row[0:8]]
            action = int(row[8])
            next_state = [int(x) for x in row[9:17]]
            reward = int(row[17])

            # Convert to tensors
            state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            action = torch.tensor([[action]], dtype=torch.long)
            next_state = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)
            reward = torch.tensor([reward])

            # Store in agent's memory
            agent.remember(state, action, next_state, reward)

            # Train model
            agent.optimize_model()
            agent.soft_update()

agent.save_model("saved-models/{}.weights".format(modelname))
