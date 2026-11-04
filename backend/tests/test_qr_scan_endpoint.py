"""Regressão: /qr/scan gravava no banco mas devolvia 500.

A resposta incluía `roi["method"]` (string), enquanto o schema declarava
`roi: dict[str, int]`. O commit já tinha acontecido quando o Pydantic
rejeitava a resposta — o front mostrava "falha na leitura" e o item só
aparecia depois de um F5.
"""
import json

import cv2
import numpy as np

from models import Item
from tests.test_qr_service import make_qr_image


def _jpeg(payload: str) -> bytes:
    ok, buf = cv2.imencode(".jpg", make_qr_image(payload))
    assert ok
    return buf.tobytes()


def _enviar(client, payload: str):
    return client.post(
        "/qr/scan",
        files={"imagem": ("captura.jpg", _jpeg(payload), "image/jpeg")},
    )


def test_scan_cadastra_item_novo_e_responde_200(admin_client, db_session):
    payload = json.dumps(
        {"nome": "Sensor DHT22", "patrimonio": "DHT-001", "codigo_qr": "QR-DHT-001", "setor_id": 1}
    )
    resp = _enviar(admin_client, payload)
    assert resp.status_code == 200, resp.text
    corpo = resp.json()
    assert corpo["sucesso"] is True
    assert corpo["acao"] == "cadastrado"
    assert corpo["item"]["nome"] == "Sensor DHT22"
    assert isinstance(corpo["roi"]["method"], str)
    assert db_session.query(Item).filter(Item.patrimonio == "DHT-001").count() == 1


def test_scan_item_existente_soma_uma_unidade(admin_client, db_session):
    resp = _enviar(admin_client, json.dumps({"nome": "Placa ESP32", "patrimonio": "ESP-001"}))
    assert resp.status_code == 200, resp.text
    assert resp.json()["acao"] == "adicionado"
    db_session.expire_all()
    esp32 = db_session.query(Item).filter(Item.id == 1).one()
    assert esp32.quantidade_total == 6
    assert esp32.quantidade_disponivel == 2


def test_scan_sem_qr_na_imagem_responde_200_com_sucesso_false(admin_client):
    em_branco = np.full((480, 640, 3), 255, dtype=np.uint8)
    ok, buf = cv2.imencode(".jpg", em_branco)
    assert ok
    resp = admin_client.post(
        "/qr/scan", files={"imagem": ("captura.jpg", buf.tobytes(), "image/jpeg")}
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["sucesso"] is False
