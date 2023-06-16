@echo off

set scenarioname=scenario2

REM SSH key name
set sshkey=mptcprootkey

REM Path to SSH on controller
set keypath=..\keys\

REM Address of VM Host Machine
set vmhostaddr=localhost

REM Access to the source host
set srcvm=FB13-Host1
set srchost=Host1
set /A srchostport=1122
set srchostaddr=172.16.1.2
set srchostmpaddr=172.16.2.2

REM Access to the destination host
set dstvm=FB13-Host2
set dsthost=Host2
set /A dsthostport=1222
set dsthostaddr=172.16.3.2
set dsthostmpaddr=0

REM Access to the two dummynet routers
set /A router1port=2122
set /A router2port=2222

REM File to be transferred
set filename=100M.file
set rcvfilepath=/tmp
set filesource=/root/%filename%
set filedest=%dsthostaddr%:%rcvfilepath%

REM Dummynet data rate
set vm1drate=3Mbps
set vm2drate=6Mbps
set plr=0
set queue=50

REM Number of times to repeat transfer for training
set /A repeats=10

REM Select scheduler algorithm to use
set schedalgo=dqn

REM Configure desired dummynet settings
(echo Configuring DummynetVM1 for %vm1drate%)
ssh -p %router1port% -i %keypath%/%sshkey% root@%vmhostaddr% "ipfw pipe 1 config plr %plr% queue %queue% bw %vm1drate%"
ssh -p %router1port% -i %keypath%/%sshkey% root@%vmhostaddr% "ipfw pipe 2 config plr %plr% queue %queue% bw %vm1drate%"

(echo Configuring DummynetVM2 for %vm2drate%)
ssh -p %router2port% -i %keypath%/%sshkey% root@%vmhostaddr% "ipfw pipe 1 config plr %plr% queue %queue% bw %vm2drate%"
ssh -p %router2port% -i %keypath%/%sshkey% root@%vmhostaddr% "ipfw pipe 2 config plr %plr% queue %queue% bw %vm2drate%"

REM Set addresses on test hosts
(echo Configure %srchost% with mp_addr %srchostmpaddr%)
(echo Configure %dsthost% with mp_addr %dsthostmpaddr%)

REM Note this use of sysctl results in an error message but does achieve
REM the desired result of clearing the net.inet.tcp.mptcp.mp_addresses list.
ssh -p %srchostport% -i %keypath%/%sshkey% root@%vmhostaddr% "sysctl net.inet.tcp.mptcp.mp_addresses="%srchostmpaddr%""
ssh -p %dsthostport% -i %keypath%/%sshkey% root@%vmhostaddr% "sysctl net.inet.tcp.mptcp.mp_addresses="%dsthostmpaddr%""

REM Set DQN as scheduler algorithm on source host
(echo Configure %srchost% with scheduler.aglorithm %schedalgo%)
ssh -p %srchostport% -i %keypath%/%sshkey% root@%vmhostaddr% "sysctl net.inet.tcp.mptcp.scheduler.algorithm="%schedalgo%""

REM Use rsync to transfer file for training X times
for /l %%x in (1, 1, %repeats%) do (
   (echo Executing rsync on %srchost% - %%x/%repeats%)
    REM Log into receiver and clear file
    ssh -p %dsthostport% -i %keypath%/%sshkey% root@%vmhostaddr% "rm -f %rcvfilepath%/%filename%"
    timeout /t 1 /nobreak > NUL
    REM Log into client host (srchost) and start rsync
    ssh -p %srchostport% -i %keypath%/%sshkey% root@%vmhostaddr% "rsync -e 'ssh -i /root/.ssh/%sshkey% -o StrictHostKeyChecking=no ' --progress '%filesource%' '%filedest%'"
)

REM completed
(echo Evaluate complete)
goto :eof

REM error
:error
    (echo Abort test)
    goto :eof