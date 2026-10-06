# Modelos treinados

Mantenho estes dois arquivos pequenos como artefatos intencionais da avaliação:

- `model_float32.npz`: pesos e bias do classificador antes da quantização.
- `model_int8.npz`: pesos int8, bias int32 e escalas de quantização.

São arrays NumPy, carregados com `allow_pickle=False`, e não ambientes Python ou executáveis. O script `scripts/train.py` pode reproduzi-los com o dataset local e as versões de `requirements.txt`.

O modelo quantizado também está exportado em `main/generated/model_data.h`. Esse header é versionado para permitir compilar sem refazer o treinamento. As entradas do teste são exportadas separadamente e não fazem parte destes modelos.

As métricas e a configuração escolhida estão em `results/metrics.json`.
