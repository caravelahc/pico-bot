# Pico-Bot

Bot para automatizar a criação de stickers a partir de imagens ou mensagens.

Código disponível no repositório:
[http://github.com/caravelahc/pico-bot]()

Feito por [@diogojs](https://t.me/diogojs) e [@caravelahc](https://t.me/caravelahc).


## A) Como Instalar

### A.1) Python

Tenha certeza que possui o Python com versão maior ou igual à 3.7.0.

### A.2) Gerenciador de pacotes `poetry`

Primeiro de tudo, instale o `poetry`, que é um gerenciador de pacotes e dependências do Python.

### A.3) Dependências

Para instalar as dependências do projeto, utilizamos o gerenciador de dependências `poetry`, executando o comando:
```
poetry install
```

Caso possua problemas com a instalação através do `poetry`, é possível criar um ambiente local manualmente, para que possamos instalar os pacotes sem afetar o sistema:
```
python3.7 -m venv .venv
source .venv/bin/activate
```
Estando dentro do VENV (virtual env), tente rodar novamente `poetry install`, ou instale as dependências listadas no arquivo `pyproject.toml` manualmente, com o comando:
```
python3.7 -m pip install <dependencia>
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

### B.3) "DB_Path"

Pode deixar o valor apenas como `picobot/bot.db`. Não nos é muito interessante agora.


## C) Como Usar

### Criar novo pacote de Stickers:

Cria um novo pack/pacote de stickers, que lhe permitirá adicionar stickers nele e compartilhar para uso/edição dos demais usuários do Telegram.
```
/newpack@<NomeDoBot> <NomeDoPacoteDeStickers>
```

### Adicionar sticker no Pack:

Adiciona sticker a um pack, com o respectivo emoji. Envie esse comando como legenda de uma imagem, em resposta a uma imagem/mensagem para criar um novo sticker, ou como resposta a um sticker existente para apenas adicioná-lo ao pack.
```
/addsticker@<NomeDoBot> [NomeDoPack] <Emoji>
```

### Remover sticker do Pack:

Remove o sticker do pack (não recuperável), sendo que `<Posicao>` é a posição do sticker dentro do pack. Caso `<Posicao>` seja igual à 0 (zero), removerá o primeiro sticker, caso o seu valor seja **1 (um)** removerá o segundo sticker, e assim por diante.
```
/delsticker@<NomeDoBot> [NomeDoPack] <Posicao>
```

### Configurar pack de stickers padrão:

Configura seu pack padrão.
```
/setdefaultpack@<NomeDoBot> [NomeDoPack]
```

### Tornar pack público:

Torna seu pack público, de forma que qualquer pessoa pode editá-lo (adicionar e remover stickers).
```
/setpublic <NomeDoPack>
```

### Tornar pack privado:

Torna seu pack privado para edição, de forma que qualquer pessoa possa apenas visualizá-lo e utilizá-lo, sem opção de adicionar ou remover stickers.
```
/setprivate <NomeDoPack>
```


## D) Outros Comandos Úteis

### Logar na instância do GCloud via SSH:
```
gcloud compute ssh <instance_name_on_gcloud>
```

## E) Para colaborar no projeto:

### E.1) Instale as dependências com o `poetry`:

Execute o comando

```
poetry install
```

para criar o ambiente e instalar as dependências.

### E.2) Instale os hooks de `pre-commit`:

Execute

```
pre-commit install
```

para instalar os hooks que checam a formatação do código e rodam os programas de análise estática.

### E.3) Após fazer modificações, execute os testes:

Execute

```
summon test
```

para garantir que nenhum teste deixou de rodar corretamente.
