'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { obterUsuarioAtual, type Usuario } from '@/lib/api';
import MeuPerfil from '@/components/MeuPerfil';
import Header from '@/components/Header';

export default function PaginaPerfil() {
  const router = useRouter();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    const verificarAutenticacao = async () => {
      const usuarioAtual = await obterUsuarioAtual();
      if (!usuarioAtual) {
        router.push('/login');
        return;
      }
      setUsuario(usuarioAtual);
      setCarregando(false);
    };

    verificarAutenticacao();
  }, [router]);

  // Enquanto a sessão não é confirmada, não renderiza nada do perfil —
  // evita piscar o conteúdo antes de um eventual redirect para /login.
  if (carregando || !usuario) {
    return (
      <div className="profile-page-shell">
        <p className="text-center text-slate-500">Carregando perfil...</p>
      </div>
    );
  }

  return (
    <div className="profile-page-shell">
      <Header usuario={usuario} paginaAtual="perfil" />
      <MeuPerfil onUsuarioAtualizado={setUsuario} />
    </div>
  );
}
