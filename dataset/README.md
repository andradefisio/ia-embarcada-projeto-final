# Dataset local UCI HAR

Baixo o dataset na [página oficial da UCI](https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones) e salvo o download nesta pasta com o nome:

```text
human+activity+recognition+using+smartphones.zip
```

Não preciso descompactar: os scripts leem o ZIP externo e o ZIP interno `UCI HAR Dataset.zip`.

O download fica ignorado pelo Git. Somente este README é versionado nesta pasta. A descrição original está em `docs/UCI HAR Dataset.names`.

Para preparar os dados usados pelo firmware, sem treinar novamente:

```powershell
python scripts/export_test_data.py
```

O script gera `main/generated/test_data.h` com `test/X_test.txt` e `test/y_test.txt`. O header também fica fora do histórico Git, pois reproduz dados do download.

SHA-256 do download utilizado nesta avaliação: `c00b803081a5c797cd5e4b83700a9810b38d53d9d84e01917e090e1fdbc81031`.

Referência: Reyes-Ortiz et al. (2013), *Human Activity Recognition Using Smartphones*, UCI Machine Learning Repository, DOI [10.24432/C54S4K](https://doi.org/10.24432/C54S4K).
