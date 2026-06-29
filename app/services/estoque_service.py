from app import db
from app.models.estoque import Estoque
from app.models.produto import Produto
from app.models.unidade import Unidade
from app.utils.responses import erro_response


def criar_estoque_service(data, perfil):
    if perfil != "GERENTE":
        return erro_response(
            "SEM_PERMISSAO",
            "Usuário sem permissão.",
            403
        )

    produto_id = data.get("produto_id")
    unidade_id = data.get("unidade_id")
    quantidade = data.get("quantidade")

    if produto_id is None or unidade_id is None or quantidade is None:
        return erro_response(
            "DADOS_INVALIDOS",
            "produto_id, unidade_id e quantidade são obrigatórios.",
            422,
            [
                {"field": "produto_id", "issue": "Campo obrigatório"},
                {"field": "unidade_id", "issue": "Campo obrigatório"},
                {"field": "quantidade", "issue": "Campo obrigatório"}
            ]
        )

    try:
        produto_id = int(produto_id)
    except (TypeError, ValueError):
        return erro_response(
            "PRODUTO_INVALIDO",
            "produto_id deve ser um número inteiro.",
            422,
            [{"field": "produto_id", "issue": "Deve ser um número inteiro"}]
        )

    try:
        unidade_id = int(unidade_id)
    except (TypeError, ValueError):
        return erro_response(
            "UNIDADE_INVALIDA",
            "unidade_id deve ser um número inteiro.",
            422,
            [{"field": "unidade_id", "issue": "Deve ser um número inteiro"}]
        )

    try:
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        return erro_response(
            "QUANTIDADE_INVALIDA",
            "A quantidade deve ser um número inteiro.",
            422,
            [{"field": "quantidade", "issue": "Deve ser um número inteiro"}]
        )

    if quantidade < 0:
        return erro_response(
            "QUANTIDADE_INVALIDA",
            "A quantidade não pode ser negativa.",
            422,
            [{"field": "quantidade", "issue": "Não pode ser negativa"}]
        )

    produto = Produto.query.get(produto_id)

    if not produto:
        return erro_response(
            "PRODUTO_NAO_ENCONTRADO",
            "Produto não encontrado.",
            404,
            [{"field": "produto_id", "issue": "Produto inexistente"}]
        )

    unidade = Unidade.query.get(unidade_id)

    if not unidade:
        return erro_response(
            "UNIDADE_NAO_ENCONTRADA",
            "Unidade não encontrada.",
            404,
            [{"field": "unidade_id", "issue": "Unidade inexistente"}]
        )

    estoque_existente = Estoque.query.filter_by(
        produto_id=produto_id,
        unidade_id=unidade_id
    ).first()

    if estoque_existente:
        return erro_response(
            "ESTOQUE_JA_CADASTRADO",
            "Já existe estoque cadastrado para este produto nesta unidade.",
            409,
            [
                {
                    "field": "produto_id/unidade_id",
                    "issue": "Estoque já cadastrado para essa combinação"
                }
            ]
        )

    estoque = Estoque(
        produto_id=produto_id,
        unidade_id=unidade_id,
        quantidade=quantidade
    )

    db.session.add(estoque)
    db.session.commit()

    return {
        "id": estoque.id,
        "produto_id": estoque.produto_id,
        "unidade_id": estoque.unidade_id,
        "quantidade": estoque.quantidade
    }, 201


def listar_estoque_service(perfil, page=1, limit=10):
    perfis_permitidos = ["GERENTE", "ATENDENTE", "COZINHA"]

    if perfil not in perfis_permitidos:
        return erro_response(
            "SEM_PERMISSAO",
            "Usuário sem permissão para consultar estoque.",
            403,
            [
                {
                    "field": "perfil",
                    "issue": "Apenas GERENTE, ATENDENTE ou COZINHA podem consultar estoque"
                }
            ]
        )

    total = Estoque.query.count()

    estoques = (
        Estoque.query
        .order_by(Estoque.id)
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
                "id": e.id,
                "produto_id": e.produto_id,
                "unidade_id": e.unidade_id,
                "quantidade": e.quantidade
            }
            for e in estoques
        ]
    }, 200


def atualizar_estoque_service(id, data, perfil):
    if perfil != "GERENTE":
        return erro_response(
            "SEM_PERMISSAO",
            "Usuário sem permissão.",
            403
        )

    estoque = Estoque.query.get(id)

    if not estoque:
        return erro_response(
            "ESTOQUE_NAO_ENCONTRADO",
            "Estoque não encontrado.",
            404,
            [{"field": "id", "issue": "Estoque inexistente"}]
        )

    quantidade = data.get("quantidade")

    if quantidade is None:
        return erro_response(
            "QUANTIDADE_OBRIGATORIA",
            "Informe a quantidade do estoque.",
            422,
            [{"field": "quantidade", "issue": "Campo obrigatório"}]
        )

    try:
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        return erro_response(
            "QUANTIDADE_INVALIDA",
            "A quantidade deve ser um número inteiro.",
            422,
            [{"field": "quantidade", "issue": "Deve ser um número inteiro"}]
        )

    if quantidade < 0:
        return erro_response(
            "QUANTIDADE_INVALIDA",
            "A quantidade não pode ser negativa.",
            422,
            [{"field": "quantidade", "issue": "Não pode ser negativa"}]
        )

    estoque.quantidade = quantidade

    db.session.commit()

    return {
        "id": estoque.id,
        "produto_id": estoque.produto_id,
        "unidade_id": estoque.unidade_id,
        "quantidade": estoque.quantidade
    }, 200