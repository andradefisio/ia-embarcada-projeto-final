"""Treino no computador; exporto apenas a inferência inteira para o ESP32-S3."""
import json
import csv
import platform
import warnings
import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from sklearn.exceptions import ConvergenceWarning
from dataset_io import ROOT, load_data, quantize, rows
from export_test_data import export_test_data

LABELS = ['Andando', 'Subindo escadas', 'Descendo escadas', 'Sentado', 'Em pe', 'Deitado']


def evaluate(y, pred):
    return {'accuracy': float(accuracy_score(y, pred)),
            'macro_f1': float(f1_score(y, pred, average='macro')),
            'confusion_matrix': confusion_matrix(y, pred).tolist(),
            'per_class': classification_report(y, pred, target_names=LABELS, output_dict=True)}


def main():
    warnings.simplefilter('error', ConvergenceWarning)
    x, y, subjects, xt, yt, subjects_test, digest = load_data()
    assert x.shape == (7352, 561) and xt.shape == (2947, 561)
    assert not set(subjects) & set(subjects_test)
    assert np.isfinite(x).all() and np.isfinite(xt).all()
    # Separo pessoas, e não janelas: janelas vizinhas não devem vazar para a validação.
    fit, val = next(GroupShuffleSplit(n_splits=1, test_size=.25, random_state=42).split(x, y, subjects))
    trials = []
    for c in [.1, 1., 10.]:
        model = LogisticRegression(C=c, max_iter=3000, solver='lbfgs', tol=1e-5)
        model.fit(x[fit], y[fit])
        score = accuracy_score(y[val], model.predict(x[val]))
        trials.append({'C': c, 'validation_accuracy': float(score)})
        print(f'C={c}: validacao por pessoa={score:.4%}', flush=True)
    best = max(trials, key=lambda t: t['validation_accuracy'])['C']
    # Só depois da escolha por validação uso todo o treino oficial.
    model = LogisticRegression(C=best, max_iter=3000, solver='lbfgs', tol=1e-5).fit(x, y)
    w = model.coef_.astype(np.float32)
    b = model.intercept_.astype(np.float32)
    sw = float(np.max(np.abs(w)) / 127)
    qw = np.clip(np.rint(w / sw), -127, 127).astype(np.int8)
    # Bias usa a escala do acumulador: sx * sw. Assim o argmax é totalmente inteiro.
    qb = np.rint(b / (sw / 127)).astype(np.int32)
    qxt = quantize(xt)
    scores = qxt.astype(np.int32) @ qw.astype(np.int32).T + qb
    fp = np.argmax(xt @ w.T + b, axis=1)
    qp = np.argmax(scores, axis=1)
    bounds = 561 * 127 * 127 + np.abs(qb.astype(np.int64))
    assert bounds.max() < np.iinfo(np.int32).max
    # Amostras escolhidas pela ordem original e pelo rótulo, nunca pelo acerto do modelo.
    demo = export_test_data(xt, yt)
    out = ROOT / 'results'
    out.mkdir(exist_ok=True)
    models = ROOT / 'models'
    models.mkdir(exist_ok=True)
    gen = ROOT / 'main/generated'
    gen.mkdir(parents=True, exist_ok=True)
    np.savez(models / 'model_float32.npz', weights=w, bias=b)
    np.savez(models / 'model_int8.npz', weights=qw, bias=qb, input_scale=1/127, weight_scale=sw)
    (gen / 'model_data.h').write_text(
        '// Gerado por scripts/train.py. Pesos int8 e bias int32; não editar.\n'
        '#pragma once\n#include <stdint.h>\n#define HAR_FEATURES 561\n#define HAR_CLASSES 6\n'
        f'static const int8_t HAR_WEIGHTS[6][561] = {{\n{rows(qw)}\n}};\n'
        f'static const int32_t HAR_BIAS[6] = {{{",".join(map(str, qb))}}};\n'
        'static const char *const HAR_LABELS[6] = {' + ','.join(json.dumps(s) for s in LABELS) + '};\n', encoding='utf-8')
    metrics = {
        'dataset_sha256': digest, 'python': platform.python_version(),
        'numpy': np.__version__, 'sklearn': sklearn.__version__,
        'train_count': len(y), 'test_count': len(yt), 'features': 561,
        'train_subjects': sorted(map(int, np.unique(subjects))),
        'test_subjects': sorted(map(int, np.unique(subjects_test))),
        'validation_subjects': sorted(map(int, np.unique(subjects[val]))),
        'validation_trials': trials, 'selected_C': best,
        'float32': evaluate(yt, fp), 'int8': evaluate(yt, qp),
        'prediction_agreement': float(np.mean(fp == qp)),
        'float32_parameter_bytes': w.nbytes + b.nbytes,
        'int8_parameter_bytes': qw.nbytes + qb.nbytes,
        'input_scale': 1/127, 'weight_scale': sw,
        'max_accumulator_bound': int(bounds.max()),
        'demo_indices_zero_based': demo.tolist(),
        'demo_accuracy': float(np.mean(qp[demo] == yt[demo])),
        'labels': LABELS,
    }
    (out / 'metrics.json').write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding='utf-8')
    with (out / 'test_predictions.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['index_zero_based', 'subject', 'true_class_1_to_6', 'float_class_1_to_6', 'int8_class_1_to_6'])
        writer.writerows(zip(range(len(yt)), subjects_test, yt+1, fp+1, qp+1))
    print(json.dumps({k: metrics[k] for k in ['selected_C', 'float32_parameter_bytes', 'int8_parameter_bytes', 'prediction_agreement', 'demo_accuracy']}, indent=2))
    print(f'Teste float32: {metrics["float32"]["accuracy"]:.4%}; int8: {metrics["int8"]["accuracy"]:.4%}')


if __name__ == '__main__':
    main()
