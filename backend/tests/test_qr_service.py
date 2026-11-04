import cv2
import numpy as np
import qrcode
import pytest

from qr_service import decode_qr_from_bytes


def make_qr_image(payload="AVT-001", size=180, angle=0, center=(320, 240), canvas=(640, 480)):
    code = qrcode.QRCode(version=1, box_size=10, border=4)
    code.add_data(payload)
    code.make(fit=True)
    image = np.array(code.make_image(fill_color="black", back_color="white").convert("RGB"))
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, (size, size), interpolation=cv2.INTER_NEAREST)

    if angle:
        h, w = image.shape[:2]
        matrix = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1)
        cos, sin = abs(matrix[0, 0]), abs(matrix[0, 1])
        new_w = int(h * sin + w * cos)
        new_h = int(h * cos + w * sin)
        matrix[0, 2] += new_w / 2 - w / 2
        matrix[1, 2] += new_h / 2 - h / 2
        image = cv2.warpAffine(image, matrix, (new_w, new_h), borderValue=(255, 255, 255))

    result = np.full((canvas[1], canvas[0], 3), 255, dtype=np.uint8)
    x = int(center[0] - image.shape[1] / 2)
    y = int(center[1] - image.shape[0] / 2)
    if x < 0 or y < 0 or x + image.shape[1] > canvas[0] or y + image.shape[0] > canvas[1]:
        raise ValueError("QR não cabe na imagem de teste")
    result[y:y + image.shape[0], x:x + image.shape[1]] = image
    ok, encoded = cv2.imencode(".png", result)
    assert ok
    return encoded.tobytes()


def test_qr_normal():
    result, meta = decode_qr_from_bytes(make_qr_image("AVT-001"))
    assert result is not None
    assert result.patrimonio == "AVT-001"
    assert meta["method"].startswith("opencv_qr")


@pytest.mark.parametrize("angle", [15, 30, 45])
def test_qr_inclinado(angle):
    result, _ = decode_qr_from_bytes(make_qr_image("AVT-002", size=100, angle=angle))
    assert result is not None
    assert result.patrimonio == "AVT-002"


@pytest.mark.parametrize("size", [70, 60, 50])
def test_qr_pequeno(size):
    result, _ = decode_qr_from_bytes(make_qr_image("AVT-003", size=size))
    assert result is not None
    assert result.patrimonio == "AVT-003"


def test_qr_fora_da_roi_nao_e_lido():
    result, meta = decode_qr_from_bytes(make_qr_image("AVT-999", size=140, center=(90, 90)))
    assert result is None
    assert meta["method"] == "none"


def test_imagem_invalida():
    with pytest.raises(ValueError):
        decode_qr_from_bytes(b"nao-e-uma-imagem")


def test_qr_json_com_dados_de_cadastro():
    payload = '{"nome":"Placa ESP32","patrimonio":"ESP-001","codigo_qr":"QR-ESP-001","area":"Laboratório","setor_id":1}'
    result, _ = decode_qr_from_bytes(make_qr_image(payload, size=220))
    assert result is not None
    assert result.nome == "Placa ESP32"
    assert result.patrimonio == "ESP-001"
    assert result.codigo_qr == "QR-ESP-001"
    assert result.area == "Laboratório"
    assert result.setor_id == 1
