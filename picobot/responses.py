ERROR_MSG = 'Something went wrong.'

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
