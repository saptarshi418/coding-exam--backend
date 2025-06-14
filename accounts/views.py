from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .serializers import ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, UserProfileSerializer, UserRegistrationSerializer , LoginSerializer, VerifyResetOTPSerializer
from .models import User
import random
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta



class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            send_mail(
                'Your OTP for Email Verification',
                f'Your OTP is {user.otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            return Response({'message': 'User registered successfully. Please check your email for the OTP.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            user = User.objects.get(email=email)
            if user.otp == otp:
                user.is_verified = True
                user.otp = ''
                user.save()
                return Response({'message': 'Email verified successfully.'})
            else:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)




class ResendOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                return Response({'message': 'Email already verified.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate new OTP
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.save()

            # Send email
            send_mail(
                'Your New OTP for Email Verification',
                f'Your new OTP is {otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            return Response({'message': 'OTP resent successfully.'})
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)



# class LoginView(APIView):
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             token, created = Token.objects.get_or_create(user=user)
#             return Response({
#                 'token': token.key,
#                 'message': 'Login successful.'
#             })
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Logout successful.'})
        except:
            return Response({'error': 'Token not found or already logged out.'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                otp = str(random.randint(100000, 999999))
                user.otp = otp
                user.otp_created_at = timezone.now()
                user.save()

                send_mail(
                    'OTP for Password Reset',
                    f'Your OTP for resetting password is: {otp}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                return Response({'message': 'OTP sent to email.'})
            except User.DoesNotExist:
                return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyResetOTPView(APIView):
    def post(self, request):
        serializer = VerifyResetOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
                if user.otp != otp:
                    return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
                if timezone.now() > user.otp_created_at + timedelta(minutes=10):
                    return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'message': 'OTP verified. You can now reset your password.'})
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            try:
                user = User.objects.get(email=email)
                if user.otp != otp:
                    return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
                if timezone.now() > user.otp_created_at + timedelta(minutes=10):
                    return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(new_password)
                user.otp = ''
                user.otp_created_at = None
                user.save()
                return Response({'message': 'Password has been reset successfully.'})
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ResetPasswordWithOTPAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not email or not otp or not new_password:
            return Response({'error': 'Email, OTP and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            # Check OTP and expiration (optional, e.g., valid for 10 minutes)
            if user.otp != otp:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

            # Optional: Check OTP expiry
            if user.otp_created_at and (timezone.now() - user.otp_created_at).seconds > 600:
                return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.otp = ''
            user.otp_created_at = None
            user.save()

            return Response({'message': 'Password reset successfully.'})
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


class DeactivateAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({'message': 'Account deactivated successfully.'})