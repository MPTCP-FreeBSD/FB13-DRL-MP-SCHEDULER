#include <Python.h>
#include <malloc.h>
#include <sys/syscall.h>

#include "py_syscalls.h"

static PyObject *method_mp_sched_dqn_set_proc(PyObject *self, PyObject *args) {
    int err = syscall(585);
    return PyLong_FromLong(err);
}

static PyObject *method_mp_sched_dqn_clear_proc(PyObject *self, PyObject *args) {
    int err = syscall(586);
    return PyLong_FromLong(err);
}

static PyObject *method_mp_sched_dqn_get_state(PyObject *self, PyObject *args) {
    u_int ref;
    struct state sf1_prev_state;
    struct state sf2_prev_state;
    struct state sf1_state;
    struct state sf2_state;
    int prev_action;
    
    int err = syscall(587, &ref, &sf1_prev_state, &sf2_prev_state, &sf1_state, &sf2_state, &prev_action);
    if (err < 0) {
        PyErr_SetString(PyExc_Exception, "Error during system call.");
        return NULL;
    }

    PyObject *state = PyList_New(0);
    PyList_Append(state, PyLong_FromLong(sf1_state.awnd));
    PyList_Append(state, PyLong_FromLong(sf1_state.cwnd));
    PyList_Append(state, PyLong_FromLong(sf1_state.swnd));
    PyList_Append(state, PyLong_FromLong(sf1_state.rtt));
    PyList_Append(state, PyLong_FromLong(sf1_state.rttvar));
    PyList_Append(state, PyLong_FromLong(sf2_state.awnd));
    PyList_Append(state, PyLong_FromLong(sf2_state.cwnd));
    PyList_Append(state, PyLong_FromLong(sf2_state.swnd));
    PyList_Append(state, PyLong_FromLong(sf2_state.rtt));
    PyList_Append(state, PyLong_FromLong(sf2_state.rttvar));
    
    PyObject *prev_state = PyList_New(0);
    PyList_Append(prev_state, PyLong_FromLong(sf1_prev_state.awnd));
    PyList_Append(prev_state, PyLong_FromLong(sf1_prev_state.cwnd));
    PyList_Append(prev_state, PyLong_FromLong(sf1_prev_state.swnd));
    PyList_Append(prev_state, PyLong_FromLong(sf1_prev_state.rtt));
    PyList_Append(prev_state, PyLong_FromLong(sf1_prev_state.rttvar));
    PyList_Append(prev_state, PyLong_FromLong(sf2_prev_state.awnd));
    PyList_Append(prev_state, PyLong_FromLong(sf2_prev_state.cwnd));
    PyList_Append(prev_state, PyLong_FromLong(sf2_prev_state.swnd));
    PyList_Append(prev_state, PyLong_FromLong(sf2_prev_state.rtt));
    PyList_Append(prev_state, PyLong_FromLong(sf2_prev_state.rttvar));
    
    PyObject *values = PyTuple_New(4);
    PyTuple_SetItem(values, 0, PyLong_FromLong(ref));
    PyTuple_SetItem(values, 1, state);
    PyTuple_SetItem(values, 2, prev_state);
    PyTuple_SetItem(values, 3, PyLong_FromLong(prev_action));
    
    return values;
}

static PyObject *method_mp_sched_dqn_select_subflow(PyObject *self, PyObject *args) {
    u_int ref;
    int action;

    /* Parse arguments */
    if(!PyArg_ParseTuple(args, "II", &ref, &action)) {
        PyErr_SetString(PyExc_Exception, "Error parsing arguments.");
        return NULL;
    }

    int err = syscall(588, ref, action);
    return PyLong_FromLong(err);
}

static PyObject *method_cc_drl_update_cwnd(PyObject *self, PyObject *args) {
    u_int cwnd, laddr, lport;

    /* Parse arguments */
    if(!PyArg_ParseTuple(args, "III", &cwnd, &laddr, &lport)) {
        PyErr_SetString(PyExc_Exception, "Error parsing arguments.");
        return NULL;
    }

    int err = syscall(583, cwnd, laddr, lport);
    return PyLong_FromLong(err);
}

static PyObject *method_cc_drl_get_buffer(PyObject *self, PyObject *args) {
    struct pkt *buffer;
    int size;

    buffer = malloc(sizeof(struct pkt) * CC_DRL_MAX_QUEUE);

    int err = syscall(584, buffer, &size);
    if (err < 0) {
        PyErr_SetString(PyExc_Exception, "Error during system call.");
        return NULL;
    }

    PyObject *list = PyList_New(0);
    for (int i = 0; i < size; i++) {
        PyObject *item = PyList_New(0);
        PyList_Append(item, PyLong_FromLong(buffer[i].cwnd));
	    PyList_Append(item, PyLong_FromLong(buffer[i].smoothed_rtt));
	    PyList_Append(item, PyLong_FromLong(buffer[i].cong_events));
	    PyList_Append(item, PyLong_FromLong(buffer[i].laddr));
	    PyList_Append(item, PyLong_FromLong(buffer[i].lport));
	    PyList_Append(list, item);
    }

    free(buffer);

    return list;
}

static PyMethodDef PyMethods_syscalls[] = {
    {"mp_sched_dqn_set_proc", method_mp_sched_dqn_set_proc, METH_VARARGS, "Python wrapper for mp_sched_dqn_set_proc system call"},
    {"mp_sched_dqn_clear_proc", method_mp_sched_dqn_clear_proc, METH_VARARGS, "Python wrapper for mp_sched_dqn_clear_proc system call"},
    {"mp_sched_dqn_get_state", method_mp_sched_dqn_get_state, METH_VARARGS, "Python wrapper for mp_sched_dqn_get_state system call"},
    {"mp_sched_dqn_select_subflow", method_mp_sched_dqn_select_subflow, METH_VARARGS, "Python wrapper for mp_sched_dqn_select_subflow system call"},
    {"cc_drl_update_cwnd", method_cc_drl_update_cwnd, METH_VARARGS, "Python wrapper for cc_drl_update_cwnd system call"},
    {"cc_drl_get_buffer", method_cc_drl_get_buffer, METH_VARARGS, "Python wrapper for cc_drl_get_buffer system call"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef PyModule_syscalls = {
    PyModuleDef_HEAD_INIT,
    "syscalls",
    "Python wrapper for FreeBSD13.1 MPTCP ystem calls.",
    -1,
    PyMethods_syscalls
};

PyMODINIT_FUNC PyInit_syscalls(void) {
    return PyModule_Create(&PyModule_syscalls);
}
