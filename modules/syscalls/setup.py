from distutils.core import setup, Extension

def main():
    setup(name="syscalls",
          version="1.0.0",
          description="Python wrapper for FreeBSD13.1 MPTCP system calls.",
          author="Brenton Fleming",
          author_email="bkfl@deakin.edu.au",
          ext_modules=[Extension("syscalls", ["py_syscalls.c"])])

if __name__ == "__main__":
    main()
