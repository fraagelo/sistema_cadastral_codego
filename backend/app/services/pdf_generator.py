import base64
import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.config import settings
from app.schemas.anexo_viii_d import AnexoViiiDCreate, SOLICITACOES_ANEXO_VIII_D
from app.schemas.anexo_viii_a import AnexoViiiACreate
from app.schemas.anexo_iii import AnexoIiiCreate, DOCUMENTOS_ANEXO_III
from app.schemas.anexo_v_declaracao_uso import AnexoVDeclaracaoUsoCreate
from app.schemas.anexo_v_cfo import AnexoVCfoCreate
from app.schemas.anexo_vii_mce import AnexoViiMceCreate, MCE_ESTRUTURA

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def _carregar_brasao_base64() -> str:
    caminho = os.path.join(TEMPLATES_DIR, "assets", "brasao_codego.png")
    with open(caminho, "rb") as f:
        conteudo = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{conteudo}"


_BRASAO_DATA_URI = _carregar_brasao_base64()


def _formatar_cnpj(digits: str) -> str:
    if len(digits) != 14:
        return digits
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def _formatar_cpf(digits: str) -> str:
    if len(digits) != 11:
        return digits
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def _formatar_telefone(digits: str) -> str:
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return digits


def _formatar_cep(digits: str) -> str:
    if len(digits) != 8:
        return digits
    return f"{digits[:5]}-{digits[5:]}"


MESES_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def _data_por_extenso(data: datetime) -> str:
    return f"{data.day:02d} de {MESES_PT[data.month - 1]} de {data.year}"


def _mes_ano_por_extenso(mes_ano: str) -> str:
    """'2026-09' -> 'setembro/2026'"""
    ano, mes = mes_ano.split("-")
    return f"{MESES_PT[int(mes) - 1]}/{ano}"


def _formatar_percentual(valor: float) -> str:
    if not valor:
        return ""
    return f"{valor:g}%".replace(".", ",")


def gerar_pdf_anexo_viii_d(dados: AnexoViiiDCreate, protocolo: str) -> str:
    """
    Renderiza o template do Anexo VIII-D (Formulário para pedido de Anuência para
    Alienação entre Particulares) preenchido com os dados reais do requerimento,
    e gera o PDF em disco. Retorna o caminho do arquivo gerado.
    """
    template = _env.get_template("anexo_viii_d.html")

    # Monta a lista de solicitações marcadas, na ordem original do documento.
    # O item "Outros" é marcado à parte para ser desenhado como uma linha
    # preenchida (sublinhado), no mesmo espírito do "Outros:____________"
    # do modelo original.
    itens_solicitacao = []
    for chave, rotulo in SOLICITACOES_ANEXO_VIII_D.items():
        if chave not in dados.solicitacoes:
            continue
        if chave == "outros":
            itens_solicitacao.append({"texto": "Outros:", "valor_linha": dados.outros_texto})
        else:
            itens_solicitacao.append({"texto": rotulo, "valor_linha": None})

    html_renderizado = template.render(
        brasao_data_uri=_BRASAO_DATA_URI,
        protocolo=protocolo,
        processo_numero=dados.processo_numero,
        nome_empresarial=dados.nome_empresarial,
        cnpj=_formatar_cnpj(dados.cnpj),
        endereco=dados.endereco,
        telefone=_formatar_telefone(dados.telefone),
        email=dados.email,
        cidade_data=datetime.now().strftime("Goiânia, %d/%m/%Y"),
        representante_nome=dados.representante_nome,
        representante_estado_civil=dados.representante_estado_civil,
        representante_rg=dados.representante_rg,
        representante_cpf=_formatar_cpf(dados.representante_cpf),
        representante_endereco=dados.representante_endereco,
        itens_solicitacao=itens_solicitacao,
        motivacao=dados.motivacao,
    )

    os.makedirs(settings.upload_dir, exist_ok=True)
    nome_arquivo = f"{protocolo}_anexo_viii_d.pdf"
    caminho_completo = os.path.join(settings.upload_dir, nome_arquivo)

    HTML(string=html_renderizado).write_pdf(caminho_completo)

    return caminho_completo


def gerar_pdf_anexo_viii_a(dados: AnexoViiiACreate, protocolo: str) -> str:
    """
    Renderiza o template do Anexo VIII-A (Formulário de Pedido de Anuência para
    Alienação entre Particulares) preenchido com os dados reais do requerimento,
    e gera o PDF em disco. Retorna o caminho do arquivo gerado.
    """
    template = _env.get_template("anexo_viii_a.html")

    html_renderizado = template.render(
        brasao_data_uri=_BRASAO_DATA_URI,
        protocolo=protocolo,
        processo_numero=dados.processo_numero,
        nome_empresarial=dados.nome_empresarial,
        cnpj=_formatar_cnpj(dados.cnpj),
        endereco=dados.endereco,
        telefone=_formatar_telefone(dados.telefone),
        email=dados.email,
        cidade_data=datetime.now().strftime("Goiânia, %d/%m/%Y"),
        representante_nome=dados.representante_nome,
        representante_estado_civil=dados.representante_estado_civil,
        representante_rg=dados.representante_rg,
        representante_cpf=_formatar_cpf(dados.representante_cpf),
        representante_endereco=dados.representante_endereco,
        area_via=dados.area_via,
        area_modulos=dados.area_modulos,
        area_quadra=dados.area_quadra,
        area_distrito=dados.area_distrito,
        comprador_nome_empresarial=dados.comprador_nome_empresarial,
        comprador_cnpj=_formatar_cnpj(dados.comprador_cnpj),
    )

    os.makedirs(settings.upload_dir, exist_ok=True)
    nome_arquivo = f"{protocolo}_anexo_viii_a.pdf"
    caminho_completo = os.path.join(settings.upload_dir, nome_arquivo)

    HTML(string=html_renderizado).write_pdf(caminho_completo)

    return caminho_completo


def gerar_pdf_anexo_iii(dados: AnexoIiiCreate, protocolo: str) -> str:
    """
    Renderiza o template do Anexo III (Solicitação de Área) preenchido com os
    dados reais do requerimento, e gera o PDF em disco. Retorna o caminho do
    arquivo gerado.
    """
    template = _env.get_template("anexo_iii.html")

    # Check list na ordem original do documento, marcando o que foi informado
    # como anexado ao requerimento.
    documentos = [
        {"texto": rotulo, "marcado": chave in dados.documentos}
        for chave, rotulo in DOCUMENTOS_ANEXO_III.items()
    ]

    html_renderizado = template.render(
        brasao_data_uri=_BRASAO_DATA_URI,
        protocolo=protocolo,
        municipio_interesse=dados.municipio_interesse,
        metragem_necessaria=dados.metragem_necessaria,
        nome_empresarial=dados.nome_empresarial,
        cnpj=_formatar_cnpj(dados.cnpj),
        endereco_correspondencia_empresa=dados.endereco_correspondencia_empresa,
        representante_nome=dados.representante_nome,
        representante_cpf=_formatar_cpf(dados.representante_cpf),
        representante_rg=dados.representante_rg,
        representante_nome_mae=dados.representante_nome_mae,
        email=dados.email,
        telefones=dados.telefones,
        representante_endereco_correspondencia=dados.representante_endereco_correspondencia,
        cnaes=dados.cnaes,
        documentos=documentos,
        cidade_data=f"Goiânia, {_data_por_extenso(datetime.now())}.",
    )

    os.makedirs(settings.upload_dir, exist_ok=True)
    nome_arquivo = f"{protocolo}_anexo_iii.pdf"
    caminho_completo = os.path.join(settings.upload_dir, nome_arquivo)

    HTML(string=html_renderizado).write_pdf(caminho_completo)

    return caminho_completo


def gerar_pdf_anexo_v_declaracao_uso(dados: AnexoVDeclaracaoUsoCreate, protocolo: str) -> str:
    """
    Renderiza o template do Anexo V (Declaração de Uso da Rede de Abastecimento
    de Água e de Esgoto da CODEGO) preenchido com os dados reais do requerimento,
    e gera o PDF em disco. Retorna o caminho do arquivo gerado.
    """
    template = _env.get_template("anexo_v_declaracao_uso.html")

    html_renderizado = template.render(
        brasao_data_uri=_BRASAO_DATA_URI,
        protocolo=protocolo,
        processo_numero=dados.processo_numero,
        nome_empresarial=dados.nome_empresarial,
        cnpj=_formatar_cnpj(dados.cnpj),
        endereco=dados.endereco,
        telefone=_formatar_telefone(dados.telefone),
        email=dados.email,
        cidade_data=datetime.now().strftime("Goiânia, %d/%m/%Y"),
        representante_nome=dados.representante_nome,
        representante_estado_civil=dados.representante_estado_civil,
        representante_rg=dados.representante_rg,
        representante_cpf=_formatar_cpf(dados.representante_cpf),
        representante_endereco=dados.representante_endereco,
    )

    os.makedirs(settings.upload_dir, exist_ok=True)
    nome_arquivo = f"{protocolo}_anexo_v_declaracao_uso.pdf"
    caminho_completo = os.path.join(settings.upload_dir, nome_arquivo)

    HTML(string=html_renderizado).write_pdf(caminho_completo)

    return caminho_completo


# Quantidade de meses por tabela no PDF do CFO. Cronogramas mais longos são
# quebrados em várias tabelas (de 4 trimestres cada) para caber na página.
MESES_POR_BLOCO_CFO = 12


def gerar_pdf_anexo_v_cfo(dados: AnexoVCfoCreate, protocolo: str) -> str:
    """
    Renderiza o template do Anexo V (Cronograma Físico da Obra — CFO) preenchido
    com os dados reais do requerimento, e gera o PDF em disco. Retorna o caminho
    do arquivo gerado.
    """
    template = _env.get_template("anexo_v_cfo.html")

    ano_inicio, mes_inicio = (int(p) for p in dados.inicio_obras.split("-"))
    total = len(dados.servicos[0].percentuais)

    meses = []
    for i in range(total):
        indice_mes = mes_inicio - 1 + i
        ano = ano_inicio + indice_mes // 12
        mes = indice_mes % 12
        meses.append({
            "rotulo": f"{i + 1}º mês",
            "referencia": f"{MESES_PT[mes][:3]}/{str(ano)[2:]}",
        })

    # Monta os blocos (tabelas) com os cabeçalhos de trimestre e as linhas de
    # serviço já formatadas, para o template só precisar iterar.
    blocos = []
    for inicio_bloco in range(0, total, MESES_POR_BLOCO_CFO):
        fim_bloco = min(inicio_bloco + MESES_POR_BLOCO_CFO, total)
        trimestres = [
            {
                "rotulo": f"{t // 3 + 1}º Trimestre",
                "colunas": min(t + 3, fim_bloco) - t,
            }
            for t in range(inicio_bloco, fim_bloco, 3)
        ]
        linhas = [
            {
                "descricao": servico.descricao,
                "celulas": [_formatar_percentual(p) for p in servico.percentuais[inicio_bloco:fim_bloco]],
            }
            for servico in dados.servicos
        ]
        blocos.append({
            "meses": meses[inicio_bloco:fim_bloco],
            "trimestres": trimestres,
            "linhas": linhas,
        })

    html_renderizado = template.render(
        brasao_data_uri=_BRASAO_DATA_URI,
        protocolo=protocolo,
        nome_empresa=dados.nome_empresa,
        endereco=dados.endereco,
        area_empresa=dados.area_empresa,
        area_construida=dados.area_construida,
        inicio_obras=_mes_ano_por_extenso(dados.inicio_obras),
        termino_obras=_mes_ano_por_extenso(dados.termino_obras),
        blocos=blocos,
    )

    os.makedirs(settings.upload_dir, exist_ok=True)
    nome_arquivo = f"{protocolo}_anexo_v_cfo.pdf"
    caminho_completo = os.path.join(settings.upload_dir, nome_arquivo)

    HTML(string=html_renderizado).write_pdf(caminho_completo)

    return caminho_completo


def gerar_pdf_anexo_vii_mce(dados: AnexoViiMceCreate, protocolo: str) -> str:
    """
    Renderiza o template do Memorial de Caracterização do Empreendimento (MCE)
    preenchido com os dados reais do requerimento, e gera o PDF em disco.
    Retorna o caminho do arquivo gerado.
    """
    template = _env.get_template("anexo_vii_mce.html")

    valores = dados.model_dump()
    valores["cnpj"] = _formatar_cnpj(dados.cnpj)
    valores["cep"] = _formatar_cep(dados.cep)
    valores["telefone"] = _formatar_telefone(dados.telefone)
    valores["mao_obra_total"] = dados.mao_obra_total

    # Resolve a estrutura do MCE com os valores preenchidos. Campos opcionais
    # deixados em branco aparecem como "Não informado" no documento.
    secoes = []
    for secao in MCE_ESTRUTURA:
        subsecoes = []
        for subsecao in secao["subsecoes"]:
            itens = []
            for campo, rotulo in subsecao["campos"]:
                valor = valores[campo]
                if isinstance(valor, str):
                    valor = valor.strip()
                itens.append({"rotulo": rotulo, "valor": valor if valor != "" else "Não informado"})
            subsecoes.append({**subsecao, "itens": itens})
        secoes.append({"titulo": secao["titulo"], "subsecoes": subsecoes})

    html_renderizado = template.render(
        brasao_data_uri=_BRASAO_DATA_URI,
        protocolo=protocolo,
        secoes=secoes,
        local_data=f"{dados.local_cidade_uf}, {_data_por_extenso(datetime.now())}",
        responsavel_nome=dados.responsavel_nome,
        responsavel_cargo=dados.responsavel_cargo,
        razao_social=dados.razao_social,
        cnpj=_formatar_cnpj(dados.cnpj),
    )

    os.makedirs(settings.upload_dir, exist_ok=True)
    nome_arquivo = f"{protocolo}_anexo_vii_mce.pdf"
    caminho_completo = os.path.join(settings.upload_dir, nome_arquivo)

    HTML(string=html_renderizado).write_pdf(caminho_completo)

    return caminho_completo
