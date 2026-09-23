const API_BASE_URL = window.CODEGO_API_BASE_URL || 'http://localhost:8000';

const form = document.getElementById('form-anexo-iii');
const submitButton = document.getElementById('btn-submit');
const feedbackEl = document.getElementById('feedback');

function onlyDigits(value) {
  return value.replace(/\D/g, '');
}

function maskCnpj(digits) {
  return digits
    .slice(0, 14)
    .replace(/(\d{2})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1/$2')
    .replace(/(\d{4})(\d{1,2})$/, '$1-$2');
}

function maskCpf(digits) {
  return digits
    .slice(0, 11)
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
}

function maskTelefone(digits) {
  const d = digits.slice(0, 11);
  if (d.length <= 10) {
    return d
      .replace(/(\d{2})(\d)/, '($1) $2')
      .replace(/(\d{4})(\d{1,4})$/, '$1-$2');
  }
  return d
    .replace(/(\d{2})(\d)/, '($1) $2')
    .replace(/(\d{5})(\d{1,4})$/, '$1-$2');
}

document.getElementById('cnpj').addEventListener('input', (e) => {
  e.target.value = maskCnpj(onlyDigits(e.target.value));
});
document.getElementById('representante_cpf').addEventListener('input', (e) => {
  e.target.value = maskCpf(onlyDigits(e.target.value));
});

function maskCep(digits) {
  return digits.slice(0, 8).replace(/(\d{5})(\d{1,3})$/, '$1-$2');
}

function configurarBuscaCep(cepInputId, statusId, enderecoInputId, campoErro) {
  const cepInput = document.getElementById(cepInputId);
  const statusEl = document.getElementById(statusId);
  const enderecoInput = document.getElementById(enderecoInputId);

  cepInput.addEventListener('input', (e) => {
    e.target.value = maskCep(onlyDigits(e.target.value));
    statusEl.textContent = '';
    statusEl.className = 'field__hint';
  });

  cepInput.addEventListener('blur', async () => {
    const cepDigits = onlyDigits(cepInput.value);
    if (cepDigits.length !== 8) {
      return;
    }

    statusEl.textContent = 'Buscando endereço...';
    statusEl.className = 'field__hint';

    try {
      const response = await fetch(`https://viacep.com.br/ws/${cepDigits}/json/`);
      const dados = await response.json();

      if (dados.erro) {
        statusEl.textContent = 'CEP não encontrado. Preencha o endereço manualmente.';
        statusEl.className = 'field__hint field__hint--warn';
        return;
      }

      const partes = [dados.logradouro, dados.bairro, `${dados.localidade}-${dados.uf}`]
        .filter((parte) => parte && parte.trim());
      const enderecoEncontrado = partes.join(', ');

      if (!enderecoInput.value.trim()) {
        enderecoInput.value = enderecoEncontrado;
      }

      statusEl.textContent = `Endereço encontrado: ${enderecoEncontrado}. Complete com número/complemento, se necessário.`;
      statusEl.className = 'field__hint field__hint--ok';
      clearError(campoErro);
    } catch (error) {
      statusEl.textContent = 'Não foi possível consultar o CEP agora. Preencha o endereço manualmente.';
      statusEl.className = 'field__hint field__hint--warn';
    }
  });
}

configurarBuscaCep(
  'cep_busca',
  'cep_busca-status',
  'endereco_correspondencia_empresa',
  'endereco_correspondencia_empresa'
);
configurarBuscaCep(
  'representante_cep_busca',
  'representante_cep_busca-status',
  'representante_endereco_correspondencia',
  'representante_endereco_correspondencia'
);

// Linhas de CNAE com algum campo preenchido (linhas totalmente vazias são ignoradas).
function coletarCnaes() {
  return Array.from(document.querySelectorAll('#cnaes-group .cnae-row'))
    .map((linha) => ({
      numero: linha.querySelector('[data-cnae="numero"]').value.trim(),
      descricao: linha.querySelector('[data-cnae="descricao"]').value.trim(),
    }))
    .filter((cnae) => cnae.numero || cnae.descricao);
}

function setError(fieldName, message) {
  const errorEl = document.querySelector(`[data-error-for="${fieldName}"]`);
  if (!errorEl) return;
  const field = document.getElementById(fieldName);
  if (field) field.closest('.field')?.classList.add('field--invalid');
  errorEl.textContent = message;
}

function clearError(fieldName) {
  const errorEl = document.querySelector(`[data-error-for="${fieldName}"]`);
  if (!errorEl) return;
  const field = document.getElementById(fieldName);
  if (field) field.closest('.field')?.classList.remove('field--invalid');
  errorEl.textContent = '';
}

function validateEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

const CAMPOS_TEXTO_OBRIGATORIOS = [
  ['municipio_interesse', 'Informe o município de interesse.'],
  ['metragem_necessaria', 'Informe a metragem necessária.'],
  ['nome_empresarial', 'Informe o nome empresarial.'],
  ['endereco_correspondencia_empresa', 'Informe o endereço para correspondência da empresa.'],
  ['representante_nome', 'Informe o nome do representante.'],
  ['representante_rg', 'Informe o RG do representante.'],
  ['representante_nome_mae', 'Informe o nome da mãe do representante.'],
  ['representante_endereco_correspondencia', 'Informe o endereço para correspondência do representante.'],
];

function validateForm() {
  let valid = true;

  for (const [id, mensagem] of CAMPOS_TEXTO_OBRIGATORIOS) {
    const el = document.getElementById(id);
    if (!el.value.trim()) {
      setError(id, mensagem);
      valid = false;
    } else {
      clearError(id);
    }
  }

  const cnpjDigits = onlyDigits(document.getElementById('cnpj').value);
  if (cnpjDigits.length !== 14) {
    setError('cnpj', 'CNPJ deve ter 14 dígitos.');
    valid = false;
  } else {
    clearError('cnpj');
  }

  const cpfDigits = onlyDigits(document.getElementById('representante_cpf').value);
  if (cpfDigits.length !== 11) {
    setError('representante_cpf', 'CPF deve ter 11 dígitos.');
    valid = false;
  } else {
    clearError('representante_cpf');
  }

  const emailValue = document.getElementById('email').value.trim();
  if (!validateEmail(emailValue)) {
    setError('email', 'Informe um e-mail válido.');
    valid = false;
  } else {
    clearError('email');
  }

  const telDigits = onlyDigits(document.getElementById('telefones').value);
  if (telDigits.length < 10) {
    setError('telefones', 'Informe ao menos um telefone com DDD.');
    valid = false;
  } else {
    clearError('telefones');
  }

  // Cada linha de CNAE preenchida precisa ter número e descrição; ao menos uma linha.
  const cnaes = coletarCnaes();
  if (cnaes.some((cnae) => !cnae.numero || !cnae.descricao)) {
    setError('cnaes', 'Preencha o número e a descrição de cada CNAE informado.');
    valid = false;
  } else if (cnaes.length === 0) {
    setError('cnaes', 'Informe ao menos um CNAE.');
    valid = false;
  } else {
    clearError('cnaes');
  }

  if (typeof grecaptcha !== 'undefined' && !grecaptcha.getResponse()) {
    setError('recaptcha', 'Confirme que você não é um robô.');
    valid = false;
  } else {
    clearError('recaptcha');
  }

  return valid;
}

function showFeedback(html, type) {
  feedbackEl.innerHTML = html;
  feedbackEl.className = `feedback feedback--${type}`;
  feedbackEl.hidden = false;
  feedbackEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideFeedback() {
  feedbackEl.hidden = true;
  feedbackEl.innerHTML = '';
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? 'Gerando documento…' : 'Gerar documento PDF';
}

function extrairMensagemErro(payload) {
  if (!payload) return 'Não foi possível processar o cadastro. Tente novamente.';
  if (typeof payload.detail === 'string') return payload.detail;
  if (Array.isArray(payload.detail)) {
    return payload.detail.map((erro) => erro.msg || 'Campo inválido.').join(' ');
  }
  return 'Não foi possível processar o cadastro. Tente novamente.';
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  hideFeedback();

  if (!validateForm()) {
    return;
  }

  const payload = {
    municipio_interesse: document.getElementById('municipio_interesse').value.trim(),
    metragem_necessaria: document.getElementById('metragem_necessaria').value.trim(),
    nome_empresarial: document.getElementById('nome_empresarial').value.trim(),
    cnpj: document.getElementById('cnpj').value,
    endereco_correspondencia_empresa: document.getElementById('endereco_correspondencia_empresa').value.trim(),
    representante_nome: document.getElementById('representante_nome').value.trim(),
    representante_cpf: document.getElementById('representante_cpf').value,
    representante_rg: document.getElementById('representante_rg').value.trim(),
    representante_nome_mae: document.getElementById('representante_nome_mae').value.trim(),
    email: document.getElementById('email').value.trim(),
    telefones: document.getElementById('telefones').value.trim(),
    representante_endereco_correspondencia: document.getElementById('representante_endereco_correspondencia').value.trim(),
    cnaes: coletarCnaes(),
    documentos: Array.from(document.querySelectorAll('input[name="documentos"]:checked')).map((el) => el.value),
    g_recaptcha_response: typeof grecaptcha !== 'undefined' ? grecaptcha.getResponse() : '',
  };

  setLoading(true);

  try {
    const response = await fetch(`${API_BASE_URL}/api/cadastro/anexo-iii`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      showFeedback(
        `<p class="feedback__title">Não foi possível gerar o documento</p><p>${extrairMensagemErro(data)}</p>`,
        'error'
      );
      return;
    }

    const protocolo = data.processo.protocolo;
    const pdfUrl = `${API_BASE_URL}${data.pdf_download_url}`;

    showFeedback(
      `<p class="feedback__title">Documento gerado com sucesso</p>
       <p>Baixe o PDF, assine (digitalmente ou impresso) e prossiga para a etapa de reenvio do documento assinado.</p>
       <p class="feedback__protocolo">Protocolo: ${protocolo}</p>
       <div class="feedback__actions">
         <a class="feedback__link" href="${pdfUrl}" target="_blank" rel="noopener">Baixar documento PDF</a>
         <a class="feedback__link feedback__link--secondary" href="upload-assinado.html?protocolo=${encodeURIComponent(protocolo)}">Já assinei, enviar documento →</a>
       </div>`,
      'success'
    );

    form.reset();
  } catch (error) {
    showFeedback(
      `<p class="feedback__title">Falha de conexão</p><p>Não foi possível falar com o servidor. Verifique se a API está em execução e tente novamente.</p>`,
      'error'
    );
  } finally {
    setLoading(false);
    if (typeof grecaptcha !== 'undefined') {
      grecaptcha.reset();
    }
  }
});
