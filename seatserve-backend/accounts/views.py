from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from accounts.models import User
from accounts.serializers import UserSerializer, UserCreateSerializer

security_logger = logging.getLogger('security')


class LoginThrottle(UserRateThrottle):
    """Rate limit login attempts"""
    scope = 'login'


class RegisterThrottle(UserRateThrottle):
    """Rate limit registration attempts"""
    scope = 'register'


class UserRegistrationView(viewsets.ViewSet):
    """Handle user registration"""
    throttle_classes = [RegisterThrottle]
    permission_classes = (AllowAny,)

    def create(self, request):
        """Register a new user (restaurant owner)"""
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.role = 'RESTAURANT'
            user.save()
            security_logger.info(f'New user registered: {user.email}')
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        security_logger.warning(f'Registration failed: {request.data.get("email")}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAuthView(viewsets.ViewSet):
    """Handle user login and token refresh"""
    throttle_classes = [LoginThrottle]
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login user and return JWT tokens"""
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            if user.check_password(password) and user.is_active:
                refresh = RefreshToken.for_user(user)
                security_logger.info(f'Login successful: {email}')
                return Response({
                    'success': True,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            security_logger.warning(f'Failed login attempt: {email} (invalid credentials)')
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            security_logger.warning(f'Failed login attempt: {email} (user not found)')
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """Refresh JWT token"""
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            security_logger.warning(f'Token refresh failed: {str(e)}')
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout user (token invalidation on client side)"""
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)


class UserProfileView(viewsets.ViewSet):
    """Manage user profile"""
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
