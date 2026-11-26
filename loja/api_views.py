from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Pedido, Produto
from .serializers import PedidoSerializer, ProdutoSerializer

class ProdutoListCreateView(generics.ListCreateAPIView):
    queryset = Produto.objects.select_related("categoria", "vendedor").order_by("nome")
    serializer_class = ProdutoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def perform_create(self, serializer):
        serializer.save(vendedor=self.request.user)

class PedidoCreateView(generics.CreateAPIView):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
