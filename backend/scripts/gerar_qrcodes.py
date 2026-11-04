"""Gera cartões QR de teste para o Avante Almoxarifado.

Uso simples (compatibilidade):
  python scripts/gerar_qrcodes.py --quantidade 20 --saida ../qrcodes

Para testar o cadastro automático, o QR deve carregar os dados do item:
  python scripts/gerar_qrcodes.py --quantidade 20 --saida ../qrcodes --estruturado

O formato estruturado contém nome, patrimônio, código QR, área e setor_id.
"""
import argparse
import json
from pathlib import Path

import qrcode

parser = argparse.ArgumentParser()
parser.add_argument("--quantidade", type=int, default=20)
parser.add_argument("--saida", default="../qrcodes")
parser.add_argument(
    "--estruturado",
    action="store_true",
    help="Gera QR Codes com todos os dados necessários para cadastro automático.",
)
parser.add_argument("--area", default="Laboratório")
parser.add_argument("--setor-id", type=int, default=1)
parser.add_argument("--setor-nome", default="")
args = parser.parse_args()

saida = Path(args.saida)
saida.mkdir(parents=True, exist_ok=True)

for i in range(1, args.quantidade + 1):
    codigo = f"AVT-{i:03d}"
    if args.estruturado:
        payload = {
            "nome": f"Item de teste {i}",
            "patrimonio": codigo,
            "codigo_qr": codigo,
            "area": args.area,
            "setor_id": args.setor_id,
        }
        if args.setor_nome:
            payload["setor_nome"] = args.setor_nome
        conteudo = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    else:
        conteudo = codigo

    img = qrcode.make(conteudo)
    img.save(saida / f"{codigo}.png")

print(f"{args.quantidade} QR Codes gerados em {saida.resolve()}")
