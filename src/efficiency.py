"""
efficiency.py
=============
Computational efficiency benchmarking:
- Training runtime (seconds)
- Inference latency (ms per 1,000 samples)
- Disk model size
- Parameter counts
"""

import os
import time
import numpy as np
import pandas as pd
import joblib

def measure_efficiency_metrics(
    model_name: str,
    fit_fn,
    predict_fn,
    sample_texts: list[str],
    model_obj = None,
    save_path: str = None
) -> dict:
    """
    Measures training duration, inference latency, and disk footprint.
    """
    # 1. Training time
    start_train = time.perf_counter()
    trained_model = fit_fn()
    train_time = time.perf_counter() - start_train
    
    # 2. Inference latency over sample_texts
    # Warmup
    _ = predict_fn(sample_texts[:10])
    
    start_infer = time.perf_counter()
    _ = predict_fn(sample_texts)
    infer_time = time.perf_counter() - start_infer
    
    latency_per_1k = (infer_time / max(len(sample_texts), 1)) * 1000.0 * 1000.0  # ms
    
    # 3. Model size on disk
    model_size_mb = 0.0
    if save_path and os.path.exists(save_path):
        if os.path.isfile(save_path):
            model_size_mb = os.path.getsize(save_path) / (1024 * 1024)
        elif os.path.isdir(save_path):
            total_b = sum(os.path.getsize(os.path.join(dirpath, f)) for dirpath, _, filenames in os.walk(save_path) for f in filenames)
            model_size_mb = total_b / (1024 * 1024)

    # 4. Parameter count
    param_count = 0
    if hasattr(trained_model, "coef_"):
        param_count = int(trained_model.coef_.size + getattr(trained_model, "intercept_", np.array([])).size)
    elif hasattr(trained_model, "num_parameters"):
        param_count = int(trained_model.num_parameters())
    elif hasattr(model_obj, "num_parameters"):
        param_count = int(model_obj.num_parameters())

    return {
        "model": model_name,
        "train_time_sec": round(float(train_time), 3),
        "inference_latency_ms_per_1k": round(float(latency_per_1k), 2),
        "model_size_mb": round(float(model_size_mb), 2),
        "parameter_count": param_count
    }
