'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { logout, type Usuario } from '@/lib/api';

type HeaderProps = { usuario: Usuario; paginaAtual: 'inicio' | 'admin' | 'perfil' };

export default function Header({ usuario, paginaAtual }: HeaderProps) {
  const router = useRouter();
  const [saindo, setSaindo] = useState(false);
  async function sair() {
    if (saindo) return;
    setSaindo(true);
    try { await logout(); } finally { router.replace('/login'); }
  }

  const nome = usuario.nome_completo || usuario.username;
  const inicial = nome.trim().charAt(0).toUpperCase() || 'U';
  return (
    <header className="app-header">
      <Link href="/" className="header-brand" aria-label="Avante Almoxarifado — início">
        <span className="header-brand-mark"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 2 9 5v10l-9 5-9-5V7l9-5Z"/><path d="m3 7 9 5 9-5M12 12v10"/></svg></span>
        <span><strong>AVANTE</strong><small>ALMOXARIFADO</small></span>
      </Link>
      <div className="header-user-area">
        <span className="header-greeting"><small>Bem-vindo(a),</small><strong>{nome}</strong></span>
        <span className="avatar-initials header-avatar overflow-hidden">{usuario.foto_perfil ? <img src={usuario.foto_perfil} alt="Foto do usuário" className="h-full w-full object-cover" /> : inicial}</span>
        <div className="header-links">
          {usuario.is_admin && paginaAtual === 'inicio' && <Link href="/admin" className="header-link">Painel administrativo</Link>}
          {((usuario.is_admin && paginaAtual === 'admin') || paginaAtual === 'perfil') && <Link href="/" className="header-link">Almoxarifado</Link>}
          {paginaAtual !== 'perfil' && <Link href="/perfil" className="header-link">Meu perfil</Link>}
          <button type="button" onClick={() => void sair()} disabled={saindo} className="header-link header-logout">{saindo ? 'Saindo…' : 'Sair'}</button>
        </div>
      </div>
    </header>
  );
}
