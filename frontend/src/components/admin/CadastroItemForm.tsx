'use client';

import type { ReactNode } from 'react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { cadastrarItem, ApiError, type Setor } from '@/lib/api';

const itemSchema = z.object({
  nome: z.string().trim().min(2, 'Informe o nome do item.').max(150, 'Use no máximo 150 caracteres.'),
  patrimonio: z.string().max(50, 'Use no máximo 50 caracteres.').optional(),
  codigoQr: z.string().max(120, 'Use no máximo 120 caracteres.').optional(),
  area: z.string().max(120, 'Use no máximo 120 caracteres.').optional(),
  setorId: z.string().min(1, 'Selecione um setor.'),
  quantidadeTotal: z.coerce.number().int('Informe um número inteiro.').positive('A quantidade deve ser maior que zero.').max(100000, 'Quantidade muito alta.'),
});
type ItemFormData = z.infer<typeof itemSchema>;

function CampoCadastro({ id, rotulo, erro, ajuda, children, largo = false }: { id: string; rotulo: string; erro?: string; ajuda?: string; children: ReactNode; largo?: boolean }) {
  return <div className={`stock-v2-field ${largo ? 'stock-v2-field--wide' : ''}`}><label htmlFor={id}>{rotulo}</label>{children}{ajuda && <small>{ajuda}</small>}{erro && <p className="stock-v2-field-error">{erro}</p>}</div>;
}

export default function CadastroItemForm({ setores, onItemCadastrado }: { setores: Setor[]; onItemCadastrado: () => void }) {
  const [mensagem, setMensagem] = useState<{ tipo: 'sucesso' | 'erro'; texto: string } | null>(null);
  const { register, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm<ItemFormData>({
    resolver: zodResolver(itemSchema),
    defaultValues: { nome: '', patrimonio: '', codigoQr: '', area: '', setorId: '', quantidadeTotal: 1 },
  });

  async function onSubmit(dados: ItemFormData) {
    setMensagem(null);
    try {
      await cadastrarItem({
        nome: dados.nome.trim(),
        patrimonio: dados.patrimonio?.trim() || undefined,
        codigo_qr: dados.codigoQr?.trim() || dados.patrimonio?.trim() || undefined,
        area: dados.area?.trim() || undefined,
        setor_id: Number(dados.setorId),
        quantidade_total: dados.quantidadeTotal,
      });
      setMensagem({ tipo: 'sucesso', texto: 'Item cadastrado no inventário com sucesso. A lista foi atualizada.' });
      reset({ nome: '', patrimonio: '', codigoQr: '', area: '', setorId: '', quantidadeTotal: 1 });
      onItemCadastrado();
    } catch (falha) {
      setMensagem({ tipo: 'erro', texto: falha instanceof ApiError ? falha.message : 'Não foi possível cadastrar o item. Confira os dados e tente novamente.' });
    }
  }

  return (
    <section className="stock-v2-form-card" aria-labelledby="stock-create-title">
      <div className="stock-v2-form-heading"><div><h3 id="stock-create-title">Dados do item</h3><p>Os campos marcados com * são necessários para registrar o item.</p></div><span className="stock-v2-required-tag">* Obrigatório</span></div>
      {mensagem && <div className={`stock-v2-alert ${mensagem.tipo === 'sucesso' ? 'stock-v2-alert--success' : 'stock-v2-alert--error'}`} role={mensagem.tipo === 'erro' ? 'alert' : 'status'}><span>{mensagem.texto}</span>{mensagem.tipo === 'sucesso' && <span className="stock-v2-success-mark" aria-hidden="true">✓</span>}</div>}
      <form onSubmit={handleSubmit(onSubmit)} className="stock-v2-create-form" noValidate>
        <div className="stock-v2-edit-grid">
          <CampoCadastro id="new-item-name" rotulo="Nome do item *" erro={errors.nome?.message} largo>
            <input id="new-item-name" {...register('nome')} placeholder="Ex.: Placa ESP32, multímetro, cabo USB" autoFocus aria-invalid={Boolean(errors.nome)} />
          </CampoCadastro>
          <CampoCadastro id="new-item-sector" rotulo="Setor *" erro={errors.setorId?.message}>
            <select id="new-item-sector" {...register('setorId')} aria-invalid={Boolean(errors.setorId)} disabled={setores.length === 0}>
              <option value="">{setores.length ? 'Selecione o setor responsável' : 'Setores indisponíveis'}</option>
              {setores.map((setor) => <option key={setor.id} value={String(setor.id)}>{setor.nome}</option>)}
            </select>
            {setores.length === 0 && <button type="button" className="stock-v2-inline-action" onClick={() => window.location.reload()}>Recarregar setores</button>}
          </CampoCadastro>
          <CampoCadastro id="new-item-patrimony" rotulo="Número de patrimônio" erro={errors.patrimonio?.message} ajuda="Opcional. Use um código único quando houver. ">
            <input id="new-item-patrimony" {...register('patrimonio')} placeholder="Ex.: AVT-001" aria-invalid={Boolean(errors.patrimonio)} />
          </CampoCadastro>
          <CampoCadastro id="new-item-qr" rotulo="Código QR" erro={errors.codigoQr?.message} ajuda="Opcional. Se vazio, o patrimônio será usado como identificador.">
            <input id="new-item-qr" {...register('codigoQr')} placeholder="Ex.: AVT-001 ou QR-0001" aria-invalid={Boolean(errors.codigoQr)} />
          </CampoCadastro>
          <CampoCadastro id="new-item-area" rotulo="Área" erro={errors.area?.message} ajuda="Opcional. Identifique o ambiente físico.">
            <input id="new-item-area" {...register('area')} placeholder="Ex.: Laboratório de eletrônica" aria-invalid={Boolean(errors.area)} />
          </CampoCadastro>
          <CampoCadastro id="new-item-quantity" rotulo="Quantidade inicial *" erro={errors.quantidadeTotal?.message} ajuda="Número inteiro maior que zero.">
            <input id="new-item-quantity" type="number" min={1} max={100000} step={1} {...register('quantidadeTotal')} aria-invalid={Boolean(errors.quantidadeTotal)} />
          </CampoCadastro>
        </div>
        <div className="stock-v2-create-actions"><p><strong>Dica:</strong> use o mesmo código no patrimônio e no QR quando o item tiver identificação patrimonial.</p><button type="submit" className="button button-primary" disabled={isSubmitting || setores.length === 0}>{isSubmitting ? <><span className="loading-inline loading-inline--light" /> Cadastrando…</> : 'Cadastrar item'}</button></div>
      </form>
    </section>
  );
}
