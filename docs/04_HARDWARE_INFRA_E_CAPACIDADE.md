# Volume 04 — Hardware, Infraestrutura e Capacidade

**Produto:** Avante Almoxarifado · **Versão:** 3.1.0 · **Data:** 24/11/2026 · **Status:** Aprovado em 24/11/2026
**Responsável:** Luís Eduardo de Sousa Barbosa
**Relação:** detalha ADR-002, ADR-012, ADR-023 e RNF-05, RNF-06, RNF-20, RNF-21, RNF-22.

---

## 1. Ponto de partida

O servidor da Avante é um **notebook antigo**: memória **DDR3**, disco **rígido (HD)**, desempenho modesto. Serão cerca de **30 pessoas com acesso**, mas poucas ao mesmo tempo. Este volume mostra, com números, por que o sistema cabe nesse hardware e define o que precisa ser verificado no notebook real antes de qualquer código (R0).

**Por que cabe:**
- o banco da Avante deve ficar **abaixo de 200 MB em 5 anos** (§6), então cabe inteiro na memória de cache, e o HD pesa pouco nas consultas;
- o uso simultâneo esperado (até 10 pessoas ativas) gera em média cerca de 1 requisição por segundo, com picos de 10 — carga baixa para a API;
- tudo que é pesado (QR, visão computacional, compressão de imagens) roda no celular ou na estação, não no servidor.

**O que o HD e a idade do notebook exigem:** disciplina de disco (§4.3), monitoramento da saúde do HD (§7) e um plano de energia (§8).

## 2. Perfis de hardware

| Item | **Mínimo** (notebook da Avante) | **Recomendado** | **Comercial certificado** (R4) |
|---|---|---|---|
| Processador | x86-64 (64 bits), 2 núcleos | 4 núcleos | Intel 8ª geração+ ou AMD Ryzen 2000+ (compatível com Windows 11) |
| Memória | **4 GB** (DDR3 aceito) | 8 GB | 8 GB |
| Disco | HD com ≥ 120 GB livres | SSD SATA ≥ 240 GB | SSD ≥ 256 GB |
| TPM | Não exigido | Desejável | TPM 2.0 |
| Rede | **Cabo** 100 Mbps, IP reservado no roteador | Cabo 1 Gbps | Cabo 1 Gbps |
| Energia | Bateria funcional **ou** nobreak | Nobreak | Nobreak |
| SO | Debian 13 ou Ubuntu Server 24.04/26.04 LTS **sem interface gráfica** | Idem | Idem ou Windows 11 Pro |
| Metas de desempenho (RNF-05) | p95 < 500 ms leitura · < 800 ms estoque · tempo real < 3 s | < 300 ms · < 500 ms · < 2 s | Iguais ao Recomendado |

**Notebook real da Avante** (ficha em `docs/evidencias/R0/FICHA_NOTEBOOK_SERVIDOR.md`, D-22): tem **8 GB** de memória DDR3 e HD. O orçamento de memória dos serviços **continua o do Perfil Mínimo** (§4.1, 4 GB), porque o produto precisa funcionar nele; a memória extra é folga, não orçamento.

**Abaixo do Mínimo** (ex.: 2 GB de memória ou processador de 32 bits), o instalador recusa e indica a melhoria necessária (RF-COM-01). Pentes de DDR3 para notebook são baratos; se o notebook tiver 2 GB, a troca para 4 ou 8 GB resolve.

**Por que sem interface gráfica:** um ambiente de desktop consome de 500 MB a 1 GB de memória à toa. O servidor é administrado pelo navegador (painel de administração) e por SSH/CLI `avante`.

**Windows:** o notebook da Avante, por ter processador anterior à 8ª geração Intel e provavelmente não ter TPM 2.0, **não atende aos requisitos oficiais do Windows 11**. O suporte a Windows existe para clientes com hardware do perfil Comercial (R4).

## 3. Verificação do notebook real (tarefa R0-04)

Nada é assumido: os valores abaixo são coletados no notebook e registrados no relatório da R0. O roteiro é um script (`ops/verificar-hardware.sh`) que só **lê** informações.

| Verificação | Como | Por que importa |
|---|---|---|
| Modelo, processador, núcleos, 64 bits | `lscpu`, `dmidecode -t system` | Perfil e compatibilidade |
| Memória instalada e máxima suportada | `free -h`, `dmidecode -t memory` | Orçamento (§4) e possibilidade de upgrade |
| Disco: tipo, tamanho, **saúde SMART** | `lsblk -d -o NAME,ROTA,SIZE,MODEL`, `smartctl -a` | HD velho pode estar perto de falhar |
| Velocidade real do disco | `fio` (leitura/escrita aleatória e sequencial, 60 s) | Calibrar metas e tempo de backup |
| TPM | `ls /sys/class/tpm/`, versão | Decide a opção de criptografia (ADR-012) |
| Bateria: saúde e capacidade | `upower -i` | Tempo de autonomia em queda de energia; bateria inchada é risco de segurança |
| Religamento automático ao voltar energia | Opções da BIOS (ex.: "AC Power Recovery") | Define se RNF-06 depende de nobreak |
| Temperatura em carga | `lm-sensors` durante teste de carga | Notebook velho com poeira esquenta e reduz desempenho |
| Rede | Placa cabeada, velocidade negociada | Servidor por Wi-Fi é instável |

**Teste de carga de aceitação (R0-05):** k6 simulando 10 usuários ativos e 60 conexões de tempo real sobre uma base sintética de 100 mil movimentações, medindo p95, uso de memória, CPU, I/O e temperatura. O resultado confirma ou revisa as metas † do RNF-05.

## 4. Orçamento de recursos (Perfil Mínimo — 4 GB)

### 4.1 Memória por serviço

| Serviço | Uso normal | Pico | Limite imposto | Observação |
|---|---|---|---|---|
| Sistema operacional (sem interface gráfica) | ~350 MB | — | — | Inclui systemd, journald, SSH |
| PostgreSQL 18 | ~350 MB | ~500 MB | Pela configuração (§4.2) | Não recebe limite rígido: matar o banco força recuperação; o controle é por parâmetros |
| API (2 processos Uvicorn) | ~300 MB | ~450 MB | 450 MB | Reinício automático se ultrapassar |
| Worker (1 tarefa pesada por vez) | ~120 MB | ~400 MB | 400 MB | Tarefas com limite próprio de memória e tempo |
| Caddy | ~40 MB | ~100 MB | 128 MB | — |
| Cliente VPN | ~50 MB | ~60 MB | 96 MB | Se a opção A da ADR-007 for escolhida |
| Backup (restic) | 0 | ~400 MB | 400 MB | Só de madrugada, nunca junto com tarefa pesada do worker |
| **Total dos serviços** | **≈ 860 MB** | **≈ 1.630 MB** | — | Dentro do RNF-20 (≤ 1,5 GB normal; ≤ 2,0 GB pico) |
| **Com o SO** | ≈ 1,2 GB | ≈ 2,0 GB | — | Sobram ≈ 2 GB para cache de disco mesmo no pico |

Memória de troca: **zram de 1 GB** (comprimida na RAM) + arquivo de troca de 2 GB no disco como reserva; `vm.swappiness=10`. Uso de troca sustentado acima de 20% gera alerta.

### 4.2 Parâmetros do PostgreSQL (ponto de partida, calibrado na R0)

| Parâmetro | Valor | Motivo |
|---|---|---|
| `shared_buffers` | 256MB | ~6% da RAM; o restante do cache fica com o SO |
| `effective_cache_size` | 1536MB | Informa ao planejador o cache disponível |
| `work_mem` | 4MB | Consultas simples; evita estouro com várias conexões |
| `maintenance_work_mem` | 64MB | Vacuum e índices sem pressionar a memória |
| `max_connections` | 25 | Pool da API (2 processos × 8) + worker + manutenção |
| `random_page_cost` | 4 | Valor para HD (cai para 1,1 se houver SSD) |
| `effective_io_concurrency` | 1 | HD não se beneficia de I/O paralelo |
| `jit` | off | Economiza memória e CPU em consultas curtas |
| `max_parallel_workers_per_gather` | 0 | 2 núcleos: paralelismo não compensa |
| `wal_compression` | zstd | Menos escrita no HD e backup menor |
| `checkpoint_timeout` / `max_wal_size` | 15min / 1GB | Checkpoints menos frequentes = menos I/O aleatório |
| `synchronous_commit` / `fsync` / `full_page_writes` | on / on / on | **Integridade não é negociável** |
| `archive_mode` / `archive_timeout` | on / 300s | RPO ≤ 15 min (ADR-012) |
| `timezone` | UTC | ADR-015 |

### 4.3 Disciplina de disco (RNF-22)

- Banco e arquivos no mesmo HD, mas com **escritas sequenciais privilegiadas** (WAL comprimido, checkpoints espaçados).
- Backup, reconciliação, relatórios grandes e vacuum manual rodam **fora do horário de uso** (o laboratório funciona de segunda a sexta, das 8h às 20h; janela padrão: 1h–5h) e com prioridade baixa de I/O (`IOSchedulingClass=idle`).
- Imagens chegam já comprimidas e redimensionadas pelo aparelho (ADR-008); o servidor não gera miniaturas.
- Logs com teto (`journald SystemMaxUse=500M`) e rotação.
- Nenhuma consulta frequente sem índice: o CI roda `EXPLAIN` das consultas críticas e falha em varredura completa de tabela grande.

### 4.4 Processamento

- API: 2 processos (um por núcleo). Trabalho síncrono pesado nunca roda dentro da API.
- Worker: 1 tarefa pesada por vez, `Nice=10`, `CPUWeight` baixo.
- Hashing de senha (Argon2id) calibrado para ≤ 300 ms no processador real (medido na R0), respeitando o mínimo de segurança.

## 5. Carga esperada (Edição Avante)

| Grandeza | Estimativa | Base |
|---|---|---|
| Pessoas com acesso | ~30 | Informado pelo responsável |
| Ativas ao mesmo tempo (pico) | até 10 | ⅓ do total; a medir no piloto |
| Conexões de tempo real | até 60 | Cada pessoa com celular e notebook abertos, com folga |
| Requisições | ~1/s em média; picos de 10/s | 10 pessoas, uma ação a cada ~10 s |
| Movimentações | ~40 por dia útil (~10 mil/ano) | Estimativa; a medir |
| Teste de carga | 2× o pico (20 usuários virtuais) | Margem de segurança |

## 6. Armazenamento (RNF-21)

| Conteúdo | Estimativa | Retenção |
|---|---|---|
| Banco (com auditoria e índices) | ≈ 30 MB/ano (≈ 150 MB em 5 anos) | Permanente |
| Fotos do catálogo | ≈ 1,8 GB (2.000 itens × 3 fotos × 300 KB) | Enquanto o item existir |
| Anexos de suporte e ocorrências | ≤ 1 GB/ano | Configurável (padrão: 2 anos após o fechamento) |
| Imagens de referência/validação de visão (R3) | ≤ 1 GB | Enquanto o modelo estiver em uso |
| WAL local | ≤ 2 GB | 7 dias (cópias externas no backup) |
| Logs | ≤ 500 MB | 30 dias |
| **Total estimado** | **≤ 8 GB no 1º ano; ≈ +3 GB/ano** | Alerta a 80% do disco |

Os números são estimativas iniciais: o `avante doctor` mede o crescimento real e projeta quando o disco chega a 80%.

## 7. Saúde do hardware

| Risco | Monitoramento | Ação |
|---|---|---|
| HD falhando (setores realocados, erros de leitura) | `smartd` com teste curto semanal e longo mensal; atributos críticos no painel de saúde | Alerta imediato ao Proprietário; plano de troca de disco (Volume 10, runbook "HD com falha") |
| Superaquecimento | `lm-sensors` a cada 5 min | Alerta acima do limite do processador; limpeza e pasta térmica na manutenção semestral |
| Memória com defeito | `memtest86+` na R0 | Trocar o pente antes de instalar |
| Bateria inchada ou viciada | `upower` mensal; inspeção visual semestral | Bateria inchada é **risco de incêndio**: remover e usar o notebook na tomada com nobreak |
| Notebook fechado/suspenso | Configuração de energia (ADR-002) | Verificado pelo `avante doctor` |

## 8. Energia

| Situação | Comportamento esperado |
|---|---|
| Queda curta (< autonomia da bateria/nobreak) | Nada acontece; alerta de "servidor na bateria" |
| Bateria crítica | Desligamento ordenado: serviços param, banco grava tudo, sistema desliga |
| Energia volta | Se a BIOS religar sozinha (ou houver nobreak que mantém o notebook ligado), o serviço volta em < 5 min (RNF-06). Se a BIOS **não** tiver religamento automático, alguém precisa ligar o notebook — essa limitação é registrada na R0 e mitigada com nobreak |
| Queda sem desligamento ordenado | PostgreSQL recupera pelo WAL (sem perda de transações confirmadas); `avante doctor` verifica a integridade após o boot |

## 9. Rede

- Servidor **por cabo**, com IP reservado no roteador; Wi-Fi do servidor desligado.
- Celulares e notebooks pelo Wi-Fi da rede local; de fora, pela VPN ou túnel (ADR-007).
- Nome do servidor resolvido para o IP local (validado na R0, incluindo roteadores que bloqueiam respostas DNS com IP privado).

## 10. Melhorias de hardware recomendadas (não exigidas)

| Melhoria | Custo relativo | Ganho esperado | Como será decidido |
|---|---|---|---|
| Trocar o HD por SSD SATA | Baixo | Boot e reinício muito mais rápidos, backup e restauração mais rápidos, servidor mais resistente a impacto, latência estável | Medição antes/depois na R0 (`fio` + teste de carga); decisão do responsável |
| Ir para 8 GB de memória (2 × 4 GB DDR3) | Baixo | Mais cache de disco e folga no pico | Se o teste de carga mostrar troca (swap) relevante |
| Nobreak pequeno | Baixo a médio | Atravessa quedas curtas; desligamento ordenado garantido | Recomendado se a bateria estiver fraca ou a BIOS não religar sozinha |

## 11. Quando migrar de máquina

Migrar para hardware melhor (procedimento: restaurar backup na máquina nova, Volume 10) quando qualquer um ocorrer por duas semanas seguidas: p95 acima da meta do RNF-05; uso de troca acima de 20%; disco acima de 80% sem possibilidade de limpeza; alerta SMART crítico; temperatura acima do limite mesmo após manutenção.
