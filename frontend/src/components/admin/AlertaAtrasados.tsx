'use client';

import { useEffect, useState } from 'react';
import { obterResumoAtrasados, type ResumoAtrasados } from '@/lib/api';

export default function AlertaAtrasados({ refreshKey }: { refreshKey: number }) {
  const [resumo, setResumo] = useState<ResumoAtrasados | null>(null);

  useEffect(() => {
    // Falha silenciosa de propósito: este é um banner informativo a mais,
    // não deve quebrar o painel se der erro — a lista completa de
    // empréstimos (que já mostra status ATRASADO por linha) continua
    // funcionando normalmente de qualquer forma.
    obterResumoAtrasados()
      .then(setResumo)
      .catch(() => setResumo(null));
  }, [refreshKey]);

  if (!resumo || resumo.total_atrasados === 0) return null;

  return (
    <div className="max-w-3xl mx-auto mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-800 font-medium">
      ⚠️ {resumo.total_atrasados} empréstimo{resumo.total_atrasados > 1 ? 's' : ''} atrasado
      {resumo.total_atrasados > 1 ? 's' : ''} no momento — confira a aba &ldquo;Empréstimos&rdquo;.
    </div>
  );
}
