import sys
import shlex
import subprocess

from benchcab.internal import QSUB_FNAME

def create_job_script(project: str, user: str, config_path: str, sci_config_path: str):
    pass

def submit_job():
    cmd = shlex.split(f"qsub {QSUB_FNAME}")
    sb = subprocess.run(cmd, capture_output=True)
    if sb.returncode != 0:
        print("Error when submitting job to NCI queue")
        print(sb.stderr)
        sys.exit(1)

    print(f"Benchmark submitted in PBS job: {sb.stdout}")