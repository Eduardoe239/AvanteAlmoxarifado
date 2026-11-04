"""Leitura local de QR Code com ROI fixa e tolerância a QR pequeno/inclinado.

A imagem é recortada para a ROI antes do processamento. O detector tenta algumas
variações leves (escala, contraste e rotação) para melhorar a leitura de cartões
reais sem transformar a rotina em um processamento pesado para hardware antigo.
O OCR (Tesseract) continua sendo apenas fallback para o texto impresso.
"""
import json
import re
from dataclasses import dataclass

import cv2
import numpy as np

ROI_X = 0.20
ROI_Y = 0.15
ROI_W = 0.60
ROI_H = 0.70
MAX_PROCESSING_WIDTH = 1280

# Limites para manter o processamento compatível com máquinas mais antigas.
QR_UPSCALE_FACTORS = (1.5, 2.0, 2.5, 3.0, 4.0)
QR_ROTATION_ANGLES = (-45, -30, -15, 15, 30, 45)


@dataclass
class QRReadResult:
    raw: str
    patrimonio: str | None = None
    codigo_qr: str | None = None
    nome: str | None = None
    area: str | None = None
    setor_id: int | None = None
    setor_nome: str | None = None


def _parse_payload(raw: str) -> QRReadResult:
    """Interpreta QR estruturado para cadastro automático.

    Formato recomendado:
    {"nome":"Placa ESP32","patrimonio":"ESP-001","codigo_qr":"QR-ESP-001",
     "area":"Laboratório","setor_id":1}
    Também aceita setor/setor_nome no lugar de setor_id.
    """
    raw = raw.strip()
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            patrimonio = data.get("patrimonio") or data.get("codigo") or data.get("id")
            codigo_qr = data.get("codigo_qr") or data.get("qr_code") or data.get("qr") or patrimonio
            setor_id = data.get("setor_id")
            try:
                setor_id = int(setor_id) if setor_id is not None else None
            except (TypeError, ValueError):
                setor_id = None
            setor_nome = data.get("setor_nome") or data.get("setor")
            return QRReadResult(
                raw=raw,
                patrimonio=str(patrimonio).strip() if patrimonio else None,
                codigo_qr=str(codigo_qr).strip() if codigo_qr else None,
                nome=str(data.get("nome")).strip() if data.get("nome") else None,
                area=str(data.get("area")).strip() if data.get("area") else None,
                setor_id=setor_id,
                setor_nome=str(setor_nome).strip() if setor_nome else None,
            )
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    match = re.search(r"(AVT-[A-Za-z0-9._-]+)", raw, re.I)
    patrimonio = match.group(1).upper() if match else raw
    return QRReadResult(raw=raw, patrimonio=patrimonio, codigo_qr=raw)


def _try_decode(detector: cv2.QRCodeDetector, image: np.ndarray) -> str | None:
    """Tenta uma leitura direta e depois uma versão em tons de cinza."""
    for candidate in (image, cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image):
        try:
            text, _, _ = detector.detectAndDecode(candidate)
            if text:
                return text
        except cv2.error:
            continue
    return None


def _rotate_bound(image: np.ndarray, angle: float) -> np.ndarray:
    """Gira sem cortar os cantos, preservando o QR nas bordas."""
    h, w = image.shape[:2]
    center = (w / 2.0, h / 2.0)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = abs(matrix[0, 0])
    sin = abs(matrix[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    matrix[0, 2] += (new_w / 2.0) - center[0]
    matrix[1, 2] += (new_h / 2.0) - center[1]
    return cv2.warpAffine(image, matrix, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=255)


def _qr_variants(roi: np.ndarray):
    """Gera poucas variantes baratas, priorizando o caso normal."""
    yield roi

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    yield gray

    # Aumentar o QR ajuda quando ele ocupa poucos pixels da ROI.
    for factor in QR_UPSCALE_FACTORS:
        enlarged = cv2.resize(roi, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
        yield enlarged
        enlarged_gray = cv2.cvtColor(enlarged, cv2.COLOR_BGR2GRAY)
        yield enlarged_gray
        # INTER_NEAREST preserva melhor módulos muito pequenos do QR.
        if factor >= 2.0:
            nearest = cv2.resize(roi, None, fx=factor, fy=factor, interpolation=cv2.INTER_NEAREST)
            yield nearest
            nearest_gray = cv2.cvtColor(nearest, cv2.COLOR_BGR2GRAY)
            yield nearest_gray
            if factor >= 3.0:
                _, otsu = cv2.threshold(nearest_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                yield otsu

    # Uma versão com contraste local ajuda em cartões com iluminação irregular.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    yield clahe.apply(gray)

    # Só depois das tentativas normais, testar rotações moderadas.
    for angle in QR_ROTATION_ANGLES:
        rotated = _rotate_bound(roi, angle)
        yield rotated
        yield cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
        # QR pequeno + inclinado: escala 1.5 e, em último caso, 2x preservando módulos.
        yield cv2.resize(rotated, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        if angle in (-45, -30, 30, 45):
            yield cv2.resize(rotated, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_NEAREST)


def _decode_roi(roi: np.ndarray) -> tuple[str | None, str]:
    detector = cv2.QRCodeDetector()
    for index, candidate in enumerate(_qr_variants(roi)):
        text = _try_decode(detector, candidate)
        if text:
            # Primeiras variantes são diretas; as demais servem para condições difíceis.
            if index <= 2:
                method = "opencv_qr"
            elif index <= 12:
                method = "opencv_qr_upscaled"
            else:
                method = "opencv_qr_rotated"
            return text, method
    return None, "none"


def decode_qr_from_bytes(content: bytes) -> tuple[QRReadResult | None, dict]:
    arr = np.frombuffer(content, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Imagem inválida ou não suportada.")

    h, w = image.shape[:2]
    scale = min(1.0, MAX_PROCESSING_WIDTH / max(w, 1))
    if scale < 1.0:
        image = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        h, w = image.shape[:2]

    x = int(w * ROI_X)
    y = int(h * ROI_Y)
    rw = int(w * ROI_W)
    rh = int(h * ROI_H)
    roi = image[y:y + rh, x:x + rw]

    text, method = _decode_roi(roi)
    if text:
        result = _parse_payload(text)
        return result, {"x": x, "y": y, "width": rw, "height": rh, "method": method}

    # Fallback OCR: texto humano impresso no cartão.
    try:
        import pytesseract
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        ocr = pytesseract.image_to_string(threshold, config="--psm 6").strip()
        match = re.search(r"AVT-[A-Za-z0-9._-]+", ocr, re.I)
        if match:
            result = _parse_payload(match.group(0))
            return result, {"x": x, "y": y, "width": rw, "height": rh, "method": "ocr_fallback"}
    except Exception:
        pass

    return None, {"x": x, "y": y, "width": rw, "height": rh, "method": "none"}
