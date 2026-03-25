import subprocess
import sys

commands = [
    "python app.py",
    "python SMTPmain.py"
]

procs = [subprocess.Popen(i, shell=True) for i in commands]

for p in procs:
    p.wait()