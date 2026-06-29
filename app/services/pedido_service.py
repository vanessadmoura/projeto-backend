from flask import current_app

from app import db
from app.models.pedido import Pedido, CanalPedido, StatusPedido
from app.models.pedido_item import PedidoItem
from app.models.produto import Produto
from app.models.estoque import Estoque
from app.models.usuario import Usuario
from app.models.unidade import Unidade
from app.utils.responses import erro_response


def criar_pedido_service(data, usuario_id, perfil):
    if perfil != "CLIENTE":
        return erro_response(
            "SEM_PERMISSAO",
            "Apenas clientes podem criar pedidos.",
            403,
            [
                {
                    "field": "perfil",
                    "issue": "Somente usuários com perfil CLIENTE podem criar pedidos"
                }
            ]
        )

    unidade_id = data.get("unidadeId")
    canal_pedido = data.get("canalPedido")
    itens_data = data.get("itens")

    if unidade_id is None:
        return erro_response(
            "UNIDADE_OBRIGATORIA",
            "unidadeId é obrigatório.",
            422,
            [{"field": "unidadeId", "issue": "Campo obrigatório"}]
        )

    try:
        unidade_id = int(unidade_id)
    except (TypeError, ValueError):
        return erro_response(
            "UNIDADE_INVALIDA",
            "unidadeId deve ser um número inteiro.",
            422,
            [{"field": "unidadeId", "issue": "Deve ser um número inteiro"}]
        )

    if not canal_pedido:
        return erro_response(
            "CANAL_OBRIGATORIO",
            "canalPedido é obrigatório.",
            422,
            [{"field": "canalPedido", "issue": "Campo obrigatório"}]
        )

    if canal_pedido not in CanalPedido.__members__:
        return erro_response(
            "CANAL_INVALIDO",
            "Canal informado é inválido.",
            422,
            [{"field": "canalPedido", "issue": "Valor permitido: APP, TOTEM, BALCAO, PICKUP ou WEB"}]
        )

    if not isinstance(itens_data, list) or len(itens_data) == 0:
        return erro_response(
            "ITENS_OBRIGATORIOS",
            "O pedido deve possuir pelo menos um item.",
            422,
            [{"field": "itens", "issue": "Deve ser uma lista com pelo menos um item"}]
        )

    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return erro_response(
            "USUARIO_NAO_ENCONTRADO",
            "Usuário não encontrado.",
            404,
            [{"field": "usuarioId", "issue": "Usuário inexistente"}]
        )

    unidade = Unidade.query.get(unidade_id)

    if not unidade:
        return erro_response(
            "UNIDADE_NAO_ENCONTRADA",
            "Unidade não encontrada.",
            404,
            [{"field": "unidadeId", "issue": "Unidade inexistente"}]
        )

    pedido = Pedido(
        cliente_id=usuario.id,
        unidade_id=unidade.id,
        canal_pedido=CanalPedido[canal_pedido],
        total=0
    )

    total_pedido = 0

    for indice, item in enumerate(itens_data):
        if not isinstance(item, dict):
            return erro_response(
                "ITEM_INVALIDO",
                f"O item na posição {indice} deve ser um objeto JSON.",
                422,
                [{"field": f"itens[{indice}]", "issue": "Deve ser um objeto JSON"}]
            )

        produto_id = item.get("produtoId")
        quantidade = item.get("quantidade")

        if produto_id is None or quantidade is None:
            return erro_response(
                "ITEM_INVALIDO",
                "produtoId e quantidade são obrigatórios.",
                422,
                [
                    {"field": f"itens[{indice}].produtoId", "issue": "Campo obrigatório"},
                    {"field": f"itens[{indice}].quantidade", "issue": "Campo obrigatório"}
                ]
            )

        try:
            produto_id = int(produto_id)
        except (TypeError, ValueError):
            return erro_response(
                "PRODUTO_INVALIDO",
                "produtoId deve ser um número inteiro.",
                422,
                [{"field": f"itens[{indice}].produtoId", "issue": "Deve ser um número inteiro"}]
            )

        try:
            quantidade = int(quantidade)
        except (TypeError, ValueError):
            return erro_response(
                "QUANTIDADE_INVALIDA",
                "A quantidade deve ser um número inteiro.",
                422,
                [{"field": f"itens[{indice}].quantidade", "issue": "Deve ser um número inteiro"}]
            )

        if quantidade <= 0:
            return erro_response(
                "QUANTIDADE_INVALIDA",
                "A quantidade deve ser maior que zero.",
                422,
                [{"field": f"itens[{indice}].quantidade", "issue": "Deve ser maior que zero"}]
            )

        produto = Produto.query.get(produto_id)

        if not produto:
            return erro_response(
                "PRODUTO_NAO_ENCONTRADO",
                "Produto não encontrado.",
                404,
                [{"field": f"itens[{indice}].produtoId", "issue": "Produto inexistente"}]
            )

        estoque = Estoque.query.filter_by(
            produto_id=produto.id,
            unidade_id=unidade.id
        ).first()

        if not estoque:
            return erro_response(
                "ESTOQUE_NAO_ENCONTRADO",
                "Produto sem estoque cadastrado nesta unidade.",
                404,
                [
                    {
                        "field": f"itens[{indice}].produtoId",
                        "issue": "Produto sem estoque cadastrado para a unidade informada"
                    }
                ]
            )

        if estoque.quantidade < quantidade:
            return erro_response(
                "ESTOQUE_INSUFICIENTE",
                "Quantidade insuficiente em estoque nesta unidade.",
                409,
                [
                    {
                        "field": f"itens[{indice}].quantidade",
                        "issue": f"Disponível: {estoque.quantidade}"
                    }
                ]
            )

        subtotal = produto.preco * quantidade
        total_pedido += subtotal

        pedido_item = PedidoItem(
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            subtotal=subtotal
        )

        pedido.itens.append(pedido_item)
        estoque.quantidade -= quantidade

    pedido.total = total_pedido

    db.session.add(pedido)
    db.session.commit()

    current_app.logger.info(
        f"Pedido criado: id={pedido.id}, cliente={pedido.cliente_id}, "
        f"unidade={pedido.unidade_id}, canal={pedido.canal_pedido.value}, "
        f"total={pedido.total}"
    )

    return {
        "id": pedido.id,
        "cliente_id": pedido.cliente_id,
        "unidadeId": pedido.unidade_id,
        "canalPedido": pedido.canal_pedido.value,
        "status": pedido.status.value,
        "total": pedido.total,
        "createdAt": pedido.created_at.isoformat(),
        "updatedAt": pedido.updated_at.isoformat(),
        "itens": [
            {
                "produtoId": item.produto_id,
                "quantidade": item.quantidade,
                "precoUnitario": item.preco_unitario,
                "subtotal": item.subtotal
            }
            for item in pedido.itens
        ]
    }, 201


def listar_pedidos_service(canal=None, usuario_id=None, perfil=None, page=1, limit=10):
    perfis_permitidos = ["CLIENTE", "ATENDENTE", "COZINHA", "GERENTE"]

    if perfil not in perfis_permitidos:
        return erro_response(
            "SEM_PERMISSAO",
            "Usuário sem permissão para listar pedidos.",
            403,
            [{"field": "perfil", "issue": "Perfil não autorizado para listar pedidos"}]
        )

    if canal and canal not in CanalPedido.__members__:
        return erro_response(
            "CANAL_INVALIDO",
            "Canal informado é inválido.",
            422,
            [{"field": "canalPedido", "issue": "Valor permitido: APP, TOTEM, BALCAO, PICKUP ou WEB"}]
        )

    query = Pedido.query

    if perfil == "CLIENTE":
        query = query.filter_by(cliente_id=usuario_id)

    if canal:
        query = query.filter_by(canal_pedido=CanalPedido[canal])

    total = query.count()

    pedidos = (
        query
        .order_by(Pedido.id)
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
                "id": p.id,
                "cliente_id": p.cliente_id,
                "unidadeId": p.unidade_id,
                "canalPedido": p.canal_pedido.value,
                "status": p.status.value,
                "total": p.total,
                "createdAt": p.created_at.isoformat(),
                "updatedAt": p.updated_at.isoformat(),
                "itens": [
                    {
                        "produtoId": item.produto_id,
                        "quantidade": item.quantidade,
                        "precoUnitario": item.preco_unitario,
                        "subtotal": item.subtotal
                    }
                    for item in p.itens
                ]
            }
            for p in pedidos
        ]
    }, 200


def atualizar_status_service(id, data, perfil):
    perfis_permitidos = ["COZINHA", "ATENDENTE", "GERENTE"]

    if perfil not in perfis_permitidos:
        return erro_response(
            "SEM_PERMISSAO",
            "Usuário sem permissão para alterar status do pedido.",
            403,
            [{"field": "perfil", "issue": "Perfil não autorizado para alterar status"}]
        )

    pedido = Pedido.query.get(id)

    if not pedido:
        return erro_response(
            "PEDIDO_NAO_ENCONTRADO",
            "Pedido não encontrado.",
            404,
            [{"field": "id", "issue": "Pedido inexistente"}]
        )

    novo_status = data.get("status")

    if not novo_status:
        return erro_response(
            "STATUS_OBRIGATORIO",
            "Status é obrigatório.",
            422,
            [{"field": "status", "issue": "Campo obrigatório"}]
        )

    if novo_status not in StatusPedido.__members__:
        return erro_response(
            "STATUS_INVALIDO",
            "Status informado é inválido.",
            422,
            [
                {
                    "field": "status",
                    "issue": "Valor permitido: AGUARDANDO_PAGAMENTO, EM_PREPARO, PRONTO, ENTREGUE ou CANCELADO"
                }
            ]
        )

    status_atual = pedido.status
    status_destino = StatusPedido[novo_status]

    transicoes_permitidas = {
        StatusPedido.AGUARDANDO_PAGAMENTO: [
            StatusPedido.CANCELADO
        ],
        StatusPedido.EM_PREPARO: [
            StatusPedido.PRONTO,
            StatusPedido.CANCELADO
        ],
        StatusPedido.PRONTO: [
            StatusPedido.ENTREGUE,
            StatusPedido.CANCELADO
        ],
        StatusPedido.ENTREGUE: [],
        StatusPedido.CANCELADO: []
    }

    if status_destino == status_atual:
        return erro_response(
            "STATUS_SEM_ALTERACAO",
            "O pedido já está com o status informado.",
            409,
            [{"field": "status", "issue": f"Status atual: {status_atual.value}"}]
        )

    if status_destino not in transicoes_permitidas[status_atual]:
        return erro_response(
            "TRANSICAO_STATUS_INVALIDA",
            (
                f"Não é permitido alterar o pedido de "
                f"{status_atual.value} para {status_destino.value}."
            ),
            409,
            [
                {
                    "field": "status",
                    "issue": f"Transição inválida: {status_atual.value} -> {status_destino.value}"
                }
            ]
        )

    if perfil == "COZINHA" and status_destino not in [
        StatusPedido.PRONTO,
        StatusPedido.CANCELADO
    ]:
        return erro_response(
            "SEM_PERMISSAO",
            "Cozinha só pode alterar pedido para PRONTO ou CANCELADO.",
            403,
            [{"field": "perfil", "issue": "COZINHA possui transições restritas"}]
        )

    status_anterior = pedido.status.value

    pedido.status = status_destino

    db.session.commit()

    current_app.logger.info(
        f"Status do pedido alterado: id={pedido.id}, "
        f"de={status_anterior}, para={pedido.status.value}, "
        f"perfil={perfil}"
    )

    return {
        "pedidoId": pedido.id,
        "statusAnterior": status_anterior,
        "novoStatus": pedido.status.value,
        "updatedAt": pedido.updated_at.isoformat()
    }, 200