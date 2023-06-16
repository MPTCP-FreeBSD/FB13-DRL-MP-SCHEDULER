import time, paramiko, random, select


host = "localhost"
port = 2122
username = "root"
password = "mptcproot"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password, port=port)

BW_MIN = 2
BW_MAX = 10

bw = (BW_MAX + BW_MIN / 2)

while True:
    # Adjust bandwidth random value between -2 and +2
    bw += random.randint(-2,2)
    # Cap bw between min and max
    bw = min(bw, BW_MAX)
    bw = max(bw, BW_MIN)
    # Set new bandwidth for pipe 1 and 2
    stdin, stdout, stderr = ssh.exec_command('ipfw pipe 1 config plr 0 queue 50 bw {0}Mbps'.format(bw))
    while not stdout.channel.exit_status_ready():
        # Only print data if there is data to read in the channel
        if stdout.channel.recv_ready():
            rl, wl, xl = select.select([ stdout.channel ], [ ], [ ], 0.0)
            if len(rl) > 0:
                tmp = stdout.channel.recv(1024)
                output = tmp.decode()
                print(output)
    ssh.exec_command('ipfw pipe 2 config bw {0}Mbps'.format(bw))
    while not stdout.channel.exit_status_ready():
        # Only print data if there is data to read in the channel
        if stdout.channel.recv_ready():
            rl, wl, xl = select.select([ stdout.channel ], [ ], [ ], 0.0)
            if len(rl) > 0:
                tmp = stdout.channel.recv(1024)
                output = tmp.decode()
                print(output)
    # sleep for 500ms - 1s
    time.sleep(random.randint(500, 1000) / 1000)