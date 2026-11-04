/**
 * Normaliza datas da API: os campos datetime do backend representam UTC,
 * mas alguns serializadores removem o sufixo Z. Sem esse sufixo, o browser
 * interpreta a data como horário local e pode exibir o dia incorreto.
 */
function interpretarDataApi(valor: string): Date {
  const temFuso = /(?:Z|[+-]\d{2}:\d{2})$/i.test(valor);
  return new Date(temFuso ? valor : `${valor}Z`);
}

export function formatarData(iso: string | null | undefined): string {
  if (!iso) return '—';
  const data = interpretarDataApi(iso);
  if (Number.isNaN(data.getTime())) return '—';
  return data.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

export function rotuloStatusEmprestimo(status: string): string {
  const rotulos: Record<string, string> = {
    EM_ANDAMENTO: 'Em andamento',
    DEVOLVIDO: 'Devolvido',
    PENDENTE_DEVOLUCAO: 'Aguardando conferência',
    ATRASADO: 'Atrasado',
  };
  return rotulos[status] || status.toLocaleLowerCase('pt-BR').replace(/_/g, ' ');
}
