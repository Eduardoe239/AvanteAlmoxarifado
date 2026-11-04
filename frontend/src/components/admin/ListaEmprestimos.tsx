'use client';

import { useEffect, useState } from 'react';
import { listarEmprestimosAdmin, devolverEmprestimoAdmin, ApiError, type EmprestimoAdmin } from '@/lib/api';
import { formatarData, rotuloStatusEmprestimo } from '@/lib/formatacao';

function corDoStatus(status: string) {
  switch (status) {
    case 'EM_ANDAMENTO':
      return 'bg-blue-50 text-blue-700';
    case 'DEVOLVIDO':
      return 'bg-green-50 text-green-700';
    case 'PENDENTE_DEVOLUCAO':
      return 'bg-amber-50 text-amber-700';
    case 'ATRASADO':
      return 'bg-red-50 text-red-700';
    default:
      return 'bg-slate-100 text-slate-700';
  }
}

const TAMANHO_PAGINA = 10;

export default function ListaEmprestimos({ refreshKey }: { refreshKey: number }) {
  const [emprestimos, setEmprestimos] = useState<EmprestimoAdmin[]>([]);
  const [pagina, setPagina] = useState(1);
  const [totalPaginas, setTotalPaginas] = useState(1);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [devolvendoId, setDevolvendoId] = useState<number | null>(null);

  function carregar() {
    setCarregando(true);
    setErro(null);
    listarEmprestimosAdmin(pagina, TAMANHO_PAGINA)
      .then((resposta) => {
        setEmprestimos(resposta.itens);
        setTotalPaginas(resposta.total_paginas);
        setTotal(resposta.total);
      })
      .catch((e) => {
        const texto = e instanceof ApiError ? e.message : 'Não foi possível carregar os empréstimos.';
        setErro(texto);
      })
      .finally(() => setCarregando(false));
  }

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey, pagina]);

  // Sempre que a lista é recarregada por causa de um evento externo
  // (cadastro de item, devolução em outra aba), volta pra primeira página
  // — evita o usuário ficar "preso" numa página que não existe mais.
  useEffect(() => {
    setPagina(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey]);

  async function devolver(id: number) {
    setDevolvendoId(id);
    try {
      await devolverEmprestimoAdmin(id);
      carregar();
    } catch (e) {
      const texto = e instanceof ApiError ? e.message : 'Não foi possível confirmar a devolução.';
      setErro(texto);
    } finally {
      setDevolvendoId(null);
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-8">
      <h2 className="text-xl font-bold text-slate-800 mb-6">Empréstimos registrados</h2>

      {carregando && <p className="text-slate-500">Carregando...</p>}

      {erro && !carregando && <div role="alert" className="workflow-error"><span>{erro}</span><button type="button" onClick={carregar}>Tentar novamente</button></div>}

      {!carregando && !erro && emprestimos.length === 0 && (
        <div className="workflow-empty"><strong>Nenhum empréstimo registrado</strong><p>Quando houver retiradas de equipamentos, elas aparecerão nesta lista.</p></div>
      )}

      {!carregando && !erro && emprestimos.length > 0 && (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500">
                  <th className="py-2 pr-4 font-semibold">Quem pegou</th>
                  <th className="py-2 pr-4 font-semibold">Setor</th>
                  <th className="py-2 pr-4 font-semibold">Item</th>
                  <th className="py-2 pr-4 font-semibold">Dias</th>
                  <th className="py-2 pr-4 font-semibold">Retirada</th>
                  <th className="py-2 pr-4 font-semibold">Devolução prevista</th>
                  <th className="py-2 pr-4 font-semibold">Status</th>
                  <th className="py-2 pr-4 font-semibold">Ação</th>
                </tr>
              </thead>
              <tbody>
                {emprestimos.map((e) => (
                  <tr key={e.id} className="border-b border-slate-100">
                    <td className="py-2 pr-4 text-slate-800">{e.usuario_nome}</td>
                    <td className="py-2 pr-4 text-slate-600">{e.setor_nome || '—'}</td>
                    <td className="py-2 pr-4 text-slate-600">{e.item_nome}</td>
                    <td className="py-2 pr-4 text-slate-600">{e.dias_solicitados}</td>
                    <td className="py-2 pr-4 text-slate-600">{formatarData(e.data_retirada)}</td>
                    <td className="py-2 pr-4 text-slate-600">
                      {formatarData(e.data_devolucao_prevista)}
                    </td>
                    <td className="py-2 pr-4">
                      <span className={`px-2 py-1 rounded-md text-xs font-semibold ${corDoStatus(e.status)}`}>
                        {rotuloStatusEmprestimo(e.status)}
                      </span>
                    </td>
                    <td className="py-2 pr-4">
                      {e.status === 'DEVOLVIDO' ? (
                        <span className="text-slate-400 text-xs">—</span>
                      ) : (
                        <button
                          onClick={() => devolver(e.id)}
                          disabled={devolvendoId === e.id}
                          className="text-xs font-semibold text-blue-700 hover:text-blue-900 underline disabled:opacity-60 disabled:cursor-not-allowed"
                        >
                          {devolvendoId === e.id ? 'Confirmando...' : e.status === 'PENDENTE_DEVOLUCAO' ? 'Aprovar devolução' : 'Confirmar devolução'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between mt-4 text-sm text-slate-500">
            <span>
              {total} empréstimo{total !== 1 ? 's' : ''} no total — página {pagina} de {totalPaginas}
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setPagina((p) => Math.max(1, p - 1))}
                disabled={pagina <= 1}
                className="px-3 py-1 border border-slate-300 rounded disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50"
              >
                Anterior
              </button>
              <button
                onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))}
                disabled={pagina >= totalPaginas}
                className="px-3 py-1 border border-slate-300 rounded disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50"
              >
                Próxima
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
