from decimal import Decimal
from django.contrib import admin
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .admin import ProdutoAdmin
from .models import Categoria, ItemPedido, Pedido, Produto

class Base(TestCase):
    def setUp(self):
        self.v1=User.objects.create_user("vend1",password="senha123",is_staff=True)
        self.v2=User.objects.create_user("vend2",password="senha123",is_staff=True)
        self.cliente=User.objects.create_user("cliente",password="senha123")
        self.cat=Categoria.objects.create(nome="Livros")
        self.p1=Produto.objects.create(vendedor=self.v1,categoria=self.cat,nome="Caneta",preco=Decimal("3.50"),estoque=10)
        self.p2=Produto.objects.create(vendedor=self.v2,categoria=self.cat,nome="Caderno",preco=Decimal("20.00"),estoque=2)
    def add(self,p,n=1):
        for _ in range(n): self.client.post(reverse("adicionar_carrinho",args=[p.id]))

class AdminTests(Base):
    def test_vend1_so_ve_os_seus(self):
        r=RequestFactory().get("/");r.user=self.v1
        self.assertEqual(list(ProdutoAdmin(Produto,admin.site).get_queryset(r)),[self.p1])
    def test_vend2_so_ve_os_seus(self):
        r=RequestFactory().get("/");r.user=self.v2
        self.assertEqual(list(ProdutoAdmin(Produto,admin.site).get_queryset(r)),[self.p2])
    def test_superuser_ve_todos(self):
        u=User.objects.create_superuser("root","root@exemplo.com","senha123")
        r=RequestFactory().get("/");r.user=u
        self.assertEqual(ProdutoAdmin(Produto,admin.site).get_queryset(r).count(),2)
    def test_define_vendedor_ao_salvar(self):
        r=RequestFactory().post("/");r.user=self.v1
        p=Produto(categoria=self.cat,nome="Régua",preco=Decimal("1"),estoque=1)
        ProdutoAdmin(Produto,admin.site).save_model(r,p,None,False)
        self.assertEqual(p.vendedor,self.v1)

class CarrinhoTests(Base):
    def test_carrinho_anonimo(self):
        self.add(self.p1,2);r=self.client.get(reverse("carrinho"))
        self.assertEqual(r.context["total"],Decimal("7.00"))
    def test_adicionar_exige_post(self):
        self.assertEqual(self.client.get(reverse("adicionar_carrinho",args=[self.p1.id])).status_code,405)
    def test_carrinho_vazio(self):
        self.assertContains(self.client.get(reverse("carrinho")),"Seu carrinho está vazio")
    def test_produto_inexistente(self):
        self.assertEqual(self.client.post(reverse("adicionar_carrinho",args=[999])).status_code,302)

class CheckoutTests(Base):
    def setUp(self):
        super().setUp();self.client.force_login(self.cliente)
    def test_checkout_exige_login(self):
        self.client.logout();self.add(self.p1)
        self.assertEqual(self.client.post(reverse("checkout")).status_code,302)
    def test_compra_baixa_estoque_e_limpa(self):
        self.add(self.p1,3);self.add(self.p2);self.client.post(reverse("checkout"))
        pedido=Pedido.objects.get();self.assertEqual(pedido.itens.count(),2);self.assertEqual(pedido.total,Decimal("30.50"))
        self.p1.refresh_from_db();self.p2.refresh_from_db()
        self.assertEqual((self.p1.estoque,self.p2.estoque),(7,1));self.assertEqual(self.client.session["carrinho"],{})
    def test_falta_estoque_nao_grava_nada(self):
        self.add(self.p1);self.add(self.p2,3);self.client.post(reverse("checkout"))
        self.assertEqual(Pedido.objects.count(),0);self.assertEqual(ItemPedido.objects.count(),0)
        self.p1.refresh_from_db();self.assertEqual(self.p1.estoque,10);self.assertTrue(self.client.session["carrinho"])
    def test_preco_historico(self):
        self.add(self.p1);self.client.post(reverse("checkout"));self.p1.preco=Decimal("99");self.p1.save()
        self.assertEqual(ItemPedido.objects.get().preco_unitario,Decimal("3.50"))
    def test_carrinho_vazio_nao_cria_pedido(self):
        self.client.post(reverse("checkout"));self.assertEqual(Pedido.objects.count(),0)

class APITests(Base):
    def test_get_produtos_publico(self):
        r=APIClient().get(reverse("api-produtos"));self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()),2)
    def test_post_produto_exige_login(self):
        r=APIClient().post(reverse("api-produtos"),{"nome":"X","preco":"1.00","estoque":1,"categoria":self.cat.id})
        self.assertIn(r.status_code,(401,403))
    def test_vendedor_api_automatico(self):
        c=APIClient();c.force_authenticate(self.v1)
        r=c.post(reverse("api-produtos"),{"nome":"Lápis","preco":"2","estoque":5,"categoria":self.cat.id,"vendedor":self.v2.id})
        self.assertEqual(r.status_code,201);self.assertEqual(Produto.objects.get(nome="Lápis").vendedor,self.v1)
    def test_pedido_usa_preco_do_banco(self):
        c=APIClient();c.force_authenticate(self.cliente)
        r=c.post(reverse("api-pedidos"),{"itens":[{"produto":self.p1.id,"quantidade":2,"preco_unitario":"0.01"}]},format="json")
        self.assertEqual(r.status_code,201,r.content);self.assertEqual(ItemPedido.objects.get().preco_unitario,Decimal("3.50"))
        self.p1.refresh_from_db();self.assertEqual(self.p1.estoque,8)
    def test_pedido_sem_estoque(self):
        c=APIClient();c.force_authenticate(self.cliente)
        r=c.post(reverse("api-pedidos"),{"itens":[{"produto":self.p1.id,"quantidade":1},{"produto":self.p2.id,"quantidade":5}]},format="json")
        self.assertEqual(r.status_code,400);self.assertEqual(Pedido.objects.count(),0)
        self.p1.refresh_from_db();self.assertEqual(self.p1.estoque,10)
    def test_post_pedido_exige_login(self):
        self.assertIn(APIClient().post(reverse("api-pedidos"),{"itens":[]},format="json").status_code,(401,403))
    def test_catalogo_tem_fetch_localstorage(self):
        r=self.client.get(reverse("catalogo"));self.assertContains(r,"fetch('/api/produtos/')");self.assertContains(r,"localStorage")
    def test_pedido_vazio_rejeitado(self):
        c=APIClient();c.force_authenticate(self.cliente)
        self.assertEqual(c.post(reverse("api-pedidos"),{"itens":[]},format="json").status_code,400)

class LoginTests(Base):
    def test_carrinho_sem_login_exibe_link(self):
        self.add(self.p1);r=self.client.get(reverse("carrinho"))
        self.assertContains(r,"entre na sua conta");self.assertNotContains(r,"Finalizar compra")
    def test_carrinho_preservado_apos_login(self):
        self.add(self.p1,2);self.client.force_login(self.cliente);r=self.client.get(reverse("carrinho"))
        self.assertContains(r,"Finalizar compra");self.assertEqual(r.context["total"],Decimal("7.00"))
