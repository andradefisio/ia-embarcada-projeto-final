"""Compilo o núcleo C e comparo os 17.682 escores com o NumPy."""
import ctypes
import json
from pathlib import Path
import subprocess
import numpy as np
from dataset_io import ROOT, read_dataset_files, quantize

ZIG = ROOT / '.local/tools/ziglang/zig.exe'
OUT = ROOT / '.local/native'
OUT.mkdir(parents=True, exist_ok=True)
if not ZIG.exists():
    raise SystemExit('Instale o compilador local: python -m pip install --target .local/tools ziglang==0.13.0')
subprocess.run([str(ZIG), 'cc', '-shared', '-O2', str(ROOT / 'scripts/native_inference.c'),
                '-o', str(OUT / 'inference.dll')], check=True)
lib = ctypes.CDLL(str(OUT / 'inference.dll'))
lib.predict.argtypes = [ctypes.POINTER(ctypes.c_int8), ctypes.POINTER(ctypes.c_int32)]
lib.predict.restype = ctypes.c_int
data = read_dataset_files({'test/X_test.txt': float, 'test/y_test.txt': int})
xt, yt = data['test/X_test.txt'], data['test/y_test.txt'] - 1
qxt = quantize(xt)
with np.load(ROOT / 'models/model_int8.npz', allow_pickle=False) as model:
    reference = qxt.astype(np.int32) @ model['weights'].astype(np.int32).T + model['bias']
actual = np.empty(reference.shape, dtype=np.int32)
predictions = []
for i, x in enumerate(qxt):
    predictions.append(lib.predict(x.ctypes.data_as(ctypes.POINTER(ctypes.c_int8)),
                                  actual[i].ctypes.data_as(ctypes.POINTER(ctypes.c_int32))))
assert np.array_equal(reference, actual), 'Diferenca entre o C embarcado e o Python!'
assert np.array_equal(np.argmax(reference, axis=1), predictions)
result = {'samples': len(yt), 'scores_verified': int(reference.size), 'all_scores_equal': True,
          'correct': int(np.sum(np.array(predictions) == yt)),
          'accuracy': float(np.mean(np.array(predictions) == yt))}
(ROOT / 'results').mkdir(exist_ok=True)
(ROOT / 'results/c_verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
