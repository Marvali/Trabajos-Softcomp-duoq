# Implementation Changes – Persistent Hashmap for Coral Caching

## Overview
This document records the refactor of the **coral power calculation caching** mechanism in `reef_optimization.py`. The previous implementation utilized a linear search over a list of previously calculated "ranking" entries, which was inefficient and only checked for corals based on their grid position rather than their configuration. This has been replaced by a **Persistent Hashmap** (using `pickle`) that provides O(1) lookups for any coral configuration.

## Motivation
- **Efficiency** – The previous linear search became slower as the number of corals increased. A hashmap lookup is constant time O(1).
- **Correctness** – The previous search relied on position `(row, col)`. If a coral moved, it was recalculated. The new approach hashes the coral's layout (grid), so identical corals are recognized regardless of their position.
- **Persistence** – By saving the cache to disk (`coral_cache.pkl`), expensive power calculations are saved across different runs of the program, significantly speeding up subsequent executions.

## Changes Made
1. **Implemented `PersistentCoralCache` Class**
   - A class that wraps a standard Python dictionary.
   - Loads from `coral_cache.pkl` on initialization.
   - Saves to `coral_cache.pkl` automatically when requested (e.g., at end of execution).
   - Use of `pickle` allows efficient binary serialization.

2. **Updated `calculate_coral_power`**
   - Now checks the global `CORAL_CACHE` before performing the heavy calculation.
   - Key: `gr.tobytes()` (byte representation of the numpy array layout).
   - Value: `float` (calculated power).
   - If a cache miss occurs, the power is calculated and then stored in the cache.

3. **Refactored `evaluate_reef_power`**
   - Removed the inefficient linear search block:
     ```python
     # REMOVED:
     for k, entry in enumerate(existingRanking):
         if int(entry[1]) == i + 1 and int(entry[2]) == j + 1: ...
     ```
   - Replaced it with a direct call to the cache-enabled `calculate_coral_power`.

## Implementation Details
```python
class PersistentCoralCache:
    def __init__(self, filename="coral_cache.pkl"):
        # ... loads cache using pickle ...

    def get(self, key):
        return self.cache.get(key)

# In calculate_coral_power:
gr_key = np.ascontiguousarray(gr).tobytes()
cached_power = CORAL_CACHE.get(gr_key)
if cached_power is not None:
    return cached_power
```

## Performance Impact
- **Lookup Time**: Reduced from O(N) (linear scan of ranking) to O(1) (hash lookup).
- **Recalculation**: Calculating power for a coral takes significant time. Persistence ensures that across multiple runs, we never re-evaluate the exact same coral configuration, potentially saving minutes or hours of computation in extensive experiments.

## Usage
- The cache file `coral_cache.pkl` is automatically created in the working directory.
- It is read on startup and updated/saved at the end of the `evaluate_reef_power` function and the CRO algorithm.
- If you change the wind data or power curve parameters significantly, **you should delete `coral_cache.pkl`** to force recalculation, as the cache keys (layout only) do not currently encode environment parameters.

---
*Document generated on 2025‑12‑10 by Antigravity – a powerful agentic AI coding assistant.*