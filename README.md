# Marketplace Simplificado — Projeto 5 (IESB)

Sistema de marketplace acadêmico feito com Django, Django REST Framework, SQLite e JavaScript.

## Funcionalidades
- Categorias e produtos cadastrados pelo Admin.
- Vendedores veem somente seus próprios produtos no Admin.
- Catálogo público que consome a API usando `fetch()`.
- Carrinho salvo na sessão do servidor, mesmo sem login.
- Checkout com `transaction.atomic()` e validação de estoque.
- Histórico do preço pago em cada item do pedido.
- API de produtos (GET público e POST autenticado) e API de pedidos.
- Contador do carrinho em `localStorage`.

## Instalação no VS Code — Windows

1. Extraia o ZIP e abra a pasta `marketplace_iesb` no VS Code.
2. Abra **Terminal > Novo Terminal**.
3. Crie o ambiente virtual:
   `python -m venv venv`
4. Ative:
   `venv\Scripts\Activate.ps1`
5. Se o PowerShell bloquear, execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` e tente ativar novamente.
6. Instale:
   `pip install -r requirements.txt`
7. Gere as tabelas:
   `python manage.py makemigrations loja`
   `python manage.py migrate`
8. Crie o administrador:
   `python manage.py createsuperuser`
9. Inicie:
   `python manage.py runserver`

Acesse:
- Loja: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- API: http://127.0.0.1:8000/api/produtos/

## Testes
`python manage.py test`

## Primeiro uso
Entre no Admin, cadastre uma categoria e produtos com preço, estoque e vendedor. Depois acesse a loja para testar o carrinho e a compra. Para criar vendedores, cadastre usuários, marque **Membro da equipe** e conceda as permissões de Produto.

## Observações
O projeto usa SQLite local por padrão, então não precisa configurar Supabase ou arquivo `.env`. `db.sqlite3` é criado automaticamente. A configuração `DEBUG=True` é para desenvolvimento local, não produção.
