"""Leitura do download local e quantização compartilhadas pelos scripts."""
from pathlib import Path
import hashlib
import io
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / 'dataset/human+activity+recognition+using+smartphones.zip'


def read_dataset_files(files):
    if not DATASET.exists():
        raise FileNotFoundError(f'Baixe o UCI HAR conforme dataset/README.md: {DATASET}')
    # O download da UCI contém outro ZIP. Não preciso descompactar o dataset.
    with zipfile.ZipFile(DATASET) as outer:
        with zipfile.ZipFile(io.BytesIO(outer.read('UCI HAR Dataset.zip'))) as inner:
            return {name: np.loadtxt(io.BytesIO(inner.read('UCI HAR Dataset/' + name)), dtype=dtype)
                    for name, dtype in files.items()}


def load_data():
    data = read_dataset_files({
        'train/X_train.txt': float, 'train/y_train.txt': int, 'train/subject_train.txt': int,
        'test/X_test.txt': float, 'test/y_test.txt': int, 'test/subject_test.txt': int,
    })
    return (data['train/X_train.txt'], data['train/y_train.txt'] - 1,
            data['train/subject_train.txt'], data['test/X_test.txt'],
            data['test/y_test.txt'] - 1, data['test/subject_test.txt'],
            hashlib.sha256(DATASET.read_bytes()).hexdigest())


def quantize(x):
    # Intervalo da UCI: [-1, 1]. Zero point = 0; escala = 1/127.
    return np.clip(np.rint(x * 127), -127, 127).astype(np.int8)


def rows(a):
    return ',\n'.join('{' + ','.join(map(str, row)) + '}' for row in a)
