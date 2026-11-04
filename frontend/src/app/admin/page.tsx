'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import LeitorQRAlmoxarifado from '@/components/admin/LeitorQRAlmoxarifado';
import GerenciarItens from '@/components/admin/GerenciarItens';
import ImportarNotaFiscal from '@/components/admin/ImportarNotaFiscal';
import ListaEmprestimos from '@/components/admin/ListaEmprestimos';
import CadastroAdminForm from '@/components/admin/CadastroAdminForm';
import GerenciarUsuarios from '@/components/admin/GerenciarUsuarios';
import GerarQRCodes from '@/components/admin/GerarQRCodes';
import HistoricoNotasFiscais from '@/components/admin/HistoricoNotasFiscais';
import CaixaContato from '@/components/admin/CaixaContato';
import {
  listarSetores,
  obterUsuarioAtual,
  listarItensAdmin,
  listarEmprestimosAdmin,
  obterResumoAtrasados,
  listarUsuariosAdmin,
  logout,
  ApiError,
  type Setor,
  type Usuario,
  type Item,
} from '@/lib/api';

type Secao = 'inicio' | 'itens' | 'qr' | 'notas' | 'emprestimos' | 'usuarios' | 'contato';
type Icone = 'grid' | 'box' | 'qr' | 'file' | 'arrows' | 'users' | 'settings' | 'logout' | 'plus' | 'refresh' | 'chevron' | 'alert' | 'search';

function Icon({ nome, size = 19 }: { nome: Icone; size?: number }) {
  const common = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const, 'aria-hidden': true as const };
  const paths: Record<Icone, ReactNode> = {
    grid: <><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></>,
    box: <><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="M3 8v9l9 4 9-4V8M12 13v8"/></>,
    qr: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3h-3zM20 14v2M17 20h4M20 18v3"/></>,
    file: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h8"/></>,
    arrows: <><path d="M7 7h13l-3-3M17 17H4l3 3"/><path d="M20 7v5M4 17v-5"/></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></>,
    settings: <><circle cx="12" cy="12" r="3"/><path d="m19.4 15 .1.1 1.2 1-1.5 2.6-1.5-.5a7.8 7.8 0 0 1-1.7 1l-.3 1.6h-3l-.3-1.6a7.8 7.8 0 0 1-1.7-1l-1.5.5-1.5-2.6 1.2-1a7 7 0 0 1 0-2l-1.2-1 1.5-2.6 1.5.5a7.8 7.8 0 0 1 1.7-1l.3-1.6h3l.3 1.6a7.8 7.8 0 0 1 1.7 1l1.5-.5 1.5 2.6-1.2 1a7 7 0 0 1 0 2Z"/></>,
    logout: <><path d="M10 17l5-5-5-5M15 12H3"/><path d="M12 3h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6"/></>,
    plus: <><path d="M12 5v14M5 12h14"/></>,
    refresh: <><path d="M20 7v5h-5"/><path d="M4 17v-5h5"/><path d="M5.6 9A7 7 0 0 1 17.5 6L20 12M4 12l2.5 6a7 7 0 0 0 11.9-3"/></>,
    chevron: <path d="m9 18 6-6-6-6"/>,
    alert: <><path d="m10.3 3.9-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3.1l-8-14a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/></>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
  };
  return <svg {...common}>{paths[nome]}</svg>;
}

const NAVEGACAO: { id: Secao; label: string; icon: Icone; group?: string }[] = [
  { id: 'inicio', label: 'Visão geral', icon: 'grid', group: 'WORKSPACE' },
  { id: 'itens', label: 'Estoque e itens', icon: 'box' },
  { id: 'qr', label: 'Leitor de QR Code', icon: 'qr', group: 'OPERAÇÕES' },
  { id: 'notas', label: 'Notas fiscais', icon: 'file' },
  { id: 'emprestimos', label: 'Empréstimos', icon: 'arrows' },
  { id: 'usuarios', label: 'Usuários e acessos', icon: 'users', group: 'ADMINISTRAÇÃO' },
  { id: 'contato', label: 'Contato e suporte', icon: 'settings' },
];

function formatarNumero(valor: number) {
  return new Intl.NumberFormat('pt-BR').format(valor);
}

export default function AdminPage() {
  const router = useRouter();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [setores, setSetores] = useState<Setor[]>([]);
  const [secao, setSecao] = useState<Secao>('inicio');
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [refreshItens, setRefreshItens] = useState(0);
  const [refreshEmprestimos, setRefreshEmprestimos] = useState(0);
  const [refreshUsuarios, setRefreshUsuarios] = useState(0);
  const [menuMobile, setMenuMobile] = useState(false);
  const [buscaNav, setBuscaNav] = useState('');
  const [atualizando, setAtualizando] = useState(false);
  const [itensResumoCarregado, setItensResumoCarregado] = useState(false);
  const [erroResumoItens, setErroResumoItens] = useState(false);
  const [itens, setItens] = useState<Item[]>([]);
  const [totalEmprestimos, setTotalEmprestimos] = useState<number | null>(null);
  const [totalAtrasados, setTotalAtrasados] = useState<number | null>(null);
  const [totalUsuarios, setTotalUsuarios] = useState<number | null>(null);

  useEffect(() => {
    let ativo = true;
    async function verificarAcesso() {
      setCarregando(true);
      setErro(null);
      try {
        const usuarioAtual = await obterUsuarioAtual();
        if (!ativo) return;
        if (!usuarioAtual) { router.replace('/login'); return; }
        if (!usuarioAtual.is_admin) { router.replace('/'); return; }
        setUsuario(usuarioAtual);
        const listaSetores = await listarSetores();
        if (ativo) setSetores(listaSetores);
      } catch (e) {
        if (ativo) setErro(e instanceof ApiError ? e.message : 'Não foi possível carregar o painel administrativo. Verifique a conexão com o servidor.');
      } finally {
        if (ativo) setCarregando(false);
      }
    }
    void verificarAcesso();
    return () => { ativo = false; };
  }, [router]);

  const carregarResumo = useCallback(async () => {
    setAtualizando(true);
    const [resItens, resEmprestimos, resAtrasados, resUsuarios] = await Promise.allSettled([
      listarItensAdmin(), listarEmprestimosAdmin(1, 1), obterResumoAtrasados(), listarUsuariosAdmin(),
    ]);
    if (resItens.status === 'fulfilled') { setItens(resItens.value); setErroResumoItens(false); }
    else { setItens([]); setErroResumoItens(true); }
    setItensResumoCarregado(true);
    setTotalEmprestimos(resEmprestimos.status === 'fulfilled' ? resEmprestimos.value.total : null);
    setTotalAtrasados(resAtrasados.status === 'fulfilled' ? resAtrasados.value.total_atrasados : null);
    setTotalUsuarios(resUsuarios.status === 'fulfilled' ? resUsuarios.value.filter((u) => u.ativo).length : null);
    setAtualizando(false);
  }, []);

  useEffect(() => { if (usuario) void carregarResumo(); }, [usuario, carregarResumo, refreshItens, refreshEmprestimos, refreshUsuarios]);

  const estatisticas = useMemo(() => {
    const ativos = itens.filter((item) => item.status === 'ATIVO');
    return {
      tiposAtivos: ativos.length,
      unidades: ativos.reduce((soma, item) => soma + item.quantidade_total, 0),
      disponiveis: ativos.reduce((soma, item) => soma + item.quantidade_disponivel, 0),
      setores: new Set(ativos.map((item) => item.setor_atual_id).filter(Boolean)).size,
    };
  }, [itens]);

  async function sair() {
    try { await logout(); } finally { router.replace('/login'); }
  }

  function mudarSecao(novaSecao: Secao) {
    setSecao(novaSecao);
    setMenuMobile(false);
  }

  const normalizarTexto = (valor: string) => valor.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR');
  const navegacaoFiltrada = NAVEGACAO.filter((item) => normalizarTexto(item.label).includes(normalizarTexto(buscaNav.trim())));
  const titulo = NAVEGACAO.find((item) => item.id === secao)?.label || 'Visão geral';
  const primeiroNome = (usuario?.nome_completo || usuario?.username || 'Administrador').trim().split(/\s+/)[0];

  if (carregando) return <main className="app-loading"><div className="loading-mark"><Icon nome="box" size={28} /></div><p>Preparando seu ambiente de trabalho…</p><span>Avante Almoxarifado</span></main>;
  if (erro) return <main className="app-error"><div className="error-panel"><div className="error-icon"><Icon nome="alert" size={24} /></div><h1>Não foi possível abrir o painel</h1><p>{erro}</p><button className="button button-primary" onClick={() => window.location.reload()}>Tentar novamente</button><Link href="/login" className="text-link">Voltar para o login</Link></div></main>;
  if (!usuario) return null;

  return (
    <main className="admin-shell">
      {menuMobile && <button aria-label="Fechar menu" className="sidebar-scrim" onClick={() => setMenuMobile(false)} />}
      <aside className={`admin-sidebar ${menuMobile ? 'is-open' : ''}`}>
        <div className="brand-lockup"><div className="brand-mark"><Icon nome="box" size={23} /></div><div><strong>AVANTE</strong><span>ALMOXARIFADO</span></div><span className="brand-version">LAB</span></div>
        <div className="sidebar-context"><span className="context-dot" /> Ambiente operacional</div>
        <label className="sidebar-search"><Icon nome="search" size={17} /><input value={buscaNav} onChange={(e) => setBuscaNav(e.target.value)} placeholder="Buscar seção…" aria-label="Buscar seção no menu" />{buscaNav && <button type="button" onClick={() => setBuscaNav('')} aria-label="Limpar busca">×</button>}</label>
        <nav className="sidebar-nav" aria-label="Navegação administrativa">
          {navegacaoFiltrada.length === 0 ? <p className="nav-empty">Nenhuma seção encontrada.</p> : navegacaoFiltrada.map((item) => (
            <div key={item.id}>
              {item.group && !buscaNav.trim() && <p className="nav-group-label">{item.group}</p>}
              <button className={`sidebar-nav-item ${secao === item.id ? 'is-active' : ''}`} onClick={() => mudarSecao(item.id)} aria-current={secao === item.id ? 'page' : undefined}>
                <Icon nome={item.icon} size={18} /><span>{item.label}</span>{secao === item.id && <span className="nav-active-dot" />}
              </button>
            </div>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-support"><div className="support-icon"><Icon nome="settings" size={18} /></div><div><strong>Operação segura</strong><span>Controle de acesso ativo</span></div></div>
          <div className="sidebar-user"><div className="avatar-initials">{primeiroNome.slice(0, 1).toUpperCase()}</div><div className="sidebar-user-text"><strong>{usuario.nome_completo || usuario.username}</strong><span>Administrador</span></div><button className="icon-button sidebar-logout" onClick={() => void sair()} aria-label="Sair da conta" title="Sair"><Icon nome="logout" size={17} /></button></div>
        </div>
      </aside>

      <section className="admin-workspace">
        <header className="workspace-topbar">
          <div className="topbar-heading"><button className="mobile-menu-button" onClick={() => setMenuMobile(true)} aria-label="Abrir menu"><span /><span /><span /></button><div><div className="breadcrumb"><span>Avante</span><Icon nome="chevron" size={13} /><strong>{titulo}</strong></div><p>Gestão do laboratório e controle patrimonial</p></div></div>
          <div className="topbar-actions"><span className="system-status"><span className={`status-dot ${atualizando ? 'is-syncing' : erroResumoItens ? 'is-warning' : ''}`} />{atualizando ? 'Sincronizando dados' : erroResumoItens ? 'Verifique a conexão' : itensResumoCarregado ? 'Dados sincronizados' : 'Conectando ao sistema'}</span><Link href="/perfil" className="topbar-profile"><span className="avatar-initials avatar-small">{primeiroNome.slice(0, 1).toUpperCase()}</span><span>Meu perfil</span></Link></div>
        </header>

        {secao === 'inicio' && <div className="workspace-content">
          <div className="page-heading-row"><div><p className="eyebrow">RESUMO OPERACIONAL</p><h1>Bom dia, {primeiroNome}.</h1><p className="page-subtitle">Aqui está o panorama atual do almoxarifado.</p></div><button className="button button-secondary" onClick={() => void carregarResumo()} disabled={atualizando}><Icon nome="refresh" size={16} />{atualizando ? 'Atualizando…' : 'Atualizar dados'}</button></div>
          <div className="metric-grid">
            <article className="metric-card"><div className="metric-head"><span className="metric-icon blue"><Icon nome="box" size={19} /></span><span className="metric-label">Tipos de itens ativos</span></div><div className="metric-number">{itensResumoCarregado && !erroResumoItens ? formatarNumero(estatisticas.tiposAtivos) : '—'}</div><div className="metric-caption">Registros disponíveis no catálogo</div><div className="metric-accent blue-accent" /></article>
            <article className="metric-card"><div className="metric-head"><span className="metric-icon violet"><Icon nome="grid" size={19} /></span><span className="metric-label">Unidades em estoque</span></div><div className="metric-number">{itensResumoCarregado && !erroResumoItens ? formatarNumero(estatisticas.unidades) : '—'}</div><div className="metric-caption">Total de unidades de itens ativos</div><div className="metric-accent violet-accent" /></article>
            <article className="metric-card"><div className="metric-head"><span className="metric-icon green"><Icon nome="box" size={19} /></span><span className="metric-label">Unidades disponíveis</span></div><div className="metric-number">{itensResumoCarregado && !erroResumoItens ? formatarNumero(estatisticas.disponiveis) : '—'}</div><div className="metric-caption">Prontas para empréstimo</div><div className="metric-accent green-accent" /></article>
            <article className="metric-card"><div className="metric-head"><span className="metric-icon amber"><Icon nome="alert" size={19} /></span><span className="metric-label">Empréstimos atrasados</span></div><div className="metric-number">{totalAtrasados === null ? '—' : formatarNumero(totalAtrasados)}</div><div className="metric-caption">Precisam de acompanhamento</div><div className="metric-accent amber-accent" /></article>
          </div>

          {totalAtrasados !== null && totalAtrasados > 0 && <button className="attention-banner" onClick={() => mudarSecao('emprestimos')}><span className="attention-icon"><Icon nome="alert" size={20} /></span><span><strong>{totalAtrasados} empréstimo(s) precisam de atenção</strong><small>Consulte os registros e confirme as devoluções pendentes.</small></span><Icon nome="chevron" size={18} /></button>}

          <div className="dashboard-grid">
            <section className="content-card quick-actions-card"><div className="card-heading"><div><h2>Acesso rápido</h2><p>Vá direto às operações mais utilizadas.</p></div></div><div className="quick-action-list">
              <button onClick={() => mudarSecao('itens')} className="quick-action"><span className="quick-action-icon blue"><Icon nome="plus" size={19} /></span><span><strong>Cadastrar ou editar itens</strong><small>Atualize o catálogo do almoxarifado</small></span><Icon nome="chevron" size={17} /></button>
              <button onClick={() => mudarSecao('qr')} className="quick-action"><span className="quick-action-icon violet"><Icon nome="qr" size={19} /></span><span><strong>Registrar por QR Code</strong><small>Cadastre itens ou adicione unidades</small></span><Icon nome="chevron" size={17} /></button>
              <button onClick={() => mudarSecao('notas')} className="quick-action"><span className="quick-action-icon green"><Icon nome="file" size={19} /></span><span><strong>Importar nota fiscal</strong><small>Extraia e revise produtos de XML ou PDF</small></span><Icon nome="chevron" size={17} /></button>
              <button onClick={() => mudarSecao('emprestimos')} className="quick-action"><span className="quick-action-icon amber"><Icon nome="arrows" size={19} /></span><span><strong>Gerenciar empréstimos</strong><small>{totalEmprestimos === null ? 'Consulte as movimentações' : `${formatarNumero(totalEmprestimos)} registro(s) no sistema`}</small></span><Icon nome="chevron" size={17} /></button>
            </div></section>
            <section className="content-card stock-overview-card"><div className="card-heading"><div><h2>Saúde do estoque</h2><p>Visão consolidada dos itens ativos.</p></div><span className="subtle-tag">Ao vivo</span></div>
              {itens.length === 0 ? <div className="empty-state compact-empty"><span className="empty-state-icon"><Icon nome="box" size={22} /></span><strong>{!itensResumoCarregado || atualizando ? 'Carregando indicadores…' : erroResumoItens ? 'Não foi possível consultar o estoque' : 'Nenhum item cadastrado'}</strong><p>{erroResumoItens ? 'Verifique a conexão com o servidor e tente novamente.' : 'Quando os itens forem cadastrados, o resumo do estoque aparecerá aqui.'}</p><button className="text-action" onClick={() => void carregarResumo()}>Tentar atualizar</button></div> : <><div className="stock-figures"><div><span>Setores com itens</span><strong>{formatarNumero(estatisticas.setores)}</strong></div><div><span>Itens inativos</span><strong>{formatarNumero(itens.filter((i) => i.status !== 'ATIVO').length)}</strong></div></div><div className="availability-row"><div><span>Disponibilidade geral</span><strong>{estatisticas.unidades > 0 ? Math.round((estatisticas.disponiveis / estatisticas.unidades) * 100) : 0}%</strong></div><div className="progress-track"><span style={{ width: `${estatisticas.unidades > 0 ? Math.min(100, Math.round((estatisticas.disponiveis / estatisticas.unidades) * 100)) : 0}%` }} /></div><p>{formatarNumero(estatisticas.disponiveis)} de {formatarNumero(estatisticas.unidades)} unidade(s) disponíveis.</p></div><button className="text-action" onClick={() => mudarSecao('itens')}>Ver catálogo completo <Icon nome="chevron" size={15} /></button></>}
            </section>
          </div>
          <footer className="workspace-footer"><span>Avante Almoxarifado</span><span>Gestão de patrimônio · Ambiente administrativo</span></footer>
        </div>}

        {secao === 'itens' && <div className="workspace-content"><div className="page-heading-row"><div><p className="eyebrow">PATRIMÔNIO</p><h1>Estoque e itens</h1><p className="page-subtitle">Acompanhe o inventário, consulte a disponibilidade e gerencie cada registro em um só lugar.</p></div></div><GerenciarItens setores={setores} refreshKey={refreshItens} onItensAlterados={() => setRefreshItens((n) => n + 1)} /><footer className="workspace-footer"><span>Avante Almoxarifado</span><span>As alterações são gravadas no sistema.</span></footer></div>}
        {secao === 'qr' && <div className="workspace-content"><div className="page-heading-row"><div><p className="eyebrow">AUTOMAÇÃO DE ENTRADA</p><h1>Leitor de QR Code</h1><p className="page-subtitle">Use a câmera para identificar um item e registrar sua entrada no estoque.</p></div><span className="count-chip">Câmera + leitura</span></div><LeitorQRAlmoxarifado setores={setores} onItemCadastrado={() => setRefreshItens((n) => n + 1)} /><GerarQRCodes refreshKey={refreshItens} /><footer className="workspace-footer"><span>Entrada rastreável</span><span>Confirme visualmente cada operação.</span></footer></div>}
        {secao === 'notas' && <div className="workspace-content"><div className="page-heading-row"><div><p className="eyebrow">ENTRADA POR DOCUMENTO</p><h1>Notas fiscais</h1><p className="page-subtitle">Extraia produtos de XML ou PDF, revise as quantidades e importe para o estoque.</p></div><span className="count-chip">XML · PDF · imagem</span></div><ImportarNotaFiscal setores={setores} onImportado={() => setRefreshItens((n) => n + 1)} /><HistoricoNotasFiscais /><footer className="workspace-footer"><span>Importação assistida</span><span>Revise o conteúdo antes de confirmar.</span></footer></div>}
        {secao === 'emprestimos' && <div className="workspace-content"><div className="page-heading-row"><div><p className="eyebrow">MOVIMENTAÇÃO DE MATERIAIS</p><h1>Empréstimos</h1><p className="page-subtitle">Acompanhe retiradas, prazos e devoluções do laboratório.</p></div><span className="count-chip">{totalEmprestimos === null ? 'Carregando total…' : `${formatarNumero(totalEmprestimos)} registro(s)`}</span></div><ListaEmprestimos refreshKey={refreshEmprestimos} /><footer className="workspace-footer"><span>Controle de movimentação</span><span>Confirme as devoluções após receber os materiais.</span></footer></div>}
        {secao === 'usuarios' && <div className="workspace-content"><div className="page-heading-row"><div><p className="eyebrow">CONTROLE DE ACESSO</p><h1>Usuários e acessos</h1><p className="page-subtitle">Gerencie contas do laboratório e permissões administrativas.</p></div><span className="count-chip">{totalUsuarios === null ? '—' : `${totalUsuarios} usuário(s) ativo(s)`}</span></div><div className="section-layout"><CadastroAdminForm setores={setores} onAdminCadastrado={() => setRefreshUsuarios((n) => n + 1)} /><GerenciarUsuarios usuarioLogado={usuario} setores={setores} refreshKey={refreshUsuarios} /></div><footer className="workspace-footer"><span>Acesso restrito</span><span>Conceda permissões administrativas apenas quando necessário.</span></footer></div>}
        {secao === 'contato' && <div className="workspace-content"><div className="page-heading-row"><div><p className="eyebrow">SUPORTE E COMUNICAÇÃO</p><h1>Contato e suporte</h1><p className="page-subtitle">Receba solicitações dos usuários e responda em um canal registrado.</p></div></div><CaixaContato /><footer className="workspace-footer"><span>Atendimento registrado</span><span>As respostas ficam disponíveis ao usuário no painel dele.</span></footer></div>}
      </section>
    </main>
  );
}
