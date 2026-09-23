from pydantic import BaseModel, EmailStr, field_validator

# Chaves e rótulos da "Documentação que acompanha o requerimento" do Anexo III,
# na ordem em que aparecem no documento original. A chave é o que o front-end
# envia; o rótulo é o texto exato usado no PDF.
DOCUMENTOS_ANEXO_III: dict[str, str] = {
    "certidao_simplificada": (
        "I - Certidão simplificada da empresa interessada, emitida pela Junta Comercial, "
        "em até 30 (trinta) dias;"
    ),
    "identidade_cpf_responsavel": (
        "II - Cópia do documento de identidade e CPF do responsável pela administração da sociedade;"
    ),
    "certidoes_negativas_fazenda": (
        "III - Certidão negativa de débitos junto à fazenda pública federal, estadual "
        "e municipal, emitida em até 30 (trinta) dias;"
    ),
    "procuracao": (
        "IV - Em caso do exercício de representação, procuração nos termos do art. 5º "
        "do presente regulamento;"
    ),
    "contrato_social": "V - Cópia do contrato social;",
    "regularidade_fgts": "VI - Certificado de regularidade do FGTS;",
    "certidao_trabalhista": "VII - Certidão negativa de débitos trabalhistas;",
    "matricula_imovel": (
        "VIII - Certidão de inteiro teor da matrícula do imóvel (em caso de solicitação para área "
        "específica ou em demais casos em que a documentação elencada neste artigo for requerida);"
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

    @field_validator("cnpj")
    @classmethod
    def valida_cnpj(cls, v: str):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos.")
        return digits

    @field_validator("representante_cpf")
    @classmethod
    def valida_cpf_representante(cls, v: str):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) != 11:
            raise ValueError("CPF do representante deve ter 11 dígitos.")
        return digits

    @field_validator("telefones")
    @classmethod
    def valida_telefones(cls, v: str):
        # Campo livre ("Telefones", no plural), mas precisa ter ao menos um
        # número completo com DDD.
        if len("".join(filter(str.isdigit, v))) < 10:
            raise ValueError("Informe ao menos um telefone com DDD (mínimo 10 dígitos).")
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
