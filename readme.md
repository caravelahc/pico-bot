# Pico-Bot

Bot para automatizar a criação de stickers a partir de imagens ou mensagens.
Utilize o comando `/help` para ver os comandos disponíveis.

Código disponível no repositório:
[http://github.com/caravelahc/pico-bot]()

Feito por [@diogojs](https://t.me/diogojs) e [@caravelahc](https://t.me/caravelahc).

## A) Como Instalar

### A.1) Python

Tenha certeza que possui o Python com versão maior ou igual à 3.7.0. 

### A.2) Gerenciador de pacotes `poetry`

Primeiro de tudo, instale o `poetry`, que é um gerenciador de pacotes e dependências do Python.

### A.3) Dependências

Para instalar as dependências do projeto, vamos criar um ambiente local para que possamos instalar os pacotes sem afetar o sistema:

```
python3.7 -m venv .venv
source .venv/bin/activate
```

Estando dentro do VENV (virtual env), basta executar o seguinte comando e aguardar:

```
poetry install
```

## B) Como Configurar

Todas as variáveis que precisam ser configuradas são localizadas no arquivo `config.json.copy`, que deve ser renomeado para `config.json` com o seguinte comando:

```
cp config.json.copy config.json
```

### B.1) "Token"

Vamos criar o nosso Bot junto ao Telegram para obter o `token` e poder configurar o arquivo `config.json` com o valor retornado. Isso pode ser feito com o usuário do Telegram chamado [@BotFather](https://t.me/BotFather). Para criar e configurar o seu primeiro Bot, [clique aqui](https://telegram.me/BotFather) e siga as instruções dadas pelo Bot ao longo do processo (em inglês).

### B.2) "Creator_ID"

Consulte o seu ID de usuário no Telegram através de um bot como o [@userinfobot](https://t.me/userinfobot), que lhe fornece facilmente o ID (identificador único) da sua conta.


## C) Comandos Úteis

**Logar no servidor do GCloud:**

```
gcloud compute ssh sagan-was-right
```

