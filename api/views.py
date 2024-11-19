from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .models import CustomUser
from .serializers import RegistrationSerializer

from rest_framework_simplejwt.tokens import TokenError

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Générer un token d'activation
            token = RefreshToken.for_user(user).access_token

            # Construire le lien d'activation
            activation_link = f"http://127.0.0.1:8000/api/activate/{token}/"

            # Envoyer un email d'activation
            send_mail(
                subject="Activation de votre compte",
                message=f"Merci de vous inscrire. Activez votre compte ici : {activation_link}",
                from_email="playstorexclone@gmail.com",
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response(
                {"message": "Inscription réussie. Veuillez vérifier votre email pour activer votre compte."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountAPIView(APIView):
    def get(self, request, token):
        try:
            # Décoder le token
            user = CustomUser.objects.get(id=RefreshToken(token).get("user_id"))
            user.is_active = True
            user.save()
            return Response({"message": "Compte activé avec succès !"}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"message": "Token invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)