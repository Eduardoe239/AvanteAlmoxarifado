'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import FormularioEmprestimo from '@/components/FormularioEmprestimo';
import MeusEmprestimos from '@/components/MeusEmprestimos';
import Header from '@/components/Header';
import ContatoAdministradores from '@/components/ContatoAdministradores';
import { apiFetch, obterUsuarioAtual, ApiError, type Item, type Usuario } from '@/lib/api';

export default function Home() {
  const router = useRouter();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [itens, setItens] = useState<Item[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [refreshEmprestimos, setRefreshEmprestimos] = useState(0);

  const carregarInicial = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      const usuarioAtual = await obterUsuarioAtual();
      if (!usuarioAtual) { router.replace('/login'); return; }
      setUsuario(usuarioAtual);
      const itensResp = await apiFetch('/itens/');
      setItens(itensResp);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : 'Não foi possível carregar os dados do laboratório. Verifique sua conexão e tente novamente.');
    } finally {
      setCarregando(false);
    }
  }, [router]);

  const atualizarItens = useCallback(async () => {
    try { setItens(await apiFetch('/itens/')); }
    catch { /* Mantém os dados atuais até a próxima atualização. */ }
  }, []);

  const aoRegistrarEmprestimo = useCallback(() => {
    void atualizarItens();
    setRefreshEmprestimos((n) => n + 1);
  }, [atualizarItens]);

  useEffect(() => { void carregarInicial(); }, [carregarInicial]);

  return (
    <main className="member-page">
      {usuario && <Header usuario={usuario} paginaAtual="inicio" />}
      <div className="member-content">
        <div className="member-page-title">
          <div><p className="eyebrow">ESPAÇO DO COLABORADOR</p><h1>Almoxarifado</h1><p>Consulte a disponibilidade de equipamentos e acompanhe suas retiradas.</p></div>
          {!carregando && !erro && <span className="count-chip">{itens.filter((item) => item.quantidade_disponivel > 0 && item.status === 'ATIVO').length} tipo(s) disponíveis</span>}
        </div>
        {carregando && <div className="content-card member-loading"><span className="loading-inline" /> <span>Carregando o catálogo e sua sessão…</span></div>}
        {erro && !carregando && <div role="alert" className="member-error"><strong>Não foi possível carregar o almoxarifado</strong><p>{erro}</p><button className="button button-primary" onClick={() => void carregarInicial()}>Tentar novamente</button></div>}
        {!carregando && !erro && <div className="member-layout"><section className="member-primary"><FormularioEmprestimo itens={itens} onEmprestimoRegistrado={aoRegistrarEmprestimo} /></section><section className="member-secondary"><MeusEmprestimos refreshKey={refreshEmprestimos} onDevolucaoRegistrada={atualizarItens} /><ContatoAdministradores /></section></div>}
        <footer className="workspace-footer"><span>Avante Almoxarifado</span><span>Solicitações e devoluções são registradas no sistema.</span></footer>
      </div>
    </main>
  );
}
