import dateutil.parser

from django.contrib.auth import get_user_model
from django.http import Http404
from django.utils.translation import ugettext as _
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import detail_route

from services.rest.serializers import (
    ShareholderSerializer, CompanySerializer, UserSerializer,
    PositionSerializer, AddCompanySerializer, UserWithEmailOnlySerializer,
    CountrySerializer, OptionPlanSerializer, OptionTransactionSerializer,
    SecuritySerializer, OperatorSerializer, OptionHolderSerializer)
from services.rest.permissions import UserCanAddCompanyPermission, \
    SafeMethodsOnlyPermission,\
    UserCanEditCompanyPermission, \
    UserIsOperatorPermission
from shareholder.models import (
    Shareholder, Company, Position, Country, OptionPlan,
    OptionTransaction, Security, Operator
    )

User = get_user_model()


class ShareholderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # FIXME filter by user perms
    serializer_class = ShareholderSerializer
    permission_classes = [
        UserIsOperatorPermission,
    ]

    def get_object(self):
        try:
            return Shareholder.objects.get(pk=self.kwargs.get('pk'))
        except Shareholder.DoesNotExist:
            raise Http404

    def get_queryset(self):
        user = self.request.user
        return Shareholder.objects.filter(company__operator__user=user)\
            .distinct()


class OperatorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # FIXME filter by user perms
    serializer_class = OperatorSerializer
    permission_classes = [
        UserIsOperatorPermission,
    ]

    def get_object(self, pk):
        try:
            return Operator.objects.get(pk=pk)
        except Operator.DoesNotExist:
            raise Http404

    def get_queryset(self):
        user = self.request.user
        return Operator.objects.filter(company__operator__user=user)\
            .distinct()

    def destroy(self, request, pk=None):
        operator = self.get_object(pk)
        company_ids = request.user.operator_set.all().values_list(
            'company__id', flat=True).distinct()
        # cannot remove himself
        if operator not in request.user.operator_set.all():
            # user can only edit corps he manages
            if operator.company.id in company_ids:
                operator.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        # else:
        return Response(status=status.HTTP_403_FORBIDDEN)


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # FIXME filter by user perms
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [
        UserCanEditCompanyPermission,
    ]

    def get_queryset(self):
        user = self.request.user
        return Company.objects.filter(operator__user=user)

    # FIXME add perms like that to decor. permission_classes=[IsAdminOrIsSelf]
    @detail_route(methods=['post'])
    def upload(self, request, pk=None):
        obj = self.get_object()
        # modify data
        serializer = CompanySerializer(data=request.data)
        # add file to serializer
        if serializer.is_valid():
            obj.logo = request.FILES['logo']
            obj.save()
            return Response(CompanySerializer(
                obj,
                context={'request': request}).data,
                status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def option_holder(self, request, pk=None):
        """ returns the captable part for all option holders """
        obj = self.get_object()
        ohs = obj.get_active_option_holders()
        page = self.paginate_queryset(ohs)
        if page is not None:
            serializer = OptionHolderSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = OptionHolderSerializer(ohs, many=True, context={'request': request})
        return Response(serializer.data)


class AddCompanyView(APIView):
    """ view to initially setup a company """

    queryset = Company.objects.none()
    permission_classes = [
        UserCanAddCompanyPermission,
    ]

    def post(self, request, format=None):
        serializer = AddCompanySerializer(data=request.data)
        if serializer.is_valid() and request.user.is_authenticated():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddShareSplit(APIView):
    """ creates a share split. danger: can be set to be in the past and ALL
    following transactions must be adjusted
    """
    permission_classes = [
        UserCanAddCompanyPermission,
    ]

    def _validate_data(self, data):
        errors = {}
        if not data.get('execute_at'):
            errors.update({'execute_at': [_('Field may not be empty.')]})
        if not data.get('dividend'):
            errors.update({'dividend': [_('Field may not be empty.')]})
        if not data.get('divisor'):
            errors.update({'divisor': [_('Field may not be empty.')]})
        if not data.get('security'):
            errors.update({'security': [_('Field may not be empty.')]})

        if not errors:
            return True, {}
        else:
            return False, errors

    def post(self, request, fomat=None):
        data = request.data
        is_valid, errors = self._validate_data(data)
        if is_valid:
            # get company and run company.split_shares(data)
            company = request.user.operator_set.earliest('id').company
            data.update({
                'execute_at': dateutil.parser.parse(data['execute_at']),
                'security': Security.objects.get(id=data['security']['pk'])
            })
            company.split_shares(data)

            positions = Position.objects.filter(
                buyer__company__operator__user=request.user).order_by(
                    '-bought_at')

            serializer = PositionSerializer(
                positions, many=True, context={'request': request})
            return Response(
                {'success': True, 'data': serializer.data},
                status=status.HTTP_201_CREATED)

        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint to get user base info """
    serializer_class = UserSerializer
    permission_classes = [
        SafeMethodsOnlyPermission,
    ]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(id=user.id)


class CountryViewSet(viewsets.ModelViewSet):
    """ API endpoint to get user base info """
    serializer_class = CountrySerializer
    permission_classes = [
        SafeMethodsOnlyPermission,
    ]

    def get_queryset(self):
        countries = Country.objects.all()
        return countries


class InviteeUpdateView(APIView):
    """ API endpoint to get user base info """
    permission_classes = (AllowAny,)

    def post(self, request, format=None):

        serializer = UserWithEmailOnlySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(username=serializer.validated_data['email'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PositionViewSet(viewsets.ModelViewSet):
    """ API endpoint to get positions """
    serializer_class = PositionSerializer
    permission_classes = [
        UserIsOperatorPermission,
    ]

    def get_queryset(self):
        user = self.request.user
        return Position.objects.filter(
            Q(buyer__company__operator__user=user) |
            Q(seller__company__operator__user=user)
        ).order_by('-bought_at', '-pk')

    @detail_route(
        methods=['post'], permission_classes=[UserIsOperatorPermission])
    def confirm(self, request, pk=None):
        """ confirm position and make it unchangable """
        position = self.get_object()
        position.is_draft = False
        position.save()
        return Response({"success": True}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """ delete position. but not if is_draft-False"""

        position = self.get_object()
        if position.is_draft is True:
            position.delete()
            return Response(
                {"success": True}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {
                    'success': False,
                    'errors': [_('Confirmed position cannot be deleted.')]
                },
                status=status.HTTP_400_BAD_REQUEST)


class SecurityViewSet(viewsets.ModelViewSet):
    """ API endpoint to get options """
    serializer_class = SecuritySerializer
    permission_classes = [
        SafeMethodsOnlyPermission,
    ]

    def get_queryset(self):
        user = self.request.user
        return Security.objects.filter(company__operator__user=user)


class OptionPlanViewSet(viewsets.ModelViewSet):
    """ API endpoint to get options """
    serializer_class = OptionPlanSerializer
    permission_classes = [
        # UserCanAddOptionPlanPermission,
    ]

    def get_queryset(self):
        user = self.request.user
        return OptionPlan.objects.filter(company__operator__user=user)

    # FIXME add perms like that to decor. permission_classes=[IsAdminOrIsSelf]
    @detail_route(methods=['post'])
    def upload(self, request, pk=None):
        op = self.get_object()
        # modify data
        serializer = OptionPlanSerializer(data=request.data)
        # add file to serializer
        if serializer.is_valid():
            op.pdf_file = request.FILES['pdf_file']
            op.save()
            op.generate_pdf_file_preview()
            return Response(OptionPlanSerializer(
                op,
                context={'request': request}).data,
                status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class OptionTransactionViewSet(viewsets.ModelViewSet):
    """ API endpoint to get options """
    serializer_class = OptionTransactionSerializer
    permission_classes = [
        UserIsOperatorPermission
    ]

    def get_queryset(self):
        user = self.request.user
        return OptionTransaction.objects.filter(
            option_plan__company__operator__user=user)

    @detail_route(
        methods=['post'], permission_classes=[UserIsOperatorPermission])
    def confirm(self, request, pk=None):
        """ confirm position and make it unchangable """
        position = self.get_object()
        position.is_draft = False
        position.save()
        return Response({"success": True}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """ delete position. but not if is_draft-False"""

        position = self.get_object()
        if position.is_draft is True:
            position.delete()
            return Response(
                {"success": True}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {
                    'success': False,
                    'errors': [_('Confirmed position cannot be deleted.')]
                },
                status=status.HTTP_400_BAD_REQUEST)
