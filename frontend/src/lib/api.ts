const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL && typeof window !== 'undefined') {
  // Falha alto e cedo em vez de deixar todo fetch quebrar silenciosamente.
  console.error(
    'NEXT_PUBLIC_API_URL não está definida. Configure o .env.local (veja .env.local.example).'
  );
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export type Usuario = {
  id: number;
  username: string;
  nome_completo: string | null;
  email: string | null;
  setor_id: number | null;
  is_admin: boolean;
  foto_perfil?: string | null;
};

export type Setor = {
  id: number;
  nome: string;
};

export type Item = {
  id: number;
  nome: string;
  patrimonio: string | null;
  codigo_qr: string | null;
  area: string | null;
  setor_atual_id: number | null;
  quantidade_total: number;
  quantidade_disponivel: number;
  status: string;
};

export type Emprestimo = {
  id: number;
  item_id: number;
  item_nome: string;
  dias_solicitados: number;
  data_retirada: string;
  data_devolucao_prevista: string;
  data_limite_tolerancia: string;
  data_devolucao_real: string | null;
  status: string;
};

export type EmprestimoAdmin = {
  id: number;
  item_id: number;
  item_nome: string;
  usuario_id: number | null;
  usuario_nome: string;
  setor_nome: string | null;
  dias_solicitados: number;
  data_retirada: string;
  data_devolucao_prevista: string;
  data_limite_tolerancia: string;
  data_devolucao_real: string | null;
  status: string;
};

export type PaginaEmprestimosAdmin = {
  itens: EmprestimoAdmin[];
  total: number;
  pagina: number;
  tamanho_pagina: number;
  total_paginas: number;
};

export type ResumoAtrasados = {
  total_atrasados: number;
  itens: EmprestimoAdmin[];
};

export type UsuarioAdmin = {
  id: number;
  username: string;
  nome_completo: string | null;
  email: string | null;
  setor_id: number | null;
  setor_nome: string | null;
  is_admin: boolean;
  ativo: boolean;
};

/**
 * Wrapper de fetch autenticado. A sessão viaja num cookie httpOnly setado
 * pelo backend no /login — o frontend nunca lê nem guarda o JWT diretamente
 * (por isso `credentials: 'include'` em vez de um header Authorization
 * manual). Em caso de 401 (sem sessão, expirada ou inválida), redireciona
 * para o login em vez de deixar a tela travada num erro silencioso.
 */
export async function apiFetch(path: string, options: RequestInit = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...options.headers,
    },
  });

  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    throw new ApiError(401, 'Sessão expirada. Faça login novamente.');
  }

  if (!response.ok) {
    let detail = 'Erro inesperado ao comunicar com o servidor.';
    try {
      const corpo = await response.json();
      if (Array.isArray(corpo.detail)) {
        // erro de validação do Pydantic (422): pega a primeira mensagem
        detail = corpo.detail[0]?.msg || corpo.detail[0] || detail;
      } else if (typeof corpo.detail === 'string') {
        detail = corpo.detail;
      }
      // Log do erro no console para debug
      console.error(`API Error [${response.status}]:`, corpo);
    } catch {
      // resposta sem corpo JSON, mantém mensagem genérica
      console.error(`API Error [${response.status}]: ${response.statusText}`);
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return null;
  return response.json();
}

export async function login(username: string, senha: string): Promise<Usuario> {
  const body = new URLSearchParams();
  body.set('username', username);
  body.set('password', senha);

  const response = await fetch(`${API_URL}/login`, {
    method: 'POST',
    credentials: 'include', // permite o navegador aceitar o Set-Cookie da resposta
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });

  if (!response.ok) {
    let detail = 'Usuário ou senha incorretos.';
    try {
      const corpo = await response.json();
      detail = corpo.detail || detail;
    } catch {
      // ignora
    }
    throw new ApiError(response.status, detail);
  }

  return response.json();
}

export async function logout(): Promise<void> {
  await fetch(`${API_URL}/logout`, {
    method: 'POST',
    credentials: 'include',
  });
}

/** Verifica se a sessão (cookie) ainda é válida, consultando o backend —
 * o JS não tem como ler um cookie httpOnly diretamente. */
export async function obterUsuarioAtual(): Promise<Usuario | null> {
  try {
    return await apiFetch('/me');
  } catch {
    return null;
  }
}

/** Obtém o perfil do usuário atual (mesmo que obterUsuarioAtual, mas pode ser usado explicitamente) */
export async function obterMeuPerfil(): Promise<Usuario> {
  return apiFetch('/me');
}

/** Atualiza o perfil do usuário atual */
export async function atualizarMeuPerfil(dados: {
  nome_completo?: string;
  email?: string | null;
  setor_id?: number;
  senha_atual?: string;
  nova_senha?: string;
}): Promise<Usuario> {
  return apiFetch('/me', {
    method: 'PATCH',
    body: JSON.stringify(dados),
  });
}

/** Lista pública dos setores fixos da organização — usada nos formulários
 * de cadastro (membro e item), inclusive antes do login. */
export async function listarSetores(): Promise<Setor[]> {
  const response = await fetch(`${API_URL}/setores/`);
  if (!response.ok) {
    throw new ApiError(response.status, 'Não foi possível carregar os setores.');
  }
  return response.json();
}

export type DadosCadastroMembro = {
  username: string;
  senha: string;
  nome_completo: string;
  email: string;
  setor_id: number;
};

export async function cadastrarMembro(dados: DadosCadastroMembro): Promise<Usuario> {
  const response = await fetch(`${API_URL}/cadastro`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados),
  });

  if (!response.ok) {
    let detail = 'Não foi possível concluir o cadastro.';
    try {
      const corpo = await response.json();
      if (Array.isArray(corpo.detail)) {
        // erro de validação do Pydantic (422): pega a primeira mensagem
        detail = corpo.detail[0]?.msg || detail;
      } else {
        detail = corpo.detail || detail;
      }
    } catch {
      // ignora
    }
    throw new ApiError(response.status, detail);
  }

  return response.json();
}

export async function listarItens(): Promise<Item[]> {
  return apiFetch('/itens/');
}

export async function criarEmprestimo(itemId: number, diasSolicitados: number, quantidade: number = 1) {
  return apiFetch('/emprestimos/', {
    method: 'POST',
    body: JSON.stringify({ item_id: itemId, dias_solicitados: diasSolicitados, quantidade }),
  });
}

export async function listarMeusEmprestimos(): Promise<Emprestimo[]> {
  return apiFetch('/emprestimos/meus/');
}

export async function devolverMeuEmprestimo(emprestimoId: number): Promise<Emprestimo> {
  return apiFetch(`/emprestimos/${emprestimoId}/devolver`, { method: 'POST' });
}

// --- Painel do administrador ---

export type DadosCadastroItem = {
  nome: string;
  patrimonio?: string;
  codigo_qr?: string;
  area?: string;
  setor_id: number;
  quantidade_total: number;
};

export async function cadastrarItem(dados: DadosCadastroItem): Promise<Item> {
  return apiFetch('/admin/itens/', {
    method: 'POST',
    body: JSON.stringify(dados),
  });
}

export async function listarItensAdmin(): Promise<Item[]> {
  return apiFetch('/admin/itens/');
}

export type DadosEdicaoItem = Partial<Omit<DadosCadastroItem, 'patrimonio' | 'codigo_qr' | 'area'>> & {
  patrimonio?: string | null;
  codigo_qr?: string | null;
  area?: string | null;
};

export async function editarItem(itemId: number, dados: DadosEdicaoItem): Promise<Item> {
  return apiFetch(`/admin/itens/${itemId}`, {
    method: 'PATCH',
    body: JSON.stringify(dados),
  });
}

export async function desativarItem(itemId: number): Promise<Item> {
  return apiFetch(`/admin/itens/${itemId}/desativar`, { method: 'POST' });
}

export async function reativarItem(itemId: number): Promise<Item> {
  return apiFetch(`/admin/itens/${itemId}/reativar`, { method: 'POST' });
}

export async function removerItem(itemId: number): Promise<void> {
  await apiFetch(`/admin/itens/${itemId}`, { method: 'DELETE' });
}

export type QRScanResponse = {
  sucesso: boolean;
  mensagem: string;
  raw: string | null;
  patrimonio: string | null;
  codigo_qr: string | null;
  nome: string | null;
  area: string | null;
  setor_id: number | null;
  setor_nome: string | null;
  item: Item | null;
  acao: 'adicionado' | 'cadastrado' | null;
  roi: { x: number; y: number; width: number; height: number; method?: string } | null;
  metodo: string | null;
};

export async function escanearQR(blob: Blob): Promise<QRScanResponse> {
  const form = new FormData();
  form.append('imagem', blob, 'captura.jpg');
  const response = await fetch(`${API_URL}/qr/scan`, {
    method: 'POST',
    credentials: 'include',
    body: form,
  });
  if (response.status === 401) {
    if (typeof window !== 'undefined') window.location.href = '/login';
    throw new ApiError(401, 'Sessão expirada. Faça login novamente.');
  }
  if (!response.ok) {
    let detail = 'Não foi possível processar a leitura.';
    try {
      const corpo = await response.json();
      detail = corpo.detail || detail;
    } catch {}
    throw new ApiError(response.status, detail);
  }
  return response.json();
}

export async function listarEmprestimosAdmin(
  pagina: number = 1,
  tamanhoPagina: number = 20
): Promise<PaginaEmprestimosAdmin> {
  return apiFetch(`/admin/emprestimos/?pagina=${pagina}&tamanho_pagina=${tamanhoPagina}`);
}

export async function obterResumoAtrasados(): Promise<ResumoAtrasados> {
  return apiFetch('/admin/emprestimos/atrasados/resumo');
}

export async function devolverEmprestimoAdmin(emprestimoId: number): Promise<EmprestimoAdmin> {
  return apiFetch(`/admin/emprestimos/${emprestimoId}/devolver`, { method: 'POST' });
}

export async function listarUsuariosAdmin(): Promise<UsuarioAdmin[]> {
  return apiFetch('/admin/usuarios/');
}

export async function desativarUsuario(usuarioId: number): Promise<UsuarioAdmin> {
  return apiFetch(`/admin/usuarios/${usuarioId}/desativar`, { method: 'POST' });
}

export async function reativarUsuario(usuarioId: number): Promise<UsuarioAdmin> {
  return apiFetch(`/admin/usuarios/${usuarioId}/reativar`, { method: 'POST' });
}

export type DadosEdicaoUsuario = {
  username?: string;
  nome_completo?: string;
  email?: string | null;
  setor_id?: number | null;
  nova_senha?: string;
};

export async function editarUsuario(usuarioId: number, dados: DadosEdicaoUsuario): Promise<UsuarioAdmin> {
  return apiFetch(`/admin/usuarios/${usuarioId}`, {
    method: 'PATCH',
    body: JSON.stringify(dados),
  });
}

export async function excluirUsuario(usuarioId: number): Promise<void> {
  await apiFetch(`/admin/usuarios/${usuarioId}`, { method: 'DELETE' });
}

export type DadosCadastroAdmin = {
  username: string;
  senha: string;
  nome_completo: string;
  email: string;
  setor_id: number;
};

export async function cadastrarAdministrador(dados: DadosCadastroAdmin): Promise<Usuario> {
  return apiFetch('/admin/administradores/', {
    method: 'POST',
    body: JSON.stringify(dados),
  });
}


export type ProdutoNotaExtraido = { codigo: string; nome: string; quantidade: number; unidade: string; valorUnitario: number; valorTotal: number };
export async function extrairProdutosPDF(file: File): Promise<{ nome_arquivo: string; produtos: ProdutoNotaExtraido[]; aviso: string }> {
  const form = new FormData(); form.append('arquivo', file);
  return apiFetch('/admin/notas-fiscais/extrair-pdf', { method: 'POST', body: form });
}
export async function registrarNotaFiscal(dados: { nome_arquivo: string; tipo_arquivo: string; produtos: ProdutoNotaExtraido[]; total_cadastrados: number; observacoes?: string }) {
  return apiFetch('/admin/notas-fiscais/', { method: 'POST', body: JSON.stringify(dados) });
}
export async function listarNotasFiscais(): Promise<Array<{id:number;nome_arquivo:string;tipo_arquivo:string;status:string;total_produtos:number;total_cadastrados:number;produtos:ProdutoNotaExtraido[];observacoes?:string;criada_em:string;responsavel:string}>> {
  return apiFetch('/admin/notas-fiscais/');
}
export async function enviarContato(dados: { assunto: string; mensagem: string; anexos?: Array<{nome:string; data:string}> }) {
  return apiFetch('/contato/', { method: 'POST', body: JSON.stringify(dados) });
}
export async function listarMinhasMensagens(): Promise<Array<{id:number;assunto:string;mensagem:string;status:string;resposta:string|null;criada_em:string;anexos?:Array<{nome:string;data:string}>;historico?:Array<{autor_nome:string;autor_foto:string|null;tipo:string;mensagem:string;criada_em:string}>}>> { return apiFetch('/contato/minhas/'); }
export async function listarMensagensContato(): Promise<Array<{id:number;assunto:string;mensagem:string;status:string;resposta:string|null;criada_em:string;usuario_nome:string;usuario_email:string|null;usuario_foto:string|null;anexos?:Array<{nome:string;data:string}>;historico?:Array<{autor_nome:string;autor_foto:string|null;tipo:string;mensagem:string;criada_em:string}>}>> { return apiFetch('/admin/contato/'); }
export async function responderContato(id:number, resposta:string) { return apiFetch(`/admin/contato/${id}`, {method:'PATCH',body:JSON.stringify({resposta})}); }
export async function enviarFotoPerfil(file: File): Promise<{foto_perfil:string}> { const form = new FormData(); form.append('arquivo', file); return apiFetch('/me/foto', {method:'POST', body:form}); }

export async function atualizarStatusChamado(id:number, acao:'CONCLUIR'|'REABRIR'|'NAO_RESOLVIDO') { return apiFetch(`/contato/${id}/status`, {method:'PATCH',body:JSON.stringify({acao})}); }
