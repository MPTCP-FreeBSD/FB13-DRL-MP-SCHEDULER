@echo off

REM Copy the public and private keys across to all the testbed hosts.
REM Assumes that NAT forwarding has been configured and each of the VMs is running.

REM This _should_ be run on the controller host, but will work if run from elsewhere. 

REM Assumes this is run on the VM Host machine
set controller=localhost

REM NAT forwarding ports
set /A host1port=1122
set /A host2port=1222
set /A router1port=2122
set /A router2port=2222

REM SSH key paths
set pubkey=../../keys/mptcprootkey.pub
set privkey=../../keys/mptcprootkey

REM First test host
(echo create .ssh folder)
ssh -i %privkey% -p %host1port% root@%controller% "mkdir .ssh/"
(echo Copying root public key to host at port %host1port%)
scp -i %privkey% -o StrictHostKeyChecking=no -P %host1port% %pubkey% root@%controller%:/root/.ssh/authorized_keys
(echo set authorized keys permissions to 644)
ssh -i %privkey% -p %host1port% root@%controller% "chmod 644 .ssh/authorized_keys"
(echo Copying root private key to host at port %host1port%)
scp -i %privkey% -o StrictHostKeyChecking=no -P %host1port% %privkey% root@%controller%:/root/.ssh/
(echo set private key permissions to 400)
ssh -i %privkey% -p %host1port% root@%controller% "chmod 400 .ssh/mptcprootkey"

REM Second test host
(echo create .ssh folder)
ssh -i %privkey% -p %host2port% root@%controller% "mkdir .ssh/"
(echo Copying root public key to host at port %host2port%)
scp -i %privkey% -o StrictHostKeyChecking=no -P %host2port% %pubkey% root@%controller%:/root/.ssh/authorized_keys
(echo set authorized keys permissions to 644)
ssh -i %privkey% -p %host2port% root@%controller% "chmod 644 .ssh/authorized_keys"
(echo Copying root private key to host at port %host2port%)
scp -i %privkey% -o StrictHostKeyChecking=no -P %host2port% %privkey% root@%controller%:/root/.ssh/
(echo set private key permissions to 400)
ssh -i %privkey% -p %host2port% root@%controller% "chmod 400 .ssh/mptcprootkey"

REM First router
(echo create .ssh folder)
ssh -i %privkey% -p %router1port% root@%controller% "mkdir .ssh/"
(echo Copying root public key to host at port %router1port%)
scp -i %privkey% -o StrictHostKeyChecking=no -P %router1port% %pubkey% root@%controller%:/root/.ssh/authorized_keys
(echo set authorized keys permissions to 644)
ssh -i %privkey% -p %router1port% root@%controller% "chmod 644 .ssh/authorized_keys"
(echo Copying root private key to host at port %router1port%)
scp -i %privkey% -o StrictHostKeyChecking=no -P %router1port% %privkey% root@%controller%:/root/.ssh/
(echo set private key permissions to 400)
ssh -i %privkey% -p %router1port% root@%controller% "chmod 400 .ssh/mptcprootkey"

REM Second router
(echo create .ssh folder)
ssh -i %privkey% -p %router2port% root@%controller% "mkdir .ssh/"
(echo Copying root public key to host at port %router2port%)
scp -i %privkey% -o StrictHostKeyChecking=no -P %router2port% %pubkey% root@%controller%:/root/.ssh/authorized_keys
(echo set authorized keys permissions to 644)
ssh -i %privkey% -p %router2port% root@%controller% "chmod 644 .ssh/authorized_keys"
(echo Copying root private key to host at port %router2port%)
scp -i %privkey% -o StrictHostKeyChecking=no -P %router2port% %privkey% root@%controller%:/root/.ssh/
(echo set private key permissions to 400)
ssh -i %privkey% -p %router2port% root@%controller% "chmod 400 .ssh/mptcprootkey"

echo done
