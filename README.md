# auth-android-api
# Auth Android API

Este projeto é uma API de autenticação para um aplicativo Android. A API permite o registro e login de usuários utilizando diferentes métodos de autenticação, incluindo email e senha, Google, Facebook e dados biométricos. 

## Funcionalidades

- Registro de usuários com diferentes métodos de autenticação.
- Login de usuários com diferentes métodos de autenticação.
- Verificação de tokens de acesso.
- Integração com Google OAuth2 para autenticação.

## Estrutura do Projeto

- `routers.py`: Define as rotas da API para registro e login de usuários.
- `utils.py`: Contém funções utilitárias, como a verificação de tokens do Google.
- `models.py`: Define os modelos de dados utilizados pela API.
- `main.py`: Ponto de entrada da aplicação FastAPI.
- `depends.py`: Define as dependências da API, como a verificação de tokens e a sessão do banco de dados.
- `db/connection.py`: Configura a conexão com o banco de dados e cria as tabelas automaticamente.
- `config.py`: Contém configurações e constantes utilizadas pela API.
- `auth_user.py`: Implementa a lógica de autenticação e registro de usuários.

## Como Executar

1. .
2. .
3. .
4. .

## Notas de Lançamento

- (14/01/2025): Implementação inicial do cadastro e login com Google e email/senha.
- (16/01/2025): Melhorias gerais e correções de bugs.

## TODO

- Validar se é possível fazer login ou cadastro sem token.
- Implementar autenticação com Facebook.
```
