# Resultados do projeto

Treinei o modelo no computador, quantizei os parâmetros e exportei o núcleo de inferência para C. Mantive o teste oficial separado do treinamento e da escolha da regularização.

## Avaliação das 2.947 janelas de teste

| Métrica | Float32 | Quantizado |
|---|---:|---:|
| Acurácia | 96,1317% | 96,3692% |
| F1 macro | 96,1258% | 96,3588% |
| Bytes dos parâmetros | 13488 | 3390 |

A redução de memória dos parâmetros foi de 74,8665%. Esses valores não incluem código, rótulos ou dados de teste. A concordância das previsões float32/int8 foi de 99,4910%.

O resultado quantizado foi ligeiramente melhor neste teste. Não interpreto isso como uma vantagem garantida da quantização; arredondamentos mudaram algumas fronteiras de decisão.

## Matriz de confusão do modelo quantizado

Linhas representam classes reais; colunas representam previsões. Classes: 1 andando; 2 subindo escadas; 3 descendo escadas; 4 sentado; 5 em pé; 6 deitado.

| Real / Previsto | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 493 | 0 | 3 | 0 | 0 | 0 |
| 2 | 23 | 447 | 1 | 0 | 0 | 0 |
| 3 | 3 | 12 | 405 | 0 | 0 | 0 |
| 4 | 0 | 3 | 0 | 441 | 47 | 0 |
| 5 | 1 | 0 | 0 | 14 | 517 | 0 |
| 6 | 0 | 0 | 0 | 0 | 0 | 537 |

## Resultado por atividade — quantizado

| Atividade | Precisão | Recall | F1 | Janelas |
|---|---:|---:|---:|---:|
| Andando | 94,8077% | 99,3952% | 97,0472% | 496 |
| Subindo escadas | 96,7532% | 94,9045% | 95,8199% | 471 |
| Descendo escadas | 99,0220% | 96,4286% | 97,7081% | 420 |
| Sentado | 96,9231% | 89,8167% | 93,2347% | 491 |
| Em pe | 91,6667% | 97,1805% | 94,3431% | 532 |
| Deitado | 100,0000% | 100,0000% | 100,0000% | 537 |

## Escolha do modelo

Separei os participantes [1, 3, 8, 15, 25, 27] para validação interna, sem usar o teste oficial. Depois da escolha, refiz o treino usando todas as 7.352 janelas de treinamento.

| C | Acurácia na validação por pessoa |
|---:|---:|
| 0.1 | 95,1969% |
| 1.0 | 95,5812% |
| 10.0 | 95,4851% |

Escolhi C = 1.0. O modelo usa 561 entradas e 6 saídas. A demonstração curta usa 30 exemplos e teve 100,0000%; ela serve para apresentar o fluxo, e não para estimar o desempenho global.

## Verificações e limites

O script de treinamento verifica a dimensão das matrizes, valores finitos e a separação entre pessoas do treino e do teste. O limite conservador do acumulador inteiro foi 9049862, abaixo de 2.147.483.647.

O arquivo `results/c_verification.json` registra a comparação do núcleo C com todos os escores Python. O log ESP-IDF está em `.local/logs/build_output.txt`. A compilação e a verificação nativa não são evidências de execução no Wokwi nem em placa física. O ensaio no Wokwi deve ser registrado pelo monitor serial; tempos do simulador não representam desempenho do hardware.

O firmware recebe as características prontas da UCI, não sinais brutos de um MPU6050. As próximas etapas seriam implementar a extração ou treinar outro modelo com os sinais, e medir latência, memória e energia na placa física.

Dataset: [UCI HAR](https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones), Reyes-Ortiz et al., 2013, DOI 10.24432/C54S4K. Versões utilizadas: Python 3.12.9, NumPy 2.5.3, scikit-learn 1.8.0.
