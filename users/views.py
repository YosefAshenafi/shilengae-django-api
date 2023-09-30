from django.db.models import Q
from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from firebase_admin import auth

from .serializers import ShilengaeUserProfileSerializer, ShilengaeUserSerializer, \
    ShilengaeUserPreferenceSerializer, ShilengaeUserDeleteSerializer, \
    ShilengaeUserUpdatePasswordSerializer
from .models import ShilengaeUser, ShilengaeUserProfile, ShilengaeUserPreference


class LoggedInUserApiView(generics.GenericAPIView):
    serializer_class = ShilengaeUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        return Response(self.get_serializer(request.user).data)


class GetUserProfileApiView(generics.GenericAPIView):
    serializer_class = ShilengaeUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = ShilengaeUser.objects.get(pk=user_id)
        return Response(self.get_serializer(user).data)

class UpdateUserPasswordApiView(generics.GenericAPIView):
    serializer_class = ShilengaeUserUpdatePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShilengaeUser.objects.all()
    
    def post(self, request, *args, **kwargs):
        user: ShilengaeUser = request.user

        if not user.check_password(request.data.get('old_password')):
            raise serializers.ValidationError('Old password is incorrect')

        if len(request.data.get('new_password1', '')) < 6:
            raise serializers.ValidationError('Password must be at least 6 characters long')

        if request.data.get('new_password1') != request.data.get('new_password2'):
            raise serializers.ValidationError('Passwords do not match')
        
        user.set_password(request.data.get('new_password1'))
        user.save()

        return Response({'detail': 'Password updated successfully'})


class DeleteUserApiView(generics.GenericAPIView):
    serializer_class = ShilengaeUserDeleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # delete user by mobile country code and mobile number and delete user from firebase
        mobile_country_code = request.data.get('mobile_country_code')
        mobile_number = request.data.get('mobile_number')
        password = request.data.get('password')

        user: ShilengaeUser = ShilengaeUser.objects.filter(
            Q(mobile_country_code=mobile_country_code) & Q(mobile_number=mobile_number)).first()
        
        if user != request.user:
            raise serializers.ValidationError('Does not have permission to delete this account')

        if not user.check_password(password):
            raise serializers.ValidationError('Password is incorrect')

        if not user:
            return Response({'error': 'User not found'}, status=404)

        if user and user.firebase_uid:
            auth.delete_user(user.firebase_uid)

        user.delete()

        return Response({"success": "True", "detail": "User has been deleted"})


class DeleteUserByIdApiView(generics.GenericAPIView):
    serializer_class = ShilengaeUserDeleteSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShilengaeUser.objects.all()

    def post(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"success": "True", "detail": "User has been deleted"})


class IsUserRegisteredApiView(generics.GenericAPIView):
    serializer_class = ShilengaeUserDeleteSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        mobile_country_code = request.data.get('mobile_country_code')
        mobile_number = request.data.get('mobile_number')
        user = ShilengaeUser.objects.filter(
            Q(mobile_country_code=mobile_country_code) & Q(mobile_number=mobile_number)).first()
        if user:
            return Response({"registered": True, "detail": "User has registered"})
        else:
            return Response({"registered": False, "detail": "User not registered"})


class UpdateUserProfileApiView(generics.UpdateAPIView):
    serializer_class = ShilengaeUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user.profile

class UpdateUserApiView(generics.UpdateAPIView):
    serializer_class = ShilengaeUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShilengaeUser.objects.all()

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ListUsersApiView(generics.ListAPIView):
    serializer_class = ShilengaeUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = ShilengaeUser.objects

        if self.request.user.type == ShilengaeUser.ROLE.ADMIN:
            queryset = queryset.filter(country=self.request.user.profile.operating_country)
        if self.request.user.type == ShilengaeUser.ROLE.SUPERADMIN:
            queryset = queryset.filter(Q(country = self.request.user.profile.operating_country) \
                                        | Q(profile__operable_countries = self.request.user.profile.operating_country))
        
        return queryset.exclude(type=ShilengaeUser.ROLE.USER)


class ListRegularUsersApiView(generics.ListAPIView):
    serializer_class = ShilengaeUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        filter = {'country__isnull': False,
                  'type': ShilengaeUser.ROLE.USER}
        filter = Q(**filter)

        if self.request.query_params.get('search'):
            search = self.request.query_params.get('search')
            filter &= (Q(first_name__icontains=search) | Q(last_name__icontains=search) | \
                            Q(mobile_number__icontains=search) | Q(email__icontains=search))

        if self.request.user.type == ShilengaeUser.ROLE.ADMIN or self.request.user.type == ShilengaeUser.ROLE.SUPERADMIN:
            filter &= Q(country=self.request.user.profile.operating_country)

        return ShilengaeUser.objects.filter(filter)


class SearchUserApiView(generics.ListAPIView):
    serializer_class = ShilengaeUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_term = self.request.query_params.get('search_term', '')
        return ShilengaeUser.objects.filter(Q(username__icontains=search_term) |
                                            Q(first_name__icontains=search_term) |
                                            Q(last_name__icontains=search_term))


class UpdateUserPreferenceApiView(generics.GenericAPIView):
    serializer_class = ShilengaeUserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = ShilengaeUser.objects.get(pk=request.user.pk)
        user_preference = ShilengaeUserPreference.objects.get(user=user)
        serializer = self.get_serializer(user_preference, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class UploadUserProfileImageApiView(generics.GenericAPIView):
    serializer_class = ShilengaeUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = ShilengaeUser.objects.get(pk=user_id)
        user_profile = ShilengaeUserProfile.objects.get(user=user)
        serializer = self.get_serializer(user_profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)