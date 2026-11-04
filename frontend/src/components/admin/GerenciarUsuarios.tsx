'use client';

import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  listarUsuariosAdmin,
  desativarUsuario,
  reativarUsuario,
  editarUsuario,
  excluirUsuario,
  ApiError,
  type UsuarioAdmin,
  type Usuario,
  type Setor,
  type DadosEdicaoUsuario,
} from '@/lib/api';

const edicaoSchema = z.object({
  nomeCompleto: z
    .string()
    .min(3, 'Informe o nome completo.')
    .refine((v) => v.trim().length >= 3 && v.trim().split(/\s+/).length >= 2, 'Informe nome e sobrenome.'),
  username: z
    .string()
    .min(3, 'Mínimo de 3 caracteres.')
    .regex(/^[a-zA-Z0-9._-]+$/, 'Use apenas letras, números, ponto, hífen ou underscore.'),
  email: z.union([
    z.string().email('Informe um e-mail válido.'),
    z.literal(''),
  ]),
  setorId: z.string().optional(),
  novaSenha: z
    .string()
    .optional()
    .refine((v) => !v || (v.length >= 8 && /[A-Za-z]/.test(v) && /[0-9]/.test(v)), {
      message: 'A nova senha precisa ter 8+ caracteres, com letra e número.',
    }),
});
type EdicaoFormData = z.infer<typeof edicaoSchema>;

function LinhaUsuario({
  usuario,
  setores,
  ehVoceMesmo,
  onAtualizado,
}: {
  usuario: UsuarioAdmin;
  setores: Setor[];
  ehVoceMesmo: boolean;
  onAtualizado: () => void;
}) {
  const [editando, setEditando] = useState(false);
  const [confirmandoExclusao, setConfirmandoExclusao] = useState(false);
  const [processando, setProcessando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<EdicaoFormData>({
    resolver: zodResolver(edicaoSchema),
    defaultValues: {
      nomeCompleto: usuario.nome_completo || '',
      username: usuario.username,
      email: usuario.email || '',
      setorId: usuario.setor_id ? String(usuario.setor_id) : '',
      novaSenha: '',
    },
  });

  function iniciarEdicao() {
    reset({
      nomeCompleto: usuario.nome_completo || '',
      username: usuario.username,
      email: usuario.email || '',
      setorId: usuario.setor_id ? String(usuario.setor_id) : '',
      novaSenha: '',
    });
    setErro(null);
    setEditando(true);
  }

  async function salvar(dados: EdicaoFormData) {
    setErro(null);
    try {
      const payload: DadosEdicaoUsuario = {
        nome_completo: dados.nomeCompleto.trim(),
        username: dados.username.trim(),
        email: dados.email.trim() || null,
        setor_id: dados.setorId ? Number(dados.setorId) : null,
      };
      if (dados.novaSenha?.trim()) payload.nova_senha = dados.novaSenha;

      await editarUsuario(usuario.id, payload);
      setEditando(false);
      onAtualizado();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : 'Não foi possível salvar as alterações.');
    }
  }

  async function alternarStatus() {
    if (usuario.ativo && !window.confirm(`Desativar o acesso de ${usuario.nome_completo || usuario.username}? A pessoa não poderá entrar no sistema até ser reativada.`)) return;
    setProcessando(true);
    setErro(null);
    try {
      if (usuario.ativo) {
        await desativarUsuario(usuario.id);
      } else {
        await reativarUsuario(usuario.id);
      }
      onAtualizado();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : 'Não foi possível alterar o status do usuário.');
    } finally {
      setProcessando(false);
    }
  }

  async function confirmarExclusao() {
    setProcessando(true);
    setErro(null);
    try {
      await excluirUsuario(usuario.id);
      onAtualizado();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : 'Não foi possível excluir o usuário.');
      setConfirmandoExclusao(false);
    } finally {
      setProcessando(false);
    }
  }

  if (editando) {
    return (
      <tr className="border-b border-slate-100 bg-slate-50">
        <td className="py-2 pr-2" colSpan={7}>
          <form onSubmit={handleSubmit(salvar)} className="flex flex-wrap items-start gap-2 p-2">
            <div>
              <input
                {...register('nomeCompleto')}
                className="p-2 border border-slate-300 rounded text-sm w-40"
                placeholder="Nome completo"
              />
              {errors.nomeCompleto && (
                <p className="text-red-500 text-xs mt-1">{errors.nomeCompleto.message}</p>
              )}
            </div>
            <div>
              <input
                {...register('username')}
                className="p-2 border border-slate-300 rounded text-sm w-32"
                placeholder="Usuário"
              />
              {errors.username && <p className="text-red-500 text-xs mt-1">{errors.username.message}</p>}
            </div>
            <div>
              <input
                {...register('email')}
                type="email"
                className="p-2 border border-slate-300 rounded text-sm w-44"
                placeholder="E-mail"
              />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
            </div>
            {/* O setor vale para qualquer usuário, admin incluído — um
                administrador também pertence a um setor da organização. */}
            <div>
              <select {...register('setorId')} className="p-2 border border-slate-300 rounded text-sm bg-white">
                <option value="">Sem setor</option>
                {setores.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.nome}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <input
                {...register('novaSenha')}
                type="password"
                className="p-2 border border-slate-300 rounded text-sm w-40"
                placeholder="Nova senha (opcional)"
              />
              {errors.novaSenha && <p className="text-red-500 text-xs mt-1">{errors.novaSenha.message}</p>}
            </div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-3 py-2 bg-slate-900 text-white rounded text-sm font-semibold disabled:opacity-60"
            >
              Salvar
            </button>
            <button
              type="button"
              onClick={() => setEditando(false)}
              className="px-3 py-2 text-slate-500 text-sm hover:text-slate-800"
            >
              Cancelar
            </button>
          </form>
          {erro && <p className="text-red-600 text-xs px-2 pb-2">{erro}</p>}
        </td>
      </tr>
    );
  }

  if (confirmandoExclusao) {
    return (
      <tr className="border-b border-slate-100 bg-red-50">
        <td className="py-3 px-2" colSpan={7}>
          <div className="flex items-center justify-between">
            <p className="text-sm text-red-800 font-medium">
              Excluir permanentemente <strong>{usuario.nome_completo || usuario.username}</strong>? O
              histórico de empréstimos dessa pessoa é preservado, mas a conta não pode ser recuperada.
            </p>
            <div className="flex gap-2 shrink-0 ml-4">
              <button
                onClick={confirmarExclusao}
                disabled={processando}
                className="px-3 py-1.5 bg-red-600 text-white rounded text-sm font-semibold hover:bg-red-700 disabled:opacity-60"
              >
                {processando ? 'Excluindo...' : 'Sim, excluir'}
              </button>
              <button
                onClick={() => setConfirmandoExclusao(false)}
                disabled={processando}
                className="px-3 py-1.5 border border-slate-300 rounded text-sm text-slate-600 hover:bg-slate-50"
              >
                Cancelar
              </button>
            </div>
          </div>
          {erro && <p className="text-red-600 text-xs mt-2">{erro}</p>}
        </td>
      </tr>
    );
  }

  return (
    <tr className="border-b border-slate-100">
      <td className="py-2 pr-4 text-slate-800">
        {usuario.nome_completo || '—'}
        {ehVoceMesmo && <span className="text-slate-400 text-xs ml-1">(você)</span>}
      </td>
      <td className="py-2 pr-4 text-slate-600">{usuario.username}</td>
      <td className="py-2 pr-4 text-slate-600">{usuario.email || '—'}</td>
      <td className="py-2 pr-4 text-slate-600">{usuario.setor_nome || '—'}</td>
      <td className="py-2 pr-4 text-slate-600">{usuario.is_admin ? 'Administrador' : 'Membro'}</td>
      <td className="py-2 pr-4">
        <span
          className={`px-2 py-1 rounded-md text-xs font-semibold ${
            usuario.ativo ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'
          }`}
        >
          {usuario.ativo ? 'Ativo' : 'Inativo'}
        </span>
      </td>
      <td className="py-2 pr-4 whitespace-nowrap">
        <button
          onClick={iniciarEdicao}
          className="text-blue-700 hover:text-blue-900 text-sm font-semibold mr-3"
        >
          Editar
        </button>
        {ehVoceMesmo ? (
          <span className="text-slate-400 text-sm">—</span>
        ) : (
          <>
            <button
              onClick={alternarStatus}
              disabled={processando}
              className={`text-sm font-semibold mr-3 disabled:opacity-60 ${
                usuario.ativo ? 'text-orange-600 hover:text-orange-800' : 'text-green-700 hover:text-green-900'
              }`}
            >
              {usuario.ativo ? 'Desativar' : 'Reativar'}
            </button>
            <button
              onClick={() => setConfirmandoExclusao(true)}
              className="text-red-600 hover:text-red-800 text-sm font-semibold"
            >
              Excluir
            </button>
          </>
        )}
        {erro && <p className="text-red-600 text-xs mt-1">{erro}</p>}
      </td>
    </tr>
  );
}

export default function GerenciarUsuarios({
  usuarioLogado,
  setores,
  refreshKey,
}: {
  usuarioLogado: Usuario;
  setores: Setor[];
  refreshKey: number;
}) {
  const [usuarios, setUsuarios] = useState<UsuarioAdmin[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [versao, setVersao] = useState(0);

  useEffect(() => {
    setCarregando(true);
    setErro(null);
    listarUsuariosAdmin()
      .then(setUsuarios)
      .catch((e) => setErro(e instanceof ApiError ? e.message : 'Não foi possível carregar os usuários.'))
      .finally(() => setCarregando(false));
  }, [refreshKey, versao]);

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-8">
      <h2 className="text-xl font-bold text-slate-800 mb-6">Usuários cadastrados</h2>

      {carregando && <p className="text-slate-500">Carregando...</p>}
      {erro && !carregando && <p className="text-red-600 font-medium">{erro}</p>}

      {!carregando && !erro && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500">
                <th className="py-2 pr-4 font-semibold">Nome</th>
                <th className="py-2 pr-4 font-semibold">Usuário</th>
                <th className="py-2 pr-4 font-semibold">E-mail</th>
                <th className="py-2 pr-4 font-semibold">Setor</th>
                <th className="py-2 pr-4 font-semibold">Papel</th>
                <th className="py-2 pr-4 font-semibold">Status</th>
                <th className="py-2 pr-4 font-semibold">Ações</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map((u) => (
                <LinhaUsuario
                  key={u.id}
                  usuario={u}
                  setores={setores}
                  ehVoceMesmo={u.id === usuarioLogado.id}
                  onAtualizado={() => setVersao((v) => v + 1)}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
