# API.md — Endpoints atuais (baseline V1)

Gerado por extração automática de `backend/main.py` (F0-06). Todas as rotas estão na raiz — sem prefixo `/api/v1` (gap já registrado na auditoria).

| Método | Rota | Handler | response_model | status_code |
|---|---|---|---|---|
| POST | `/login` | `login()` | `UsuarioResponse` | 200/default |
| POST | `/logout` | `logout()` | `-` | 200/default |
| GET | `/me` | `me()` | `UsuarioResponse` | 200/default |
| PATCH | `/me` | `atualizar_meu_perfil()` | `UsuarioResponse` | 200/default |
| POST | `/me/desativar-conta` | `desativar_minha_conta()` | `-` | 204 |
| POST | `/cadastro` | `cadastrar_membro()` | `UsuarioResponse` | 201 |
| GET | `/setores/` | `listar_setores()` | `list[SetorResponse]` | 200/default |
| POST | `/qr/scan` | `escanear_qr()` | `QRScanResponse` | 200/default |
| GET | `/itens/` | `listar_itens()` | `list[ItemResponse]` | 200/default |
| POST | `/emprestimos/` | `registrar_emprestimo()` | `EmprestimoResponse` | 200/default |
| GET | `/emprestimos/meus/` | `listar_meus_emprestimos()` | `list[EmprestimoResponse]` | 200/default |
| POST | `/emprestimos/{emprestimo_id}/devolver` | `devolver_meu_emprestimo()` | `EmprestimoResponse` | 200/default |
| GET | `/admin/itens/` | `listar_itens_admin()` | `list[ItemResponse]` | 200/default |
| POST | `/admin/itens/` | `cadastrar_item()` | `ItemResponse` | 201 |
| PATCH | `/admin/itens/{item_id}` | `editar_item()` | `ItemResponse` | 200/default |
| POST | `/admin/itens/{item_id}/desativar` | `desativar_item()` | `ItemResponse` | 200/default |
| POST | `/admin/itens/{item_id}/reativar` | `reativar_item()` | `ItemResponse` | 200/default |
| DELETE | `/admin/itens/{item_id}` | `remover_item()` | `-` | 204 |
| GET | `/admin/emprestimos/` | `listar_emprestimos_admin()` | `PaginaEmprestimosAdmin` | 200/default |
| GET | `/admin/emprestimos/atrasados/resumo` | `resumo_emprestimos_atrasados()` | `ResumoAtrasados` | 200/default |
| POST | `/admin/emprestimos/{emprestimo_id}/devolver` | `devolver_emprestimo_admin()` | `EmprestimoAdminResponse` | 200/default |
| POST | `/admin/administradores/` | `cadastrar_administrador()` | `UsuarioResponse` | 201 |
| GET | `/admin/usuarios/` | `listar_usuarios_admin()` | `list[UsuarioAdminResponse]` | 200/default |
| POST | `/admin/usuarios/{usuario_id}/desativar` | `desativar_usuario()` | `UsuarioAdminResponse` | 200/default |
| POST | `/admin/usuarios/{usuario_id}/reativar` | `reativar_usuario()` | `UsuarioAdminResponse` | 200/default |
| PATCH | `/admin/usuarios/{usuario_id}` | `editar_usuario()` | `UsuarioAdminResponse` | 200/default |
| DELETE | `/admin/usuarios/{usuario_id}` | `excluir_usuario()` | `-` | 204 |

**Total: 27 rotas.**
