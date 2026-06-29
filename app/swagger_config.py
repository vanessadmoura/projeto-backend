template = {
    "swagger": "2.0",
    "info": {
        "title": "API Raízes do Nordeste",
        "description": "Sistema de gestão da rede Raízes do Nordeste",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": [
        "http"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Informe o token JWT no formato: Bearer <seu_token>"
        }
    }
}