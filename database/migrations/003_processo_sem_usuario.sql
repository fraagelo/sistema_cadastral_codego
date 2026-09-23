-- Migração: processo sem usuário vinculado
-- Formulários cujo modelo oficial não pede CNPJ/e-mail (ex.: Cronograma
-- Físico da Obra — Anexo V) não geram cadastro em "usuarios".

ALTER TABLE processos_documentos
    MODIFY usuario_id INT NULL;
