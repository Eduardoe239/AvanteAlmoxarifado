'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { cadastrarAdministrador, ApiError, type Setor } from '@/lib/api';

// Mesmas regras de senha do backend (schemas.py:_validar_senha_forte).
const adminSchema = z
  .object({
    nomeCompleto: z
      .string()
      .min(3, 'Informe o nome completo.')
      .refine((v) => v.trim().split(/\s+/).length >= 2, 'Informe nome e sobrenome.'),
    username: z
      .string()
      .min(3, 'Mínimo de 3 caracteres.')
      .regex(/^[a-zA-Z0-9._-]+$/, 'Use apenas letras, números, ponto, hífen ou underscore.'),
    email: z.string().min(1, 'Informe o e-mail.').email('Informe um e-mail válido.'),
    setorId: z.string().min(1, 'Selecione um setor.'),
    senha: z
      .string()
      .min(8, 'A senha deve ter pelo menos 8 caracteres.')
      .regex(/[A-Za-z]/, 'A senha deve conter pelo menos uma letra.')
      .regex(/[0-9]/, 'A senha deve conter pelo menos um número.'),
    confirmarSenha: z.string(),
  })
  .refine((d) => d.senha === d.confirmarSenha, {
    message: 'As senhas não coincidem.',
    path: ['confirmarSenha'],
  });
type AdminFormData = z.infer<typeof adminSchema>;

export default function CadastroAdminForm({
  setores,
  onAdminCadastrado,
}: {
  setores: Setor[];
  onAdminCadastrado?: () => void;
}) {
  const [mensagem, setMensagem] = useState<{ tipo: 'sucesso' | 'erro'; texto: string } | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<AdminFormData>({ resolver: zodResolver(adminSchema) });

  const onSubmit = async (dados: AdminFormData) => {
    setMensagem(null);
    try {
      await cadastrarAdministrador({
        username: dados.username,
        senha: dados.senha,
        nome_completo: dados.nomeCompleto,
        email: dados.email,
        setor_id: Number(dados.setorId),
      });
      setMensagem({ tipo: 'sucesso', texto: 'Novo administrador cadastrado com sucesso.' });
      reset();
      onAdminCadastrado?.();
    } catch (e) {
      const texto = e instanceof ApiError ? e.message : 'Não foi possível cadastrar o administrador.';
      setMensagem({ tipo: 'erro', texto });
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-8">
      <h2 className="text-xl font-bold text-slate-800 mb-2">Cadastrar novo administrador</h2>
      <p className="text-sm text-slate-500 mb-6">
        A pessoa cadastrada aqui terá acesso completo ao painel administrativo.
      </p>

      {mensagem && (
        <div
          className={`p-3 mb-5 rounded-md text-sm font-medium ${
            mensagem.tipo === 'sucesso' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}
        >
          {mensagem.texto}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Nome completo</label>
          <input
            {...register('nomeCompleto')}
            type="text"
            className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          />
          {errors.nomeCompleto && <p className="text-red-500 text-sm mt-1">{errors.nomeCompleto.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Usuário</label>
          <input
            {...register('username')}
            type="text"
            className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          />
          {errors.username && <p className="text-red-500 text-sm mt-1">{errors.username.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">E-mail</label>
          <input
            {...register('email')}
            type="email"
            className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          />
          {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Setor</label>
          <select
            {...register('setorId')}
            defaultValue=""
            className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all bg-white"
          >
            <option value="" disabled>
              Selecione um setor
            </option>
            {setores.map((s) => (
              <option key={s.id} value={s.id}>
                {s.nome}
              </option>
            ))}
          </select>
          {errors.setorId && <p className="text-red-500 text-sm mt-1">{errors.setorId.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Senha</label>
          <input
            {...register('senha')}
            type="password"
            autoComplete="new-password"
            className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          />
          {errors.senha && <p className="text-red-500 text-sm mt-1">{errors.senha.message}</p>}
          <p className="text-slate-400 text-xs mt-1">Mínimo 8 caracteres, com letra e número.</p>
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Confirmar senha</label>
          <input
            {...register('confirmarSenha')}
            type="password"
            autoComplete="new-password"
            className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          />
          {errors.confirmarSenha && (
            <p className="text-red-500 text-sm mt-1">{errors.confirmarSenha.message}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-70 disabled:cursor-not-allowed mt-2"
        >
          {isSubmitting ? 'Cadastrando...' : 'Cadastrar administrador'}
        </button>
      </form>
    </div>
  );
}
