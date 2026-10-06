# Evidências de validação

## Treinamento e quantização

Executei `python scripts/train.py` com o dataset local. A escolha de regularização usou somente a validação interna por participante. A avaliação final usou as 2.947 janelas do teste oficial, cujos participantes não aparecem no treino.

O modelo float32 atingiu 96,1317% de acurácia; o quantizado, 96,3692%. As métricas completas e a matriz de confusão estão em `results/metrics.json`. Cada janela avaliada está registrada em `results/test_predictions.csv`.

## Núcleo de inferência em C

Executei `python scripts/verify.py`, compilando `scripts/native_inference.c`, que inclui o mesmo `main/har_inference.h` utilizado pelo ESP32.

Conferi **17.682 escores inteiros**, seis para cada uma das 2.947 janelas. Todos foram exatamente iguais à referência NumPy. A classificação em C teve **2.840 acertos**, correspondendo a 96,3692%. A evidência está em `results/c_verification.json`.

## Compilação e simulação

O log da compilação está em `.local/logs/build_output.txt`. O firmware e a imagem completa ficam em `build/` e acompanham o pacote de entrega.

A compilação com ESP-IDF v5.5.5 terminou com sucesso. A aplicação tem 1.847.520 bytes e cabe na partição de 3 MiB. A imagem completa, incluindo bootloader e tabela de partições, tem 1.913.056 bytes.

Não registrei execução no Wokwi nem teste em uma placa física nesta preparação. Para obter essa evidência, inicio **Wokwi: Start Simulator**, aguardo a demonstração curta terminar e clico **TESTE COMPLETO**. O resultado esperado é **2840/2947** e **96,3692%**. Salvo uma captura do monitor serial com o resultado e a matriz de confusão.

Não uso o tempo de inferência do simulador como medição do hardware físico.
