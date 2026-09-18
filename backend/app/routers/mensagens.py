import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.orm import Mensagem, AnexoMensagem
from app.schemas.mensagens import MensagemOut
from app.services.validacao_arquivos import validar_anexo, salvar_arquivo
from app.services.recaptcha import verificar_recaptcha
from app.services.email_service import enviar_email_nova_mensagem

router = APIRouter()


@router.post("", response_model=MensagemOut, status_code=201)
async def enviar_mensagem(
    remetente_nome: str = Form(...),
    assunto: str = Form(...),
    conteudo: str = Form(...),
    processo_id: int | None = Form(None),
    protocolo: str | None = Form(None),
    g_recaptcha_response: str = Form(default=""),
    anexos: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    """Módulo de Mensagem e Anexos: envia uma mensagem com anexos complementares (Etapa 4)."""
    recaptcha_ok, recaptcha_erro = verificar_recaptcha(g_recaptcha_response)
    if not recaptcha_ok:
        raise HTTPException(status_code=422, detail=recaptcha_erro)

    mensagem = Mensagem(
        processo_id=processo_id,
        remetente_nome=remetente_nome,
        assunto=assunto,
        conteudo=conteudo,
    )
    db.add(mensagem)
    db.commit()
    db.refresh(mensagem)

    caminhos_anexos = []
    for anexo in anexos:
        conteudo_bytes = await anexo.read()
        if not conteudo_bytes:
            continue
        validar_anexo(anexo, conteudo_bytes)
        nome_storage = f"msg{mensagem.id}_{anexo.filename}"
        caminho = salvar_arquivo(conteudo_bytes, settings.upload_dir, nome_storage)
        caminhos_anexos.append(caminho)

        registro_anexo = AnexoMensagem(
            mensagem_id=mensagem.id,
            nome_original=anexo.filename,
            caminho_storage=caminho,
            tamanho_bytes=len(conteudo_bytes),
            tipo_mime=anexo.content_type or "application/octet-stream",
        )
        db.add(registro_anexo)

    db.commit()
    db.refresh(mensagem)

    # Notifica o e-mail fixo da empresa sobre a nova mensagem (mesmo padrão
    # usado no documento assinado -- NOTIFICATION_EMAIL, não um e-mail do
    # remetente da mensagem, já que o formulário não pede e-mail dele).
    if settings.notification_email:
        enviar_email_nova_mensagem(
            destinatario_email=settings.notification_email,
            remetente_nome=remetente_nome,
            assunto=assunto,
            conteudo=conteudo,
            protocolo=protocolo,
            caminhos_anexos=caminhos_anexos,
        )

    return mensagem


@router.get("/{processo_id}", response_model=list[MensagemOut])
def listar_mensagens_do_processo(processo_id: int, db: Session = Depends(get_db)):
    """Lista as mensagens vinculadas a um processo específico."""
    return db.query(Mensagem).filter(Mensagem.processo_id == processo_id).all()
