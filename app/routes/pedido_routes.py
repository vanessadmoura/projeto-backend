from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.services.pedido_service import (
    criar_pedido_service,
    listar_pedidos_service,
    atualizar_status_service
)
from app.utils.responses import erro_response


pedido_bp = Blueprint(
    "pedidos",
    __name__,
    url_prefix="/pedidos"
)


def perfil_atual():
    claims = get_jwt()
    return claims.get("perfil")


def obter_paginacao():
    page = request.args.get("page", 1)
    limit = request.args.get("limit", 10)

    try:
        page = int(page)
        limit = int(limit)
    except (TypeError, ValueError):
        return None, None, erro_response(
            "PAGINACAO_INVALIDA",
            "page e limit devem ser números inteiros maiores que zero.",
            422,
            [
                {"field": "page", "issue": "Deve ser um número inteiro maior que zero"},
                {"field": "limit", "issue": "Deve ser um número inteiro maior que zero"}
            ]
        )

    if page <= 0 or limit <= 0:
        return None, None, erro_response(
            "PAGINACAO_INVALIDA",
            "page e limit devem ser números inteiros maiores que zero.",
            422,
            [
                {"field": "page", "issue": "Deve ser maior que zero"},
                {"field": "limit", "issue": "Deve ser maior que zero"}
            ]
        )

    if limit > 100:
        return None, None, erro_response(
            "LIMITE_INVALIDO",
            "O limite máximo permitido é 100.",
            422,
            [{"field": "limit", "issue": "Valor máximo permitido: 100"}]
        )

    return page, limit, None


@pedido_bp.route("", methods=["POST"])
@jwt_required()
def criar_pedido():
    """
    Cria um novo pedido
    ---
    tags:
      - Pedidos
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - unidadeId
            - canalPedido
            - itens
          properties:
            unidadeId:
              type: integer
              example: 1
            canalPedido:
              type: string
              enum:
                - APP
                - TOTEM
                - BALCAO
                - PICKUP
                - WEB
              example: APP
            itens:
              type: array
              items:
                type: object
                required:
                  - produtoId
                  - quantidade
                properties:
                  produtoId:
                    type: integer
                    example: 1
                  quantidade:
                    type: integer
                    example: 2
    responses:
      201:
        description: Pedido criado com sucesso
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão para criar pedido
      404:
        description: Usuário, unidade, produto ou estoque não encontrado
      409:
        description: Estoque insuficiente
      422:
        description: Dados inválidos
    """
    resposta, status = criar_pedido_service(
    request.get_json(silent=True) or {},
    int(get_jwt_identity()),
    perfil_atual()
)

    return jsonify(resposta), status


@pedido_bp.route("", methods=["GET"])
@jwt_required()
def listar_pedidos():
    """
    Lista pedidos cadastrados com paginação.
    Clientes visualizam apenas seus próprios pedidos.
    Gerente, atendente e cozinha visualizam todos os pedidos.
    ---
    tags:
      - Pedidos
    security:
      - Bearer: []
    parameters:
      - in: query
        name: canalPedido
        required: false
        type: string
        enum:
          - APP
          - TOTEM
          - BALCAO
          - PICKUP
          - WEB
        description: Canal de origem do pedido para filtro
        example: APP
      - in: query
        name: page
        required: false
        type: integer
        description: Número da página
        example: 1
      - in: query
        name: limit
        required: false
        type: integer
        description: Quantidade de itens por página
        example: 10
    responses:
      200:
        description: Lista de pedidos retornada com sucesso
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão
      422:
        description: Canal ou paginação inválida
    """
    canal = request.args.get("canalPedido")

    page, limit, erro = obter_paginacao()

    if erro:
        resposta, status = erro
        return jsonify(resposta), status

    resposta, status = listar_pedidos_service(
        canal,
        int(get_jwt_identity()),
        perfil_atual(),
        page,
        limit
    )

    return jsonify(resposta), status


@pedido_bp.route("/<int:id>/status", methods=["PATCH"])
@jwt_required()
def atualizar_status(id):
    """
    Atualiza o status de um pedido
    ---
    tags:
      - Pedidos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID do pedido
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum:
                - AGUARDANDO_PAGAMENTO
                - EM_PREPARO
                - PRONTO
                - ENTREGUE
                - CANCELADO
              example: PRONTO
    responses:
      200:
        description: Status atualizado com sucesso
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão
      404:
        description: Pedido não encontrado
      409:
        description: Transição de status inválida
      422:
        description: Status inválido ou obrigatório
    """
    resposta, status = atualizar_status_service(
        id,
        request.get_json(silent=True) or {},
        perfil_atual()
    )

    return jsonify(resposta), status