"""
Cria (ou atualiza a senha de) um usuário administrador.

Uso:
    python scripts/create_admin.py <username> <senha> [--admin] [--email endereco@dominio.com]

O e-mail é opcional aqui (o CLI é um atalho pra criar o primeiro admin
antes de o sistema ter uma interface no ar) — se não for informado agora,
um admin já existente pode completá-lo depois pelo painel
(PATCH /admin/usuarios/{id}).

Rode isso direto no servidor/ambiente, nunca exponha essa lógica como
endpoint HTTP público — criação de usuário admin não pode ser algo que
qualquer requisição externa consiga disparar.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Usuario
from auth import gerar_hash_senha
from schemas import _validar_senha_forte


def main():
    if len(sys.argv) < 3:
        print(
            "Uso: python scripts/create_admin.py <username> <senha> [--admin] "
            "[--email endereco@dominio.com]"
        )
        sys.exit(1)

    username = sys.argv[1]
    senha = sys.argv[2]
    resto = sys.argv[3:]
    is_admin = "--admin" in resto

    email = None
    if "--email" in resto:
        indice = resto.index("--email")
        if indice + 1 >= len(resto):
            print("Uso: --email precisa vir seguido do endereço de e-mail.")
            sys.exit(1)
        email = resto[indice + 1]

    try:
        _validar_senha_forte(senha)
    except ValueError as exc:
        print(f"Senha inválida: {exc}")
        sys.exit(1)

    db = SessionLocal()
    try:
        try:
            existente = db.query(Usuario).filter(Usuario.username == username).first()
        except Exception as exc:
            print(
                "Erro ao consultar a tabela de usuários. "
                "Rode 'alembic upgrade head' antes de criar o admin (o schema "
                f"do banco pode não ter sido criado ainda). Detalhe: {exc}"
            )
            sys.exit(1)
        if existente:
            existente.hashed_password = gerar_hash_senha(senha)
            existente.is_admin = is_admin or existente.is_admin
            existente.ativo = True
            if email:
                existente.email = email
            db.commit()
            print(f"Usuário '{username}' atualizado.")
        else:
            novo = Usuario(
                username=username,
                hashed_password=gerar_hash_senha(senha),
                email=email,
                is_admin=is_admin,
                ativo=True,
            )
            db.add(novo)
            db.commit()
            print(f"Usuário '{username}' criado (admin={is_admin}, email={email or '(não informado)'}).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
