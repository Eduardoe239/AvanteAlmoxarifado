'use client';

import type { ReactNode } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import CadastroItemForm from '@/components/admin/CadastroItemForm';
import {
  listarItensAdmin,
  editarItem,
  desativarItem,
  reativarItem,
  removerItem,
  ApiError,
  type Item,
  type Setor,
  type DadosEdicaoItem,
} from '@/lib/api';

type AbaEstoque = 'inventario' | 'cadastro';
type FiltroStatus = 'todos' | 'ativos' | 'inativos';
type Ordenacao = 'nome' | 'disponibilidade' | 'status';
type AcaoPendente = { tipo: 'remover' | 'desativar'; item: Item };

const edicaoSchema = z.object({
  nome: z.string().trim().min(2, 'Informe o nome do item.').max(150, 'Use no máximo 150 caracteres.'),
  patrimonio: z.string().max(50, 'Use no máximo 50 caracteres.').optional(),
  codigoQr: z.string().max(120, 'Use no máximo 120 caracteres.').optional(),
  area: z.string().max(120, 'Use no máximo 120 caracteres.').optional(),
  setorId: z.string().min(1, 'Selecione um setor.'),
  quantidadeTotal: z.coerce.number().int('Informe um número inteiro.').positive('A quantidade deve ser maior que zero.').max(100000, 'Quantidade muito alta.'),
});
type EdicaoFormData = z.infer<typeof edicaoSchema>;

function formatarNumero(valor: number) {
  return new Intl.NumberFormat('pt-BR').format(valor);
}

function normalizarTexto(valor: string) {
  return valor.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR');
}

function IconeEstoque({ nome, tamanho = 18 }: { nome: 'box' | 'search' | 'refresh' | 'plus' | 'filter' | 'edit' | 'trash' | 'check' | 'close' | 'chevron' | 'layers' | 'package' | 'available' | 'inactive' | 'qr' | 'building'; tamanho?: number }) {
  const props = { width: tamanho, height: tamanho, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const, 'aria-hidden': true as const };
  const paths: Record<typeof nome, ReactNode> = {
    box: <><path d="m12 3 9 5-9 5-9-5 9-5Z" /><path d="M3 8v9l9 4 9-4V8M12 13v8" /></>,
    search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>,
    refresh: <><path d="M20 7v5h-5" /><path d="M4 17v-5h5" /><path d="M5.6 9A7 7 0 0 1 17.5 6L20 12M4 12l2.5 6a7 7 0 0 0 11.9-3" /></>,
    plus: <path d="M12 5v14M5 12h14" />,
    filter: <><path d="M4 6h16M7 12h10m-7 6h4" /><circle cx="8" cy="6" r="1" /><circle cx="15" cy="12" r="1" /><circle cx="12" cy="18" r="1" /></>,
    edit: <><path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z" /></>,
    trash: <><path d="M3 6h18M8 6V4h8v2m-9 0 1 14h8l1-14M10 10v6m4-6v6" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    close: <path d="m6 6 12 12M18 6 6 18" />,
    chevron: <path d="m9 18 6-6-6-6" />,
    layers: <><path d="m12 3 9 5-9 5-9-5 9-5Z" /><path d="m3 12 9 5 9-5M3 16l9 5 9-5" /></>,
    package: <><path d="M4 7.5 12 3l8 4.5v9L12 21l-8-4.5Z" /><path d="M4 7.5 12 12l8-4.5M12 12v9" /></>,
    available: <><circle cx="12" cy="12" r="9" /><path d="m8 12 2.5 2.5L16 9" /></>,
    inactive: <><circle cx="12" cy="12" r="9" /><path d="M8 12h8" /></>,
    qr: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><path d="M14 14h3v3h-3zM20 14v2M17 20h4M20 18v3" /></>,
    building: <><rect x="4" y="3" width="16" height="18" rx="2" /><path d="M9 21v-4h6v4M8 7h1m6 0h1M8 11h1m6 0h1" /></>,
  };
  return <svg {...props}>{paths[nome]}</svg>;
}

function CampoEdicao({
  id,
  rotulo,
  children,
  erro,
  largo = false,
}: {
  id: string;
  rotulo: string;
  children: ReactNode;
  erro?: string;
  largo?: boolean;
}) {
  return (
    <div className={`stock-v2-field ${largo ? 'stock-v2-field--wide' : ''}`}>
      <label htmlFor={id}>{rotulo}</label>
      {children}
      {erro && <p className="stock-v2-field-error">{erro}</p>}
    </div>
  );
}

function ModalEditarItem({
  item,
  setores,
  onFechar,
  onSalvo,
}: {
  item: Item;
  setores: Setor[];
  onFechar: () => void;
  onSalvo: () => void;
}) {
  const [erro, setErro] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<EdicaoFormData>({
    resolver: zodResolver(edicaoSchema),
    defaultValues: {
      nome: item.nome,
      patrimonio: item.patrimonio || '',
      codigoQr: item.codigo_qr || '',
      area: item.area || '',
      setorId: item.setor_atual_id !== null ? String(item.setor_atual_id) : '',
      quantidadeTotal: item.quantidade_total,
    },
  });

  useEffect(() => {
    const tratarEscape = (evento: KeyboardEvent) => { if (evento.key === 'Escape' && !isSubmitting) onFechar(); };
    window.addEventListener('keydown', tratarEscape);
    return () => window.removeEventListener('keydown', tratarEscape);
  }, [onFechar, isSubmitting]);

  async function salvar(dados: EdicaoFormData) {
    setErro(null);
    try {
      const payload: DadosEdicaoItem = {
        nome: dados.nome.trim(),
        setor_id: Number(dados.setorId),
        codigo_qr: dados.codigoQr?.trim() || null,
        area: dados.area?.trim() || null,
        patrimonio: dados.patrimonio?.trim() || null,
        quantidade_total: dados.quantidadeTotal,
      };
      await editarItem(item.id, payload);
      onSalvo();
    } catch (falha) {
      setErro(falha instanceof ApiError ? falha.message : 'Não foi possível salvar as alterações. Confira os dados e tente novamente.');
    }
  }

  return (
    <div className="stock-v2-modal-backdrop" onMouseDown={(evento) => { if (evento.target === evento.currentTarget && !isSubmitting) onFechar(); }}>
      <section className="stock-v2-modal" role="dialog" aria-modal="true" aria-labelledby="stock-edit-title">
        <header className="stock-v2-modal-heading">
          <div className="stock-v2-modal-icon"><IconeEstoque nome="edit" tamanho={20} /></div>
          <div><h2 id="stock-edit-title">Editar item</h2><p>Atualize os dados de identificação e estoque.</p></div>
          <button type="button" className="stock-v2-icon-button" onClick={onFechar} disabled={isSubmitting} aria-label="Fechar edição"><IconeEstoque nome="close" /></button>
        </header>
        <form onSubmit={handleSubmit(salvar)} className="stock-v2-edit-form" noValidate>
          <div className="stock-v2-edit-grid">
            <CampoEdicao id="edit-item-name" rotulo="Nome do item" erro={errors.nome?.message}>
              <input id="edit-item-name" {...register('nome')} autoFocus aria-invalid={Boolean(errors.nome)} />
            </CampoEdicao>
            <CampoEdicao id="edit-item-sector" rotulo="Setor" erro={errors.setorId?.message}>
              <select id="edit-item-sector" {...register('setorId')} aria-invalid={Boolean(errors.setorId)}><option value="">Selecione um setor</option>{setores.map((setor) => <option key={setor.id} value={String(setor.id)}>{setor.nome}</option>)}</select>
            </CampoEdicao>
            <CampoEdicao id="edit-item-patrimony" rotulo="Patrimônio" erro={errors.patrimonio?.message}>
              <input id="edit-item-patrimony" {...register('patrimonio')} placeholder="Ex.: AVT-001" aria-invalid={Boolean(errors.patrimonio)} />
            </CampoEdicao>
            <CampoEdicao id="edit-item-qr" rotulo="Código QR" erro={errors.codigoQr?.message}>
              <input id="edit-item-qr" {...register('codigoQr')} placeholder="Código de identificação" aria-invalid={Boolean(errors.codigoQr)} />
            </CampoEdicao>
            <CampoEdicao id="edit-item-area" rotulo="Área" erro={errors.area?.message}>
              <input id="edit-item-area" {...register('area')} placeholder="Ex.: Laboratório de eletrônica" aria-invalid={Boolean(errors.area)} />
            </CampoEdicao>
            <CampoEdicao id="edit-item-quantity" rotulo="Quantidade total" erro={errors.quantidadeTotal?.message}>
              <input id="edit-item-quantity" type="number" min={1} max={100000} step={1} {...register('quantidadeTotal')} aria-invalid={Boolean(errors.quantidadeTotal)} />
            </CampoEdicao>
          </div>
          <p className="stock-v2-edit-note">Disponíveis agora: <strong>{formatarNumero(item.quantidade_disponivel)}</strong> de <strong>{formatarNumero(item.quantidade_total)}</strong>. Se houver unidades emprestadas, a API pode impedir uma redução incompatível da quantidade total.</p>
          {erro && <div className="stock-v2-alert stock-v2-alert--error" role="alert">{erro}</div>}
          <footer className="stock-v2-modal-actions"><button type="button" className="button button-secondary" onClick={onFechar} disabled={isSubmitting}>Cancelar</button><button type="submit" className="button button-primary" disabled={isSubmitting}>{isSubmitting ? <><span className="loading-inline loading-inline--light" /> Salvando…</> : 'Salvar alterações'}</button></footer>
        </form>
      </section>
    </div>
  );
}

function LinhaItem({
  item,
  setores,
  processando,
  onEditar,
  onAcao,
}: {
  item: Item;
  setores: Setor[];
  processando: boolean;
  onEditar: (item: Item) => void;
  onAcao: (tipo: 'remover' | 'alternarStatus', item: Item) => void;
}) {
  const setorNome = setores.find((setor) => Number(setor.id) === Number(item.setor_atual_id))?.nome || 'Setor não informado';
  const ativo = item.status === 'ATIVO';
  const disponibilidade = item.quantidade_total > 0 ? Math.max(0, Math.min(100, Math.round((item.quantidade_disponivel / item.quantidade_total) * 100))) : 0;

  return (
    <tr className="stock-v2-row">
      <td data-label="Item">
        <div className="stock-v2-item-cell"><span className={`stock-v2-item-icon ${ativo ? '' : 'is-inactive'}`}><IconeEstoque nome="package" tamanho={19} /></span><span className="stock-v2-item-copy"><strong>{item.nome}</strong><small>{item.patrimonio ? `Patrimônio ${item.patrimonio}` : `ID ${item.id}`}</small></span></div>
      </td>
      <td data-label="Setor"><span className="stock-v2-secondary-cell"><IconeEstoque nome="building" tamanho={14} />{setorNome}</span></td>
      <td data-label="Área"><span className="stock-v2-muted-cell">{item.area || '—'}</span></td>
      <td data-label="Código QR"><span className={`stock-v2-code ${item.codigo_qr ? '' : 'is-empty'}`}>{item.codigo_qr || 'Não definido'}</span></td>
      <td data-label="Disponibilidade">
        <div className="stock-v2-availability"><div><strong>{formatarNumero(item.quantidade_disponivel)}</strong><span> / {formatarNumero(item.quantidade_total)}</span></div><div className="stock-v2-progress"><span style={{ width: `${disponibilidade}%` }} /></div></div>
      </td>
      <td data-label="Status"><span className={`stock-v2-status ${ativo ? 'is-active' : 'is-inactive'}`}><span />{ativo ? 'Ativo' : 'Inativo'}</span></td>
      <td data-label="Ações">
        <div className="stock-v2-row-actions">
          <button type="button" className="stock-v2-action-button stock-v2-action-edit" onClick={() => onEditar(item)} aria-label={`Editar ${item.nome}`} title="Editar item"><IconeEstoque nome="edit" tamanho={15} /><span>Editar</span></button>
          <button type="button" className={`stock-v2-action-button ${ativo ? 'stock-v2-action-deactivate' : 'stock-v2-action-reactivate'}`} onClick={() => onAcao('alternarStatus', item)} disabled={processando} aria-label={ativo ? `Desativar ${item.nome}` : `Reativar ${item.nome}`} title={ativo ? 'Desativar item' : 'Reativar item'}>{processando ? <span className="loading-inline" /> : ativo ? <IconeEstoque nome="inactive" tamanho={15} /> : <IconeEstoque nome="check" tamanho={15} />}<span>{ativo ? 'Desativar' : 'Reativar'}</span></button>
          <button type="button" className="stock-v2-icon-button stock-v2-delete-button" onClick={() => onAcao('remover', item)} disabled={processando} aria-label={`Remover ${item.nome}`} title="Remover item"><IconeEstoque nome="trash" tamanho={16} /></button>
        </div>
      </td>
    </tr>
  );
}

export default function GerenciarItens({
  setores,
  refreshKey,
  onItensAlterados,
}: {
  setores: Setor[];
  refreshKey: number;
  onItensAlterados?: () => void;
}) {
  const [itens, setItens] = useState<Item[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [versao, setVersao] = useState(0);
  const [aba, setAba] = useState<AbaEstoque>('inventario');
  const [pesquisa, setPesquisa] = useState('');
  const [filtroStatus, setFiltroStatus] = useState<FiltroStatus>('todos');
  const [filtroSetor, setFiltroSetor] = useState('todos');
  const [ordenacao, setOrdenacao] = useState<Ordenacao>('nome');
  const [ordemAscendente, setOrdemAscendente] = useState(true);
  const [pagina, setPagina] = useState(1);
  const [itemEditando, setItemEditando] = useState<Item | null>(null);
  const [acaoPendente, setAcaoPendente] = useState<AcaoPendente | null>(null);
  const [itemProcessando, setItemProcessando] = useState<number | null>(null);
  const [erroAcao, setErroAcao] = useState<string | null>(null);
  const [sucessoAcao, setSucessoAcao] = useState<string | null>(null);
  const [confirmandoAcao, setConfirmandoAcao] = useState(false);
  const tamanhoPagina = 10;

  const notificarAlteracao = useCallback(() => {
    if (onItensAlterados) onItensAlterados();
    else setVersao((valor) => valor + 1);
  }, [onItensAlterados]);

  useEffect(() => {
    let ativo = true;
    setCarregando(true);
    setErro(null);
    listarItensAdmin()
      .then((lista) => { if (ativo) setItens(lista); })
      .catch((falha) => {
        if (!ativo) return;
        setErro(falha instanceof ApiError ? falha.message : 'Não foi possível carregar os itens. Verifique a conexão e tente novamente.');
      })
      .finally(() => { if (ativo) setCarregando(false); });
    return () => { ativo = false; };
  }, [refreshKey, versao]);

  const estatisticas = useMemo(() => {
    const ativos = itens.filter((item) => item.status === 'ATIVO');
    return {
      tiposCadastrados: itens.length,
      tiposAtivos: ativos.length,
      unidades: itens.reduce((soma, item) => soma + item.quantidade_total, 0),
      disponiveis: ativos.reduce((soma, item) => soma + item.quantidade_disponivel, 0),
      inativos: itens.filter((item) => item.status !== 'ATIVO').length,
    };
  }, [itens]);

  const itensFiltrados = useMemo(() => {
    const termo = normalizarTexto(pesquisa.trim());
    const filtrados = itens.filter((item) => {
      const setorNome = setores.find((setor) => Number(setor.id) === Number(item.setor_atual_id))?.nome || '';
      const correspondeTexto = !termo || [item.nome, item.patrimonio, item.codigo_qr, item.area, setorNome, String(item.id)]
        .some((valor) => normalizarTexto(String(valor || '')).includes(termo));
      const correspondeStatus = filtroStatus === 'todos' || (filtroStatus === 'ativos' ? item.status === 'ATIVO' : item.status !== 'ATIVO');
      const correspondeSetor = filtroSetor === 'todos' || String(item.setor_atual_id ?? '') === filtroSetor;
      return correspondeTexto && correspondeStatus && correspondeSetor;
    });
    filtrados.sort((a, b) => {
      let comparacao = 0;
      if (ordenacao === 'nome') comparacao = a.nome.localeCompare(b.nome, 'pt-BR', { sensitivity: 'base' });
      else if (ordenacao === 'disponibilidade') {
        const percentualA = a.quantidade_total > 0 ? a.quantidade_disponivel / a.quantidade_total : 0;
        const percentualB = b.quantidade_total > 0 ? b.quantidade_disponivel / b.quantidade_total : 0;
        comparacao = percentualA - percentualB;
      } else comparacao = a.status.localeCompare(b.status, 'pt-BR');
      return ordemAscendente ? comparacao : -comparacao;
    });
    return filtrados;
  }, [itens, pesquisa, filtroStatus, filtroSetor, setores, ordenacao, ordemAscendente]);

  const totalPaginas = Math.max(1, Math.ceil(itensFiltrados.length / tamanhoPagina));
  const itensVisiveis = itensFiltrados.slice((pagina - 1) * tamanhoPagina, pagina * tamanhoPagina);

  useEffect(() => { setPagina(1); }, [pesquisa, filtroStatus, filtroSetor]);
  useEffect(() => { if (pagina > totalPaginas) setPagina(totalPaginas); }, [pagina, totalPaginas]);

  function ordenarPor(campo: Ordenacao) {
    if (ordenacao === campo) setOrdemAscendente((atual) => !atual);
    else { setOrdenacao(campo); setOrdemAscendente(true); }
    setPagina(1);
  }

  async function alternarStatus(item: Item) {
    setItemProcessando(item.id);
    setErroAcao(null);
    setSucessoAcao(null);
    try {
      await reativarItem(item.id);
      setSucessoAcao(`“${item.nome}” foi reativado.`);
      notificarAlteracao();
    } catch (falha) {
      setErroAcao(falha instanceof ApiError ? falha.message : 'Não foi possível reativar o item.');
    } finally {
      setItemProcessando(null);
    }
  }

  function solicitarAcao(tipo: 'remover' | 'alternarStatus', item: Item) {
    setErroAcao(null);
    setSucessoAcao(null);
    if (tipo === 'alternarStatus' && item.status !== 'ATIVO') {
      void alternarStatus(item);
      return;
    }
    setAcaoPendente({ tipo: tipo === 'remover' ? 'remover' : 'desativar', item });
  }

  async function confirmarAcao() {
    if (!acaoPendente) return;
    setConfirmandoAcao(true);
    setErroAcao(null);
    try {
      if (acaoPendente.tipo === 'remover') {
        await removerItem(acaoPendente.item.id);
        setSucessoAcao(`“${acaoPendente.item.nome}” foi removido do catálogo.`);
      } else {
        await desativarItem(acaoPendente.item.id);
        setSucessoAcao(`“${acaoPendente.item.nome}” foi desativado. O histórico será preservado.`);
      }
      setAcaoPendente(null);
      notificarAlteracao();
    } catch (falha) {
      setErroAcao(falha instanceof ApiError ? falha.message : acaoPendente.tipo === 'remover' ? 'Não foi possível remover o item. Se ele tiver histórico de empréstimos, desative-o para preservar os registros.' : 'Não foi possível desativar o item.');
    } finally {
      setConfirmandoAcao(false);
    }
  }

  return (
    <section className="stock-v2-shell" aria-labelledby="stock-v2-title">
      <div className="stock-v2-summary-card">
        <div className="stock-v2-summary-heading">
          <div><p className="eyebrow">CONTROLE DE PATRIMÔNIO</p><h2 id="stock-v2-title">Inventário do almoxarifado</h2><p>Consulte a disponibilidade e mantenha os registros atualizados.</p></div>
          <button type="button" className="button button-secondary stock-v2-refresh" onClick={() => { setSucessoAcao(null); setErro(null); setVersao((valor) => valor + 1); }} disabled={carregando} aria-label="Atualizar inventário"><IconeEstoque nome="refresh" tamanho={16} />{carregando ? 'Atualizando…' : 'Atualizar'}</button>
        </div>
        <div className="stock-v2-metrics" aria-label="Resumo do estoque">
          <article className="stock-v2-metric"><span className="stock-v2-metric-icon stock-v2-metric-icon--blue"><IconeEstoque nome="layers" tamanho={19} /></span><div><span>Tipos cadastrados</span><strong>{carregando && itens.length === 0 ? '—' : formatarNumero(estatisticas.tiposCadastrados)}</strong><small>Registros no catálogo</small></div></article>
          <article className="stock-v2-metric"><span className="stock-v2-metric-icon stock-v2-metric-icon--indigo"><IconeEstoque nome="package" tamanho={19} /></span><div><span>Unidades registradas</span><strong>{carregando && itens.length === 0 ? '—' : formatarNumero(estatisticas.unidades)}</strong><small>Quantidade total cadastrada</small></div></article>
          <article className="stock-v2-metric"><span className="stock-v2-metric-icon stock-v2-metric-icon--green"><IconeEstoque nome="available" tamanho={19} /></span><div><span>Unidades disponíveis</span><strong>{carregando && itens.length === 0 ? '—' : formatarNumero(estatisticas.disponiveis)}</strong><small>Itens ativos para empréstimo</small></div></article>
          <article className="stock-v2-metric"><span className="stock-v2-metric-icon stock-v2-metric-icon--slate"><IconeEstoque nome="inactive" tamanho={19} /></span><div><span>Itens inativos</span><strong>{carregando && itens.length === 0 ? '—' : formatarNumero(estatisticas.inativos)}</strong><small>Preservados no histórico</small></div></article>
        </div>
      </div>

      <div className="stock-v2-workspace">
        <div className="stock-v2-tabs" role="tablist" aria-label="Gerenciamento de estoque">
          <button type="button" role="tab" aria-selected={aba === 'inventario'} className={`stock-v2-tab ${aba === 'inventario' ? 'is-active' : ''}`} onClick={() => setAba('inventario')}><IconeEstoque nome="layers" tamanho={16} /> Inventário <span>{formatarNumero(itens.length)}</span></button>
          <button type="button" role="tab" aria-selected={aba === 'cadastro'} className={`stock-v2-tab ${aba === 'cadastro' ? 'is-active' : ''}`} onClick={() => setAba('cadastro')}><IconeEstoque nome="plus" tamanho={16} /> Cadastrar item</button>
          <div className="stock-v2-tab-spacer" />
          {aba === 'inventario' && <span className="stock-v2-sync-status"><span />{carregando ? 'Sincronizando' : 'Dados do sistema'}</span>}
        </div>

        {aba === 'cadastro' ? (
          <div className="stock-v2-registration-view" role="tabpanel">
            <div className="stock-v2-registration-intro"><span className="stock-v2-registration-icon"><IconeEstoque nome="plus" tamanho={20} /></span><div><h3>Novo item no inventário</h3><p>Preencha os dados principais. Campos identificadores opcionais podem ser adicionados depois.</p></div></div>
            <CadastroItemForm setores={setores} onItemCadastrado={notificarAlteracao} />
          </div>
        ) : (
          <div className="stock-v2-inventory-view" role="tabpanel">
            <div className="stock-v2-inventory-heading"><div><h3>Itens cadastrados</h3><p>Pesquise, filtre e gerencie os registros do patrimônio.</p></div><span className="stock-v2-record-count">{formatarNumero(itensFiltrados.length)} resultado(s)</span></div>

            <div className="stock-v2-toolbar">
              <label className="stock-v2-search"><IconeEstoque nome="search" tamanho={18} /><input value={pesquisa} onChange={(evento) => setPesquisa(evento.target.value)} placeholder="Buscar nome, patrimônio, QR, setor…" aria-label="Buscar no inventário" />{pesquisa && <button type="button" onClick={() => setPesquisa('')} aria-label="Limpar busca"><IconeEstoque nome="close" tamanho={15} /></button>}</label>
              <label className="stock-v2-filter"><span><IconeEstoque nome="filter" tamanho={15} /> Status</span><select value={filtroStatus} onChange={(evento) => setFiltroStatus(evento.target.value as FiltroStatus)} aria-label="Filtrar pelo status"><option value="todos">Todos</option><option value="ativos">Ativos</option><option value="inativos">Inativos</option></select></label>
              <label className="stock-v2-filter stock-v2-filter--sector"><span><IconeEstoque nome="building" tamanho={15} /> Setor</span><select value={filtroSetor} onChange={(evento) => setFiltroSetor(evento.target.value)} aria-label="Filtrar pelo setor"><option value="todos">Todos os setores</option>{setores.map((setor) => <option key={setor.id} value={String(setor.id)}>{setor.nome}</option>)}</select></label>
              {(pesquisa || filtroStatus !== 'todos' || filtroSetor !== 'todos') && <button type="button" className="stock-v2-clear-filters" onClick={() => { setPesquisa(''); setFiltroStatus('todos'); setFiltroSetor('todos'); }}>Limpar filtros</button>}
            </div>

            {erroAcao && !acaoPendente && <div className="stock-v2-alert stock-v2-alert--error" role="alert"><span>{erroAcao}</span><button type="button" onClick={() => setErroAcao(null)} aria-label="Fechar mensagem"><IconeEstoque nome="close" tamanho={15} /></button></div>}
            {sucessoAcao && <div className="stock-v2-alert stock-v2-alert--success" role="status"><IconeEstoque nome="check" tamanho={16} /><span>{sucessoAcao}</span><button type="button" onClick={() => setSucessoAcao(null)} aria-label="Fechar mensagem"><IconeEstoque nome="close" tamanho={15} /></button></div>}

            {carregando && itens.length === 0 ? (
              <div className="stock-v2-loading" role="status"><span className="loading-inline" /><strong>Carregando inventário…</strong><p>Buscando os registros mais recentes.</p></div>
            ) : erro && itens.length === 0 ? (
              <div className="stock-v2-empty stock-v2-empty--error" role="alert"><span className="stock-v2-empty-icon"><IconeEstoque nome="refresh" tamanho={22} /></span><strong>Não foi possível carregar o inventário</strong><p>{erro}</p><button type="button" className="button button-primary" onClick={() => setVersao((valor) => valor + 1)}>Tentar novamente</button></div>
            ) : itens.length === 0 ? (
              <div className="stock-v2-empty"><span className="stock-v2-empty-icon"><IconeEstoque nome="box" tamanho={23} /></span><strong>Seu inventário ainda está vazio</strong><p>Cadastre o primeiro item ou use o leitor de QR Code para registrar uma entrada.</p><button type="button" className="button button-primary" onClick={() => setAba('cadastro')}><IconeEstoque nome="plus" tamanho={16} /> Cadastrar primeiro item</button></div>
            ) : itensFiltrados.length === 0 ? (
              <div className="stock-v2-empty"><span className="stock-v2-empty-icon"><IconeEstoque nome="search" tamanho={23} /></span><strong>Nenhum item encontrado</strong><p>Experimente outro termo ou remova um dos filtros ativos.</p><button type="button" className="button button-secondary" onClick={() => { setPesquisa(''); setFiltroStatus('todos'); setFiltroSetor('todos'); }}>Limpar filtros</button></div>
            ) : (
              <>
                {erro && <div className="stock-v2-alert stock-v2-alert--warning" role="status">Não foi possível atualizar os dados. Exibindo a última lista carregada. <button type="button" onClick={() => setVersao((valor) => valor + 1)}>Tentar novamente</button></div>}
                <div className={`stock-v2-table-wrap ${carregando ? 'is-refreshing' : ''}`}>
                  <table className="stock-v2-table">
                    <thead><tr>
                      <th scope="col" aria-sort={ordenacao === 'nome' ? (ordemAscendente ? 'ascending' : 'descending') : 'none'}><button type="button" onClick={() => ordenarPor('nome')}>Item <span className={`stock-v2-sort-mark ${ordenacao === 'nome' ? 'is-selected' : ''}`}>{ordenacao === 'nome' ? (ordemAscendente ? '↑' : '↓') : '↕'}</span></button></th>
                      <th scope="col">Setor</th><th scope="col">Área</th><th scope="col">Código QR</th>
                      <th scope="col" aria-sort={ordenacao === 'disponibilidade' ? (ordemAscendente ? 'ascending' : 'descending') : 'none'}><button type="button" onClick={() => ordenarPor('disponibilidade')}>Disponibilidade <span className={`stock-v2-sort-mark ${ordenacao === 'disponibilidade' ? 'is-selected' : ''}`}>{ordenacao === 'disponibilidade' ? (ordemAscendente ? '↑' : '↓') : '↕'}</span></button></th>
                      <th scope="col" aria-sort={ordenacao === 'status' ? (ordemAscendente ? 'ascending' : 'descending') : 'none'}><button type="button" onClick={() => ordenarPor('status')}>Status <span className={`stock-v2-sort-mark ${ordenacao === 'status' ? 'is-selected' : ''}`}>{ordenacao === 'status' ? (ordemAscendente ? '↑' : '↓') : '↕'}</span></button></th>
                      <th scope="col"><span className="stock-v2-actions-heading">Ações</span></th>
                    </tr></thead>
                    <tbody>{itensVisiveis.map((item) => <LinhaItem key={item.id} item={item} setores={setores} processando={itemProcessando === item.id || (confirmandoAcao && acaoPendente?.item.id === item.id)} onEditar={setItemEditando} onAcao={solicitarAcao} />)}</tbody>
                  </table>
                </div>
                <footer className="stock-v2-pagination"><span>Exibindo <strong>{(pagina - 1) * tamanhoPagina + 1}–{Math.min(pagina * tamanhoPagina, itensFiltrados.length)}</strong> de <strong>{formatarNumero(itensFiltrados.length)}</strong> itens</span><div><button type="button" className="stock-v2-page-button" onClick={() => setPagina((valor) => Math.max(1, valor - 1))} disabled={pagina <= 1} aria-label="Página anterior">‹</button><span className="stock-v2-page-indicator">Página <strong>{pagina}</strong> de <strong>{totalPaginas}</strong></span><button type="button" className="stock-v2-page-button" onClick={() => setPagina((valor) => Math.min(totalPaginas, valor + 1))} disabled={pagina >= totalPaginas} aria-label="Próxima página">›</button></div></footer>
              </>
            )}
          </div>
        )}
      </div>

      {itemEditando && <ModalEditarItem key={itemEditando.id} item={itemEditando} setores={setores} onFechar={() => setItemEditando(null)} onSalvo={() => { const nome = itemEditando.nome; setItemEditando(null); setSucessoAcao(`Alterações de “${nome}” foram salvas.`); notificarAlteracao(); }} />}
      {acaoPendente && (
        <div className="stock-v2-modal-backdrop" onMouseDown={(evento) => { if (evento.target === evento.currentTarget && !confirmandoAcao) { setAcaoPendente(null); setErroAcao(null); } }}>
          <section className="stock-v2-confirm-modal" role="alertdialog" aria-modal="true" aria-labelledby="stock-confirm-title" aria-describedby="stock-confirm-description">
            <span className={`stock-v2-confirm-icon ${acaoPendente.tipo === 'remover' ? 'is-danger' : 'is-warning'}`}><IconeEstoque nome={acaoPendente.tipo === 'remover' ? 'trash' : 'inactive'} tamanho={22} /></span>
            <h2 id="stock-confirm-title">{acaoPendente.tipo === 'remover' ? 'Remover item do catálogo?' : 'Desativar item?'}</h2>
            <p id="stock-confirm-description">{acaoPendente.tipo === 'remover' ? <>Você está prestes a remover <strong>{acaoPendente.item.nome}</strong>. Se houver histórico de empréstimos, o sistema poderá bloquear a remoção. Nesse caso, desative o item para preservar os registros.</> : <>O item <strong>{acaoPendente.item.nome}</strong> deixará de aparecer como disponível para novas operações. O histórico existente será preservado.</>}</p>
            {erroAcao && <div className="stock-v2-alert stock-v2-alert--error" role="alert">{erroAcao}</div>}
            <div className="stock-v2-modal-actions"><button type="button" className="button button-secondary" onClick={() => { setAcaoPendente(null); setErroAcao(null); }} disabled={confirmandoAcao}>Cancelar</button><button type="button" className={`button ${acaoPendente.tipo === 'remover' ? 'stock-v2-danger-button' : 'stock-v2-warning-button'}`} onClick={() => void confirmarAcao()} disabled={confirmandoAcao}>{confirmandoAcao ? 'Processando…' : acaoPendente.tipo === 'remover' ? 'Sim, remover item' : 'Confirmar desativação'}</button></div>
          </section>
        </div>
      )}
    </section>
  );
}
