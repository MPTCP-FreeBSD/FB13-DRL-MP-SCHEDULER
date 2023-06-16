#pragma once

#define CC_DRL_MAX_QUEUE 10000

struct pkt {
	u_int		cwnd;
	int		smoothed_rtt;
	int		cong_events;

	u_int		laddr;
	u_int		lport;
};

struct state {
    int awnd;
    int cwnd;
    int swnd;
    int rtt;
    int rttvar;
};