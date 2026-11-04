'use client';

import type { ReactNode } from 'react';
import { useEffect, useMemo, useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  obterMeuPerfil,
  atualizarMeuPerfil,
  enviarFotoPerfil,
  listarSetores,
  ApiError,
  type Usuario,
  type Setor,
} from '@/lib/api';

const perfilSchema = z.object({
  nome_completo: z
    .string()
    .trim()
    .min(3, 'Informe pelo menos 3 caracteres.')
    .refine((valor) => valor.split(/\s+/).length >= 2, 'Informe nome e sobrenome.'),
  setor_id: z.string().min(1, 'Selecione um setor.'),
  email: z.string().trim().email('Informe um e-mail válido.').or(z.literal('')),
});

type PerfilFormData = z.infer<typeof perfilSchema>;

const senhaSchema = z.object({
  senha_atual: z.string().min(1, 'Informe sua senha atual.'),
  nova_senha: z
    .string()
    .min(8, 'Use pelo menos 8 caracteres.')
    .refine((valor) => /[A-Za-z]/.test(valor), 'Inclua pelo menos uma letra.')
    .refine((valor) => /[0-9]/.test(valor), 'Inclua pelo menos um número.'),
  confirmar_senha: z.string().min(1, 'Confirme a nova senha.'),
}).refine((dados) => dados.nova_senha === dados.confirmar_senha, {
  message: 'As senhas não coincidem.',
  path: ['confirmar_senha'],
});

type SenhaFormData = z.infer<typeof senhaSchema>;
type Aviso = { tipo: 'sucesso' | 'erro'; texto: string };

function IconePerfil({ nome, tamanho = 19 }: { nome: 'user' | 'shield' | 'mail' | 'building' | 'edit' | 'lock' | 'check' | 'key' | 'refresh'; tamanho?: number }) {
  const props = {
    width: tamanho,
    height: tamanho,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    'aria-hidden': true as const,
  };
  const paths: Record<typeof nome, ReactNode> = {
    user: <><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></>,
    shield: <><path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z" /><path d="m9 12 2 2 4-4" /></>,
    mail: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" /></>,
    building: <><rect x="4" y="3" width="16" height="18" rx="2" /><path d="M9 21v-4h6v4M8 7h1m6 0h1M8 11h1m6 0h1" /></>,
    edit: <><path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z" /></>,
    lock: <><rect x="4" y="10" width="16" height="11" rx="2" /><path d="M8 10V7a4 4 0 1 1 8 0v3M12 14v3" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    key: <><circle cx="8" cy="15" r="5" /><path d="m11.5 11.5 8-8L22 6l-2 2 2 2-3 3-2-2-2 2" /></>,
    refresh: <><path d="M20 7v5h-5" /><path d="M4 17v-5h5" /><path d="M5.6 9A7 7 0 0 1 17.5 6L20 12M4 12l2.5 6a7 7 0 0 0 11.9-3" /></>,
  };
  return <svg {...props}>{paths[nome]}</svg>;
}

function iniciais(nome: string) {
  const partes = nome.trim().split(/\s+/).filter(Boolean);
  if (partes.length === 0) return 'U';
  return partes.length === 1
    ? partes[0].slice(0, 2).toUpperCase()
    : `${partes[0][0]}${partes[partes.length - 1][0]}`.toUpperCase();
}

export default function MeuPerfil({ onUsuarioAtualizado }: { onUsuarioAtualizado?: (usuario: Usuario) => void }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [setores, setSetores] = useState<Setor[]>([]);
  const [estadoSetores, setEstadoSetores] = useState<'carregando' | 'pronto' | 'erro'>('carregando');
  const [carregando, setCarregando] = useState(true);
  const [erroCarregamento, setErroCarregamento] = useState<string | null>(null);
  const [tentativa, setTentativa] = useState(0);
  const [tentativaSetores, setTentativaSetores] = useState(0);
  const [editandoPerfil, setEditandoPerfil] = useState(false);
  const [alterandoSenha, setAlterandoSenha] = useState(false);
  const [avisoPerfil, setAvisoPerfil] = useState<Aviso | null>(null);
  const [avisoSenha, setAvisoSenha] = useState<Aviso | null>(null);
  const [enviandoFoto, setEnviandoFoto] = useState(false);
  const [fotoSelecionada, setFotoSelecionada] = useState<string | null>(null);
  const [arquivoFoto, setArquivoFoto] = useState<File | null>(null);
  const [zoomFoto, setZoomFoto] = useState(1);
  const [posicaoXFoto, setPosicaoXFoto] = useState(50);
  const [posicaoYFoto, setPosicaoYFoto] = useState(50);
  const [arrastandoFoto, setArrastandoFoto] = useState(false);
  const areaCorteRef = useRef<HTMLDivElement>(null);
  const arrastoRef = useRef<{ x: number; y: number; px: number; py: number } | null>(null);

  const setoresPorId = useMemo(() => new Map(setores.map((setor) => [Number(setor.id), setor.nome])), [setores]);
  const nomeExibicao = usuario?.nome_completo?.trim() || usuario?.username || 'Usuário';
  const setorAtual = usuario?.setor_id ? setoresPorId.get(Number(usuario.setor_id)) || 'Setor não identificado' : 'Setor não definido';

  const {
    register: registrarPerfil,
    handleSubmit: enviarPerfil,
    reset: resetPerfil,
    formState: { errors: errosPerfil, isSubmitting: salvandoPerfil },
  } = useForm<PerfilFormData>({
    resolver: zodResolver(perfilSchema),
    defaultValues: { nome_completo: '', setor_id: '', email: '' },
  });

  const {
    register: registrarSenha,
    handleSubmit: enviarSenha,
    reset: resetSenha,
    formState: { errors: errosSenha, isSubmitting: salvandoSenha },
  } = useForm<SenhaFormData>({
    resolver: zodResolver(senhaSchema),
    defaultValues: { senha_atual: '', nova_senha: '', confirmar_senha: '' },
  });

  useEffect(() => {
    let ativo = true;
    async function carregar() {
      setCarregando(true);
      setErroCarregamento(null);
      try {
        const dados = await obterMeuPerfil();
        if (!ativo) return;
        setUsuario(dados);
        onUsuarioAtualizado?.(dados);
        resetPerfil({
          nome_completo: dados.nome_completo || '',
          setor_id: dados.setor_id !== null ? String(dados.setor_id) : '',
          email: dados.email || '',
        });
      } catch (erro) {
        if (!ativo) return;
        setErroCarregamento(erro instanceof ApiError ? erro.message : 'Não foi possível carregar seu perfil. Verifique a conexão e tente novamente.');
      } finally {
        if (ativo) setCarregando(false);
      }
    }
    void carregar();
    return () => { ativo = false; };
  }, [tentativa, resetPerfil, onUsuarioAtualizado]);

  useEffect(() => {
    let ativo = true;
    setEstadoSetores('carregando');
    listarSetores()
      .then((lista) => {
        if (!ativo) return;
        setSetores(lista);
        setEstadoSetores('pronto');
      })
      .catch(() => {
        if (!ativo) return;
        setSetores([]);
        setEstadoSetores('erro');
      });
    return () => { ativo = false; };
  }, [tentativaSetores]);

  async function salvarPerfil(dados: PerfilFormData) {
    setAvisoPerfil(null);
    setAvisoSenha(null);
    try {
      const atualizado = await atualizarMeuPerfil({
        nome_completo: dados.nome_completo.trim(),
        // Campo vazio mantém o e-mail existente, como orientado na interface.
        email: dados.email.trim() || usuario?.email || null,
        setor_id: Number(dados.setor_id),
      });
      setUsuario(atualizado);
      onUsuarioAtualizado?.(atualizado);
      resetPerfil({
        nome_completo: atualizado.nome_completo || '',
        setor_id: atualizado.setor_id !== null ? String(atualizado.setor_id) : '',
        email: atualizado.email || '',
      });
      setEditandoPerfil(false);
      setAvisoPerfil({ tipo: 'sucesso', texto: 'Suas informações foram atualizadas.' });
    } catch (erro) {
      setAvisoPerfil({ tipo: 'erro', texto: erro instanceof ApiError ? erro.message : 'Não foi possível salvar as alterações. Tente novamente.' });
    }
  }

  async function salvarSenha(dados: SenhaFormData) {
    setAvisoSenha(null);
    setAvisoPerfil(null);
    try {
      const atualizado = await atualizarMeuPerfil({ senha_atual: dados.senha_atual, nova_senha: dados.nova_senha });
      setUsuario(atualizado);
      onUsuarioAtualizado?.(atualizado);
      resetSenha({ senha_atual: '', nova_senha: '', confirmar_senha: '' });
      setAlterandoSenha(false);
      setAvisoSenha({ tipo: 'sucesso', texto: 'Senha alterada com sucesso.' });
    } catch (erro) {
      setAvisoSenha({ tipo: 'erro', texto: erro instanceof ApiError ? erro.message : 'Não foi possível alterar a senha. Confira sua senha atual e tente novamente.' });
    }
  }

  function cancelarEdicaoPerfil() {
    if (usuario) {
      resetPerfil({ nome_completo: usuario.nome_completo || '', setor_id: usuario.setor_id !== null ? String(usuario.setor_id) : '', email: usuario.email || '' });
    }
    setEditandoPerfil(false);
    setAvisoPerfil(null);
  }

  function cancelarAlteracaoSenha() {
    resetSenha({ senha_atual: '', nova_senha: '', confirmar_senha: '' });
    setAlterandoSenha(false);
    setAvisoSenha(null);
  }

  function selecionarFoto(arquivo?: File) {
    if (!arquivo) return;
    if (!['image/png', 'image/jpeg', 'image/webp'].includes(arquivo.type)) {
      setAvisoPerfil({ tipo: 'erro', texto: 'Escolha uma imagem PNG, JPEG ou WebP.' });
      return;
    }
    if (arquivo.size > 2 * 1024 * 1024) {
      setAvisoPerfil({ tipo: 'erro', texto: 'A imagem deve ter no máximo 2 MB.' });
      return;
    }
    const leitor = new FileReader();
    leitor.onload = () => {
      if (typeof leitor.result === 'string') {
        setArquivoFoto(arquivo);
        setFotoSelecionada(leitor.result);
        setZoomFoto(1);
        setPosicaoXFoto(50);
        setPosicaoYFoto(50);
        setAvisoPerfil(null);
      }
    };
    leitor.readAsDataURL(arquivo);
  }

  function fecharEditorFoto() {
    setFotoSelecionada(null);
    setArquivoFoto(null);
    setArrastandoFoto(false);
  }

  async function confirmarFoto() {
    if (!fotoSelecionada || !arquivoFoto || !usuario) return;
    setEnviandoFoto(true);
    setAvisoPerfil(null);
    try {
      const imagem = new Image();
      imagem.src = fotoSelecionada;
      await new Promise<void>((resolve, reject) => {
        imagem.onload = () => resolve();
        imagem.onerror = () => reject(new Error('Não foi possível ler a imagem selecionada.'));
      });
      const tamanho = 640;
      const canvas = document.createElement('canvas');
      canvas.width = tamanho;
      canvas.height = tamanho;
      const contexto = canvas.getContext('2d');
      if (!contexto) throw new Error('Não foi possível preparar o recorte da foto.');
      const escalaBase = Math.max(tamanho / imagem.naturalWidth, tamanho / imagem.naturalHeight);
      const escala = escalaBase * zoomFoto;
      const largura = imagem.naturalWidth * escala;
      const altura = imagem.naturalHeight * escala;
      const excessoX = Math.max(0, largura - tamanho);
      const excessoY = Math.max(0, altura - tamanho);
      const deslocamentoX = (posicaoXFoto / 100) * excessoX;
      const deslocamentoY = (posicaoYFoto / 100) * excessoY;
      contexto.drawImage(imagem, -deslocamentoX, -deslocamentoY, largura, altura);
      const blob = await new Promise<Blob>((resolve, reject) => canvas.toBlob((resultado) => resultado ? resolve(resultado) : reject(new Error('Falha ao gerar o recorte.')), 'image/jpeg', 0.9));
      const fotoFinal = new File([blob], 'foto-perfil.jpg', { type: 'image/jpeg' });
      const resposta = await enviarFotoPerfil(fotoFinal);
      const atualizado = { ...usuario, foto_perfil: resposta.foto_perfil };
      setUsuario(atualizado);
      setAvisoPerfil({ tipo: 'sucesso', texto: 'Foto de perfil atualizada.' });
      onUsuarioAtualizado?.(atualizado);
      fecharEditorFoto();
    } catch (e) {
      setAvisoPerfil({ tipo: 'erro', texto: e instanceof ApiError ? e.message : (e instanceof Error ? e.message : 'Não foi possível atualizar a foto.') });
    } finally { setEnviandoFoto(false); }
  }

  function iniciarArrastoFoto(evento: React.PointerEvent<HTMLDivElement>) {
    arrastoRef.current = { x: evento.clientX, y: evento.clientY, px: posicaoXFoto, py: posicaoYFoto };
    setArrastandoFoto(true);
    evento.currentTarget.setPointerCapture(evento.pointerId);
  }

  function moverFoto(evento: React.PointerEvent<HTMLDivElement>) {
    if (!arrastandoFoto || !arrastoRef.current || !areaCorteRef.current) return;
    const caixa = areaCorteRef.current.getBoundingClientRect();
    const dx = evento.clientX - arrastoRef.current.x;
    const dy = evento.clientY - arrastoRef.current.y;
    setPosicaoXFoto(Math.max(0, Math.min(100, arrastoRef.current.px - (dx / caixa.width) * 100)));
    setPosicaoYFoto(Math.max(0, Math.min(100, arrastoRef.current.py - (dy / caixa.height) * 100)));
  }

  if (carregando) {
    return <div className="profile-v2-state"><span className="loading-inline" /><strong>Carregando suas informações</strong><p>Estamos consultando os dados da sua conta.</p></div>;
  }

  if (!usuario) {
    return (
      <div className="profile-v2-state profile-v2-state--error" role="alert">
        <span className="profile-v2-state-icon"><IconePerfil nome="user" tamanho={24} /></span>
        <h2>Não foi possível abrir seu perfil</h2>
        <p>{erroCarregamento || 'Verifique sua conexão e tente novamente.'}</p>
        <button type="button" className="button button-primary" onClick={() => setTentativa((valor) => valor + 1)}><IconePerfil nome="refresh" tamanho={16} /> Tentar novamente</button>
      </div>
    );
  }

  return (
    <main className="profile-v2-page">
      <div className="profile-v2-container">
        <div className="profile-v2-heading">
          <div>
            <p className="eyebrow">CONTA E ACESSO</p>
            <h1>Meu perfil</h1>
            <p className="page-subtitle">Gerencie seus dados pessoais e mantenha sua conta segura.</p>
          </div>
          <span className={`profile-v2-role ${usuario.is_admin ? 'is-admin' : ''}`}>
            <IconePerfil nome="shield" tamanho={15} /> {usuario.is_admin ? 'Administrador' : 'Colaborador'}
          </span>
        </div>

        <section className="profile-v2-hero" aria-label="Resumo da conta">
          <div className="profile-v2-avatar-wrap">
            <div className="profile-v2-avatar">{usuario.foto_perfil ? <img src={usuario.foto_perfil} alt="Foto de perfil" /> : iniciais(nomeExibicao)}</div>
            <label title="Alterar foto de perfil" className="profile-v2-avatar-edit"><span aria-hidden="true">✎</span><input type="file" accept="image/png,image/jpeg,image/webp" className="sr-only" disabled={enviandoFoto} onChange={e => { selecionarFoto(e.target.files?.[0]); e.currentTarget.value = ''; }} /></label>
          </div>
          <div className="profile-v2-hero-copy">
            <span className="profile-v2-overline">PERFIL DO USUÁRIO</span>
            <h2>{nomeExibicao}</h2>
            <p className="profile-v2-username">@{usuario.username}</p><p className="mt-1 text-xs text-slate-500">{enviandoFoto ? 'Enviando foto…' : 'Clique no ícone da foto para alterar (PNG, JPEG ou WebP, até 2 MB).'}</p>
            <div className="profile-v2-meta">
              <span><IconePerfil nome="mail" tamanho={15} /> {usuario.email || 'E-mail não informado'}</span>
              <span><IconePerfil nome="building" tamanho={15} /> {setorAtual}</span>
            </div>
          </div>
          <div className="profile-v2-hero-status"><span className="profile-v2-status-dot" /> Conta autenticada</div>
          <div className="profile-v2-hero-decoration" aria-hidden="true"><span /><span /><span /></div>
        </section>

        {avisoPerfil && <div className={`profile-v2-alert ${avisoPerfil.tipo === 'sucesso' ? 'is-success' : 'is-error'}`} role={avisoPerfil.tipo === 'erro' ? 'alert' : 'status'}>{avisoPerfil.tipo === 'sucesso' && <IconePerfil nome="check" tamanho={17} />}{avisoPerfil.texto}</div>}

        <div className="profile-v2-grid">
          <section className="profile-v2-card">
            <div className="profile-v2-card-heading">
              <span className="profile-v2-card-icon"><IconePerfil nome="user" /></span>
              <div className="profile-v2-card-title"><h2>Informações pessoais</h2><p>Dados utilizados para identificar você no sistema.</p></div>
              {!editandoPerfil && <button type="button" className="button button-secondary profile-v2-edit-button" onClick={() => { setEditandoPerfil(true); setAvisoPerfil(null); }}><IconePerfil nome="edit" tamanho={15} /> Editar perfil</button>}
            </div>

            {editandoPerfil ? (
              <form className="profile-v2-form" onSubmit={enviarPerfil(salvarPerfil)} noValidate>
                <div className="profile-v2-field">
                  <label htmlFor="profile-full-name">Nome completo <span aria-hidden="true">*</span></label>
                  <input id="profile-full-name" autoComplete="name" {...registrarPerfil('nome_completo')} aria-invalid={Boolean(errosPerfil.nome_completo)} aria-describedby={errosPerfil.nome_completo ? 'profile-name-error' : undefined} />
                  {errosPerfil.nome_completo && <p className="profile-v2-field-error" id="profile-name-error">{errosPerfil.nome_completo.message}</p>}
                </div>
                <div className="profile-v2-field">
                  <label htmlFor="profile-username">Nome de usuário</label>
                  <input id="profile-username" value={usuario.username} readOnly aria-readonly="true" />
                  <small>O nome de usuário não pode ser alterado por esta tela.</small>
                </div>
                <div className="profile-v2-field">
                  <label htmlFor="profile-email">E-mail</label>
                  <input id="profile-email" type="email" autoComplete="email" placeholder="nome@empresa.com" {...registrarPerfil('email')} aria-invalid={Boolean(errosPerfil.email)} aria-describedby={errosPerfil.email ? 'profile-email-error' : 'profile-email-help'} />
                  <small id="profile-email-help">Deixe em branco para manter o e-mail atual.</small>
                  {errosPerfil.email && <p className="profile-v2-field-error" id="profile-email-error">{errosPerfil.email.message}</p>}
                </div>
                <div className="profile-v2-field">
                  <label htmlFor="profile-sector">Setor <span aria-hidden="true">*</span></label>
                  <select id="profile-sector" {...registrarPerfil('setor_id')} disabled={estadoSetores !== 'pronto' || setores.length === 0} aria-invalid={Boolean(errosPerfil.setor_id)} aria-describedby={errosPerfil.setor_id ? 'profile-sector-error' : undefined}>
                    <option value="">{estadoSetores === 'carregando' ? 'Carregando setores…' : estadoSetores === 'erro' ? 'Setores indisponíveis' : 'Selecione um setor'}</option>
                    {setores.map((setor) => <option key={setor.id} value={String(setor.id)}>{setor.nome}</option>)}
                  </select>
                  {errosPerfil.setor_id && <p className="profile-v2-field-error" id="profile-sector-error">{errosPerfil.setor_id.message}</p>}
                  {estadoSetores === 'erro' && <button type="button" className="profile-v2-inline-action" onClick={() => setTentativaSetores((valor) => valor + 1)}>Tentar carregar setores novamente</button>}
                </div>
                <div className="profile-v2-form-actions">
                  <span className="profile-v2-required-note">* Campo obrigatório</span>
                  <div>
                    <button type="button" className="button button-secondary" onClick={cancelarEdicaoPerfil} disabled={salvandoPerfil}>Cancelar</button>
                    <button type="submit" className="button button-primary" disabled={salvandoPerfil || (!usuario.setor_id && (estadoSetores !== 'pronto' || setores.length === 0))}>{salvandoPerfil ? <><span className="loading-inline loading-inline--light" /> Salvando…</> : 'Salvar alterações'}</button>
                  </div>
                </div>
              </form>
            ) : (
              <div className="profile-v2-data-grid">
                <div className="profile-v2-data-field"><span>Nome completo</span><strong>{usuario.nome_completo || 'Não informado'}</strong></div>
                <div className="profile-v2-data-field"><span>Nome de usuário</span><strong>{usuario.username}</strong></div>
                <div className="profile-v2-data-field"><span>E-mail</span><strong>{usuario.email || 'Não informado'}</strong></div>
                <div className="profile-v2-data-field"><span>Setor</span><strong>{setorAtual}</strong></div>
              </div>
            )}
          </section>

          <section className="profile-v2-card profile-v2-security-card">
            <div className="profile-v2-card-heading">
              <span className="profile-v2-card-icon profile-v2-card-icon--security"><IconePerfil nome="shield" /></span>
              <div className="profile-v2-card-title"><h2>Segurança da conta</h2><p>Controle o acesso à sua conta.</p></div>
              {!alterandoSenha && <span className="profile-v2-security-badge"><IconePerfil nome="lock" tamanho={14} /> Protegida</span>}
            </div>

            {!alterandoSenha ? (
              <div className="profile-v2-security-content">
                <div className="profile-v2-security-illustration"><IconePerfil nome="key" tamanho={23} /></div>
                <div className="profile-v2-security-copy"><strong>Senha de acesso</strong><p>Atualize sua senha periodicamente e não compartilhe suas credenciais.</p></div>
                <button type="button" className="button button-secondary" onClick={() => { setAlterandoSenha(true); setAvisoSenha(null); }}>Alterar senha</button>
              </div>
            ) : (
              <form className="profile-v2-password-form" onSubmit={enviarSenha(salvarSenha)} noValidate>
                <div className="profile-v2-field">
                  <label htmlFor="profile-current-password">Senha atual <span aria-hidden="true">*</span></label>
                  <input id="profile-current-password" type="password" autoComplete="current-password" {...registrarSenha('senha_atual')} aria-invalid={Boolean(errosSenha.senha_atual)} />
                  {errosSenha.senha_atual && <p className="profile-v2-field-error">{errosSenha.senha_atual.message}</p>}
                </div>
                <div className="profile-v2-field">
                  <label htmlFor="profile-new-password">Nova senha <span aria-hidden="true">*</span></label>
                  <input id="profile-new-password" type="password" autoComplete="new-password" {...registrarSenha('nova_senha')} aria-invalid={Boolean(errosSenha.nova_senha)} />
                  <small>Mínimo de 8 caracteres, com letras e números.</small>
                  {errosSenha.nova_senha && <p className="profile-v2-field-error">{errosSenha.nova_senha.message}</p>}
                </div>
                <div className="profile-v2-field">
                  <label htmlFor="profile-confirm-password">Confirmar nova senha <span aria-hidden="true">*</span></label>
                  <input id="profile-confirm-password" type="password" autoComplete="new-password" {...registrarSenha('confirmar_senha')} aria-invalid={Boolean(errosSenha.confirmar_senha)} />
                  {errosSenha.confirmar_senha && <p className="profile-v2-field-error">{errosSenha.confirmar_senha.message}</p>}
                </div>
                <div className="profile-v2-form-actions profile-v2-form-actions--security">
                  <span className="profile-v2-required-note">Nunca reutilize senhas compartilhadas.</span>
                  <div>
                    <button type="button" className="button button-secondary" onClick={cancelarAlteracaoSenha} disabled={salvandoSenha}>Cancelar</button>
                    <button type="submit" className="button button-primary" disabled={salvandoSenha}>{salvandoSenha ? <><span className="loading-inline loading-inline--light" /> Atualizando…</> : 'Atualizar senha'}</button>
                  </div>
                </div>
              </form>
            )}
            {avisoSenha && <div className={`profile-v2-alert profile-v2-alert--inside ${avisoSenha.tipo === 'sucesso' ? 'is-success' : 'is-error'}`} role={avisoSenha.tipo === 'erro' ? 'alert' : 'status'}>{avisoSenha.tipo === 'sucesso' && <IconePerfil nome="check" tamanho={16} />}{avisoSenha.texto}</div>}
          </section>
        </div>
        {fotoSelecionada && (
          <div className="profile-photo-modal-backdrop" role="presentation" onMouseDown={(e) => { if (e.target === e.currentTarget && !enviandoFoto) fecharEditorFoto(); }}>
            <section className="profile-photo-modal" role="dialog" aria-modal="true" aria-labelledby="profile-photo-title">
              <div className="profile-photo-modal-heading"><div><span className="profile-v2-overline">PERSONALIZE SUA CONTA</span><h2 id="profile-photo-title">Ajustar foto de perfil</h2><p>Arraste a imagem para escolher o enquadramento e ajuste o zoom.</p></div><button type="button" className="profile-photo-close" onClick={fecharEditorFoto} disabled={enviandoFoto} aria-label="Cancelar">×</button></div>
              <div className="profile-photo-workspace">
                <div className="profile-photo-crop" ref={areaCorteRef} onPointerDown={iniciarArrastoFoto} onPointerMove={moverFoto} onPointerUp={() => setArrastandoFoto(false)} onPointerCancel={() => setArrastandoFoto(false)} style={{ touchAction: 'none', cursor: arrastandoFoto ? 'grabbing' : 'grab' }}>
                  <img src={fotoSelecionada} alt="Prévia da foto com enquadramento ajustável" draggable={false} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoomFoto})`, transformOrigin: `${posicaoXFoto}% ${posicaoYFoto}%`, pointerEvents: 'none' }} />
                  <span className="profile-photo-crop-guide" aria-hidden="true" />
                </div>
                <div className="profile-photo-controls"><label htmlFor="profile-photo-zoom">Zoom <strong>{zoomFoto.toFixed(1)}×</strong></label><input id="profile-photo-zoom" type="range" min="1" max="3" step="0.05" value={zoomFoto} onChange={e => setZoomFoto(Number(e.target.value))} /><div className="profile-photo-control-labels"><span>Enquadrar</span><span>Ampliar</span></div><p>A prévia circular representa como sua foto aparecerá no perfil e nas mensagens.</p></div>
              </div>
              <div className="profile-photo-modal-actions"><button type="button" className="button button-secondary" onClick={fecharEditorFoto} disabled={enviandoFoto}>Cancelar</button><button type="button" className="button button-primary" onClick={() => void confirmarFoto()} disabled={enviandoFoto}>{enviandoFoto ? 'Salvando foto…' : 'Usar esta foto'}</button></div>
            </section>
          </div>
        )}

        <footer className="profile-v2-footer"><span>Avante Almoxarifado</span><span>Suas informações são utilizadas para identificação e controle de acesso ao sistema.</span></footer>
      </div>
    </main>
  );
}
