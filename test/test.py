import time
import os
from multiprocessing import Pool


def test(t: int):
    print(f"start {os.getpid()} ppid: {os.getppid()}")
    time.sleep(t)
    print(f"end {os.getpid()} ppid: {os.getppid()}")


if __name__ == "__main__":
    with Pool(5) as p:
        print(p.map(test, [1000, 100, 10, 2012]))
