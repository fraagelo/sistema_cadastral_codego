from pydantic import BaseModel, EmailStr, field_validator

ESTADOS_CIVIS_VALIDOS = {
    "Solteiro(a)",
    "Casado(a)",
    "Divorciado(a)",
    "Viúvo(a)",
    "União estável",
}


class AnexoVDeclaracaoUsoCreate(BaseModel):
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

    @field_validator("telefone")
    @classmethod
    def valida_telefone(cls, v: str):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError("Telefone deve ter DDD + número (mínimo 10 dígitos).")
        return digits

    @field_validator("representante_estado_civil")
    @classmethod
    def valida_estado_civil(cls, v: str):
        if v not in ESTADOS_CIVIS_VALIDOS:
            raise ValueError(f"Estado civil inválido. Opções: {', '.join(sorted(ESTADOS_CIVIS_VALIDOS))}")
        return v
