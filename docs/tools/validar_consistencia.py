#!/usr/bin/env python3
"""Valida a consistência da documentação do Avante Almoxarifado.

Uso: python docs/tools/validar_consistencia.py <raiz-do-repositorio>
Verifica RF/RNF/ADR citados, referências a volumes e seções,
release dos requisitos M/S, termos antigos e IDs do diagnóstico interno.
Só biblioteca padrão. É o script usado na validação do Anexo A3.
"""
import re, pathlib, sys
root = pathlib.Path(sys.argv[1]); docs = root/"docs"
files = sorted(docs.glob("*.md")) + [root/"CLAUDE.md", root/"README.md"] + sorted((root/".claude").rglob("*.md"))
txt = {f: f.read_text(encoding="utf-8") for f in files if f.exists()}
req = (docs/"02_REQUISITOS.md").read_text(encoding="utf-8")
rf_def = set(re.findall(r"^\| (RF-[A-Z]+-\d+) \|", req, re.M)); rnf_def = set(re.findall(r"^\| (RNF-\d+) \|", req, re.M))
adr_def = set(re.findall(r"^### (ADR-\d+)", (docs/"03_ARQUITETURA_E_ADRS.md").read_text(encoding="utf-8"), re.M))
erros = []
def exp(prefix, a, b): return [f"{prefix}-{i:02d}" for i in range(int(a), int(b)+1)]
for f,t in txt.items():
    for m in re.finditer(r"\b(RF-[A-Z]+)-(\d+)(?:\.\.(\d+))?", t):
        ids = exp(m[1], m[2], m[3]) if m[3] else [f"{m[1]}-{m[2]}"]
        for i in ids:
            if i not in rf_def: erros.append(f"{f.name}: {i} inexistente")
    for m in re.finditer(r"\bRNF-(\d+)", t):
        if f"RNF-{m[1]}" not in rnf_def: erros.append(f"{f.name}: RNF-{m[1]} inexistente")
    for m in re.finditer(r"\bADR-(\d+)(?!x)", t):
        if f"ADR-{m[1]}" not in adr_def: erros.append(f"{f.name}: ADR-{m[1]} inexistente")
    for pat in ["PLANO_MESTRE","ARQUITETURA_E_DECISOES","GUIA_EXECUCAO_CLAUDE","ESPECIFICACAO_UI_UX","ESTRATEGIA_QR_CODE","RELATORIO_AUDITORIA","ANALISE_DE_ROTA.md`","MATRIZ_FUNCIONALIDADES_MVP.md`"]:
        if pat in t and f.name!="00_INDICE_E_GOVERNANCA.md": erros.append(f"{f.name}: referência antiga {pat}")
    for m in re.finditer(r"\b(Fase \d+|Gate \d+|Marco M\d)\b", t):
        if f.name not in ("00_INDICE_E_GOVERNANCA.md",): erros.append(f"{f.name}: termo antigo '{m[0]}'")
    for m in re.finditer(r"(?<!RF-)\b(AUD|SEC|INT|PERF|FE)-0\d+\b", t):
        erros.append(f"{f.name}: ID de auditoria {m[0]}")
# referências Volume NN §x
heads = {}
for f in docs.glob("*.md"):
    n = f.name[:2]; heads[n] = set(re.findall(r"^#{2,3} (\d+(?:\.\d+)*)[\. ]", f.read_text(encoding="utf-8"), re.M))
for f,t in txt.items():
    for m in re.finditer(r"Volume (\d\d) §(\d+(?:\.\d+)*)", t):
        if m[2] not in heads.get(m[1], set()): erros.append(f"{f.name}: Volume {m[1]} §{m[2]} não existe")
    for m in re.finditer(r"\(Volume (\d\d)\)|Volume (\d\d)\b", t):
        v = m[1] or m[2]
        if not list(docs.glob(f"{v}_*.md")): erros.append(f"{f.name}: Volume {v} não existe")
    for m in re.finditer(r"Anexo (A\d)", t):
        if not list(docs.glob(f"{m[1]}_*.md")): erros.append(f"{f.name}: Anexo {m[1]} não existe")
# requisitos M/S com release
for m in re.finditer(r"^\| (RF-[A-Z]+-\d+) \|.*\| ([MSC]) \| ([^|]+)\|", req, re.M):
    rel = m[3].strip()
    if m[2] in "MS" and not re.match(r"R[0-4]", rel): erros.append(f"{m[1]} prioridade {m[2]} sem release ({rel})")
print(f"RF definidos: {len(rf_def)} · RNF: {len(rnf_def)} · ADR: {len(adr_def)} · arquivos verificados: {len(txt)}")
for e in sorted(set(erros)): print("ERRO", e)
print("total de erros:", len(set(erros)))
