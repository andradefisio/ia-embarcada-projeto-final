# Resultados publicados

- `metrics.json`: configuração, participantes, versões, SHA-256 do dataset, acurácia, F1 e matrizes de confusão.
- `c_verification.json`: resultado da comparação dos 17.682 escores C com a referência NumPy.
- `test_predictions.csv`: índice da janela, identificador de participante e classes real, float32 e quantizada. Não contém os 561 valores de entrada.

Os arquivos são pequenos e permitem conferir os resultados apresentados. O treinamento e a verificação atualizam esses arquivos, por isso reviso seus diffs antes de incluir novas execuções no histórico.

Logs completos da compilação, referências intermediárias e binários ficam em `.local/`, `build/` ou `dist/`, fora do versionamento. O resumo da compilação está em `docs/validacao.md`.
