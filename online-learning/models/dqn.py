import math
import random
import threading
from collections import namedtuple, deque

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))

class ReplayMemory(object):

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

class DQN(nn.Module):

    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, 128)
        self.layer2 = nn.Linear(128, 128)
        self.layer3 = nn.Linear(128, n_actions)

    # Called with either one element to determine next action, or a batch
    # during optimization. Returns tensor([[left0exp,right0exp]...]).
    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)
    
class Agent():
    def __init__(self, n_observations, n_actions, modelname = "dqn"):
        # Define hyperparamaters
        self.__BATCH_SIZE = 128   # BATCH_SIZE is the number of transitions sampled from the replay buffer
        self.__GAMMA = 0.99       # GAMMA is the discount factor as mentioned in the previous section
        self.__EPS_START = 0.9    # EPS_START is the starting value of epsilon
        self.__EPS_END = 0.05     # EPS_END is the final value of epsilon
        self.__EPS_DECAY = 1000   # EPS_DECAY controls the rate of exponential decay of epsilon, higher means a slower decay
        self.__TAU = 0.005        # TAU is the update rate of the target network
        self.__LR = 1e-4          # LR is the learning rate of the ``AdamW`` optimizer
        # Define model parameters
        self.__observations = n_observations
        self.__actions = n_actions
        self.__steps_done = 0
        # Initialise and synchronise models
        self.__policy_net = DQN(self.__observations, self.__actions)
        self.__swap_net = DQN(self.__observations, self.__actions)
        self.__train_net = DQN(self.__observations, self.__actions)
        self.__target_net = DQN(self.__observations, self.__actions)
        state_dict = self.__policy_net.state_dict()
        self.__swap_net.load_state_dict(state_dict)
        self.__train_net.load_state_dict(state_dict)
        self.__target_net.load_state_dict(state_dict)
        self.__policy_net.eval()
        self.__swap_net.eval()
        self.__train_net.train()
        self.__target_net.eval()
        # Initialise optimizer
        self.__optimizer = optim.AdamW(self.__train_net.parameters(), lr=self.__LR, amsgrad=True)
        # Initialise replay memory
        self.__memory = ReplayMemory(10000)
        # Initialise training thread
        self.__train_thread = threading.Thread(target=self.__train)
        self.__train_cv = threading.Condition()
        self.__train_enable = False
        # Control how frequently to save the model
        self.__iterations = 0
        self.__save_frequency = 25
        self.__modelname = modelname

    def __optimize_model(self):
        if len(self.__memory) < self.__BATCH_SIZE:
            return
        transitions = self.__memory.sample(self.__BATCH_SIZE)
        # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
        # detailed explanation). This converts batch-array of Transitions
        # to Transition of batch-arrays.
        batch = Transition(*zip(*transitions))

        # Compute a mask of non-final states and concatenate the batch elements
        # (a final state would've been the one after which simulation ended)
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                            batch.next_state)), dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state
                                                    if s is not None])
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
        # columns of actions taken. These are the actions which would've been taken
        # for each batch state according to _train_net
        state_action_values = self.__train_net(state_batch).gather(1, action_batch)

        # Compute V(s_{t+1}) for all next states.
        # Expected values of actions for non_final_next_states are computed based
        # on the "older" _target_net; selecting their best reward with max(1)[0].
        # This is merged based on the mask, such that we'll have either the expected
        # state value or 0 in case the state was final.
        next_state_values = torch.zeros(self.__BATCH_SIZE)
        with torch.no_grad():
            next_state_values[non_final_mask] = self.__target_net(non_final_next_states).max(1)[0]
        # Compute the expected Q values
        expected_state_action_values = (next_state_values * self.__GAMMA) + reward_batch

        # Compute Huber loss
        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

        # Optimize the model
        self.__optimizer.zero_grad()
        loss.backward()
        # In-place gradient clipping
        torch.nn.utils.clip_grad_value_(self.__train_net.parameters(), 100)
        self.__optimizer.step()

    def __soft_update(self):
        # Soft update of the target network's weights
        # θ′ ← τ θ + (1 −τ )θ′
        target_net_state_dict = self.__target_net.state_dict()
        train_net_state_dict = self.__train_net.state_dict()
        for key in train_net_state_dict:
            target_net_state_dict[key] = train_net_state_dict[key]*self.__TAU + target_net_state_dict[key]*(1-self.__TAU)
        self.__target_net.load_state_dict(target_net_state_dict)

    def __swap_nets(self):
        # Swap _policy_net and _swap_net
        temp = self.__policy_net
        self.__policy_net = self.__swap_net
        self.__swap_net = temp

    def __train(self):
        with self.__train_cv:
            while self.__train_enable:
                if len(self.__memory) > self.__BATCH_SIZE:
                    # Optimize _train_net
                    self.__optimize_model()
                    # Soft update of target_net
                    self.__soft_update()
                    # Load weights into swap_net
                    self.__swap_net.load_state_dict(self.__train_net.state_dict())
                    # Swap policy_net to use latest training
                    self.__swap_nets()
                    # Check for save conditions
                    self.__iterations += 1
                    if self.__iterations == self.__save_frequency:
                        self.__iterations = 0
                        self.save_model("saved-models/{}.weights".format(self.__modelname))
                # Wait for new experiences
                self.__train_cv.wait()

    def start_training(self):
        # Set enable signal
        self.__train_enable = True
        # Check if thread is running
        if self.__train_thread.is_alive():
            return
        # Start thread
        self.__train_thread.start()

    def stop_training(self):
        # Signal train thread to terminate
        self.__train_enable = False
        # Check thread is running
        if self.__train_thread.is_alive():
            # Wake up thread
            with self.__train_cv:
                self.__train_cv.notify_all()
            # Wait for train thread to terminate
            self.__train_thread.join()

    def select_action(self, state):
        sample = random.random()
        eps_threshold = self.__EPS_END + (self.__EPS_START - self.__EPS_END) * \
            math.exp(-1. * self.__steps_done / self.__EPS_DECAY)
        self.__steps_done += 1
        if sample > eps_threshold:
            with torch.no_grad():
                # t.max(1) will return the largest column value of each row.
                # second column on max result is index of where max element was
                # found, so we pick action with the larger expected reward.
                return self.__policy_net(state).max(1)[1].view(1, 1)
        else:
            return torch.tensor([[random.randint(0, self.__actions - 1)]], dtype=torch.long)
    
    def remember(self, *args):
        # Store transition in memory
        self.__memory.push(*args)
        # Notify train thread of new experiences
        with self.__train_cv:
            self.__train_cv.notify_all()
    
    def optimize_model(self):
        self.__optimize_model()

    def soft_update(self):
        self.__soft_update

    def save_model(self, path):
        torch.save(self.__train_net.state_dict(), path)

    def load_model(self, path):
        state_dict = torch.load(path)
        self.__policy_net.load_state_dict(state_dict)
        self.__swap_net.load_state_dict(state_dict)
        self.__train_net.load_state_dict(state_dict)
        self.__target_net.load_state_dict(state_dict)
        self.__EPS_START = self.__EPS_END

    def state_dict(self):
        return self.__train_net.state_dict()
    
    def load_state_dict(self, state_dict):
        self.__train_net.load_state_dict(state_dict)
    











