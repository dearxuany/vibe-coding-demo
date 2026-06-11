#!/usr/bin/env python3
"""Quick Sort implementation in Python."""

import random


def quicksort(arr, low=0, high=None):
    """
    Sort an array using the Quick Sort algorithm (in-place).

    Args:
        arr:  List of comparable elements
        low:  Starting index (default 0)
        high: Ending index (default len(arr) - 1)
    """
    if high is None:
        high = len(arr) - 1

    if low < high:
        pivot_idx = partition(arr, low, high)
        quicksort(arr, low, pivot_idx - 1)
        quicksort(arr, pivot_idx + 1, high)


def partition(arr, low, high):
    """
    Partition the array around a pivot (Lomuto scheme).
    Returns the final pivot index.
    """
    # Choose median-of-three as pivot to mitigate worst-case on sorted/reverse input
    mid = (low + high) // 2
    pivot_candidates = [(arr[low], low), (arr[mid], mid), (arr[high], high)]
    pivot_candidates.sort(key=lambda x: x[0])
    pivot_val, pivot_idx = pivot_candidates[1]

    # Move pivot to end
    arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]

    i = low  # boundary for elements <= pivot
    for j in range(low, high):
        if arr[j] <= pivot_val:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1

    # Place pivot in its final position
    arr[i], arr[high] = arr[high], arr[i]
    return i


def main():
    # Test with various inputs
    test_cases = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 1, 4, 2, 8],
        [1],
        [],
        [3, 3, 3, 3],
        [9, 8, 7, 6, 5, 4, 3, 2, 1],
    ]

    for original in test_cases:
        arr = original.copy()
        quicksort(arr)
        print(f"  {original}  →  {arr}")


if __name__ == "__main__":
    # Quick smoke test with a random list
    data = [random.randint(0, 100) for _ in range(10)]
    print(f"Before: {data}")
    quicksort(data)
    print(f"After:  {data}")
    print()

    print("More tests:")
    main()
