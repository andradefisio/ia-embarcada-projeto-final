# Organização e versionamento

## Conteúdo público do projeto

```text
.
├── .gitattributes
├── .gitignore
├── .vscode/tasks.json
├── CMakeLists.txt
├── README.md
├── diagram.json
├── partitions.csv
├── requirements.txt
├── sdkconfig.defaults
├── wokwi.toml
├── apresentacao/       Apresentação final em PDF
├── dataset/README.md   Instruções para baixar os dados
├── docs/              Descrição original, relatório, roteiro e validação
├── main/              Firmware e núcleo de inferência
│   └── generated/     README e pesos exportados em model_data.h
├── models/            Dois modelos treinados pequenos, em NPZ
├── results/           Métricas, verificação C e previsões por janela
└── scripts/           Treino, exportação, verificação, build, relatório e pacote
```

Mantenho os modelos treinados e o header de pesos porque são pequenos e permitem usar o resultado do trabalho sem refazer o treinamento. Publico a apresentação em PDF e mantenho o PowerPoint editável somente na minha máquina. Os resultados resumidos documentam a avaliação.

O arquivo de previsões contém apenas índices, identificadores de participantes do dataset e rótulos. Não replica as características do dataset.

## Conteúdo local, ignorado pelo Git

| Caminho | Motivo |
|---|---|
| `.local/` | Ferramentas instaladas, logs, vídeo da aula, fontes e rascunhos da criação do PowerPoint |
| `*.pptx` | Apresentações editáveis mantidas somente na máquina local |
| `dataset/*.zip` | Download externo, reproduzível pela fonte oficial |
| `main/generated/test_data.h` | Quase 7 MB de dados derivados do teste, regeneráveis sem treinamento |
| `build/` | Objetos, ELF, binários, CMake e imagem completa gerados pelo ESP-IDF |
| `sdkconfig` | Configuração gerada nesta máquina; a base compartilhada é sdkconfig.defaults |
| `dist/` | ZIP de entrega com firmware compilado |
| `.venv/` e caches | Ambiente instalado e arquivos temporários |
| `.presentation-build/` | Compatibilidade com temporários antigos, inclusive arquivos ainda em uso |
| `.vscode/` exceto tasks e extensions | Preferências e configurações específicas da máquina |

Os arquivos locais foram preservados. Não preciso colocar ferramentas, vídeos ou logs completos no histórico para reproduzir o projeto. Logs podem expor caminhos pessoais e produzem alterações sem relação com o código.

O ZIP antigo que está na pasta superior não foi alterado. Novos pacotes são gerados em `dist/`; o pacote antigo representa a organização anterior.

## Preparar um clone novo

1. Criar o ambiente Python e instalar `requirements.txt`.
2. Baixar o dataset conforme `dataset/README.md`.
3. Executar `python scripts/export_test_data.py` para gerar as entradas do firmware.
4. Abrir um terminal ESP-IDF v5.5.5 e executar `idf.py build` e `idf.py merge-bin`.
5. Iniciar o Wokwi com `wokwi.toml` e `diagram.json`.

O modelo já acompanha o projeto. `python scripts/train.py` refaz o treinamento completo apenas quando essa for a intenção. `python scripts/report.py` atualiza o relatório a partir das métricas.

## Perfil ESP-IDF da máquina

O script de build não contém um caminho de instalação obrigatório. Posso usar um terminal ESP-IDF, informar `-IdfProfile`, definir a variável de ambiente `ESP_IDF_PROFILE`, ou criar `.local/esp-idf-profile.ps1` com a chamada ao perfil da minha instalação.

A tarefa do VS Code chama `scripts/build.ps1`. Na máquina usada para preparar este trabalho, o perfil particular foi preservado em `.local/esp-idf-profile.ps1` e fica ignorado pelo Git.

## Revisão antes de incluir arquivos no histórico

Confiro `git status --short` e reviso as mudanças em código, documentação, resultados e modelos. Um `.gitignore` não remove arquivos que já estão no histórico; nesta preparação, somente `.gitignore` e `README.md` estavam versionados.

Não incluo credenciais, o dataset, ferramentas locais, rascunhos, logs ou binários de build. A documentação da UCI e as referências permanecem junto do trabalho. Não acrescentei uma licença de autoria própria para o código sem uma escolha do autor.

Esta organização foi preparada para revisão. Não houve stage, commit ou push durante a limpeza.
