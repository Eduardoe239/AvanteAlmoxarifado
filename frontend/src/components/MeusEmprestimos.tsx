'use client';

import { useEffect, useState } from 'react';
import { formatarData, rotuloStatusEmprestimo } from '@/lib/formatacao';
import {
  listarMeusEmprestimos,
  devolverMeuEmprestimo,
  ApiError,
  type Emprestimo,
} from '@/lib/api';

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

export default function MeusEmprestimos({
  refreshKey,
  onDevolucaoRegistrada,
}: {
  refreshKey: number;
  onDevolucaoRegistrada?: () => void;
}) {
  const [emprestimos, setEmprestimos] = useState<Emprestimo[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [devolvendoId, setDevolvendoId] = useState<number | null>(null);

  function carregar() {
    setCarregando(true);
    setErro(null);
    listarMeusEmprestimos()
      .then(setEmprestimos)
      .catch((e) => {
        const texto = e instanceof ApiError ? e.message : 'Não foi possível carregar seus empréstimos.';
        setErro(texto);
      })
      .finally(() => setCarregando(false));
  }

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey]);

  async function devolver(id: number) {
    setDevolvendoId(id);
    try {
      await devolverMeuEmprestimo(id);
      carregar();
      onDevolucaoRegistrada?.();
    } catch (e) {
      const texto = e instanceof ApiError ? e.message : 'Não foi possível registrar a devolução.';
      setErro(texto);
    } finally {
      setDevolvendoId(null);
    }
  }

  const emAberto = emprestimos.filter((e) => e.status !== 'DEVOLVIDO');
  const devolvidos = emprestimos.filter((e) => e.status === 'DEVOLVIDO');
  const atrasados = emprestimos.filter((e) => e.status === 'ATRASADO');

  return (
    <div className="max-w-xl mx-auto mt-8">
      <h2 className="text-xl font-bold text-slate-800 mb-4">Meus empréstimos</h2>

      {!carregando && !erro && atrasados.length > 0 && (
        <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm font-medium">
          ⚠️ Você tem {atrasados.length} item{atrasados.length > 1 ? 's' : ''} em atraso. Devolva o
          quanto antes.
        </div>
      )}

      {carregando && <p className="workflow-loading"><span className="loading-inline" /> Carregando seus empréstimos…</p>}
      {erro && !carregando && <div role="alert" className="workflow-error"><span>{erro}</span><button type="button" onClick={carregar}>Tentar novamente</button></div>}

      {!carregando && !erro && emprestimos.length === 0 && (
        <div className="workflow-empty"><strong>Você ainda não tem empréstimos</strong><p>Quando solicitar um equipamento, você acompanhará o prazo e a devolução por aqui.</p></div>
      )}

      {!carregando && !erro && emAberto.length > 0 && (
        <div className="space-y-3 mb-6">
          {emAberto.map((e) => (
            <div
              key={e.id}
              className="bg-white rounded-lg shadow border border-gray-100 p-4 flex items-center justify-between"
            >
              <div>
                <p className="font-semibold text-slate-800">{e.item_nome}</p>
                <p className="text-sm text-slate-500">
                  Retirado em {formatarData(e.data_retirada)} · devolução prevista{' '}
                  {formatarData(e.data_devolucao_prevista)}
                </p>
                <span
                  className={`inline-block mt-1 px-2 py-0.5 rounded-md text-xs font-semibold ${corDoStatus(
                    e.status
                  )}`}
                >
                  {rotuloStatusEmprestimo(e.status)}
                </span>
              </div>
              <button
                onClick={() => devolver(e.id)}
                disabled={devolvendoId === e.id || e.status === 'PENDENTE_DEVOLUCAO'}
                className="bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {devolvendoId === e.id ? 'Enviando solicitação…' : e.status === 'PENDENTE_DEVOLUCAO' ? 'Aguardando conferência' : 'Solicitar devolução'}
              </button>
            </div>
          ))}
        </div>
      )}

      {!carregando && !erro && devolvidos.length > 0 && (
        <details className="text-sm text-slate-500">
          <summary className="cursor-pointer font-medium mb-2">
            Histórico de devoluções ({devolvidos.length})
          </summary>
          <div className="space-y-2 mt-2">
            {devolvidos.map((e) => (
              <div key={e.id} className="flex justify-between border-b border-slate-100 pb-1">
                <span>{e.item_nome}</span>
                <span>devolvido em {e.data_devolucao_real ? formatarData(e.data_devolucao_real) : '—'}</span>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
