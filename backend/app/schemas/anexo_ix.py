from pydantic import BaseModel, EmailStr, field_validator, model_validator

SIM_NAO = {"Sim", "Não"}
SIM_NAO_PARCIALMENTE = {"Sim", "Não", "Parcialmente"}

STATUS_OPERACAO_VALIDOS = {"Em operação", "Em recesso", "Paralisada", "Outro"}
RESPONSAVEL_ABASTECIMENTO_VALIDOS = {"CODEGO", "SANEAGO", "Município", "Não se aplica"}
MEDIDOR_VAZAO_VALIDOS = {"Sim", "Não", "Outro"}
RESPONSAVEL_ESGOTO_VALIDOS = {"Não se aplica", "CODEGO", "SANEAGO", "Outro"}


class AnexoIXCreate(BaseModel):
    # Cabeçalho
    tecnico_responsavel: str

    # Informações cadastrais gerais
    nome_empresarial: str
    cnpj: str
    endereco: str
    distrito: str
    telefone: str
    email: EmailStr
    responsavel: str
    num_funcionarios: str
    num_matriculas_imovel: str
    area_total_m2: str
    area_ocupada_m2: str
    taxa_ocupacao: str
    asfalto_frente: str  # Sim / Não / Parcialmente
    status_operacao: str  # Em operação / Em recesso / Paralisada / Outro
    status_operacao_prazo_dias: str | None = None
    status_operacao_paralisada_mes: str | None = None
    status_operacao_outro_texto: str | None = None

    # Informações de saneamento
    possui_hidrometro: str  # Sim / Não
    hidrometro_quantos: str | None = None
    hidrometro_1_numero: str | None = None
    hidrometro_1_faturamento: str | None = None
    hidrometro_2_numero: str | None = None
    hidrometro_2_faturamento: str | None = None

    possui_poco_artesiano: str  # Sim / Não
    poco_possui_outorga: str | None = None  # Sim / Não
    outorga_vigencia: str | None = None
    outorga_vazao: str | None = None

    responsavel_abastecimento: str  # CODEGO / SANEAGO / Município / Não se aplica
    responsavel_abastecimento_municipio: str | None = None

    possui_ete: str  # Sim / Não
    ete_ativa: str | None = None  # Sim / Não

    possui_medidor_vazao: str  # Sim / Não / Outro
    medidor_vazao_outro_texto: str | None = None

    responsavel_esgoto: str  # Não se aplica / CODEGO / SANEAGO / Outro
    responsavel_esgoto_outro_texto: str | None = None

    # Licenças (Sim/Não + vigência quando Sim)
    licenca_previa: str
    licenca_previa_vigencia: str | None = None
    licenca_instalacao: str
    licenca_instalacao_vigencia: str | None = None
    licenca_operacao: str
    licenca_operacao_vigencia: str | None = None
    licenciamento_bombeiros: str
    licenciamento_bombeiros_vigencia: str | None = None
    certidao_uso_solo: str
    certidao_uso_solo_vigencia: str | None = None
    alvara_sanitario: str
    alvara_sanitario_vigencia: str | None = None

    # Assinaturas
    responsavel_tecnico_nome: str
    responsavel_tecnico_registro: str

    g_recaptcha_response: str = ""

    @field_validator(
        "tecnico_responsavel",
        "nome_empresarial",
        "endereco",
        "distrito",
        "telefone",
        "responsavel",
        "num_funcionarios",
        "num_matriculas_imovel",
        "area_total_m2",
        "area_ocupada_m2",
        "taxa_ocupacao",
        "responsavel_tecnico_nome",
        "responsavel_tecnico_registro",
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

    @field_validator("telefone")
    @classmethod
    def valida_telefone(cls, v: str):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError("Telefone deve ter DDD + número (mínimo 10 dígitos).")
        return digits

    @field_validator("asfalto_frente")
    @classmethod
    def valida_asfalto(cls, v: str):
        if v not in SIM_NAO_PARCIALMENTE:
            raise ValueError(f"Opção inválida. Escolha entre: {', '.join(sorted(SIM_NAO_PARCIALMENTE))}")
        return v

    @field_validator("status_operacao")
    @classmethod
    def valida_status_operacao(cls, v: str):
        if v not in STATUS_OPERACAO_VALIDOS:
            raise ValueError(f"Status inválido. Escolha entre: {', '.join(sorted(STATUS_OPERACAO_VALIDOS))}")
        return v

    @field_validator(
        "possui_hidrometro",
        "possui_poco_artesiano",
        "possui_ete",
        "licenca_previa",
        "licenca_instalacao",
        "licenca_operacao",
        "licenciamento_bombeiros",
        "certidao_uso_solo",
        "alvara_sanitario",
    )
    @classmethod
    def valida_sim_nao(cls, v: str, info):
        if v not in SIM_NAO:
            raise ValueError(f"O campo '{info.field_name}' deve ser 'Sim' ou 'Não'.")
        return v

    @field_validator("responsavel_abastecimento")
    @classmethod
    def valida_responsavel_abastecimento(cls, v: str):
        if v not in RESPONSAVEL_ABASTECIMENTO_VALIDOS:
            raise ValueError(f"Opção inválida. Escolha entre: {', '.join(sorted(RESPONSAVEL_ABASTECIMENTO_VALIDOS))}")
        return v

    @field_validator("possui_medidor_vazao")
    @classmethod
    def valida_medidor_vazao(cls, v: str):
        if v not in MEDIDOR_VAZAO_VALIDOS:
            raise ValueError(f"Opção inválida. Escolha entre: {', '.join(sorted(MEDIDOR_VAZAO_VALIDOS))}")
        return v

    @field_validator("responsavel_esgoto")
    @classmethod
    def valida_responsavel_esgoto(cls, v: str):
        if v not in RESPONSAVEL_ESGOTO_VALIDOS:
            raise ValueError(f"Opção inválida. Escolha entre: {', '.join(sorted(RESPONSAVEL_ESGOTO_VALIDOS))}")
        return v

    @model_validator(mode="after")
    def valida_condicionais(self):
        if self.status_operacao == "Em recesso" and not (self.status_operacao_prazo_dias or "").strip():
            raise ValueError("Informe o prazo (em dias) para o fim do recesso.")
        if self.status_operacao == "Paralisada" and not (self.status_operacao_paralisada_mes or "").strip():
            raise ValueError("Informe desde quando (mês) a operação está paralisada.")
        if self.status_operacao == "Outro" and not (self.status_operacao_outro_texto or "").strip():
            raise ValueError("Descreva o status de operação quando selecionar 'Outro'.")

        if self.possui_hidrometro == "Sim" and not (self.hidrometro_quantos or "").strip():
            raise ValueError("Informe quantos hidrômetros a empresa possui.")

        if self.possui_poco_artesiano == "Sim" and not (self.poco_possui_outorga or "").strip():
            raise ValueError("Informe se o poço artesiano possui outorga.")
        if self.poco_possui_outorga == "Sim" and not (self.outorga_vigencia or "").strip():
            raise ValueError("Informe a vigência da outorga.")

        if self.responsavel_abastecimento == "Município" and not (self.responsavel_abastecimento_municipio or "").strip():
            raise ValueError("Informe o nome do município responsável pelo abastecimento.")

        if self.possui_ete == "Sim" and not (self.ete_ativa or "").strip():
            raise ValueError("Informe se a ETE está ativa.")

        if self.possui_medidor_vazao == "Outro" and not (self.medidor_vazao_outro_texto or "").strip():
            raise ValueError("Descreva o medidor de vazão quando selecionar 'Outro'.")

        if self.responsavel_esgoto == "Outro" and not (self.responsavel_esgoto_outro_texto or "").strip():
            raise ValueError("Descreva o responsável pela coleta/tratamento de esgoto quando selecionar 'Outro'.")

        for campo_licenca, campo_vigencia in [
            ("licenca_previa", "licenca_previa_vigencia"),
            ("licenca_instalacao", "licenca_instalacao_vigencia"),
            ("licenca_operacao", "licenca_operacao_vigencia"),
            ("licenciamento_bombeiros", "licenciamento_bombeiros_vigencia"),
            ("certidao_uso_solo", "certidao_uso_solo_vigencia"),
            ("alvara_sanitario", "alvara_sanitario_vigencia"),
        ]:
            if getattr(self, campo_licenca) == "Sim" and not (getattr(self, campo_vigencia) or "").strip():
                raise ValueError(f"Informe a vigência de '{campo_licenca}' quando marcado como 'Sim'.")

        return self
