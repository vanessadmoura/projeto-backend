from app import db
from app.models.produto import Produto
from app.utils.responses import erro_response


def criar_produto_service(data, perfil):
    if perfil != "GERENTE":
        return erro_response(
            "SEM_PERMISSAO",
            "Usuário sem permissão.",
            403,
            [{"field": "perfil", "issue": "Apenas GERENTE pode cadastrar produtos"}]
        )

    nome = data.get("nome")
    preco = data.get("preco")

    if nome is not None:
        nome = nome.strip()

    if not nome or preco is None:
        return erro_response(
            "DADOS_INVALIDOS",
            "Nome e preço são obrigatórios.",
            422,
            [
                {"field": "nome", "issue": "Campo obrigatório"},
                {"field": "preco", "issue": "Campo obrigatório"}
            ]
        )

    try:
        preco = float(preco)
    except (TypeError, ValueError):
        return erro_response(
            "PRECO_INVALIDO",
            "O preço deve ser numérico.",
            422,
            [{"field": "preco", "issue": "Deve ser numérico"}]
        )

    if preco <= 0:
        return erro_response(
            "PRECO_INVALIDO",
            "O preço deve ser maior que zero.",
            422,
            [{"field": "preco", "issue": "Deve ser maior que zero"}]
        )

    produto_existente = Produto.query.filter(
        db.func.lower(Produto.nome) == nome.lower()
    ).first()

    if produto_existente:
        return erro_response(
            "PRODUTO_JA_CADASTRADO",
            "Já existe um produto cadastrado com este nome.",
            409,
            [{"field": "nome", "issue": "Produto já cadastrado"}]
        )

    produto = Produto(nome=nome, preco=preco)

    db.session.add(produto)
    db.session.commit()

    return {
        "id": produto.id,
        "nome": produto.nome,
        "preco": produto.preco
    }, 201


def listar_produtos_service(page=1, limit=10):
    total = Produto.query.count()

    produtos = (
        Produto.query
        .order_by(Produto.id)
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
                "id": produto.id,
                "nome": produto.nome,
                "preco": produto.preco
            }
            for produto in produtos
        ]
    }, 200


def buscar_produto_service(id):
    try:
        id = int(id)
    except (TypeError, ValueError):
        return erro_response(
            "PRODUTO_INVALIDO",
            "O id do produto deve ser um número inteiro.",
            422,
            [{"field": "id", "issue": "Deve ser um número inteiro"}]
        )

    produto = Produto.query.get(id)

    if not produto:
        return erro_response(
            "PRODUTO_NAO_ENCONTRADO",
            "Produto não encontrado.",
            404,
            [{"field": "id", "issue": "Produto inexistente"}]
        )

    return {
        "id": produto.id,
        "nome": produto.nome,
        "preco": produto.preco
    }, 200