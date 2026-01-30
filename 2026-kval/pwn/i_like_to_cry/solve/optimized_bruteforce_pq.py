# Generated with ChatGPT

import os
import random
from multiprocessing import Event, Process, Queue, cpu_count

OFFSET = 0x110
TARGET = b"sh\x00"
TARGET_INT = int.from_bytes(TARGET, "big")
TARGET_BITS = len(TARGET) * 8
TARGET_MASK = (1 << TARGET_BITS) - 1

MIN_P = 10**0x14A
MAX_P = 10**0x14C - 1
MIN_Q = MIN_P
MAX_Q = MAX_P

MAX_BITS = MAX_P.bit_length()


def sample_in_range(rng, low, high):
    while True:
        candidate = rng.getrandbits(MAX_BITS)
        if candidate < low or candidate > high:
            continue
        return candidate


def matches_condition(n):
    length_bytes = (n.bit_length() + 7) // 8
    required = OFFSET + len(TARGET)
    if length_bytes < required:
        return False
    shift_bytes = length_bytes - required
    candidate = (n >> (shift_bytes * 8)) & TARGET_MASK
    return candidate == TARGET_INT


def worker(
    worker_id,
    stop_event,
    result_queue,
):
    rng = random.SystemRandom(int.from_bytes(os.urandom(16), "big") ^ worker_id)
    iterations = 0

    while not stop_event.is_set():
        iterations += 1

        p = sample_in_range(rng, MIN_P, MAX_P)
        q = sample_in_range(rng, MIN_Q, MAX_Q)
        n = p * q

        if matches_condition(n):
            if not stop_event.is_set():
                result_queue.put((p, q, n))
                stop_event.set()
            return


def main():
    worker_count = cpu_count()
    stop_event = Event()
    result_queue = Queue()

    processes = [
        Process(
            target=worker,
            args=(i, stop_event, result_queue),
            daemon=True,
        )
        for i in range(worker_count)
    ]

    for proc in processes:
        proc.start()

    try:
        p, q, n = result_queue.get()
        print("Found p and q!")
        print(f"p = {p}")
        print(f"q = {q}")
    except KeyboardInterrupt:
        print("Interrupted, stopping workers...")
    finally:
        stop_event.set()
        for proc in processes:
            proc.join()


if __name__ == "__main__":
    main()
