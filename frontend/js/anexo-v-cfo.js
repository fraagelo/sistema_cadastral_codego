const API_BASE_URL = window.CODEGO_API_BASE_URL || 'http://localhost:8000';

const form = document.getElementById('form-anexo-v-cfo');
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

configurarBuscaCep('cep_busca', 'cep_busca-status', 'endereco', 'endereco');

// ---------------------------------------------------------------------------
// Cronograma: serviços (linhas) x meses da obra (colunas).
// O estado fica em memória; a tabela só é redesenhada quando a estrutura muda
// (período alterado, serviço adicionado/removido), para não perder o foco
// enquanto o usuário digita.
// ---------------------------------------------------------------------------

// Mesma lista de serviços do modelo oficial do cronograma.
const SERVICOS_SUGERIDOS = [
  'Serviços preliminares',
  'Infraestrutura',
  'Paredes e Painéis',
  'Cobertura',
  'Pavimentação',
];
const MAX_MESES = 60;
const MESES_ABREV = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];

const cronogramaEl = document.getElementById('cronograma');
const inicioInput = document.getElementById('inicio_obras');
const terminoInput = document.getElementById('termino_obras');

let servicos = SERVICOS_SUGERIDOS.map((descricao) => ({ descricao, percentuais: [] }));

// Quantidade de meses entre início e término (inclusive). 0 se o período ainda
// não foi informado ou é inválido.
function totalMeses() {
  if (!inicioInput.value || !terminoInput.value) return 0;
  const [anoI, mesI] = inicioInput.value.split('-').map(Number);
  const [anoT, mesT] = terminoInput.value.split('-').map(Number);
  const meses = (anoT - anoI) * 12 + (mesT - mesI) + 1;
  return meses >= 1 && meses <= MAX_MESES ? meses : 0;
}

function referenciaMes(indice) {
  const [ano, mes] = inicioInput.value.split('-').map(Number);
  const posicao = mes - 1 + indice;
  const anoRef = ano + Math.floor(posicao / 12);
  return `${MESES_ABREV[posicao % 12]}/${String(anoRef).slice(2)}`;
}

function somaPercentuais(servico) {
  return servico.percentuais.reduce((total, valor) => total + (Number(valor) || 0), 0);
}

function atualizarTotal(indiceServico) {
  const celula = cronogramaEl.querySelector(`[data-total="${indiceServico}"]`);
  if (!celula) return;
  const soma = somaPercentuais(servicos[indiceServico]);
  celula.textContent = `${Number(soma.toFixed(2)).toLocaleString('pt-BR')}%`;
  celula.className = `cronograma__total ${Math.abs(soma - 100) <= 0.01 ? 'cronograma__total--ok' : 'cronograma__total--erro'}`;
}

function escapeHtml(texto) {
  return texto.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
}

function renderCronograma() {
  const meses = totalMeses();

  // Ajusta a quantidade de meses de cada serviço, preservando o que já foi digitado.
  servicos.forEach((servico) => {
    servico.percentuais = Array.from({ length: meses }, (_, i) => servico.percentuais[i] ?? '');
  });

  if (meses === 0) {
    cronogramaEl.innerHTML = '<p class="cronograma__vazio">Informe a previsão de início e de término das obras para montar o cronograma.</p>';
    return;
  }

  let trimestres = '';
  for (let inicio = 0; inicio < meses; inicio += 3) {
    const colunas = Math.min(3, meses - inicio);
    trimestres += `<th colspan="${colunas}">${inicio / 3 + 1}º Trimestre</th>`;
  }

  let cabecalhoMeses = '';
  for (let i = 0; i < meses; i += 1) {
    cabecalhoMeses += `<th>${i + 1}º mês<small>${referenciaMes(i)}</small></th>`;
  }

  const linhas = servicos.map((servico, s) => {
    const celulas = servico.percentuais.map((valor, m) => `
      <td><input type="number" min="0" max="100" step="any" inputmode="decimal"
        data-servico="${s}" data-mes="${m}" value="${valor}" aria-label="${escapeHtml(servico.descricao || 'Serviço')} — ${m + 1}º mês (%)"></td>`).join('');
    return `
      <tr>
        <td class="cronograma__servico">
          <input type="text" data-descricao="${s}" value="${escapeHtml(servico.descricao)}" placeholder="Descrição do serviço" aria-label="Serviço ${s + 1}">
        </td>
        ${celulas}
        <td class="cronograma__total" data-total="${s}"></td>
        <td><button type="button" class="btn-remover" data-remover="${s}" aria-label="Remover serviço" title="Remover serviço">&times;</button></td>
      </tr>`;
  }).join('');

  cronogramaEl.innerHTML = `
    <table>
      <thead>
        <tr><th class="cronograma__servico"></th>${trimestres}<th></th><th></th></tr>
        <tr><th class="cronograma__servico">Serviços / Mês</th>${cabecalhoMeses}<th>Total</th><th></th></tr>
      </thead>
      <tbody>${linhas}</tbody>
    </table>`;

  servicos.forEach((_, s) => atualizarTotal(s));
}

cronogramaEl.addEventListener('input', (e) => {
  const { servico, mes, descricao } = e.target.dataset;
  if (descricao !== undefined) {
    servicos[Number(descricao)].descricao = e.target.value;
  } else if (servico !== undefined) {
    servicos[Number(servico)].percentuais[Number(mes)] = e.target.value;
    atualizarTotal(Number(servico));
  }
  clearError('servicos');
});

cronogramaEl.addEventListener('click', (e) => {
  const botao = e.target.closest('[data-remover]');
  if (!botao) return;
  servicos.splice(Number(botao.dataset.remover), 1);
  renderCronograma();
});

document.getElementById('btn-adicionar-servico').addEventListener('click', () => {
  servicos.push({ descricao: '', percentuais: [] });
  renderCronograma();
  const novos = cronogramaEl.querySelectorAll('[data-descricao]');
  novos[novos.length - 1]?.focus();
});

inicioInput.addEventListener('change', renderCronograma);
terminoInput.addEventListener('change', renderCronograma);

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
  ['nome_empresa', 'Informe o nome da empresa.'],
  ['endereco', 'Informe o endereço.'],
  ['area_empresa', 'Informe a área da empresa.'],
  ['area_construida', 'Informe a área a ser construída.'],
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

  const inicio = inicioInput.value;
  const termino = terminoInput.value;
  if (!inicio) {
    setError('inicio_obras', 'Informe a previsão de início das obras.');
    valid = false;
  } else {
    clearError('inicio_obras');
  }
  if (!termino) {
    setError('termino_obras', 'Informe a previsão de término das obras.');
    valid = false;
  } else if (inicio && termino < inicio) {
    setError('termino_obras', 'O término deve ser igual ou posterior ao início.');
    valid = false;
  } else if (inicio && totalMeses() === 0) {
    setError('termino_obras', `O cronograma pode ter no máximo ${MAX_MESES} meses.`);
    valid = false;
  } else {
    clearError('termino_obras');
  }

  if (totalMeses() > 0) {
    const semDescricao = servicos.some((servico) => !servico.descricao.trim());
    const foraDe100 = servicos.find((servico) => Math.abs(somaPercentuais(servico) - 100) > 0.01);
    if (servicos.length === 0) {
      setError('servicos', 'Adicione ao menos um serviço ao cronograma.');
      valid = false;
    } else if (semDescricao) {
      setError('servicos', 'Informe a descrição de todos os serviços.');
      valid = false;
    } else if (foraDe100) {
      setError('servicos', `Os percentuais de "${foraDe100.descricao}" devem somar 100%.`);
      valid = false;
    } else {
      clearError('servicos');
    }
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
    nome_empresa: document.getElementById('nome_empresa').value.trim(),
    endereco: document.getElementById('endereco').value.trim(),
    area_empresa: document.getElementById('area_empresa').value.trim(),
    area_construida: document.getElementById('area_construida').value.trim(),
    inicio_obras: inicioInput.value,
    termino_obras: terminoInput.value,
    servicos: servicos.map((servico) => ({
      descricao: servico.descricao.trim(),
      percentuais: servico.percentuais.map((valor) => Number(valor) || 0),
    })),
    g_recaptcha_response: typeof grecaptcha !== 'undefined' ? grecaptcha.getResponse() : '',
  };

  setLoading(true);

  try {
    const response = await fetch(`${API_BASE_URL}/api/cadastro/anexo-v-cfo`, {
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
    servicos = SERVICOS_SUGERIDOS.map((descricao) => ({ descricao, percentuais: [] }));
    renderCronograma();
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
