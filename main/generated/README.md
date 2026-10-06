# Arquivos exportados para C

`model_data.h` contém os pesos do modelo treinado. Mantenho esse arquivo pequeno no Git para compilar sem refazer o treinamento.

`test_data.h` contém as 2.947 janelas do teste oficial quantizadas. Como é uma cópia derivada do dataset com quase 7 MB de texto, ele é gerado localmente e ignorado pelo Git:

```powershell
python scripts/export_test_data.py
```

O treinamento também gera os dois headers. Não edito os valores manualmente.
