from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.services.fidelidade_service import (
    consultar_pontos_service,
    registrar_consentimento_service,
    adicionar_pontos_service,
    resgatar_pontos_service
)


fidelidade_bp = Blueprint(
    "fidelidade",
    __name__,
    url_prefix="/fidelidade"
)


def perfil_atual():
    claims = get_jwt()
    return claims.get("perfil")


@fidelidade_bp.route("", methods=["GET"])
@jwt_required()
def consultar_pontos():
    """
    Consulta os pontos de fidelidade do cliente autenticado
    ---
    tags:
      - Fidelidade
    security:
      - Bearer: []
    responses:
      200:
        description: Pontos consultados com sucesso
        examples:
          application/json:
            clienteId: 2
            pontos: 20
            consentimentoLgpd: true
            dataConsentimento: "2026-02-05T12:00:00+00:00"
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão
        examples:
          application/json:
            error: SEM_PERMISSAO
            message: Apenas clientes podem consultar pontos de fidelidade.
            details: []
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade
      404:
        description: Cliente não encontrado
        examples:
          application/json:
            error: CLIENTE_NAO_ENCONTRADO
            message: Cliente não encontrado.
            details:
              - field: clienteId
                issue: Cliente inexistente
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade
    """
    cliente_id = int(get_jwt_identity())

    resposta, status = consultar_pontos_service(
        cliente_id,
        perfil_atual()
    )

    return jsonify(resposta), status


@fidelidade_bp.route("/consentimento", methods=["POST"])
@jwt_required()
def registrar_consentimento():
    """
    Registra consentimento LGPD para participação no programa de fidelidade
    ---
    tags:
      - Fidelidade
    security:
      - Bearer: []
    responses:
      200:
        description: Consentimento registrado com sucesso
        examples:
          application/json:
            clienteId: 2
            consentimentoLgpd: true
            dataConsentimento: "2026-02-05T12:00:00+00:00"
            message: Consentimento registrado com sucesso para o programa de fidelidade.
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão
        examples:
          application/json:
            error: SEM_PERMISSAO
            message: Apenas clientes podem registrar consentimento de fidelidade.
            details: []
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade/consentimento
      404:
        description: Cliente não encontrado
        examples:
          application/json:
            error: CLIENTE_NAO_ENCONTRADO
            message: Cliente não encontrado.
            details:
              - field: clienteId
                issue: Cliente inexistente
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade/consentimento
      422:
        description: Perfil inválido para fidelidade
        examples:
          application/json:
            error: PERFIL_INVALIDO
            message: Consentimento de fidelidade só pode ser registrado para clientes.
            details:
              - field: perfil
                issue: Usuário não possui perfil CLIENTE
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade/consentimento
    """
    cliente_id = int(get_jwt_identity())

    resposta, status = registrar_consentimento_service(
        cliente_id,
        perfil_atual()
    )

    return jsonify(resposta), status


@fidelidade_bp.route("/adicionar", methods=["POST"])
@jwt_required()
def adicionar_pontos():
    """
    Adiciona pontos de fidelidade para um cliente
    ---
    tags:
      - Fidelidade
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - clienteId
            - pontos
          properties:
            clienteId:
              type: integer
              example: 2
            pontos:
              type: integer
              example: 20
    responses:
      200:
        description: Pontos adicionados com sucesso
        examples:
          application/json:
            clienteId: 2
            pontos: 20
            consentimentoLgpd: true
            dataConsentimento: "2026-02-05T12:00:00+00:00"
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão
        examples:
          application/json:
            error: SEM_PERMISSAO
            message: Usuário sem permissão para adicionar pontos.
            details: []
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade/adicionar
      404:
        description: Cliente não encontrado
        examples:
          application/json:
            error: CLIENTE_NAO_ENCONTRADO
            message: Cliente não encontrado.
            details:
              - field: clienteId
                issue: Cliente inexistente
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade/adicionar
      409:
        description: Consentimento necessário ou conflito de fidelidade
        examples:
          application/json:
            error: CONSENTIMENTO_NECESSARIO
            message: O cliente precisa registrar consentimento para participar do programa de fidelidade.
            details:
              - field: consentimentoLgpd
                issue: Consentimento não registrado
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade/adicionar
      422:
        description: Dados inválidos ou pontos inválidos
        examples:
          application/json:
            error: PONTOS_INVALIDOS
            message: Os pontos devem ser maiores que zero.
            details:
              - field: pontos
                issue: Deve ser maior que zero
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade/adicionar
    """
    resposta, status = adicionar_pontos_service(
        request.get_json(silent=True) or {},
        perfil_atual()
    )

    return jsonify(resposta), status


@fidelidade_bp.route("/resgatar", methods=["POST"])
@jwt_required()
def resgatar_pontos():
    """
    Resgata pontos de fidelidade do cliente autenticado
    ---
    tags:
      - Fidelidade
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - pontos
          properties:
            pontos:
              type: integer
              example: 10
    responses:
      200:
        description: Pontos resgatados com sucesso
        examples:
          application/json:
            clienteId: 2
            pontosRestantes: 10
            consentimentoLgpd: true
            dataConsentimento: "2026-02-05T12:00:00+00:00"
            message: Pontos resgatados com sucesso.
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão
        examples:
          application/json:
            error: SEM_PERMISSAO
            message: Apenas clientes podem resgatar pontos de fidelidade.
            details: []
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade/resgatar
      409:
        description: Consentimento necessário ou pontos insuficientes
        examples:
          application/json:
            error: CONSENTIMENTO_NECESSARIO
            message: É necessário registrar consentimento antes de resgatar pontos de fidelidade.
            details:
              - field: consentimentoLgpd
                issue: Consentimento não registrado
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade/resgatar
      422:
        description: Pontos obrigatórios ou inválidos
        examples:
          application/json:
            error: PONTOS_OBRIGATORIOS
            message: Informe a quantidade de pontos.
            details:
              - field: pontos
                issue: Campo obrigatório
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /fidelidade/resgatar
    """
    cliente_id = int(get_jwt_identity())

    resposta, status = resgatar_pontos_service(
        cliente_id,
        request.get_json(silent=True) or {},
        perfil_atual()
    )

    return jsonify(resposta), status