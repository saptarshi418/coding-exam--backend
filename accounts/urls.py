from django.urls import path
from .views import ChangePasswordView, DeactivateAccountAPIView, RegisterView, ResetPasswordWithOTPAPIView, UserProfileView, VerifyOTP , ResendOTP , LogoutView ,ForgotPasswordView, VerifyResetOTPView, ResetPasswordView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTP.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTP.as_view(), name='resend-otp'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-reset-otp/', VerifyResetOTPView.as_view(), name='verify-reset-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password-otp/', ResetPasswordWithOTPAPIView.as_view(), name='reset-password-otp'),
    path('deactivate-account/', DeactivateAccountAPIView.as_view(), name='deactivate-account'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),



]

