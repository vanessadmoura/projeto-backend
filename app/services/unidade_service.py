from app import db
from app.models.unidade import Unidade
from app.models.estoque import Estoque
from app.models.produto import Produto
from app.utils.responses import erro_response


def criar_unidade_service(data, perfil):
    if perfil != "GERENTE":
        return erro_response(
            "SEM_PERMISSAO",
            "Usuário sem permissão.",
            403,
            [{"field": "perfil", "issue": "Apenas GERENTE pode cadastrar unidades"}]
        )

    nome = data.get("nome")
    cidade = data.get("cidade")

    if nome is not None:
        nome = nome.strip()

    if cidade is not None:
        cidade = cidade.strip()

    if not nome or not cidade:
        return erro_response(
            "DADOS_INVALIDOS",
            "Nome e cidade são obrigatórios.",
            422,
            [
                {"field": "nome", "issue": "Campo obrigatório"},
                {"field": "cidade", "issue": "Campo obrigatório"}
            ]
        )

    unidade_existente = Unidade.query.filter(
        db.func.lower(Unidade.nome) == nome.lower(),
        db.func.lower(Unidade.cidade) == cidade.lower()
    ).first()

    if unidade_existente:
        return erro_response(
            "UNIDADE_JA_CADASTRADA",
            "Já existe uma unidade cadastrada com este nome nesta cidade.",
            409,
            [
                {
                    "field": "nome/cidade",
                    "issue": "Unidade já cadastrada para essa combinação"
                }
            ]
        )

    unidade = Unidade(nome=nome, cidade=cidade)

    db.session.add(unidade)
    db.session.commit()

    return {
        "id": unidade.id,
        "nome": unidade.nome,
        "cidade": unidade.cidade
    }, 201


def listar_unidades_service(page=1, limit=10):
    total = Unidade.query.count()

    unidades = (
        Unidade.query
        .order_by(Unidade.id)
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages,
        "items": [
            {
                "id": unidade.id,
                "nome": unidade.nome,
                "cidade": unidade.cidade
            }
            for unidade in unidades
        ]
    }, 200


def buscar_unidade_service(id):
    try:
        id = int(id)
    except (TypeError, ValueError):
        return erro_response(
            "UNIDADE_INVALIDA",
            "O id da unidade deve ser um número inteiro.",
            422,
            [{"field": "id", "issue": "Deve ser um número inteiro"}]
        )

    unidade = Unidade.query.get(id)

    if not unidade:
        return erro_response(
            "UNIDADE_NAO_ENCONTRADA",
            "Unidade não encontrada.",
            404,
            [{"field": "id", "issue": "Unidade inexistente"}]
        )

    return {
        "id": unidade.id,
        "nome": unidade.nome,
        "cidade": unidade.cidade
    }, 200


def listar_cardapio_unidade_service(id):
    try:
        id = int(id)
    except (TypeError, ValueError):
        return erro_response(
            "UNIDADE_INVALIDA",
            "O id da unidade deve ser um número inteiro.",
            422,
            [{"field": "id", "issue": "Deve ser um número inteiro"}]
        )

    unidade = Unidade.query.get(id)

    if not unidade:
        return erro_response(
            "UNIDADE_NAO_ENCONTRADA",
            "Unidade não encontrada.",
            404,
            [{"field": "id", "issue": "Unidade inexistente"}]
        )

    estoques = Estoque.query.filter_by(unidade_id=unidade.id).all()

    cardapio = []

    for estoque in estoques:
        if estoque.quantidade <= 0:
            continue

        produto = Produto.query.get(estoque.produto_id)

        if not produto:
            continue

        cardapio.append({
            "produtoId": produto.id,
            "nome": produto.nome,
            "preco": produto.preco,
            "quantidadeDisponivel": estoque.quantidade
        })

    return {
        "unidadeId": unidade.id,
        "unidade": unidade.nome,
        "cidade": unidade.cidade,
        "cardapio": cardapio
    }, 200