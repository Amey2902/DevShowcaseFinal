from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, UserProfileSerializer
from .models import UserProfile, MagicLink


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_profile(request, username):
    try:
        user = User.objects.get(username=username)
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    profile = request.user.profile
    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(request.user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def request_magic_link(request):
    """Send magic link to user's email"""
    print("=" * 80)
    print("MAGIC LINK REQUEST RECEIVED")
    print(f"Request data: {request.data}")
    print("=" * 80)
    
    email = request.data.get('email', '').strip().lower()
    
    if not email:
        print("ERROR: No email provided")
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    print(f"Creating magic link for: {email}")
    
    try:
        # Create magic link
        magic_link = MagicLink.create_for_email(email)
        print(f"Magic link created with token: {magic_link.token}")
        
        # Build magic link URL
        frontend_url = settings.FRONTEND_URL
        magic_link_url = f"{frontend_url}/auth/verify/{magic_link.token}"
        
        print(f"Magic link URL: {magic_link_url}")
        print("Sending email...")
        
        # Send email
        send_mail(
            subject='🔐 Your DevShowcase Login Link',
            message=f'''Hi there!

Click the link below to log in to DevShowcase:

{magic_link_url}

This link will expire in 15 minutes.

If you didn't request this, you can safely ignore this email.

Best regards,
DevShowcase Team''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        print("✅ Email sent successfully!")
        print("=" * 80)
        
        return Response({
            'message': 'Magic link sent! Check your email.',
            'email': email
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        return Response({
            'error': 'Failed to send email. Please try again.',
            'details': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_magic_link(request):
    """Verify magic link token and log user in"""
    token = request.data.get('token', '').strip()
    
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        magic_link = MagicLink.objects.get(token=token)
    except MagicLink.DoesNotExist:
        return Response({'error': 'Invalid or expired link'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if link is valid
    if not magic_link.is_valid():
        return Response({'error': 'Link has expired or already been used'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Mark link as used
    magic_link.mark_as_used()
    
    # Get or create user
    email = magic_link.email
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Create new user with email as username
        username = email.split('@')[0]
        base_username = username
        counter = 1
        
        # Ensure unique username
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=None  # No password for magic link users
        )
    
    # Get or create token
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
        'message': 'Successfully logged in!'
    }, status=status.HTTP_200_OK)
