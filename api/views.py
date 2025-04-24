from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from .models import Client
from .serializers import UserSerializer, ClientSerializer
from .permissions import IsAdminUser, IsOwnerOrAdmin
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
    def get_permissions(self):
        if self.action == 'list' or self.action == 'destroy':
            # Only admins can list all clients or delete clients
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == 'retrieve':
            # Owners or admins can view specific clients
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            # Create, update, partial_update
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        # If the user is an admin, return all clients
        if self.request.user.groups.filter(name='ADMIN').exists():
            return Client.objects.all()
        # Otherwise, return only the client associated with this user
        return Client.objects.filter(user=self.request.user)