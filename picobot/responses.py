ERROR_MSG = "Algo deu errado. Utilize o comando /help."

TELEGRAM_ERROR_CODES = {
    'stickerpack_stickers_too_much': 'Este pack atingiu o tamanho limite permitido pelo Telegram.\nCrie um novo pack.',
    'stickers_too_much': 'Este pack atingiu o tamanho limite permitido pelo Telegram.\nCrie um novo pack.',
    'sticker_png_nopng': 'Este pack é de imagens e não suporta este tipo de arquivo.\nPara criar pack de vídeo use\nnewvideopack [nome_do_pack]',
    'sticker_video_nowebm': 'Este pack é de vídeos e não suporta este tipo de arquivo.\nPara criar pack de de imagens use\nnewpack [nome_do_pack]',
}

INVALID_MSG = "Mensagem inválida!"

INVALID_DOC = "O arquivo de imagem deve estar em formato PNG \
com uma camada transparente e caber em um quadrado 512x512 \
(um dos lados deve ter 512px e o outro 512px ou menos)."

ERROR_DOWNLOAD_PHOTO = "Não foi possível baixar a foto do usuário."

FILE_TOO_LARGE = "O arquivo é grande demais"

VIDEO_TOO_LONG = "O vídeo não pode ter mais de 3 segundos."

USER_NO_PACK = "Você ainda não tem nenhum pacote de sticker. \
Por favor, primeiro crie um utilizando o comando /newpack para criar um novo pacote de stickers."

ADDED_STICKER = 'Sticker adicionado!'

REMOVED_STICKER = 'Sticker excluído!'

PACK_PRIVACY_UPDATED = 'Configuração de privacidade do pack atualizada.'

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
    /setprivate <NomeDoPack> - torna seu pack privado para edição (qualquer pessoa ainda pode visualizá-lo e utilizá-lo)

    Para utilizar espaços no nome do pacote, escreva-o entre aspas simples ou duplas."""
