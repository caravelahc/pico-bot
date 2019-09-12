ERROR_MSG = "Algo deu errado. Utilize o comando /help."

INVALID_MSG = "Mensagem inválida!"

INVALID_DOC = "O arquivo de imagem deve estar em formato PNG \
com uma camada transparente e caber em um quadrado 512x512 \
(um dos lados deve ter 512px e o outro 512px ou menos)."

ERROR_DOWNLOAD_PHOTO = "Erro ao tentar baixar foto do usuário."

USER_NO_PACK = "Você ainda não tem nenhum pacote de sticker. \
Por favor, primeiro crie um utilizando o comando /newpack para criar um novo pacote de stickers."

ADDED_STICKER = 'Sticker adicionado!'

REMOVED_STICKER = 'Sticker excluído!'

REMOVE_STICKER_HELP = """Comando inválido.
- Responda a um sticker que você possui com o comando /delsticker
- Ou use /delsticker <NomeDoPack> <X>
X: posição do sticker no pack, sendo 0 (zero) o primeiro
"""

GREETING = """Olá! Bot para automatizar a criação de stickers \
a partir de imagens ou mensagens.
Utilize o comando /help para ver os comandos disponíveis.

Código disponível no repositório:
http://github.com/caravelahc/pico-bot

Feito por @diogojs e @caravelahc"""

CREATOR_ACCESS_DENIED = """Username is not in the sudoers file.
This incident will be reported."""

NO_PERMISSION = """Você não tem permissão para editar este pack.
Certifique-se de que você é dono do pack, \
ou que o mesmo é público."""

HELP_MSG = """Comandos:
    /newpack <NomeDoPack> - cria um novo pack/pacote
    /addsticker [NomeDoPack] <emoji>:
        Adiciona sticker a um pack, com o respectivo emoji. \
Envie esse comando como legenda de uma imagem, \
em resposta a uma imagem/mensagem para criar um novo sticker, \
ou como resposta a um sticker existente para apenas adicioná-lo ao pack.
    /delsticker <NomeDoPack> <Posição> - remove o sticker do pack (não recuperável)
    /setdefaultpack <NomeDoPack> - configura seu pack padrão
    /setpublic <NomeDoPack> - torna seu pack público (qualquer pessoa pode editá-lo, adicionar e remover stickers)
    /setprivate <NomeDoPack> - torna seu pack privado para edição (qualquer pessoa ainda pode visualizá-lo e utilizá-lo) """
