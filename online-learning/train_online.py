
import os, signal, sys, syscalls, threading, time, torch
from models.dqn import Agent

if len(sys.argv) != 3:
    print("Usage is train_offline.py loadmodel savemodel")
    sys.exit(0)

loadmodelpath = None
if sys.argv[1] != "None":
    loadmodelpath = "saved-models/{}.weights".format(sys.argv[1])
    if not os.path.isfile(loadmodelpath):
        print("{} not found.".format(loadmodelpath))
        sys.exit(0)

modelname = sys.argv[2]

# Observation space = 8
# subflow 1 - pipe, wnd, rtt, rttvar
# subflow 2 - pipe, wnd, rtt, rttvar
n_observation = 8

# Action space = 2
# 0 = select subflow 1, 1 = select subflow 2
n_actions = 2

# Init DQN agent
agent = Agent(n_observation, n_actions, modelname)
if loadmodelpath is not None:
    agent.load_model(loadmodelpath)

def select_subflow(ref, last_action, last_state, state, gput):
    # Convert state to tensor and select action
    state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
    action = agent.select_action(state)

    # Return subflow selection to kernel
    try:
        syscalls.mp_sched_dqn_select_subflow(ref, action.item())
    except:
        print("An error occurred in select_subflow syscall - ref={0}, action={1}".format(ref, action.item()))
        return
    
    # Convert previous state and action to tensors
    last_state = torch.tensor(last_state, dtype=torch.float32).unsqueeze(0)
    last_action = torch.tensor([[last_action]], dtype=torch.long)

    # Convert reward to tensor
    reward = torch.tensor([gput])

    # Store the transition in memory
    agent.remember(last_state, last_action, state, reward)
    

def sigusr1_handler(sig, frame):
    # Loop until we get an error to ensure all queued state entries have been handled
    while True:
        try:
            # Get state entry from kernel and process in new thread
            ref, last_action, last_state, state, gput = syscalls.mp_sched_dqn_get_state()
            threading.Thread(target=select_subflow, args=(ref, last_action, last_state, state, gput,)).start()
        except:
            break


def sigint_handler(sig, frame):
    # Stop training loop
    agent.stop_training()
    # Deregister process as DQN handler
    syscalls.mp_sched_dqn_clear_proc()
    # Exit scheduler
    sys.exit(0)


def main():
    # Set signal handlers
    signal.signal(signal.SIGUSR1, sigusr1_handler)
    signal.signal(signal.SIGINT, sigint_handler)
    # Register process as DQN handler
    syscalls.mp_sched_dqn_set_proc()
    # Start training loop
    agent.start_training()
    # Idle in background
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    main()
