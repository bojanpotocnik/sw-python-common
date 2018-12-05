import time
from typing import Optional, Tuple

__author__ = "Bojan Potočnik"

t0: float
"""Time reference point for this module."""


def reset() -> None:
    """
    The reference point of the value returned by `time.perf_counter()` is undefined,
    so that only the difference between the results of consecutive calls is valid.
    When this module is imported, the initial reference time point is marked and can
    be reset using this function.
    """
    global t0

    t0 = time.perf_counter()


def time_string(start_time: float = None, end_time: Optional[float] = None) -> str:
    """
    Get string with elapsed time information in form of:
        "x.xxx[xxx] Y"
    where `Y` is time unit decided based on amount of time passed and `x.xxx` is the calculated time
    which have 6 decimal places in case of nanoseconds.

    :param start_time: Starting point of the time which will be subtracted. If not provided, the initial starting
                       reference time saved when this module was imported will be used instead.
    :param end_time:   End point of the time from which `start_time` will be subtracted. If not provided,
                       the current time will be used.

    :return: Formatted time.
    """
    if end_time is None:
        end_time = time.perf_counter()
    if start_time is None:
        start_time = t0
    delta = end_time - start_time

    # Decide which unit to use. Usually operations timed with this function use fraction
    # of a second, that is why check from the lowest unit to the higher ones.
    if delta < 1e-6:
        # (1 µs, -∞ ns)
        unit = "ns"
        delta *= 1e9
        decimals = 6
    elif delta < 1e-3:
        # (1 ms, 1 µs]
        unit = "µs"
        delta *= 1e6
        decimals = 3
    elif delta < 1:
        # (1 s, 1 ms]
        unit = "ms"
        delta *= 1e3
        decimals = 3
    elif delta < 60:
        # (60 s, 1 s]
        unit = "s"
        # `time.perf_counter()` base unit is seconds.
        decimals = 3
    elif delta < 3600:
        # (1 h, 60 s]
        unit = "m"
        delta /= 60
        decimals = 3
    else:
        # (∞, 1 h]
        unit = "h"
        delta /= 3600
        decimals = 3

    return f"{delta:.{decimals}f} {unit}"


def get_elapsed(message: str, start_time: float, end_time: Optional[float] = None) -> str:
    """
    Get string with elapsed time information in form of:
        "Took x.xxx[xxx] Y for `message`"
    where `Y` is time unit decided based on amount of time passed and `x.xxx` is the calculated time
    which have 6 decimal places in case of nanoseconds.

    :param message:    Custom message (which caused this time elapsing).
    :param start_time: Starting point of the time which will be subtracted.
    :param end_time:   End point of the time from which `start_time` will be subtracted.

    :return: Formatted message.
    """
    return f"Took {time_string(start_time, end_time)} for {message}"


def print_elapsed(message: str, start_time: float, end_time: Optional[float] = None) -> float:
    """
    The same functionality as :py:`get_elapsed()` but prints the message and returns new time.

    :param message:    Custom message (which caused this time elapsing).
    :param start_time: Starting point of the time which will be subtracted.
    :param end_time:   End point of the time from which `start_time` will be subtracted.

    :return: Current time which can be used as a starting point for next operation.
    """
    print(get_elapsed(message, start_time, end_time))
    # Ignore time passed in this function by returning new value.
    return time.perf_counter()


def progress_data(start_time: Optional[float], iteration: Optional[int], total_iterations: Optional[int]) \
        -> Tuple[Optional[Tuple[int, int, int, int]], Optional[float]]:
    """
    Calculate elapsed time and progress.

    :param start_time:       Used for the elapsed time calculation. "Now" time point is :func:`time.perf_counter()`.
    :param iteration:        Used for progress calculation together with `total_iterations`. As this is meant as
                             and "iteration index", 1 is added before percentage calculation.
    :param total_iterations: Used for progress calculation together with `iteration`.

    :return: Tuple(elapsed time - hours; elapsed time - minutes; elapsed time - seconds; elapsed time - milliseconds)
             if start time was provided, else `None`; iteration percentage, if `iteration` and `total_iterations`
             were provided, else `None`)
    """
    if start_time is not None:
        elapsed_time = time.perf_counter() - start_time
        elapsed_time_ms = 1000.0 * (elapsed_time - int(elapsed_time))
        elapsed_time_h, elapsed_time_m = divmod(elapsed_time, 60 * 60)
        elapsed_time_m, elapsed_time_s = divmod(elapsed_time_m, 60)
        elapsed_time = (int(elapsed_time_h), int(elapsed_time_m), int(elapsed_time_s), int(elapsed_time_ms))
    else:
        elapsed_time = None

    if (iteration is not None) and (total_iterations is not None):
        # Iterations are mostly indexes ranging from [0, total_iterations).
        progress = 100.0 * (iteration + 1) / total_iterations
    else:
        progress = None

    return elapsed_time, progress


def progress_string(start_time: Optional[float],
                    iteration: Optional[int] = None, total_iterations: Optional[int] = None,
                    separator: Optional[str] = " - ", postfix: Optional[str] = None,
                    milliseconds: bool = True) -> str:
    """
    Format result of :func:`progress_data` and return the time string in form of "HH:MM:SS" or "HH:MM:SS:mmm",
    joined with the separator with the progress string in form of "XX.X % (iteration / total_iterations)",
    optionally adding a postfix.

    :param start_time:       See :func:`progress_data` function.
    :param iteration:        See :func:`progress_data` function.
    :param total_iterations: See :func:`progress_data` function.
    :param separator:        Separator between time string and progress string.
    :param postfix:          String to append at the end of the generated string (e.g. ": ").
    :param milliseconds:     If `True`, time string will include milliseconds in the form of "HH:MM:SS:mmm"
                             instead of "HH:MM:SS".

    :return: Formatted string.
    """
    elapsed_time, progress = progress_data(start_time, iteration, total_iterations)

    parts = []
    if elapsed_time:
        parts.append(f"{elapsed_time[0]:02d}:{elapsed_time[1]:02d}:{elapsed_time[2]:02d}")
        if milliseconds:
            parts.append(f".{elapsed_time[3]:03d}")

    if progress:
        if parts and separator:
            # Only append separator if there is actually any string before it.
            parts.append(separator)
        parts.append(f"{progress:.1f} % ({iteration} / {total_iterations})")

    if parts and postfix:
        # Only append postfix if there is actually any string before it.
        parts.append(postfix)

    return "".join(parts)


def _test_get_elapsed():
    times = (1, 0.1, 0.5, 0.6, 0.001, 55e-6, 55e-4, 55e-3, 55e-2, 1.234, 0.9992, 0.1, 0.2, 0.4)

    tx = time.perf_counter()
    for t in times:
        time.sleep(t)
        tx = print_elapsed("time.sleep({})".format(t), tx)


reset()

if __name__ == "__main__":
    _test_get_elapsed()
