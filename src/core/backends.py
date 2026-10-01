"""Minimal array operations for the same mathematical definitions on CPU/CUDA."""
from __future__ import annotations


class NumpyBackend:
    name = "numpy"

    def __init__(self):
        import numpy as np
        self.module = np

    def check(self, value, tail):
        np = self.module
        if not isinstance(value, np.ndarray) or value.shape[-len(tail):] != tuple(tail):
            raise ValueError(f"Expected ndarray with trailing shape {tail}")
        if value.dtype not in (np.dtype("float32"), np.dtype("float64")):
            raise ValueError("Explicit float32/float64 arrays are required")
        if not np.isfinite(value).all():
            raise ValueError("Non-finite input")

    def as_like(self, value, like):
        return self.module.asarray(value, dtype=like.dtype)

    def sum(self, value, axis):
        return self.module.sum(value, axis=axis)

    def stack(self, values, axis=-1):
        return self.module.stack(values, axis=axis)

    def cross(self, left, right):
        return self.module.cross(left, right, axis=-1)

    def einsum(self, expression, *values):
        return self.module.einsum(expression, *values)

    def sqrt(self, value):
        return self.module.sqrt(value)

    def any(self, value):
        return bool(self.module.any(value))


class TorchBackend:
    name = "torch"

    def __init__(self, device_type="cuda"):
        import torch
        if device_type not in {"cpu", "cuda"}:
            raise ValueError("The reference/mirror backend supports CPU or CUDA")
        self.module, self.device_type = torch, device_type

    def check(self, value, tail):
        torch = self.module
        if not isinstance(value, torch.Tensor) or tuple(value.shape[-len(tail):]) != tuple(tail):
            raise ValueError(f"Expected tensor with trailing shape {tail}")
        if value.dtype not in (torch.float32, torch.float64) or value.device.type != self.device_type:
            raise ValueError("Tensor dtype/device does not match the explicit backend")
        if not torch.isfinite(value).all().item():
            raise ValueError("Non-finite input")

    def as_like(self, value, like):
        return self.module.as_tensor(value, dtype=like.dtype, device=like.device)

    def sum(self, value, axis):
        return self.module.sum(value, dim=axis)

    def stack(self, values, axis=-1):
        return self.module.stack(values, dim=axis)

    def cross(self, left, right):
        return self.module.linalg.cross(left, right, dim=-1)

    def einsum(self, expression, *values):
        return self.module.einsum(expression, *values)

    def sqrt(self, value):
        return self.module.sqrt(value)

    def any(self, value):
        return bool(self.module.any(value).item())
