# -*- coding: utf-8 -*-
# Derived from animFilters 1.0, Copyright 2018 Michal Mach.
# GNU GPL version 2 or later; see upstream/ and LICENSE.txt.
"""Pure algorithms; no Qt, Maya, file writes or scene operations."""
from __future__ import absolute_import, division, print_function

import math


def decimate(keys, tolerance):
    # Preserve the upstream cumulative linear-error criterion, without recursion.
    if len(keys) < 2:
        raise ValueError("At least two samples required")
    result = {}
    segments = [sorted((float(time), float(value)) for time, value in keys.items())]
    while segments:
        values = segments.pop()
        start, start_value = values[0]
        end, end_value = values[-1]
        errors = [abs(value - (((time - start) / (end - start)) * end_value + (1 - (time - start) / (end - start)) * start_value)) for time, value in values]
        total = sum(errors)
        if total < tolerance or total == 0 or len(values) <= 2:
            result[start] = start_value
            result[end] = end_value
        else:
            split = max(range(len(errors)), key=lambda index: errors[index])
            if split in (0, len(values) - 1):
                raise ValueError("Nonfinite samples or invalid segment")
            segments.append(values[split:])
            segments.append(values[:split + 1])
    return result


def filter_samples(raw, mode="adaptive", tolerance=0.25, window_size=35, sample_frequency=30.0, cutoff=7.0, order=5):
    warnings = []
    processed = {}
    if mode in ("median", "butterworth"):
        import numpy as np
        from scipy.signal import butter, filtfilt, medfilt
    for curve, keys in raw.items():
        start, end = min(keys), max(keys)
        if mode == "adaptive":
            values = decimate(keys, tolerance)
        elif mode == "median":
            # Match upstream: filter start..end-1; original endpoint at end remains.
            size = window_size + (1 if window_size % 2 == 0 else 0)
            samples = [keys[time] for time in range(start, end)]
            if size > len(samples):
                warnings.append("{}: median kernel exceeds samples; upstream zero-padding applies".format(curve))
            filtered = medfilt(samples, size)
            values = {float(time): float(filtered[time - start]) for time in range(start, end)}
        else:
            # Keep upstream 30-frame reference and interpolation model.
            count = max(2, int(sample_frequency * (end - start) / 30.0 + 1))
            times = np.linspace(start, end, count, endpoint=True)
            samples = []
            for time in times:
                frame = int(time)
                samples.append(keys[end] if frame >= end else keys[frame] + (keys[frame + 1] - keys[frame]) * (float(time) - frame))
            b, a = butter(order, cutoff / (0.5 * sample_frequency), btype="low", analog=False)
            padlen = 3 * max(len(a), len(b))
            if len(samples) > padlen:
                filtered = filtfilt(b, a, samples)
            else:
                filtered = filtfilt(b, a, samples, method="gust")
                warnings.append("{}: short segment uses Gustafsson edge handling".format(curve))
            values = {float(time): float(value) for time, value in zip(times, filtered)}
        if not all(math.isfinite(float(value)) for value in values.values()):
            raise ValueError("Filter produced nonfinite values: " + curve)
        processed[curve] = values
    return processed, warnings
