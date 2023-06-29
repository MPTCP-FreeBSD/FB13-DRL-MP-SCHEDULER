# FreeBSD13.1 Deep Reinforcement Learning Multipath Scheduler
## Introduction
This repository contains support and distribution files for the Deep Reinforcement Learning (DRL) Multipath Scheduler for FreeBSD13.1.
The repository is divided into the following folders:
* evaluation
* keys
* modules
* offline-learning
* online-learning
* setup

The multipath kernel and package dependencies must be installed prior to using this repository.

## Install Multipath Kernel 
Switch from quarterly to latest update branch:
```
mkdir -p /usr/local/etc/pkg/repos
echo "FreeBSD: { url: "pkg+http://pkg.freebsd.org/\$\{ABI\}/latest" }" > /usr/local/etc/pkg/repos/FreeBSD.conf
```

Install package dependencies:
```
pkg install git
pkg install gdb

pkg install py39-pytorch
pkg install py39-gym
pkg install py39-packaging

pkg install rsync

pkg install jucipp
pkg install xauth
pkg install en-aspell
```

Clone multipath kernel source:
```
git clone https://github.com/MPTCP-FreeBSD/FB13.1-MPTCP-SRC.git /usr/src
```

Build and install kernel:
```
cd /usr/src
make -j2 KERNCONF=MPTCP MODULES_OVERRIDE="ipfw dummynet siftr" buildkernel
make KERNCONF=MPTCP MODULES_OVERRIDE="ipfw dummynet siftr" installkernel
shutdown -r now
```

## Evaluation
This folder contains scripts and test results for evaluating performance of the scheduler. Results are assessed against 3 scenarios:
* Scenario 1 - Both subflows configured to 6Mpbs
* Scenario 2 - Subflow 1 configured to 3Mpbs, Subflow 2 configured to 6Mpbs
* Scenario 3 - Subflow 1 initially configured to 6Mpbs, Subflow 2 configured to 3Mpbs. Dynamic_delay.py is executed to dynamically vary subflow 1 throughput.

For all evaluations, ensure the multipath scheduler algorithm is configured to use DQN:
```
sysctl net.inet.tcp.mptcp.scheduler.algorithm=dqn
```

## Keys
This folder contains the public and private ssh keys used for authentication within the test environment.

## Modules
This folder contains the python wrapper module for the multipath scheduler system calls.

To build and install the module:
```bash
cd modules/syscalls
python setup.py install
```

To import and use the module:
```python
from syscalls import *
```

## Offline Learning
This folder contains the scripts and data for performing offline training against each scenario, along with federated learning using offline data. A copy of the trained models used for evaluation is also included.

## Online Learning
This folder contains the scripts used for performing online training of the scheduler model. A copy of the trained models used for evaluation is also included.

## Setup
This folder cotains scripts and configurations files for setting up the test environment.