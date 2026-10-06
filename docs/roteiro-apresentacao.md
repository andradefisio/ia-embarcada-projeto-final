# Apresentação de 10 minutos

## 0:00–1:00 — Objetivo

“Neste trabalho desenvolvi uma aplicação de IA embarcada para reconhecer seis atividades humanas: andar, subir escadas, descer escadas, sentar, ficar em pé e deitar. Na atividade anterior trabalhei com a leitura de um MPU6050 no ESP32-S3. Agora avancei para o treinamento e a execução de um classificador no microcontrolador.”

Mostrar no README o fluxo dataset → treino → quantização → firmware → avaliação.

## 1:00–2:15 — Dataset

“Usei o UCI HAR, coletado com 30 voluntários usando smartphone na cintura. Os sensores foram amostrados a 50 Hz. Cada janela dura 2,56 segundos e já vem representada por 561 características nos domínios do tempo e da frequência.”

“Nesta demonstração alimento o ESP32 com as características do conjunto de teste, armazenadas na flash. Não faço captura de um sensor ao vivo: essa seria outra etapa, com filtros e extração de características.”

Mostrar a descrição em `docs/UCI HAR Dataset.names` e as dimensões em `results/metrics.json`.

## 2:15–3:30 — Treinamento

“Mantive o treino e o teste originais, com pessoas diferentes. Dentro do treino também separei participantes para a validação, evitando que janelas sobrepostas da mesma pessoa aparecessem nos dois lados.”

“Escolhi regressão logística multiclasse, pois é compacta e permite compreender o cálculo no ESP32. Comparei três valores de regularização na validação; escolhi C igual a 1 e só depois avaliei o teste oficial.”

Mostrar rapidamente a separação por pessoa e a exportação em `scripts/train.py`. Não ler todo o código.

## 3:30–4:45 — Quantização

“O treinamento gera pesos em ponto flutuante. Converti entradas e pesos para inteiros de 8 bits. O bias e a soma usam 32 bits para evitar overflow. A escala da entrada é 1 dividido por 127, pois as características já estão normalizadas entre menos um e um.”

“O ESP32 faz multiplicações e somas inteiras e escolhe o maior escore entre seis classes. Não preciso de softmax para decidir a classe. Não interpreto esse escore como probabilidade.”

Mostrar `main/har_inference.h`: multiplicação, acumulador e maior valor. O núcleo cabe em uma tela.

## 4:45–6:45 — Wokwi

Iniciar a simulação. Enquanto os 30 exemplos passam:

“A placa está recebendo uma janela real do teste. O monitor mostra o rótulo conhecido e a previsão calculada no ESP32. O LED verde indica acerto; o vermelho, erro. O rótulo é consultado somente depois da inferência para avaliar o modelo.”

“Escolhi cinco exemplos de cada classe pela ordem original, sem selecionar pelos acertos. Neste pequeno grupo o modelo teve 30 acertos, mas a avaliação principal usa o teste completo.”

Depois do resumo, clicar em **TESTE COMPLETO**. Mostrar o progresso e o resultado das 2.947 janelas. Se a execução demorar, continuar a fala enquanto o simulador trabalha. Não retreinar nem recompilar durante a apresentação.

## 6:45–8:15 — Resultados

“No teste oficial o modelo float32 teve 96,13% de acurácia e a versão quantizada teve 96,37%. O pequeno aumento ocorreu neste teste; não significa que quantizar sempre melhora o modelo.”

“Os parâmetros passaram de 13.488 para 3.390 bytes, uma redução de aproximadamente 75%. Esse é o tamanho do modelo, não do firmware completo. Os dados de teste também ocupam flash.”

Mostrar `docs/resultados.md`: tabela e matriz de confusão. Explicar linhas = real, colunas = previsão. Apontar os erros entre sentado e em pé.

“Comparei também todos os escores do núcleo C com a referência Python. Isso verifica a consistência da implementação; não substitui a medição em hardware físico.”

## 8:15–9:15 — Limitações

“A inferência está embarcada, mas a extração das 561 características foi feita pela UCI. Para usar um MPU6050 real, precisaria reproduzir esse processamento ou treinar outro modelo para receber janelas dos sinais diretamente.”

“Posição do sensor e perfil dos participantes influenciam os resultados. O tempo exibido no simulador não é um benchmark de uma placa física. Não apresento este trabalho como um sistema clínico validado.”

## 9:15–10:00 — Encerramento

“Neste projeto percorri treinamento, avaliação, quantização e execução de um classificador no ESP32-S3. O modelo manteve a acurácia com uma redução importante da memória dos parâmetros. Como próxima etapa, faria a aquisição real dos sinais e mediria o desempenho numa placa física.”

## Antes da aula

- Abrir a pasta correta no VS Code e deixar o firmware compilado.
- Fazer um ensaio no Wokwi para confirmar a extensão, o monitor e os botões.
- Deixar abertos README, núcleo C e relatório de resultados.
- Guardar uma captura do monitor serial após o teste completo como apoio caso a conexão falhe.
- Não inventar tempos de hardware nem evidências de simulação.

## Perguntas prováveis

**Por que não usou uma rede profunda?** “Escolhi um modelo linear compacto e explicável. Ele foi suficiente para cerca de 96% no teste oficial.”

**É TensorFlow Lite?** “Não. Quantizei explicitamente e exportei arrays C. A inferência não depende de um runtime de redes neurais.”

**O ESP32 aprende?** “Não. O treino ocorre no computador; o ESP32 executa a inferência.”

**Por que não mostra um MPU6050?** “O modelo recebe características de uma janela inteira. Um valor instantâneo do sensor não equivale às entradas esperadas.”

**O rótulo influencia a previsão?** “Não. A função recebe somente as características; consulto o rótulo depois para contar os acertos.”

**Reconhece qualquer atividade?** “Não. Sempre escolhe uma das seis classes conhecidas. Não implementei rejeição de atividades desconhecidas.”
