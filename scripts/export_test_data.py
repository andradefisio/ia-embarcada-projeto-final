"""Gero a entrada do firmware a partir do teste UCI, sem retreinar o modelo."""
import numpy as np
from dataset_io import ROOT, read_dataset_files, quantize, rows


def export_test_data(x=None, y=None):
    if x is None or y is None:
        data = read_dataset_files({'test/X_test.txt': float, 'test/y_test.txt': int})
        x, y = data['test/X_test.txt'], data['test/y_test.txt'] - 1
    assert x.shape == (2947, 561) and y.shape == (2947,)
    assert np.isfinite(x).all() and set(np.unique(y)) == set(range(6))
    qx = quantize(x)
    # Primeiras cinco janelas de cada classe, na ordem original, sem filtrar acertos.
    demo = np.array([np.flatnonzero(y == k)[j] for j in range(5) for k in range(6)])
    gen = ROOT / 'main/generated'
    gen.mkdir(parents=True, exist_ok=True)
    (gen / 'test_data.h').write_text(
        '// Teste oficial quantizado: é entrada, não uma tabela de previsões.\n#pragma once\n'
        f'#define HAR_TEST_COUNT {len(y)}\n#define HAR_DEMO_COUNT {len(demo)}\n'
        f'static const int8_t HAR_TEST_X[{len(y)}][561] = {{\n{rows(qx)}\n}};\n'
        f'static const uint8_t HAR_TEST_Y[{len(y)}] = {{{",".join(map(str, y))}}};\n'
        f'static const uint16_t HAR_DEMO_INDEX[{len(demo)}] = {{{",".join(map(str, demo))}}};\n', encoding='utf-8')
    return demo


if __name__ == '__main__':
    export_test_data()
    print('Exportado: main/generated/test_data.h (2947 janelas, 561 características).')
