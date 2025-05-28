from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer
from backend.connections import get_mysql_conn

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        根据不同的action设置不同的权限
        """
        if self.action in ['login', 'register']:
            # 登录和注册不需要认证
            permission_classes = [AllowAny]
        elif self.action in ['list', 'retrieve', 'disable_account', 'enable_account', 'destroy']:
            # 只有管理员可以查看用户列表和管理用户
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            # 其他操作需要登录
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        account = request.data.get('account')
        password = request.data.get('password')
        if not account or not password:
            return Response({'error': '请输入账号和密码'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(account=account)
            if user.check_password(password):
                if not user.is_active:
                    return Response({'error': '账号已被禁用'}, status=status.HTTP_403_FORBIDDEN)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'id': user.id,
                    'account': user.account,
                    'role': user.role,
                    'token': str(refresh.access_token),
                    'refresh': str(refresh)
                })
            return Response({'error': '账号或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': '账号或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 检查账号是否已存在
            account = serializer.validated_data.get('account')
            if User.objects.filter(account=account).exists():
                return Response({'error': '账号已存在'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建用户并设置username
            user = serializer.save()
            user.username = account  # 使用account作为username
            user.save()
            
            return Response({
                'id': user.id,
                'account': user.account,
                'role': user.role
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            # 这里可以添加token黑名单逻辑
            return Response({'message': '已成功退出登录'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def disable_account(self, request, pk=None):
        user = self.get_object()
        if user.role == 'admin':
            return Response({'error': '不能禁用管理员账号'}, status=status.HTTP_400_BAD_REQUEST)
        user.disable_account()
        return Response({'message': '账号已禁用'})

    @action(detail=True, methods=['post'])
    def enable_account(self, request, pk=None):
        user = self.get_object()
        user.enable_account()
        return Response({'message': '账号已启用'})

    @action(detail=False, methods=['get'])
    def verify_token(self, request):
        """
        验证token是否有效
        """
        if request.user.is_authenticated:
            return Response({'status': 'valid'})
        return Response({'status': 'invalid'}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.role == 'admin':
            return Response({'error': '不能删除管理员账号'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs) 