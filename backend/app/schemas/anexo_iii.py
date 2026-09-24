import re

from pydantic import BaseModel, EmailStr, field_validator
from app.schemas.validacoes import (
    cnpj_valido,
    cpf_valido,
    formatar_numero_br,
    numero_br,
    rg_valido,
    somente_digitos,
    telefone_valido,
)

# Chaves e rótulos da "Documentação que acompanha o requerimento" do Anexo III,
# na ordem em que aparecem no documento original. A chave é o que o front-end
# envia; o rótulo é o texto exato usado no PDF (as quebras de linha ficam nos
# mesmos pontos do modelo do Regulamento).
DOCUMENTOS_ANEXO_III: dict[str, str] = {
    "certidao_simplificada": (
        "I - Certidão simplificada da empresa interessada, emitida pela Junta Comercial,\n"
        "em até 30 (trinta) dias;"
    ),
    "identidade_cpf_responsavel": (
        "II - Cópia do documento de identidade e CPF do responsável pela administração da sociedade;"
    ),
    "certidoes_negativas_fazenda": (
        "III - Certidão negativa de débitos junto à fazenda pública federal, estadual\n"
        "e municipal, emitida em até 30 (trinta) dias;"
    ),
    "procuracao": (
        "IV - Em caso do exercício de representação, procuração nos termos do art. 5º\n"
        "do presente regulamento;"
    ),
    "contrato_social": "V - Cópia do contrato social;",
    "regularidade_fgts": "VI - Certificado de regularidade do FGTS;",
    "certidao_trabalhista": "VII - Certidão negativa de débitos trabalhistas;",
    "matricula_imovel": (
        "VIII - Certidão de inteiro teor da matrícula do imóvel (em caso de solicitação para área específica\n"
        "ou em demais casos em que a documentação elencada neste artigo for requerida);"
    ),
    "evtf": "IX - Estudo de Viabilidade Técnica e Financeira - EVTF (Anexo VI).",
}

MAX_CNAES = 4


class CnaeItem(BaseModel):
    numero: str
    descricao: str

    @field_validator("numero", "descricao")
    @classmethod
    def campo_nao_vazio(cls, v: str, info):
        if not v or not v.strip():
            raise ValueError(f"O campo '{info.field_name}' do CNAE é obrigatório.")
        return v.strip()


class AnexoIiiCreate(BaseModel):
    # Área pretendida
    municipio_interesse: str
    metragem_necessaria: str

    # Dados cadastrais da empresa (primeira tabela)
    nome_empresarial: str
    cnpj: str
    endereco_correspondencia_empresa: str

    # Dados cadastrais do representante (segunda tabela do modelo)
    representante_nome: str
    representante_cpf: str
    representante_rg: str
    representante_nome_mae: str
    email: EmailStr
    telefones: str
    representante_endereco_correspondencia: str

    # Atividades (Nº CNAE / Descrição da Atividade) — até 4 linhas
    cnaes: list[CnaeItem]

    # Check list da documentação que acompanha o requerimento
    documentos: list[str] = []

    g_recaptcha_response: str = ""

    @field_validator(
        "municipio_interesse",
        "metragem_necessaria",
        "nome_empresarial",
        "endereco_correspondencia_empresa",
        "representante_nome",
        "representante_rg",
        "representante_nome_mae",
        "representante_endereco_correspondencia",
    )
    @classmethod
    def campo_nao_vazio(cls, v: str, info):
        if not v or not v.strip():
            raise ValueError(f"O campo '{info.field_name}' é obrigatório.")
        return v.strip()

    @field_validator("metragem_necessaria")
    @classmethod
    def valida_metragem(cls, v: str):
        try:
            valor = numero_br(v)
        except ValueError as exc:
            raise ValueError(f"Metragem necessária: {exc}") from exc
        if valor <= 0:
            raise ValueError("A metragem necessária deve ser maior que zero.")
        return formatar_numero_br(valor)

    @field_validator("cnpj")
    @classmethod
    def valida_cnpj(cls, v: str):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos.")
        if not cnpj_valido(digits):
            raise ValueError("CNPJ inválido. Confira os números digitados.")
        return digits

    @field_validator("representante_rg")
    @classmethod
    def valida_rg(cls, v: str):
        if not rg_valido(v):
            raise ValueError("RG inválido: informe o número completo do documento (entre 5 e 14 números).")
        return v

    @field_validator("representante_cpf")
    @classmethod
    def valida_cpf_representante(cls, v: str):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) != 11:
            raise ValueError("CPF do representante deve ter 11 dígitos.")
        if not cpf_valido(digits):
            raise ValueError("CPF do representante inválido. Confira os números digitados.")
        return digits

    @field_validator("telefones")
    @classmethod
    def valida_telefones(cls, v: str):
        # Campo livre ("Telefones", no plural): um ou mais números separados por
        # "/", "," ou ";", cada um com DDD (10 dígitos fixo, 11 celular).
        numeros = [somente_digitos(parte) for parte in re.split(r"[/,;]", v or "") if parte.strip()]
        if not numeros:
            raise ValueError("Informe ao menos um telefone com DDD.")
        if len(numeros) > 3:
            raise ValueError("Informe no máximo 3 telefones.")
        if not all(telefone_valido(n) for n in numeros):
            raise ValueError(
                "Cada telefone deve ter DDD + número: 10 dígitos (fixo) ou 11 (celular). "
                "Separe os números com \"/\"."
            )
        return v.strip()

    @field_validator("cnaes")
    @classmethod
    def valida_cnaes(cls, v: list[CnaeItem]):
        if not v:
            raise ValueError("Informe ao menos um CNAE.")
        if len(v) > MAX_CNAES:
            raise ValueError(f"Informe no máximo {MAX_CNAES} CNAEs.")
        return v

    @field_validator("documentos")
    @classmethod
    def valida_documentos(cls, v: list[str]):
        invalidos = set(v) - set(DOCUMENTOS_ANEXO_III.keys())
        if invalidos:
            raise ValueError(f"Documentos inválidos: {', '.join(invalidos)}")
        return v
