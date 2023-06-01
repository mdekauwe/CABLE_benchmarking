"""Contains functions for running bitwise comparisons."""

import subprocess
import multiprocessing
import queue

from benchcab.task import Task
from benchcab.internal import CWD, SITE_OUTPUT_DIR, SITE_BITWISE_CMP_DIR, NCPUS


def get_comparison_name(task_a: Task, task_b: Task) -> str:
    """Returns the naming convention used for bitwise comparisons.

    Assumes `met_forcing_file` and `sci_conf_id` attributes are
    common to both tasks.
    """
    met_forcing_base_filename = task_a.met_forcing_file.split(".")[0]
    return (
        f"{met_forcing_base_filename}_S{task_a.sci_conf_id}"
        f"_R{task_a.branch_id}_R{task_b.branch_id}"
    )


def run_comparisons(comparisons: list[tuple[Task, Task]], verbose=False):
    """Runs bitwise comparison tasks serially."""
    for task_a, task_b in comparisons:
        run_comparison(task_a, task_b, verbose=verbose)


def run_comparisons_in_parallel(comparisons: list[tuple[Task, Task]], verbose=False):
    """Runs bitwise comparison tasks in parallel across multiple processes."""

    task_queue: multiprocessing.Queue = multiprocessing.Queue()
    for pair in comparisons:
        task_queue.put(pair)

    processes = []
    for _ in range(NCPUS):
        proc = multiprocessing.Process(target=worker, args=[task_queue, verbose])
        proc.start()
        processes.append(proc)

    for proc in processes:
        proc.join()


def worker(task_queue: multiprocessing.Queue, verbose=False):
    """Runs bitwise comparison tasks in `task_queue` until the queue is emptied."""
    while True:
        try:
            task_a, task_b = task_queue.get_nowait()
        except queue.Empty:
            return
        run_comparison(task_a, task_b, verbose=verbose)


def run_comparison(task_a: Task, task_b: Task, verbose=False):
    """Executes `nccmp -df` between the NetCDF output file of `task_a` and of `task_b`."""
    task_a_output = CWD / SITE_OUTPUT_DIR / task_a.get_output_filename()
    task_b_output = CWD / SITE_OUTPUT_DIR / task_b.get_output_filename()
    output_file = (
        CWD / SITE_BITWISE_CMP_DIR / f"{get_comparison_name(task_a, task_b)}.txt"
    )
    if verbose:
        print(
            f"Comparing files {task_a_output.name} and {task_b_output.name} bitwise..."
        )
    cmd = f"nccmp -df {task_a_output} {task_b_output} 2>&1"
    if verbose:
        print(f"  {cmd}")
    proc = subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(proc.stdout)
        print(
            f"Failure: files {task_a_output.name} {task_b_output.name} differ. "
            f"Results of diff have been written to {output_file}"
        )
    else:
        print(
            f"Success: files {task_a_output.name} {task_b_output.name} are identitical"
        )
