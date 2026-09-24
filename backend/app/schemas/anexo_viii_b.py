from pydantic import BaseModel, EmailStr, field_validator, model_validator
from app.schemas.validacoes import cnpj_valido, cpf_valido, rg_valido, telefone_valido

ESTADOS_CIVIS_VALIDOS = {
    "Solteiro(a)",
    "Casado(a)",
    "Divorciado(a)",
    "Viúvo(a)",
    "União estável",
}

TIPOS_OPERACAO_VALIDOS = {"Remembramento", "Desmembramento"}


class AnexoViiiBCreate(BaseModel):
    # Dados da empresa — tabela do formulário
    processo_numero: str
    nome_empresarial: str
    cnpj: str
    endereco: str
    telefone: str
    email: EmailStr

    # Representante legal (parágrafo de qualificação)
    representante_nome: str
    representante_estado_civil: str
    representante_rg: str
    representante_cpf: str
    representante_endereco: str

    # Tipo de operação e dados da área
    tipo_operacao: str
    area_via: str
    area_modulos: str
    area_quadra: str
    area_distrito: str
    area_total_m2: str

    # Justificativa
    justificativa: str

    g_recaptcha_response: str = ""

    @field_validator(
        "processo_numero",
        "nome_empresarial",
        "endereco",
        "telefone",
        "representante_nome",
        "representante_estado_civil",
        "representante_rg",
        "representante_endereco",
        "area_via",
        "area_modulos",
        "area_quadra",
        "area_distrito",
        "area_total_m2",
        "justificativa",
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

    @field_validator("telefone")
    @classmethod
    def valida_telefone(cls, v: str):
        digits = "".join(filter(str.isdigit, v))
        if not telefone_valido(digits):
            raise ValueError("Telefone deve ter DDD + número: 10 dígitos (fixo) ou 11 (celular).")
        return digits

    @field_validator("representante_estado_civil")
    @classmethod
    def valida_estado_civil(cls, v: str):
        if v not in ESTADOS_CIVIS_VALIDOS:
            raise ValueError(f"Estado civil inválido. Opções: {', '.join(sorted(ESTADOS_CIVIS_VALIDOS))}")
        return v

    @field_validator("tipo_operacao")
    @classmethod
    def valida_tipo_operacao(cls, v: str):
        if v not in TIPOS_OPERACAO_VALIDOS:
            raise ValueError(f"Tipo de operação inválido. Opções: {', '.join(sorted(TIPOS_OPERACAO_VALIDOS))}")
        return v
