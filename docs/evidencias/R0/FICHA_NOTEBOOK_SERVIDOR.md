# Ficha do notebook-servidor — Avante Tech Jr (R0-02, parcial)

**Data da coleta:** 24/11/2026 · **Coletado por:** Luís Eduardo de Sousa Barbosa (responsável)
**Fonte:** tela "Informações do Sistema" do Linux Mint e verificação do responsável (bateria, disco). Os números detalhados (SMART, horas de uso, temperatura, BIOS) serão coletados por `ops/verificar-hardware.sh` na R0-04.
**Destino no repositório:** `docs/evidencias/R0/FICHA_NOTEBOOK_SERVIDOR.md`

---

## 1. Hardware

| Item | Valor | Situação diante do Volume 04 |
|---|---|---|
| Placa | Compal PBL1011 v2.60 (plataforma Intel Huron River, 2011) | — |
| Processador | Intel Core i3-2310M, 2 núcleos, 2,1 GHz (Sandy Bridge) | = Perfil Mínimo |
| Instruções relevantes | x86-64, AVX; **sem AVX2**; **sem AES-NI** | Atende; ver §3 |
| Memória | 8,1 GB DDR3 | **Acima** do Perfil Mínimo (4 GB) |
| Disco | ≈ 1 TB, **HD** (rotacional) | = Perfil Mínimo; espaço muito acima do necessário |
| Saúde do disco | Normal, segundo verificação do responsável | Detalhar na R0-04 (SMART completo) |
| Vídeo | Intel HD Graphics integrada (2ª geração) | Irrelevante para servidor |
| TPM 2.0 | Não disponível (plataforma de 2011) | Confirmar na R0-04; ver §3 |
| Bateria | **Viciada**: não segura carga | Risco; ver §3 |

## 2. Sistema operacional encontrado

| Item | Valor |
|---|---|
| Distribuição | Linux Mint 22.3 (base Ubuntu 24.04), 64 bits |
| Interface | Cinnamon 6.6.9 sobre X11 |
| Kernel | 7.0.0-42-generic |

Não está na matriz de suporte (ADR-022). Decisão na §4.

## 3. Consequências para o projeto

| Achado | Consequência | Ação |
|---|---|---|
| 8 GB de memória | Folga para cache do PostgreSQL e para o sistema operacional. O orçamento dos serviços **continua** em ≤ 1,5 GB normal / ≤ 2,0 GB pico, porque o produto precisa rodar no Perfil Mínimo de 4 GB | Instalador da Avante pode usar parâmetros do PostgreSQL para 8 GB (ex.: `effective_cache_size` maior), definidos pelo perfil detectado; testes de carga continuam valendo para 4 GB no CI |
| HD rotacional | Exatamente o cenário do Volume 04 §4.3 | Manter toda a disciplina de disco (sem varreduras sequenciais, tarefas pesadas na janela 1h–5h) |
| Sem AES-NI | Criptografia mais lenta, sem impedimento | TLS priorizando ChaCha20-Poly1305 para clientes sem aceleração; medir o tempo do backup criptografado (restic) na R0-05 |
| Sem TPM 2.0 (provável) | Criptografia de disco com religamento automático não é possível | Opção do ADR-012: sem criptografia de disco + backups criptografados + local trancado; **termo de aceite de risco** assinado na R0-04 |
| Bateria viciada | Em queda de energia o notebook desliga na hora. Com PostgreSQL em `synchronous_commit=on` e ext4 com journal, transações confirmadas não se perdem, mas o desligamento brusco repetido aumenta o risco para o HD | Recomendado **nobreak** (600–700 VA é suficiente); verificar fisicamente se a bateria está **estufada** — se estiver, remover; BIOS com religamento automático ao voltar a energia (R0-02) |
| Linux Mint com interface gráfica | Fora da matriz de suporte; a interface consome memória e CPU continuamente; comportamento de desktop (suspender, atualizações interativas) | Ver §4 |

## 4. Decisão pendente: sistema operacional

| Opção | Prós | Contras |
|---|---|---|
| **A. Reinstalar Debian 13 sem interface (recomendado)** | Padrão do plano; mínimo consumo; suporte longo; o mesmo ambiente que o CI e a documentação cobrem | Apaga o disco: conferir antes se há arquivos de alguém |
| B. Reinstalar Ubuntu Server 24.04 LTS | Também suportado; família do Mint (mais familiar) | Mesmo cuidado com os arquivos |
| C. Manter o Mint e desligar a interface | Sem reinstalar | Fora da matriz de suporte; resíduos de desktop; cria uma variante que nenhum cliente terá |

**Decisão do responsável:** ________ · **Data:** ________

## 5. Pendências da R0-02 / R0-04

- [ ] Confirmar se há arquivos no notebook a preservar antes de reinstalar
- [ ] Verificar se a bateria está estufada
- [ ] BIOS: religamento automático ao voltar a energia (se a opção existir), boot pelo disco, virtualização ativa
- [ ] `memtest86+` (pelo menos uma passada completa)
- [ ] Instalar o sistema escolhido, sem interface gráfica, com SSH por chave
- [ ] Rodar `ops/verificar-hardware.sh` (R0-04) e anexar o relatório: SMART completo, horas de uso do disco, temperatura, TPM
- [ ] Termo de aceite de risco da criptografia de disco (ADR-012)
- [ ] Decidir sobre o nobreak
