ERROR_MSG = "Algo deu errado. Utilize o comando /help."

INVALID_MSG = "Mensagem inválida!"

INVALID_DOC = "O arquivo de imagem deve estar em formato PNG \
com uma camada transparente e caber em um quadrado 512x512 \
(um dos lados deve ter 512px e o outro 512px ou menos)."

ERROR_DOWNLOAD_PHOTO = "Erro ao tentar baixar foto do usuário."

USER_NO_PACK = "Você ainda não tem nenhum pacote de sticker. \
Por favor, primeiro crie um utilizando o comando /newpack para criar um novo pacote de stickers."

ADDED_STICKER = 'Sticker adicionado!'

GREETING = 'Hello!'

ACCESS_DENIED = """Username is not in the sudoers file.
This incident will be reported."""

HELP_MSG = """Bot para automatizar a criação de stickers \
    a partir de imagens ou mensagens.
    Para ativar o bot utilize /start
    Comandos:
    /newpack <NomeDoPack> - cria um novo pack/pacote
    /setpackicon - define o ícone do pack
    /addsticker <NomeDoPack> [emoji]:
        Adiciona sticker a um pack, com o respectivo emoji.
        Envie esse comando como legenda de uma imagem, \
        em resposta a uma imagem/mensagem para criar um novo sticker, \
        ou como resposta a um sticker para apenas adicioná-lo ao pack.
    /delsticker - remove o sticker do pack (não recuperável)

    Este bot também reflete os demais comandos do bot oficial de \
    stickers do telegram, para mais informações verifique a ajuda \
    do @Stickers

    Código disponível no repositório:
    http://github.com/caravelahc/pico-bot

    Feito por @diogojs"""
