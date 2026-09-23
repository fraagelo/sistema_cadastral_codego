from pydantic import BaseModel, EmailStr, field_validator, model_validator

ESTADOS_CIVIS_VALIDOS = {
    "Solteiro(a)",
    "Casado(a)",
    "Divorciado(a)",
    "Viúvo(a)",
    "União estável",
}

TIPOS_ALTERACAO_VALIDOS = {
    "Fusão",
    "Cisão",
    "Incorporação",
    "Mudança do quadro societário",
    "Mudança da atividade econômica",
    "Outra alteração do Contrato Social",
}


class AnexoViiiCCreate(BaseModel):
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

    # Tipo de alteração pretendida
    tipo_alteracao: str
    outra_alteracao_texto: str | None = None

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

    @field_validator("tipo_alteracao")
    @classmethod
    def valida_tipo_alteracao(cls, v: str):
        if v not in TIPOS_ALTERACAO_VALIDOS:
            raise ValueError(f"Tipo de alteração inválido. Opções: {', '.join(sorted(TIPOS_ALTERACAO_VALIDOS))}")
        return v

    @model_validator(mode="after")
    def valida_outra_alteracao_texto(self):
        if self.tipo_alteracao == "Outra alteração do Contrato Social" and not (self.outra_alteracao_texto or "").strip():
            raise ValueError("Descreva a alteração quando selecionar 'Outra alteração do Contrato Social'.")
        return self
