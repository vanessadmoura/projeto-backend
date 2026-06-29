# API Raízes do Nordeste

Projeto Back-end desenvolvido em **Python/Flask** para a rede de lanchonetes **Raízes do Nordeste**.

A API permite cadastro e autenticação de usuários, gerenciamento de produtos, unidades, cardápio por unidade, estoque, pedidos multicanal, pagamento mock, programa de fidelidade com consentimento LGPD e auditoria por meio de logs.

---

## Evidências do Projeto

- Repositório GitHub: `<INSERIR_LINK_PUBLICO_DO_REPOSITORIO>`
- Swagger local: `http://127.0.0.1:5000/apidocs`
- Collection Postman: `postman/API_Raizes_do_Nordeste.postman_collection.json`
- Environment Postman: `postman/API_Raizes_do_Nordeste.postman_environment.json`
- Banco de dados: SQLite com migrations via Flask-Migrate
- Fluxo principal do MVP: criação de pedido, pagamento mock e atualização de status

---

## Tecnologias Utilizadas

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Flasgger (Swagger)
- SQLite
- bcrypt
- python-dotenv

---

## Funcionalidades

- Cadastro público de clientes
- Login com autenticação JWT
- Controle de perfis: `CLIENTE`, `ATENDENTE`, `COZINHA` e `GERENTE`
- Cadastro, consulta e paginação de produtos
- Cadastro, consulta e paginação de unidades
- Consulta de cardápio por unidade com base no estoque disponível
- Cadastro, consulta, atualização e paginação de estoque por unidade
- Criação de pedidos com múltiplos itens
- Registro obrigatório do canal do pedido
- Associação do pedido a uma unidade
- Cálculo automático do valor total do pedido
- Controle de estoque durante a criação do pedido
- Bloqueio de pedidos quando não houver estoque suficiente
- Consulta de pedidos com paginação
- Filtro de pedidos por canal
- Controle de visualização de pedidos por perfil
- Atualização de status do pedido com validação de transição
- Pagamento mock aprovado ou recusado
- Devolução automática de estoque quando o pagamento mock é recusado
- Programa de fidelidade com consentimento LGPD, consulta, adição e resgate de pontos
- Tratamento de erros padronizado em JSON
- Registro de logs de auditoria

---

## Perfis de Usuário

| Perfil      | Permissões                                                                                                                                                |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CLIENTE`   | Criar pedidos, pagar os próprios pedidos, consultar os próprios pedidos, registrar consentimento LGPD, consultar pontos e resgatar fidelidade             |
| `ATENDENTE` | Consultar pedidos e registrar pagamento mock                                                                                                              |
| `COZINHA`   | Consultar pedidos e atualizar status de preparo                                                                                                           |
| `GERENTE`   | Cadastrar produtos, unidades e estoque, atualizar estoque, consultar pedidos, atualizar status, adicionar pontos de fidelidade e registrar pagamento mock |

O cadastro público em `/auth/register` cria sempre usuários com perfil `CLIENTE`.

Usuários operacionais, como `GERENTE`, `ATENDENTE` e `COZINHA`, são criados pelo arquivo `seed.py`.

---

## Usuários de Teste

Após executar o arquivo `seed.py`, ficam disponíveis os seguintes usuários:

| Perfil      | E-mail                | Senha    |
| ----------- | --------------------- | -------- |
| `GERENTE`   | `gerente@email.com`   | `123456` |
| `CLIENTE`   | `cliente@email.com`   | `123456` |
| `ATENDENTE` | `atendente@email.com` | `123456` |
| `COZINHA`   | `cozinha@email.com`   | `123456` |

---

## Canais de Pedido

O campo `canalPedido` é obrigatório na criação de pedidos.

Valores aceitos:

- `APP`
- `TOTEM`
- `BALCAO`
- `PICKUP`
- `WEB`

Exemplo:

```json
{
  "canalPedido": "APP"
}
```

---

## Status do Pedido

Os status utilizados no pedido são:

- `AGUARDANDO_PAGAMENTO`
- `EM_PREPARO`
- `PRONTO`
- `ENTREGUE`
- `CANCELADO`

Fluxo principal:

```text
Criar pedido -> AGUARDANDO_PAGAMENTO
Pagamento aprovado -> EM_PREPARO
Atualização pela cozinha/atendimento/gerência -> PRONTO
Finalização -> ENTREGUE
```

Transições permitidas:

| Status atual           | Próximos status permitidos |
| ---------------------- | -------------------------- |
| `AGUARDANDO_PAGAMENTO` | `CANCELADO`                |
| `EM_PREPARO`           | `PRONTO`, `CANCELADO`      |
| `PRONTO`               | `ENTREGUE`, `CANCELADO`    |
| `ENTREGUE`             | Nenhuma alteração          |
| `CANCELADO`            | Nenhuma alteração          |

O status `EM_PREPARO` é definido automaticamente quando o pagamento mock é aprovado.

---

## Como Executar o Projeto

### 1. Clonar o repositório

```bash
git clone <INSERIR_LINK_PUBLICO_DO_REPOSITORIO>
cd projeto-backend
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
```

### 3. Ativar ambiente virtual

No Git Bash:

```bash
source venv/Scripts/activate
```

No CMD:

```cmd
venv\Scripts\activate
```

No PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar o arquivo `.env`

Crie um arquivo chamado `.env` na raiz do projeto com base no arquivo `.env.example`.

Exemplo:

```env
SECRET_KEY=super-secret-key
JWT_SECRET_KEY=jwt-super-secret-key
DATABASE_URL=sqlite:///raizes.db
```

### 6. Executar as migrations

Se a pasta `migrations` ainda não existir, execute apenas uma vez:

```bash
python -m flask --app run:app db init
```

Para criar ou atualizar as tabelas no banco SQLite:

```bash
python -m flask --app run:app db upgrade
```

Caso tenha alterado models e precise gerar uma nova migration:

```bash
python -m flask --app run:app db migrate -m "descricao da alteracao"
python -m flask --app run:app db upgrade
```

### 7. Criar usuários de teste

```bash
python seed.py
```

Esse comando cria usuários de teste para os perfis `GERENTE`, `CLIENTE`, `ATENDENTE` e `COZINHA`.

### 8. Executar a aplicação

```bash
python run.py
```

A API ficará disponível em:

```text
http://127.0.0.1:5000
```

---

## Swagger

A documentação da API pode ser acessada localmente em:

```text
http://127.0.0.1:5000/apidocs
```

Para testar rotas protegidas no Swagger, utilize o token JWT retornado no login no formato:

```text
Bearer SEU_TOKEN_AQUI
```

---

## Collection Postman

A coleção de testes da API está disponível na pasta:

```text
postman/API_Raizes_do_Nordeste.postman_collection.json
```

Também foi disponibilizado um arquivo de ambiente do Postman:

```text
postman/API_Raizes_do_Nordeste.postman_environment.json
```

No Postman, importe os dois arquivos:

1. `API_Raizes_do_Nordeste.postman_collection.json`
2. `API_Raizes_do_Nordeste.postman_environment.json`

Depois de importar, selecione o ambiente **API Raízes do Nordeste - Ambiente Local** antes de executar as requisições.

O arquivo de ambiente contém a variável `baseUrl` e variáveis para armazenar os tokens JWT obtidos no login, como `tokenGerente`, `tokenCliente`, `tokenAtendente` e `tokenCozinha`.

Os IDs de produto, unidade, estoque, pedido e cliente podem ser ajustados manualmente no corpo das requisições ou nas URLs, conforme os registros criados durante os testes.

A Collection contém requisições organizadas por módulos, incluindo:

- Auth
- Produtos
- Unidades
- Estoque
- Pedidos
- Pagamentos
- Fidelidade
- Erros

Fluxo principal recomendado para testar a API:

1. Executar migrations.
2. Executar `python seed.py`.
3. Executar `python run.py`.
4. Importar a Collection e o Environment no Postman.
5. Selecionar o ambiente **API Raízes do Nordeste - Ambiente Local**.
6. Fazer login como gerente.
7. Criar unidade.
8. Criar produto.
9. Criar estoque para o produto em uma unidade.
10. Fazer login como cliente.
11. Criar pedido informando `unidadeId`, `canalPedido` e itens.
12. Realizar pagamento mock aprovado.
13. Atualizar o pedido para `PRONTO`.
14. Atualizar o pedido para `ENTREGUE`.
15. Criar outro pedido.
16. Realizar pagamento mock recusado.
17. Consultar cardápio da unidade.
18. Consultar pedidos.
19. Registrar consentimento LGPD do cliente para fidelidade.
20. Fazer login como gerente e adicionar pontos ao cliente.
21. Fazer login como cliente e resgatar pontos.

As rotas protegidas devem ser testadas utilizando o token JWT retornado no login. A Collection salva os tokens no Environment após as requisições de login, mas os IDs usados nos corpos das requisições podem ser conferidos e ajustados manualmente pelo avaliador.

---

## Endpoints

### Autenticação

```text
POST /auth/register
POST /auth/login
```

#### Exemplo de cadastro de cliente

```json
{
  "nome": "Maria Oliveira",
  "email": "maria@email.com",
  "senha": "123456"
}
```

O cadastro público cria sempre um usuário com perfil `CLIENTE`.

#### Exemplo de login

```json
{
  "email": "gerente@email.com",
  "senha": "123456"
}
```

---

### Produtos

```text
POST /produtos
GET /produtos?page=1&limit=10
GET /produtos/{id}
```

#### Exemplo de criação de produto

```json
{
  "nome": "X-Baião",
  "preco": 25.9
}
```

Observação: para cadastrar produto é necessário estar autenticado com perfil `GERENTE`.

#### Exemplo de resposta paginada

```json
{
  "page": 1,
  "limit": 10,
  "total": 1,
  "totalPages": 1,
  "items": [
    {
      "id": 1,
      "nome": "X-Baião",
      "preco": 25.9
    }
  ]
}
```

---

### Unidades

```text
POST /unidades
GET /unidades?page=1&limit=10
GET /unidades/{id}
GET /unidades/{id}/cardapio
```

#### Exemplo de criação de unidade

```json
{
  "nome": "Raízes do Nordeste - Fortaleza",
  "cidade": "Fortaleza"
}
```

Observação: para cadastrar unidade é necessário estar autenticado com perfil `GERENTE`.

#### Exemplo de cardápio por unidade

```json
{
  "unidadeId": 1,
  "unidade": "Raízes do Nordeste - Fortaleza",
  "cidade": "Fortaleza",
  "cardapio": [
    {
      "produtoId": 1,
      "nome": "X-Baião",
      "preco": 25.9,
      "quantidadeDisponivel": 100
    }
  ]
}
```

---

### Estoque

```text
POST /estoques
GET /estoques?page=1&limit=10
PATCH /estoques/{id}
```

#### Exemplo de criação de estoque

```json
{
  "produto_id": 1,
  "unidade_id": 1,
  "quantidade": 100
}
```

#### Exemplo de atualização de estoque

```json
{
  "quantidade": 80
}
```

Observação: para cadastrar ou atualizar estoque é necessário estar autenticado com perfil `GERENTE`.

---

### Pedidos

```text
POST /pedidos
GET /pedidos?page=1&limit=10
GET /pedidos?canalPedido=APP&page=1&limit=10
PATCH /pedidos/{id}/status
```

#### Exemplo de criação de pedido

```json
{
  "unidadeId": 1,
  "canalPedido": "APP",
  "itens": [
    {
      "produtoId": 1,
      "quantidade": 2
    }
  ]
}
```

O pedido deve possuir pelo menos um item, uma unidade válida e um canal válido.

Clientes visualizam apenas seus próprios pedidos. Gerente, atendente e cozinha visualizam todos os pedidos.

#### Exemplo de resposta paginada

```json
{
  "page": 1,
  "limit": 10,
  "total": 1,
  "totalPages": 1,
  "items": [
    {
      "id": 1,
      "cliente_id": 2,
      "unidadeId": 1,
      "canalPedido": "APP",
      "status": "AGUARDANDO_PAGAMENTO",
      "total": 51.8,
      "itens": [
        {
          "produtoId": 1,
          "quantidade": 2,
          "precoUnitario": 25.9,
          "subtotal": 51.8
        }
      ]
    }
  ]
}
```

#### Exemplo de atualização de status

```json
{
  "status": "PRONTO"
}
```

Observação: apenas usuários com perfil `GERENTE`, `ATENDENTE` ou `COZINHA` podem atualizar o status do pedido. A cozinha só pode alterar pedidos para `PRONTO` ou `CANCELADO`.

---

### Pagamentos

```text
POST /pagamentos
```

#### Exemplo de pagamento mock aprovado

```json
{
  "pedidoId": 1,
  "valor": 51.8,
  "aprovado": true
}
```

#### Exemplo de pagamento mock recusado

```json
{
  "pedidoId": 1,
  "valor": 51.8,
  "aprovado": false
}
```

Quando o pagamento mock é aprovado, o pedido passa para o status `EM_PREPARO`.

Quando o pagamento mock é recusado, o pedido passa para o status `CANCELADO` e os itens do pedido são devolvidos ao estoque da unidade.

#### Exemplo de resposta

```json
{
  "pedidoId": 1,
  "pagamentoStatus": "APROVADO",
  "novoStatusPedido": "EM_PREPARO",
  "message": "Pagamento aprovado pelo gateway mock.",
  "gatewayMock": {
    "provedor": "MOCK",
    "status": "APROVADO",
    "valor": 51.8
  }
}
```

---

### Fidelidade

```text
GET /fidelidade
POST /fidelidade/consentimento
POST /fidelidade/adicionar
POST /fidelidade/resgatar
```

#### Consulta de pontos

O cliente autenticado pode consultar seus próprios pontos de fidelidade.

```text
GET /fidelidade
```

#### Registro de consentimento LGPD

Antes de receber ou resgatar pontos, o cliente deve registrar consentimento para participar do programa de fidelidade.

```text
POST /fidelidade/consentimento
```

Exemplo de resposta:

```json
{
  "clienteId": 2,
  "consentimentoLgpd": true,
  "dataConsentimento": "2026-02-05T12:00:00+00:00",
  "message": "Consentimento registrado com sucesso para o programa de fidelidade."
}
```

#### Exemplo de adição de pontos

```json
{
  "clienteId": 2,
  "pontos": 20
}
```

Observação: apenas o perfil `GERENTE` pode adicionar pontos de fidelidade para clientes que tenham registrado consentimento LGPD.

#### Exemplo de resgate de pontos

```json
{
  "pontos": 10
}
```

Observação: apenas o perfil `CLIENTE` pode consultar e resgatar os próprios pontos de fidelidade, desde que tenha registrado consentimento e possua saldo suficiente.

---

## Paginação

As principais listagens da API aceitam paginação por query string:

```text
?page=1&limit=10
```

Endpoints com paginação:

- `GET /produtos`
- `GET /unidades`
- `GET /estoques`
- `GET /pedidos`

Exemplo de resposta:

```json
{
  "page": 1,
  "limit": 10,
  "total": 25,
  "totalPages": 3,
  "items": []
}
```

O limite máximo aceito é `100`.

Quando `page` ou `limit` forem inválidos, a API retorna erro `422` no formato padronizado.

---

## Regras de Negócio

- Todo pedido deve possuir uma unidade válida.
- Todo pedido deve possuir um canal de origem válido.
- Os canais permitidos são `APP`, `TOTEM`, `BALCAO`, `PICKUP` e `WEB`.
- Um pedido deve possuir pelo menos um item.
- Não é permitido criar pedido com quantidade menor ou igual a zero.
- Não é permitido criar pedido com produto inexistente.
- Não é permitido criar pedido sem estoque cadastrado para a unidade.
- Não é permitido criar pedido sem estoque suficiente na unidade.
- Ao criar um pedido válido, o estoque da unidade é reduzido automaticamente.
- Somente usuários com perfil `GERENTE` podem cadastrar produtos, unidades e estoque.
- Não é permitido cadastrar produto duplicado com o mesmo nome.
- Não é permitido cadastrar unidade duplicada com o mesmo nome e cidade.
- Não é permitido cadastrar estoque duplicado para o mesmo produto na mesma unidade.
- O pagamento mock só pode ser realizado para pedidos com status `AGUARDANDO_PAGAMENTO`.
- O pagamento mock aprovado altera o pedido para `EM_PREPARO`.
- O pagamento mock recusado altera o pedido para `CANCELADO`.
- Quando o pagamento mock é recusado, os itens são devolvidos ao estoque da unidade.
- O cliente só pode pagar os próprios pedidos.
- O cliente só pode consultar os próprios pedidos.
- O cliente só pode resgatar pontos se possuir saldo suficiente.
- O cliente precisa registrar consentimento LGPD para participar do programa de fidelidade.
- Apenas o gerente pode adicionar pontos de fidelidade para clientes.
- Pontos de fidelidade só podem ser atribuídos a usuários com perfil `CLIENTE`.
- Pontos de fidelidade só podem ser adicionados para clientes com consentimento LGPD registrado.
- O status do pedido respeita transições permitidas entre `AGUARDANDO_PAGAMENTO`, `EM_PREPARO`, `PRONTO`, `ENTREGUE` e `CANCELADO`.

---

## Promoções e Campanhas

As promoções e campanhas da rede Raízes do Nordeste foram previstas como regra de negócio para aplicação futura no fluxo de pedidos.

A regra proposta é que uma campanha possa ser vinculada a uma unidade, produto, canal de pedido ou período de validade. Dessa forma, o back-end poderia aplicar descontos ou benefícios antes do fechamento do valor total do pedido.

Exemplos de campanhas possíveis:

- desconto de 10% para pedidos realizados pelo canal `APP`;
- promoção exclusiva para uma unidade específica;
- campanha de produto com preço promocional por período determinado;
- bônus de pontos de fidelidade para pedidos acima de determinado valor;
- campanha de retirada no balcão ou pickup.

A aplicação da campanha deve ocorrer durante a criação do pedido, antes do cálculo final do total. O sistema deve validar:

- se a campanha está ativa;
- se a data atual está dentro do período de validade;
- se a campanha se aplica à unidade do pedido;
- se a campanha se aplica ao canal informado em `canalPedido`;
- se os produtos do pedido fazem parte da campanha;
- se o cliente possui consentimento no programa de fidelidade, quando a campanha envolver pontos.

Neste MVP, as campanhas não foram implementadas como entidade própria no banco de dados, pois a prioridade definida foi entregar o fluxo crítico recomendado: criação de pedido, validação de estoque, pagamento mock e atualização de status. Porém, a estrutura atual da API permite evolução futura para um módulo `/campanhas`, mantendo coerência com os recursos já existentes.

---

## Tratamento de Erros

A API retorna erros em formato JSON padronizado.

Exemplo:

```json
{
  "error": "ESTOQUE_INSUFICIENTE",
  "message": "Quantidade insuficiente em estoque nesta unidade.",
  "details": [
    {
      "field": "itens[0].quantidade",
      "issue": "Disponível: 3"
    }
  ],
  "timestamp": "2026-02-05T12:00:00+00:00",
  "path": "/pedidos"
}
```

Campos do erro:

| Campo       | Descrição                                         |
| ----------- | ------------------------------------------------- |
| `error`     | Código interno do erro                            |
| `message`   | Mensagem explicativa para o consumidor da API     |
| `details`   | Lista de detalhes sobre campos ou regras violadas |
| `timestamp` | Data e hora do erro em formato ISO                |
| `path`      | Caminho da rota acessada                          |

Principais códigos HTTP utilizados:

| Código | Significado                      |
| ------ | -------------------------------- |
| 200    | Requisição realizada com sucesso |
| 201    | Recurso criado com sucesso       |
| 401    | Não autenticado                  |
| 403    | Sem permissão                    |
| 404    | Recurso não encontrado           |
| 409    | Conflito com regra de negócio    |
| 422    | Dados inválidos                  |

Os erros de autenticação JWT também seguem o padrão JSON da API, incluindo token ausente, token inválido e token expirado.

---

## Logs de Auditoria

Os registros são gravados em:

```text
logs/auditoria.log
```

São registrados eventos como:

- Cadastro de usuários
- Login
- Criação de pedidos
- Alteração de status
- Pagamentos
- Consentimento LGPD de fidelidade
- Adição e resgate de pontos
- Método HTTP
- Rota acessada
- Código de resposta

Exemplo:

```text
Metodo=POST Rota=/pedidos Status=201
Novo usuário cadastrado: id=1, email=cliente@email.com, perfil=CLIENTE
Login realizado: id=1, email=cliente@email.com, perfil=CLIENTE
Pedido criado: id=5, cliente=1, unidade=1, canal=APP, total=89.90
Pagamento APROVADO: pedido=5, valor=89.90, novo_status=EM_PREPARO
Status do pedido alterado: id=5, de=EM_PREPARO, para=PRONTO
Consentimento LGPD registrado: cliente=1, fidelidade=1
```

---

## Banco de Dados

O projeto utiliza:

- SQLite
- SQLAlchemy
- Flask-Migrate

Banco criado em:

```text
instance/raizes.db
```

Para criar ou atualizar as tabelas, utilize:

```bash
python -m flask --app run:app db upgrade
```

O arquivo `.db` não precisa ser enviado preenchido, pois o banco pode ser recriado pelas migrations.

---

## Segurança

A aplicação utiliza:

- JWT para autenticação
- Senhas protegidas com bcrypt
- Controle de acesso baseado em perfis
- Validação dos dados recebidos
- Cadastro público restrito ao perfil `CLIENTE`
- Usuários operacionais criados por seed
- Controle de visualização de pedidos por perfil
- Cliente restrito aos próprios pedidos e pontos
- Controle de estoque durante a criação dos pedidos
- Pagamento externo simulado por gateway mock
- Tratamento de erros padronizado
- Logs de auditoria para ações importantes
- Arquivo `.env` ignorado pelo Git

---

## LGPD

A API utiliza dados pessoais básicos dos usuários, como nome, e-mail e senha.

Esses dados são utilizados para cadastro, autenticação, controle de acesso, identificação do cliente nos pedidos e participação no programa de fidelidade.

A senha é armazenada com hash utilizando bcrypt, não sendo salva em texto puro no banco de dados.

O acesso às funcionalidades protegidas depende de autenticação por token JWT.

Clientes visualizam apenas seus próprios pedidos e seus próprios pontos de fidelidade.

O programa de fidelidade possui controle de consentimento LGPD. Antes de receber ou resgatar pontos, o cliente precisa registrar consentimento por meio da rota:

```text
POST /fidelidade/consentimento
```

Após o consentimento, ficam registrados:

- `consentimento_lgpd`
- `data_consentimento`

Os logs de auditoria são utilizados para rastrear ações importantes dentro da aplicação, contribuindo para segurança e acompanhamento do sistema.

O arquivo `.env`, o banco SQLite local e os logs não devem ser enviados ao repositório público.

---

## Estrutura do Projeto

```text
app/
├── models/
├── routes/
├── services/
├── utils/
│   ├── __init__.py
│   └── responses.py
├── swagger_config.py
├── __init__.py

logs/
├── auditoria.log

migrations/

postman/
├── API_Raizes_do_Nordeste.postman_collection.json
├── API_Raizes_do_Nordeste.postman_environment.json

instance/

config.py
run.py
seed.py
requirements.txt
.env.example
.gitignore
README.md
```

---

## Testes

Os testes foram realizados utilizando o Postman.

A Collection está organizada em pastas por módulo:

- Auth
- Produtos
- Unidades
- Estoque
- Pedidos
- Pagamentos
- Fidelidade
- Erros

Foram testados cenários positivos e negativos, incluindo:

| Nº  | Cenário                                                 | Tipo     | Resultado esperado                                  |
| --- | ------------------------------------------------------- | -------- | --------------------------------------------------- |
| 1   | Login com usuário válido                                | Positivo | Retornar token JWT                                  |
| 2   | Login com senha inválida                                | Negativo | Retornar 401                                        |
| 3   | Criar produto com gerente                               | Positivo | Retornar 201                                        |
| 4   | Criar produto sem token                                 | Negativo | Retornar 401                                        |
| 5   | Criar produto com cliente                               | Negativo | Retornar 403                                        |
| 6   | Criar unidade com gerente                               | Positivo | Retornar 201                                        |
| 7   | Criar estoque com gerente                               | Positivo | Retornar 201                                        |
| 8   | Criar estoque duplicado                                 | Negativo | Retornar 409                                        |
| 9   | Criar pedido válido com `canalPedido`                   | Positivo | Retornar 201                                        |
| 10  | Criar pedido sem `canalPedido`                          | Negativo | Retornar 422                                        |
| 11  | Criar pedido com produto inexistente                    | Negativo | Retornar 404                                        |
| 12  | Criar pedido com estoque insuficiente                   | Negativo | Retornar 409                                        |
| 13  | Pagamento mock aprovado                                 | Positivo | Retornar 200 e status `EM_PREPARO`                  |
| 14  | Pagamento mock recusado                                 | Positivo | Retornar 200, status `CANCELADO` e devolver estoque |
| 15  | Pagamento com valor divergente                          | Negativo | Retornar 409                                        |
| 16  | Cliente consultar próprios pedidos                      | Positivo | Retornar apenas pedidos do cliente                  |
| 17  | Consultar pedidos por canal                             | Positivo | Retornar pedidos filtrados                          |
| 18  | Atualizar status de `EM_PREPARO` para `PRONTO`          | Positivo | Retornar 200                                        |
| 19  | Atualizar status com transição inválida                 | Negativo | Retornar 409                                        |
| 20  | Registrar consentimento LGPD de fidelidade              | Positivo | Retornar consentimento registrado                   |
| 21  | Gerente adicionar pontos para cliente com consentimento | Positivo | Retornar 200                                        |
| 22  | Adicionar pontos sem consentimento LGPD                 | Negativo | Retornar 409                                        |
| 23  | Cliente resgatar pontos sem saldo suficiente            | Negativo | Retornar 409                                        |
| 24  | Consultar cardápio por unidade                          | Positivo | Retornar produtos disponíveis em estoque            |
| 25  | Paginação inválida                                      | Negativo | Retornar 422                                        |
| 26  | Verificar logs de auditoria                             | Positivo | Registrar evento no arquivo de log                  |

---

## Observações Finais

Este projeto implementa o fluxo principal de uma API back-end para a rede Raízes do Nordeste, contemplando autenticação, autorização por perfil, gestão de unidades, produtos, estoque, pedidos multicanal, pagamento mock, fidelidade com consentimento LGPD, logs de auditoria, tratamento de erros padronizado, documentação Swagger e testes via Postman.

As funcionalidades de promoções e campanhas foram descritas como regra de negócio conceitual neste MVP, com possibilidade de implementação futura.
