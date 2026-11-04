# Melhorias do Almoxarifado — visão computacional e notas fiscais

## O que foi adicionado

- Seletor de câmera (USB/integrada/traseira, quando o navegador disponibiliza os dispositivos).
- Painel de leitura com estado de câmera, feedback de processamento, confirmação visual do resultado e amostra da imagem capturada.
- Histórico visual dos últimos 12 eventos de leitura, incluindo erros.
- Detecção local de QR pelo `BarcodeDetector` quando disponível, enviando a imagem ao backend apenas quando detecta um novo conteúdo e liberando nova leitura após o QR ficar ausente por alguns quadros. Isso evita contar repetidamente um QR mantido parado na câmera em navegadores compatíveis.
- Em navegadores sem `BarcodeDetector`, o leitor adota fallback conservador para evitar incrementar repetidamente o mesmo QR: depois de uma leitura, pare e reabra a câmera antes do próximo item.
- Nova seção de notas fiscais: permite visualizar PDF/imagem e importar produtos a partir do XML oficial da NF-e. O XML é analisado e os produtos/quantidades aparecem em uma tabela de revisão antes de cadastrar no estoque.
- Relatório de sucesso/falha na importação de produtos da NF-e.

## Como atualizar sem apagar o banco Docker

1. Faça backup do banco antes de atualizar.
2. Extraia os arquivos deste pacote por cima da pasta do projeto atual, mantendo seu `.env` existente.
3. Não execute `docker compose down -v`: a opção `-v` apaga volumes e pode destruir o banco.
4. Na pasta que contém `docker-compose.yml`, execute:

   ```powershell
   docker compose up -d --build
   docker compose ps
   docker compose logs --tail=100 backend frontend
   ```

5. Abra `http://localhost:3000`, entre como administrador e vá à aba Itens.

## Formato dos QR Codes

O QR para cadastro automático deve conter JSON, por exemplo:

```json
{
  "nome": "Placa ESP32",
  "patrimonio": "ESP-001",
  "codigo_qr": "QR-ESP-001",
  "area": "Laboratório",
  "setor_id": 1
}
```

O `setor_id` precisa existir no banco atual. Alternativamente, use `setor_nome` com o nome exato de um setor existente. A câmera usa o backend para validar o conteúdo e registrar a entrada.

## Importação de nota fiscal

- PDF e imagens são exibidos para consulta, mas não são convertidos automaticamente em itens.
- Para importação automática dos produtos, use o XML oficial da NF-e. O sistema extrai código do produto, descrição e quantidade comercial; o administrador seleciona o setor e a área antes de importar.
- O cadastro usa o código de produto da nota como patrimônio/código interno provisório. Revise esse mapeamento conforme a regra de patrimônio da organização.
- Produtos que já existam ou que tenham código duplicado podem falhar; o resultado informa quais não foram importados.
- Esta versão não valida assinatura fiscal, chave de acesso, autorização SEFAZ nem substitui a conferência contábil da nota.

## Observações de compatibilidade

- A câmera exige contexto seguro (HTTPS) ou `localhost`, além da permissão do navegador.
- A seleção de câmeras e a detecção local dependem do navegador/dispositivo. Recomenda-se Chrome ou Edge atualizados.
- A imagem de amostra e o histórico são mantidos na tela durante a sessão; não são um sistema persistente de auditoria.
- A compilação de produção do frontend ainda deve ser confirmada no ambiente de destino com `npm ci` e `npm run build`; nesta sessão a instalação de dependências excedeu o tempo disponível. O backend modificado foi validado com `python -m py_compile`.
