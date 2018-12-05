"""
Numpy utilities.

This module is named 'npy' because importing numpy from numpy.py produces errors.
"""
import unittest
from typing import Union, Sequence, Collection, Tuple, Optional, Any, Dict

import numpy as np

__author__ = "Bojan Potočnik"


# noinspection PyPep8Naming
class ndarray(np.ndarray):
    """
    Numpy np.ndarray wrapper with additional attributes. More info on `Subclassing ndarray
    <https://docs.scipy.org/doc/numpy-1.13.0/user/basics.subclassing.html#slightly-more-realistic-example-attribute
    -added-to-existing-array>`_.
    """

    def __new__(cls, existing_array: np.ndarray, comment: Optional[Any] = None) -> 'ndarray':
        """
        Create new np.ndarray with additional attributes.

        :param existing_array: Existing Numpy array to wrap.
        :param comment:        Comment to add as an additional attribute to the existing array object.
                               This can be any object not only string (it is only named comment for clarity).

        :return: Wrapped view of ndarray with added comment attribute.
        """
        # Input array is an already formed ndarray instance.
        # It needs to be first cast to this new class type.
        obj = np.asarray(existing_array).view(type=cls)
        # Add the new attribute to the created instance.
        obj.comment = comment
        # Save reference to the original instance (useful when this instance is required only temporary).
        obj.original_array = existing_array

        return obj

    def __array_finalize__(self, obj: 'ndarray'):
        """See `InfoArray.__array_finalize__ <https://docs.scipy.org/doc/numpy-1.13.0/user/basics.subclassing.html
        #simple-example-adding-an-extra-attribute-to-ndarray>`_ for comments."""
        if obj is None:
            return

        self.comment: Optional[Any] = getattr(obj, 'comment', None)
        self.original_array: np.ndarray = getattr(obj, 'original_array', None)


class IgnoreWarnings:
    """
    Context manager class for ignoring warnings.
    """

    def __init__(self) -> None:
        self._backup: Dict[str, str] = {}

    def start(self) -> None:
        """Start ignoring warnings."""
        # Change numpy error behaviour so that warnings about invalid values are ignored.
        self._backup = np.geterr()
        np.seterr(all='ignore')

    def stop(self) -> None:
        """Stop ignoring warnings (restore previous state)."""
        if self._backup:
            # Restore original warnings settings.
            np.seterr(**self._backup)

    def __enter__(self) -> None:
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()


def add_to_front(buffer: np.ndarray, value_s: Union[int, float, np.dtype, Collection]) -> np.ndarray:
    """
    Add new value(s) to the start of the buffer (index 0) and discard the
    oldest (index length-1), in-place without generating new array.

    :param buffer: Buffer to add data to.
    :param value_s: Value(s) to add to the front of the buffer.

    :return: The same buffer as provided (`buffer` parameter).

    """
    if isinstance(value_s, Collection):
        n = len(value_s)
        if n:
            buffer[n:] = buffer[:-n]  # Move values [0..len-n] to [n..len] - shift right for n.
            buffer[0:n] = value_s  # Add new values to the beginning ([0..n]).
    else:
        buffer[1:] = buffer[:-1]  # Move values [0..len-1] to [1..len] - shift right for 1.
        buffer[0] = value_s  # Add new value to the beginning ([0]).

    return buffer


def add_to_back(buffer: np.ndarray, value_s: Union[int, float, np.dtype, Collection]) -> np.ndarray:
    """
    Add new value(s) to the end of the buffer (index length-1) and discard the
    oldest (index 0), in-place without generating new array.

    :param buffer: Buffer to add data to.
    :param value_s: Value(s) to add to the front of the buffer.

    :return: The same buffer as provided (`buffer` parameter).

    """
    if isinstance(value_s, Collection):
        n = len(value_s)
        if n:
            buffer[:-n] = buffer[n:]  # Move values [n..len] to [0..len-n] - shift left for n.
            buffer[-n:] = value_s  # Add new values [0..n] to the end [len-n..len].
    else:
        buffer[:-1] = buffer[1:]  # Move values [1..len] to [0..len-1] - shift left for 1.
        buffer[-1] = value_s  # Add new value to the end ([len-1]).

    return buffer


def is_coherent(sequence: Union[np.ndarray, Sequence[int]]):
    """
    :return: `True` if all values in the sequence are coherent (sequential).
    """
    if isinstance(sequence, np.ndarray):
        coherent = np.all(np.diff(sequence) == 1)
    else:
        coherent = (sequence == range(sequence[0], sequence[-1] + 1))
    return coherent


def sort(*arrays: np.ndarray, reverse: bool = False) -> Tuple[np.ndarray, ...]:
    """
    Sort multiple 1D numpy arrays together based on the first provided array.

    :param reverse: Whether to sort in the reverse, descending order.

    :return: Sorted array(s) (copy).
    """
    # Get indices for sorting.
    idx = np.argsort(arrays[0])
    # A standard sorting order is ascending order.
    if reverse:
        idx = np.flip(idx, axis=0)
    # Generate new arrays which are sorted.
    result = tuple(np.take(array, indices=idx) for array in arrays)

    return result if (len(result) > 1) else result[0]


def sort_rows(array: np.ndarray, column: int, reverse: bool = False) -> np.ndarray:
    """
    Sort whole rows of N-dimensional numpy array together, based on the provided column.
    Rows are moved but values of their columns is not.

    :param array:   Array of which rows to sort.
    :param column:  Column which will dictate - will be used for sorting.
    :param reverse: Whether to sort in the reverse, descending order.

    :return: Sorted array (copy).
    """
    # Get indices for sorting - but take the whole column, not row!
    idx = np.argsort(array.T[column])
    # A standard sorting order is ascending order.
    if reverse:
        idx = np.flip(idx, axis=0)
    # Generate new array which are sorted.
    return array.take(indices=idx, axis=0)


def groups_of_same_number(array: np.ndarray, number: int) -> np.ndarray:
    """
    Find the groups of consecutive numbers in a numpy array.

    :see: https://stackoverflow.com/a/24892274/5616255

    :param array: Array to search in.
    :param number: Number of which occurrences to find.

    :return: An array with shape (m, 2), where m is the number of groups/"runs" of specified `number`.
             The first column is the index of the first `number` in each run, and the second is the
             index of the first non-`number` element after the group/run.
    """
    # Create an array that is 1 where a is 0, and pad each end with an extra 0.
    is_number = np.concatenate(([0], np.equal(array, number).view(np.int8), [0]))
    abs_diff = np.abs(np.diff(is_number))
    # Runs start and end where absolute difference is 1.
    ranges = np.where(abs_diff == 1)[0].reshape(-1, 2)

    return ranges


# #############################
# region Testing


class TestSort(unittest.TestCase):
    from0to9 = np.arange(10)
    from0to9_strings_a = np.array(tuple(f"{x}a" for x in from0to9))
    from0to9_strings_b = np.array(tuple(f"{x}b" for x in from0to9))
    from9to0 = np.arange(9, -1, -1)
    from9to0_strings_a = np.array(tuple(f"{x}a" for x in from9to0))
    from9to0_strings_b = np.array(tuple(f"{x}a" for x in from9to0))

    def test_one_array(self) -> None:
        self.assertTrue(np.all(np.equal(self.from0to9, sort(self.from0to9))))
        self.assertTrue(np.all(np.equal(self.from0to9, sort(self.from9to0))))
        self.assertTrue(np.all(np.equal(self.from9to0, sort(self.from0to9, reverse=True))))
        self.assertTrue(np.all(np.equal(self.from9to0, sort(self.from9to0, reverse=True))))

    def test_multiple_arrays(self) -> None:
        print(sort(self.from0to9, self.from0to9_strings_a, self.from0to9_strings_b))
        print(sort(self.from0to9, self.from0to9_strings_a, self.from0to9_strings_b, reverse=True))


# endregion Testing

if __name__ == "__main__":
    unittest.main()
