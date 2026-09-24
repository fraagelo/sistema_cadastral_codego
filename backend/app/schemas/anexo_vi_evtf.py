from pydantic import BaseModel, EmailStr, field_validator


class AnexoVIEvtfCreate(BaseModel):
    # 1 - Dados cadastrais
    razao_social: str
    cnpj: str
    endereco: str
    cidade: str
    uf: str
    cep: str
    telefone: str
    email: EmailStr

    conta_corrente: str | None = None
    banco: str | None = None
    agencia: str | None = None
    praca_pagamento: str | None = None

    responsavel_nome: str
    responsavel_ci_orgao: str
    responsavel_cpf: str
    responsavel_endereco: str
    responsavel_cidade_uf: str
    responsavel_cep: str
    responsavel_cargo: str
    responsavel_contato: str
    responsavel_email: EmailStr

    ramo_atividade_cnae: str
    ramo_atividade_especificacao: str

    # 2 - Dados econômicos e financeiros
    capital_social_data: str | None = None
    capital_social_ato: str | None = None
    capital_recursos_proprios: str | None = None
    capital_recursos_incentivos: str | None = None
    capital_recursos_outros: str | None = None
    capital_recursos_total: str | None = None
    composicao_nacional_pct: str | None = None
    composicao_estrangeiro_pct: str | None = None
    principais_acionistas: str | None = None

    # 4 - Concepção do projeto
    projeto_objetivo: str
    distrito_industrial: str
    area_terreno_m2: str

    prazo_implantacao_inicio: str | None = None
    prazo_implantacao_termino: str | None = None
    prazo_expansao_inicio: str | None = None
    prazo_expansao_termino: str | None = None

    eng_area_construida_implantacao: str | None = None
    eng_area_construida_expansao: str | None = None
    eng_area_estocagem_implantacao: str | None = None
    eng_area_estocagem_expansao: str | None = None
    eng_estacionamento_implantacao: str | None = None
    eng_estacionamento_expansao: str | None = None

    fluxo_producao_descricao: str

    saneamento_consumo_agua: str | None = None
    saneamento_geracao_esgoto: str | None = None
    saneamento_volume_rejeitos: str | None = None
    saneamento_estado_fisico_rejeitos: str | None = None
    saneamento_tratamento_proprio: str | None = None
    saneamento_equipamento_controle: str | None = None
    saneamento_consumo_energia: str | None = None
    saneamento_potencia_instalada: str | None = None

    empregos_diretos: str
    empregos_indiretos: str
    mao_obra_local_pct: str | None = None

    # Assinaturas
    responsavel_tecnico_nome: str
    responsavel_tecnico_registro: str

    g_recaptcha_response: str = ""

    @field_validator(
        "razao_social", "endereco", "cidade", "uf", "cep", "telefone",
        "responsavel_nome", "responsavel_ci_orgao", "responsavel_endereco",
        "responsavel_cidade_uf", "responsavel_cep", "responsavel_cargo", "responsavel_contato",
        "ramo_atividade_cnae", "ramo_atividade_especificacao",
        "projeto_objetivo", "distrito_industrial", "area_terreno_m2",
        "fluxo_producao_descricao", "empregos_diretos", "empregos_indiretos",
        "responsavel_tecnico_nome", "responsavel_tecnico_registro",
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

    @field_validator("responsavel_cpf")
    @classmethod
    def valida_cpf(cls, v: str):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) != 11:
            raise ValueError("CPF deve ter 11 dígitos.")
        return digits

    @field_validator("telefone")
    @classmethod
    def valida_telefone(cls, v: str):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError("Telefone deve ter DDD + número (mínimo 10 dígitos).")
        return digits
