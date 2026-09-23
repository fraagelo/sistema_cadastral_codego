const API_BASE_URL = window.CODEGO_API_BASE_URL || 'http://localhost:8000';

const form = document.getElementById('form-anexo-vii-mce');
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
document.getElementById('telefone').addEventListener('input', (e) => {
  e.target.value = maskTelefone(onlyDigits(e.target.value));
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

configurarBuscaCep('cep', 'cep-status', 'endereco', 'endereco');

// Campos que só se aplicam quando a resposta Sim/Não correspondente é "Sim"
// (ex.: previsão de funcionamento, data da última revisão do PCA).
function atualizarCamposCondicionais() {
  document.querySelectorAll('[data-mostrar-se]').forEach((wrapper) => {
    const controle = document.getElementById(wrapper.dataset.mostrarSe);
    const mostrar = controle.value === 'Sim';
    wrapper.hidden = !mostrar;
    if (!mostrar) {
      wrapper.querySelectorAll('input, textarea').forEach((el) => { el.value = ''; });
    }
  });
}

document.querySelectorAll('select[data-tipo="simnao"]').forEach((select) => {
  select.addEventListener('change', atualizarCamposCondicionais);
});

// Total da mão de obra = soma dos setores (o backend recalcula ao gerar o PDF).
const camposMaoDeObra = Array.from(document.querySelectorAll('input[data-tipo="int"]'));
function atualizarTotalMaoDeObra() {
  const total = camposMaoDeObra.reduce((soma, el) => soma + (parseInt(el.value, 10) || 0), 0);
  document.getElementById('mao_obra_total').value = total;
}
camposMaoDeObra.forEach((el) => el.addEventListener('input', atualizarTotalMaoDeObra));

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
  ['razao_social', 'Informe o campo "Razão Social".'],
  ['inscricao_estadual', 'Informe o campo "Inscrição Estadual".'],
  ['endereco', 'Informe o campo "Endereço Completo".'],
  ['responsavel_nome', 'Informe o campo "Nome do Responsável".'],
  ['responsavel_cargo', 'Informe o campo "Cargo do Responsável".'],
  ['cnae_principal', 'Informe o campo "CNAE Principal".'],
  ['atividade_principal', 'Informe o campo "Descrição da Atividade Principal".'],
  ['area_total_terreno', 'Informe o campo "Área Total do Terreno (m²)".'],
  ['local_cidade_uf', 'Informe o campo "Local (Cidade e Estado)".'],
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

  const emailValue = document.getElementById('email').value.trim();
  if (!validateEmail(emailValue)) {
    setError('email', 'Informe um e-mail válido.');
    valid = false;
  } else {
    clearError('email');
  }

  const cepDigits = onlyDigits(document.getElementById('cep').value);
  if (cepDigits.length !== 8) {
    setError('cep', 'CEP deve ter 8 dígitos.');
    valid = false;
  } else {
    clearError('cep');
  }

  const telDigits = onlyDigits(document.getElementById('telefone').value);
  if (telDigits.length < 10) {
    setError('telefone', 'Informe um telefone válido, com DDD.');
    valid = false;
  } else {
    clearError('telefone');
  }

  document.querySelectorAll('select[data-tipo="simnao"]').forEach((select) => {
    if (!select.value) {
      setError(select.id, 'Selecione Sim ou Não.');
      valid = false;
    } else {
      clearError(select.id);
    }
  });

  camposMaoDeObra.forEach((el) => {
    if (el.value !== '' && (!/^\d+$/.test(el.value))) {
      setError(el.id, 'Informe um número inteiro (0 ou mais).');
      valid = false;
    } else {
      clearError(el.id);
    }
  });

  const ruido = document.getElementById('monitoramento_ruido').value;
  const ruidoDescricao = document.getElementById('monitoramento_ruido_descricao').value.trim();
  if (ruido === 'Sim' && !ruidoDescricao) {
    setError('monitoramento_ruido_descricao', 'Enumere os equipamentos, horários de operação e estratégias de controle de ruído.');
    valid = false;
  } else {
    clearError('monitoramento_ruido_descricao');
  }

  // Leva o usuário ao primeiro campo com erro (o formulário é longo).
  if (!valid) {
    document.querySelector('.field--invalid, .field__error:not(:empty)')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
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

  // Todos os campos com "name" vão no payload; os de mão de obra como número.
  const payload = {};
  // (o textarea "g-recaptcha-response" injetado pelo Google é ignorado aqui).
  Array.from(form.elements).forEach((el) => {
    if (!el.name || el.name === 'g-recaptcha-response') return;
    if (el.dataset.tipo === 'int') {
      payload[el.name] = parseInt(el.value, 10) || 0;
    } else {
      payload[el.name] = el.value.trim();
    }
  });
  payload.g_recaptcha_response = typeof grecaptcha !== 'undefined' ? grecaptcha.getResponse() : '';

  setLoading(true);

  try {
    const response = await fetch(`${API_BASE_URL}/api/cadastro/anexo-vii-mce`, {
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
    atualizarCamposCondicionais();
    atualizarTotalMaoDeObra();
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
