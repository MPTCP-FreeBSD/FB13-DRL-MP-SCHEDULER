@echo off

REM Copy the config files onto each VM.
REM Assumes private/public keys have been copied already, is executed on the VM Host machine

REM Assumes this is run on the VM Host machine
set controller=localhost

REM NAT forwarding ports
set /A host1port=1122
set /A host2port=1222
set /A router1port=2122
set /A router2port=2222

REM First test host
scp -P %host1port% -i ../../keys/mptcprootkey ../confs/Host1/rc.conf root@%controller%:/etc/
scp -P %host1port% -i ../../keys/mptcprootkey ../confs/Host1/ipfw.rules root@%controller%:/etc/
scp -P %host1port% -i ../../keys/mptcprootkey ../confs/Host1/loader.conf root@%controller%:/boot/

REM Second test host
scp -P %host2port% -i ../../keys/mptcprootkey ../confs/Host2/rc.conf root@%controller%:/etc/
scp -P %host2port% -i ../../keys/mptcprootkey ../confs/Host2/ipfw.rules root@%controller%:/etc/
scp -P %host2port% -i ../../keys/mptcprootkey ../confs/Host2/loader.conf root@%controller%:/boot/

REM First router
scp -P %router1port% -i ../../keys/mptcprootkey ../confs/Router1/rc.conf root@%controller%:/etc/
scp -P %router1port% -i ../../keys/mptcprootkey ../confs/Router1/ipfw.rules root@%controller%:/etc/
scp -P %router1port% -i ../../keys/mptcprootkey ../confs/Router1/loader.conf root@%controller%:/boot/

REM Second router
scp -P %router2port% -i ../../keys/mptcprootkey ../confs/Router2/rc.conf root@%controller%:/etc/
scp -P %router2port% -i ../../keys/mptcprootkey ../confs/Router2/ipfw.rules root@%controller%:/etc/
scp -P %router2port% -i ../../keys/mptcprootkey ../confs/Router2/loader.conf root@%controller%:/boot/

echo done