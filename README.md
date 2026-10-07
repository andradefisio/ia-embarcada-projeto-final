# Reconhecimento de atividades humanas no ESP32-S3

Neste projeto treinei um classificador para reconhecer seis atividades humanas e quantizei seus parâmetros para executar a inferência no ESP32-S3. Preparei o circuito para o Wokwi com ESP-IDF, seguindo a plataforma da minha [atividade anterior](https://github.com/andradefisio/ia-embarcada-atividade-aula-02).

**Fluxo:** dataset → treinamento no computador → quantização → exportação C → inferência no ESP32 → avaliação.

## Demonstração

O ESP32 recebe vetores reais do teste UCI HAR armazenados na flash. Cada vetor contém 561 características já extraídas pela UCI. A previsão é calculada no microcontrolador; o rótulo é consultado somente depois para avaliar o resultado. Não há uma tabela de previsões prontas no firmware.

Não faço aquisição de MPU6050 ao vivo nesta etapa. Cada janela representa 128 leituras a 50 Hz, ou 2,56 segundos, com sobreposição de 50%. Para trabalhar com um sensor real, ainda seria necessário implementar os filtros e a extração das mesmas características. Um valor instantâneo de um acelerômetro virtual não equivale a essas 561 entradas.

## Resultados

| Modelo | Acurácia no teste oficial | Memória dos parâmetros |
|---|---:|---:|
| Float32 | 96,13% | 13.488 bytes |
| Pesos int8 + bias int32 | 96,37% | 3.390 bytes |

Reduzi os parâmetros em 74,87%, aproximadamente quatro vezes menos memória. A quantização mudou 15 previsões entre 2.947 janelas. O pequeno ganho de acurácia é específico deste teste; quantizar não garante melhorar o modelo.

Esses tamanhos medem pesos e bias, não o firmware. O teste completo ocupa aproximadamente 1,58 MiB de flash. Os arrays são `static const` e não são copiados integralmente para a RAM.

## Treinamento

Escolhi regressão logística multiclasse, uma camada linear com seis saídas: 3.366 multiplicações por janela. Não é uma rede profunda nem um modelo TensorFlow Lite; exportei a inferência diretamente em C.

Mantive a divisão oficial: 7.352 janelas de treino de 21 pessoas e 2.947 de teste de outras 9 pessoas. Também separei participantes na validação interna, evitando vazamento entre janelas da mesma pessoa. Comparei `C = 0.1, 1, 10`, escolhi `C = 1` com 95,58% na validação e só então treinei no treino completo e avaliei o teste.

Usei a normalização fornecida pela UCI, sem ajustar outro scaler no teste. `docs/UCI HAR Dataset.names` descreve o dataset; `features.txt` e `features_info.txt`, dentro do ZIP, detalham as características.

## Quantização

- Entrada: `qx = clip(round(x × 127), -127, 127)`; int8, escala `sx = 1/127`, zero point zero.
- Pesos: `sw = max(abs(W))/127`; `qW = round(W/sw)`; int8.
- Bias: `qb = round(b/(sx × sw))`; int32.
- Escore: `score[c] = qb[c] + Σ qx[j] × qW[c][j]`; acumulador int32.
- Classe: índice do maior escore; empate favorece a primeira classe.

A escala é comum e positiva, permitindo comparar os escores inteiros. Dispensei a softmax, que não altera a classe vencedora. Não apresento escores como probabilidades. Verifiquei um limite conservador para evitar overflow do acumulador.

## Reproduzir o treino

Na raiz do projeto, com Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/train.py
python scripts/report.py
```

O script lê `dataset/human+activity+recognition+using+smartphones.zip`, incluindo o ZIP interno. Consulte [dataset/README.md](dataset/README.md) para obter o download. O dataset e o vídeo da aula não são versionados.

O modelo treinado e o header de pesos acompanham o projeto. Para compilar a partir de um clone novo, preciso baixar o dataset e gerar somente as entradas do teste, sem retreinar:

```powershell
python -m pip install -r requirements.txt
python scripts/export_test_data.py
```

O arquivo `main/generated/test_data.h` é gerado localmente e ignorado pelo Git. Na minha máquina ele permanece disponível para o Wokwi.

As métricas, versões das bibliotecas e SHA-256 do dataset estão em `results/metrics.json`; previsões por janela em `results/test_predictions.csv`; modelos em `models/model_*.npz`.

Verificação do mesmo núcleo C no Windows, com compilador instalado só na pasta local:

```powershell
python -m pip install --target .local/tools ziglang==0.13.0
python scripts/verify.py
```

Essa verificação compara todos os escores C com a referência Python. É um teste no computador, separado da execução no simulador.

## Compilar e executar

1. Abrir **esta pasta** `ia-embarcada-projeto-final` no VS Code.
2. Preparar o dataset com `python scripts/export_test_data.py`, caso o header local ainda não exista.
3. Com ESP-IDF v5.5.5 configurado no terminal, executar `powershell -ExecutionPolicy Bypass -File scripts/build.ps1`. A tarefa `Ctrl+Shift+B` pode usar um perfil local conforme [a organização do repositório](docs/organizacao-repositorio.md).
4. Também posso executar `idf.py build` e `idf.py merge-bin` no terminal ESP-IDF. O target ESP32-S3 está definido em `sdkconfig.defaults`.
5. Executar **Wokwi: Start Simulator**. A extensão precisa estar configurada com a licença exigida pelo serviço.
6. A demonstração inicia automaticamente: 30 janelas, cinco por classe, intercaladas; 1,8 segundo por exemplo. LED verde = acerto; vermelho = erro.
7. Ao terminar, clicar **TESTE COMPLETO** para avaliar as 2.947 janelas e mostrar acurácia e matriz de confusão. **DEMO** repete a demonstração curta.

Os botões são atendidos após a execução corrente terminar. Escolhi as primeiras cinco amostras de cada classe pela ordem original, sem selecionar pelos acertos. A demonstração curta teve 30/30 acertos, mas não substitui o teste completo.

| Componente | GPIO |
|---|---:|
| Botão DEMO, pull-up interno, contato ao GND | 4 |
| Botão TESTE COMPLETO, pull-up interno, contato ao GND | 5 |
| LED verde com resistor de 330 Ω | 6 |
| LED vermelho com resistor de 330 Ω | 7 |

UART0: 115200 baud. `wokwi.toml` carrega bootloader, partições e aplicação via `build/flasher_args.json`, conforme a [documentação Wokwi](https://docs.wokwi.com/vscode/project-config). A partição de aplicação tem 3 MiB para acomodar o teste completo.

No navegador, use um projeto ESP32-S3 com este `diagram.json` e **Upload Firmware and Start Simulation**, carregando a imagem completa `build/merged-binary.bin`. Recomendo a extensão do VS Code para esta entrega.

O tempo impresso no Wokwi é do ambiente simulado, não um benchmark de uma placa física.

## Limitações

O dataset usa adultos com smartphone na cintura; outra posição de sensor ou população pode alterar o desempenho. O modelo sempre escolhe uma das seis classes, sem rejeição de atividades desconhecidas. Não considero esta aplicação um sistema clínico validado. Como próximos passos, implementaria aquisição e extração das características, ou treinaria um modelo para janelas inerciais, e mediria RAM, latência e energia na placa física.

## Referências

Reyes-Ortiz, J.; Anguita, D.; Ghio, A.; Oneto, L.; Parra, X. (2013). [Human Activity Recognition Using Smartphones](https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones). UCI Machine Learning Repository. DOI: [10.24432/C54S4K](https://doi.org/10.24432/C54S4K).

Anguita et al. *A Public Domain Dataset for Human Activity Recognition Using Smartphones*. ESANN 2013.

[Regressão logística no scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html). [ESP32-S3 no Wokwi](https://docs.wokwi.com/guides/esp32).
