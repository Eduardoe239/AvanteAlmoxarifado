'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { criarEmprestimo, ApiError, type Item } from '@/lib/api';
import { formatarData } from '@/lib/formatacao';

// Espelha exatamente a regra do backend (schemas.py:EmprestimoCreate):
// mínimo 1 dia, máximo 30 dias — nada abaixo de zero, nada acima de 30.
// quantidade: mínimo 1, máximo 100, com validação contextual
const emprestimoSchema = z.object({
  item_id: z.coerce.number().positive('Selecione um item válido.'),
  dias_solicitados: z.coerce
    .number()
    .int('Informe um número inteiro de dias.')
    .min(1, 'O tempo mínimo é de 1 dia.')
    .max(30, 'O prazo máximo é de 30 dias.'),
  quantidade: z.coerce
    .number()
    .int('Informe um número inteiro de unidades.')
    .min(1, 'O mínimo é 1 unidade.')
    .max(100, 'O máximo é 100 unidades.'),
});

type EmprestimoFormData = z.infer<typeof emprestimoSchema>;

type FormularioEmprestimoProps = {
  itens: Item[];
  onEmprestimoRegistrado?: () => void;
};

export default function FormularioEmprestimo({ itens, onEmprestimoRegistrado }: FormularioEmprestimoProps) {
  const [mensagem, setMensagem] = useState<{ tipo: 'sucesso' | 'erro'; texto: string } | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
  } = useForm<EmprestimoFormData>({ 
    resolver: zodResolver(emprestimoSchema),
    defaultValues: { quantidade: 1 },
  });

  const itemIdField = register('item_id');
  const itemIdValue = watch('item_id');
  const quantidadeValue = watch('quantidade');

  // Valores de campos select chegam como string no navegador; normalize para comparar com o ID numérico.
  const itemSelecionado = itemIdValue ? itens.find((i) => i.id === Number(itemIdValue)) : null;

  // Validar se quantidade não excede disponível
  const quantidadeExcedeDisponivel =
    itemSelecionado && quantidadeValue > itemSelecionado.quantidade_disponivel;
  const itensDisponiveis = itens.filter((item) => item.status === 'ATIVO' && item.quantidade_disponivel > 0);

  const onSubmit = async (data: EmprestimoFormData) => {
    setMensagem(null);

    // Validação final antes de enviar
    if (quantidadeExcedeDisponivel) {
      setMensagem({
        tipo: 'erro',
        texto: `Quantidade indisponível. Máximo: ${itemSelecionado?.quantidade_disponivel}`,
      });
      return;
    }

    try {
      const resultado = await criarEmprestimo(data.item_id, data.dias_solicitados, data.quantidade);
      setMensagem({
        tipo: 'sucesso',
        texto: `Empréstimo registrado! (${data.quantidade} un.) Devolução prevista para: ${formatarData(resultado.data_devolucao_prevista)}`,
      });
      reset();
      onEmprestimoRegistrado?.();
    } catch (error) {
      const mensagemErro = error instanceof ApiError ? error.message : 'Erro ao registrar empréstimo.';
      setMensagem({ tipo: 'erro', texto: mensagemErro });
    }
  };

  return (
    <section className="member-form-card bg-white rounded-xl shadow-lg border border-gray-100">
      <div className="member-card-heading"><span className="member-card-icon">↗</span><div><h2 className="text-2xl font-bold text-slate-800">Solicitar empréstimo</h2><p>Escolha o equipamento e informe o prazo de utilização.</p></div></div>

      {mensagem && (
        <div
          className={`p-4 mb-6 rounded-md font-medium ${
            mensagem.tipo === 'sucesso' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}
        >
          {mensagem.texto}
        </div>
      )}

      {itensDisponiveis.length === 0 ? (
        <div className="member-no-stock"><strong>{itens.length === 0 ? 'Nenhum equipamento ativo para empréstimo' : 'Nenhuma unidade disponível no momento'}</strong><p>{itens.length === 0 ? 'No momento, não há equipamentos ativos para solicitar. Fale com o responsável pelo almoxarifado ou consulte novamente mais tarde.' : 'Todos os itens ativos estão emprestados ou sem unidades disponíveis. Consulte novamente mais tarde.'}</p></div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">Item do catálogo</label>
            <select
              {...itemIdField}
              defaultValue=""
              className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all bg-white"
            >
              <option value="" disabled>
                Selecione o equipamento...
              </option>
              {itens.map((item) => (
                <option key={item.id} value={item.id} disabled={item.quantidade_disponivel <= 0}>
                  {item.nome} ({item.quantidade_disponivel} disponíve
                  {item.quantidade_disponivel === 1 ? 'l' : 'is'})
                </option>
              ))}
            </select>
            {errors.item_id && <p className="text-red-500 text-sm mt-1">{errors.item_id.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">
              Quantidade de unidades
            </label>
            <input
              type="number"
              min={1}
              max={itemSelecionado?.quantidade_disponivel ?? 100}
              step={1}
              {...register('quantidade')}
              placeholder="Ex: 1"
              className={`w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all ${
                quantidadeExcedeDisponivel ? 'border-red-500 bg-red-50' : 'border-slate-300'
              }`}
            />
            {errors.quantidade && <p className="text-red-500 text-sm mt-1">{errors.quantidade.message}</p>}
            {itemSelecionado && (
              <p className="text-slate-600 text-sm mt-1">
                Disponível: {itemSelecionado.quantidade_disponivel} unidade
                {itemSelecionado.quantidade_disponivel === 1 ? '' : 's'}
              </p>
            )}
            {quantidadeExcedeDisponivel && (
              <p className="text-red-500 text-sm mt-1">Quantidade excede a disponível!</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">
              Dias de permanência (1 a 30)
            </label>
            <input
              type="number"
              min={1}
              max={30}
              step={1}
              {...register('dias_solicitados')}
              placeholder="Ex: 7"
              className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            />
            {errors.dias_solicitados && (
              <p className="text-red-500 text-sm mt-1">{errors.dias_solicitados.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 px-4 rounded-lg transition-colors flex justify-center items-center disabled:opacity-70 disabled:cursor-not-allowed mt-4"
          >
            {isSubmitting ? <span className="animate-pulse">Processando...</span> : 'Registrar Empréstimo'}
          </button>
        </form>
      )}
    </section>
  );
}
