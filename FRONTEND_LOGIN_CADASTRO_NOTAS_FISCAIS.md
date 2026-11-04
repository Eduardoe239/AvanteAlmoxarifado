# Atualização do frontend — autenticação e notas fiscais

Base: `lab_almoxarifado_perfil_estoque_refatorado.zip` (versão mais recente disponível nesta conversa).

## Alterações
- Login/cadastro: apresentação modernizada com painel visual azul/índigo, formulário mais limpo, estados de foco e layout responsivo.
- Nota fiscal: área de upload com destaque visual, orientação de formatos, indicação do arquivo escolhido e cabeçalho de resultados.
- Mantida a integração existente com API, validação dos formulários, leitura do XML da NF-e, seleção de setor e cadastro de produtos.
- PDF e imagem continuam disponíveis para visualização; o cadastro automático de produtos continua dependendo do XML original da NF-e.

## Observação
As alterações são de frontend e preservam as funções de autenticação/importação existentes. Testar login, cadastro e importação de XML no ambiente Docker do projeto antes de publicar.
