"""Gero tabelas do relatório a partir das métricas efetivamente medidas."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
m = json.loads((ROOT / 'results/metrics.json').read_text(encoding='utf-8'))
def pct(n):
    return f'{100*n:.4f}%'.replace('.', ',')
text = '''# Resultados do projeto

Treinei o modelo no computador, quantizei os parâmetros e exportei o núcleo de inferência para C. Mantive o teste oficial separado do treinamento e da escolha da regularização.

## Avaliação das 2.947 janelas de teste

| Métrica | Float32 | Quantizado |
|---|---:|---:|
'''
for name, key in [('Acurácia', 'accuracy'), ('F1 macro', 'macro_f1')]:
    text += f'| {name} | {pct(m["float32"][key])} | {pct(m["int8"][key])} |\n'
text += f'| Bytes dos parâmetros | {m["float32_parameter_bytes"]} | {m["int8_parameter_bytes"]} |\n'
text += f'''
A redução de memória dos parâmetros foi de {pct(1-m['int8_parameter_bytes']/m['float32_parameter_bytes'])}. Esses valores não incluem código, rótulos ou dados de teste. A concordância das previsões float32/int8 foi de {pct(m['prediction_agreement'])}.

O resultado quantizado foi ligeiramente melhor neste teste. Não interpreto isso como uma vantagem garantida da quantização; arredondamentos mudaram algumas fronteiras de decisão.

## Matriz de confusão do modelo quantizado

Linhas representam classes reais; colunas representam previsões. Classes: 1 andando; 2 subindo escadas; 3 descendo escadas; 4 sentado; 5 em pé; 6 deitado.

| Real / Previsto | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
'''
for i, row in enumerate(m['int8']['confusion_matrix']):
    text += f'| {i+1} | ' + ' | '.join(map(str, row)) + ' |\n'
text += '\n## Resultado por atividade — quantizado\n\n| Atividade | Precisão | Recall | F1 | Janelas |\n|---|---:|---:|---:|---:|\n'
for label in m['labels']:
    c = m['int8']['per_class'][label]
    text += f'| {label} | {pct(c["precision"])} | {pct(c["recall"])} | {pct(c["f1-score"])} | {int(c["support"])} |\n'
text += f'''
## Escolha do modelo

Separei os participantes {m['validation_subjects']} para validação interna, sem usar o teste oficial. Depois da escolha, refiz o treino usando todas as 7.352 janelas de treinamento.

| C | Acurácia na validação por pessoa |
|---:|---:|
'''
for trial in m['validation_trials']:
    text += f'| {trial["C"]} | {pct(trial["validation_accuracy"])} |\n'
text += f'''
Escolhi C = {m['selected_C']}. O modelo usa 561 entradas e 6 saídas. A demonstração curta usa 30 exemplos e teve {pct(m['demo_accuracy'])}; ela serve para apresentar o fluxo, e não para estimar o desempenho global.

## Verificações e limites

O script de treinamento verifica a dimensão das matrizes, valores finitos e a separação entre pessoas do treino e do teste. O limite conservador do acumulador inteiro foi {m['max_accumulator_bound']}, abaixo de 2.147.483.647.

O arquivo `results/c_verification.json` registra a comparação do núcleo C com todos os escores Python. O log ESP-IDF está em `.local/logs/build_output.txt`. A compilação e a verificação nativa não são evidências de execução no Wokwi nem em placa física. O ensaio no Wokwi deve ser registrado pelo monitor serial; tempos do simulador não representam desempenho do hardware.

O firmware recebe as características prontas da UCI, não sinais brutos de um MPU6050. As próximas etapas seriam implementar a extração ou treinar outro modelo com os sinais, e medir latência, memória e energia na placa física.

Dataset: [UCI HAR](https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones), Reyes-Ortiz et al., 2013, DOI 10.24432/C54S4K. Versões utilizadas: Python {m['python']}, NumPy {m['numpy']}, scikit-learn {m['sklearn']}.
'''
(ROOT / 'docs/resultados.md').write_text(text, encoding='utf-8')
print('Relatorio gerado: docs/resultados.md')
