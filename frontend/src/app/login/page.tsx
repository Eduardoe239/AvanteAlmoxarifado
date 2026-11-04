'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { login, cadastrarMembro, listarSetores, ApiError, type Setor } from '@/lib/api';

const loginSchema = z.object({
  username: z.string().min(1, 'Informe o usuário.'),
  senha: z.string().min(1, 'Informe a senha.'),
});
type LoginFormData = z.infer<typeof loginSchema>;

// Mantido em sincronia com a validação do backend (schemas.py:_validar_senha_forte).
const cadastroSchema = z
  .object({
    nomeCompleto: z
      .string()
      .min(3, 'Informe seu nome completo.')
      .refine((v) => v.trim().split(/\s+/).length >= 2, 'Informe nome e sobrenome.'),
    setorId: z.string().min(1, 'Selecione um setor.'),
    username: z
      .string()
      .min(3, 'Mínimo de 3 caracteres.')
      .regex(/^[a-zA-Z0-9._-]+$/, 'Use apenas letras, números, ponto, hífen ou underscore.'),
    email: z.string().min(1, 'Informe seu e-mail.').email('Informe um e-mail válido.'),
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
type CadastroFormData = z.infer<typeof cadastroSchema>;

export default function LoginPage() {
  const router = useRouter();
  const [aba, setAba] = useState<'entrar' | 'cadastro'>('entrar');
  const [erro, setErro] = useState<string | null>(null);
  const [setores, setSetores] = useState<Setor[]>([]);
  const [carregandoSetores, setCarregandoSetores] = useState(true);
  const [erroSetores, setErroSetores] = useState(false);

  useEffect(() => {
    listarSetores()
      .then(setSetores)
      .catch(() => setErroSetores(true))
      .finally(() => setCarregandoSetores(false));
  }, []);

  const loginForm = useForm<LoginFormData>({ resolver: zodResolver(loginSchema) });
  const cadastroForm = useForm<CadastroFormData>({ resolver: zodResolver(cadastroSchema) });

  async function onSubmitLogin(dados: LoginFormData) {
    setErro(null);
    try {
      await login(dados.username, dados.senha);
      router.push('/');
    } catch (e) {
      const mensagem = e instanceof ApiError ? e.message : 'Não foi possível entrar. Tente novamente.';
      setErro(mensagem);
    }
  }

  async function onSubmitCadastro(dados: CadastroFormData) {
    setErro(null);
    try {
      await cadastrarMembro({
        username: dados.username,
        senha: dados.senha,
        nome_completo: dados.nomeCompleto,
        email: dados.email,
        setor_id: Number(dados.setorId),
      });
      // Cadastro concluído — loga automaticamente para não pedir os dados de novo.
      await login(dados.username, dados.senha);
      router.push('/');
    } catch (e) {
      const mensagem = e instanceof ApiError ? e.message : 'Não foi possível concluir o cadastro.';
      setErro(mensagem);
    }
  }

  function trocarAba(novaAba: 'entrar' | 'cadastro') {
    setAba(novaAba);
    setErro(null);
  }

  return (
    <main className="min-h-screen bg-slate-50 flex items-center justify-center p-6 login-shell">
      <div className="login-card">
        <div className="login-brand"><span className="login-brand-mark"><svg viewBox="0 0 24 24" width="23" height="23" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="m12 2 9 5v10l-9 5-9-5V7l9-5Z"/><path d="m3 7 9 5 9-5M12 12v10"/></svg></span><div><strong>AVANTE</strong><small>ALMOXARIFADO</small></div></div>
        <h1 className="text-2xl font-bold text-slate-800 mb-2 text-center">Acesse sua conta</h1>
        <p className="login-lede">Gestão de equipamentos e materiais do laboratório.</p>

        <div className="flex mb-6 border border-slate-200 rounded-lg overflow-hidden login-tabs">
          <button
            type="button"
            onClick={() => trocarAba('entrar')}
            className={`flex-1 py-2 text-sm font-semibold transition-colors ${
              aba === 'entrar' ? 'bg-slate-900 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
            }`}
          >
            Entrar
          </button>
          <button
            type="button"
            onClick={() => trocarAba('cadastro')}
            className={`flex-1 py-2 text-sm font-semibold transition-colors ${
              aba === 'cadastro' ? 'bg-slate-900 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
            }`}
          >
            Cadastro
          </button>
        </div>

        {erro && (
          <div className="p-3 mb-5 rounded-md bg-red-50 text-red-700 text-sm font-medium">
            {erro}
          </div>
        )}

        {aba === 'entrar' && (
          <form onSubmit={loginForm.handleSubmit(onSubmitLogin)} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Usuário</label>
              <input
                {...loginForm.register('username')}
                type="text"
                autoComplete="username"
                className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              />
              {loginForm.formState.errors.username && (
                <p className="text-red-500 text-sm mt-1">
                  {loginForm.formState.errors.username.message}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Senha</label>
              <input
                {...loginForm.register('senha')}
                type="password"
                autoComplete="current-password"
                className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              />
              {loginForm.formState.errors.senha && (
                <p className="text-red-500 text-sm mt-1">{loginForm.formState.errors.senha.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loginForm.formState.isSubmitting}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-70 disabled:cursor-not-allowed mt-2"
            >
              {loginForm.formState.isSubmitting ? 'Entrando...' : 'Entrar'}
            </button>
          </form>
        )}

        {aba === 'cadastro' && (
          <form onSubmit={cadastroForm.handleSubmit(onSubmitCadastro)} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Nome completo</label>
              <input
                {...cadastroForm.register('nomeCompleto')}
                type="text"
                autoComplete="name"
                className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              />
              {cadastroForm.formState.errors.nomeCompleto && (
                <p className="text-red-500 text-sm mt-1">
                  {cadastroForm.formState.errors.nomeCompleto.message}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Setor</label>
              {erroSetores ? (
                <p className="text-red-500 text-sm">
                  Não foi possível carregar a lista de setores. Recarregue a página.
                </p>
              ) : (
                <select
                  {...cadastroForm.register('setorId')}
                  disabled={carregandoSetores}
                  defaultValue=""
                  className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all bg-white disabled:opacity-60"
                >
                  <option value="" disabled>
                    {carregandoSetores ? 'Carregando...' : 'Selecione um setor'}
                  </option>
                  {setores.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.nome}
                    </option>
                  ))}
                </select>
              )}
              {cadastroForm.formState.errors.setorId && (
                <p className="text-red-500 text-sm mt-1">
                  {cadastroForm.formState.errors.setorId.message}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Usuário</label>
              <input
                {...cadastroForm.register('username')}
                type="text"
                autoComplete="username"
                className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              />
              {cadastroForm.formState.errors.username && (
                <p className="text-red-500 text-sm mt-1">
                  {cadastroForm.formState.errors.username.message}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">E-mail</label>
              <input
                {...cadastroForm.register('email')}
                type="email"
                autoComplete="email"
                placeholder="voce@exemplo.com"
                className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              />
              {cadastroForm.formState.errors.email && (
                <p className="text-red-500 text-sm mt-1">{cadastroForm.formState.errors.email.message}</p>
              )}
              <p className="text-slate-400 text-xs mt-1">
                Usado para notificações futuras (ex: aviso de atraso na devolução).
              </p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Senha</label>
              <input
                {...cadastroForm.register('senha')}
                type="password"
                autoComplete="new-password"
                className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              />
              {cadastroForm.formState.errors.senha && (
                <p className="text-red-500 text-sm mt-1">{cadastroForm.formState.errors.senha.message}</p>
              )}
              <p className="text-slate-400 text-xs mt-1">Mínimo 8 caracteres, com letra e número.</p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Confirmar senha</label>
              <input
                {...cadastroForm.register('confirmarSenha')}
                type="password"
                autoComplete="new-password"
                className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              />
              {cadastroForm.formState.errors.confirmarSenha && (
                <p className="text-red-500 text-sm mt-1">
                  {cadastroForm.formState.errors.confirmarSenha.message}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={cadastroForm.formState.isSubmitting || carregandoSetores || erroSetores}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-70 disabled:cursor-not-allowed mt-2"
            >
              {cadastroForm.formState.isSubmitting ? 'Cadastrando...' : 'Cadastrar'}
            </button>
          </form>
        )}
      </div>
    </main>
  );
}
