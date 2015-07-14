import datetime

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from shareholder.models import Shareholder, Company, Operator, Position, \
    UserProfile, Country
from services.rest.validators import DependedFieldsValidator

from utils.user import make_username

User = get_user_model()


class CompanySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Company
        fields = ('pk', 'name')

    def create(self, validated_data):

        name = validated_data.get("name")
        user = self.context.get("request").user

        company, created = Company.objects.get_or_create(name=name)
        operator, created = Operator.objects.get_or_create(company=company, user=user)

        return company


class AddCompanySerializer(serializers.Serializer):

    name = serializers.CharField(max_length=255)
    face_value = serializers.DecimalField(max_digits=19, decimal_places=4)
    count = serializers.IntegerField()

    def create(self, validated_data):
        """ check data, add company, add company_itself shareholder, add first position' """

        user = validated_data.get("user")
        company = Company.objects.create(
            share_count=validated_data.get("count"),
            name=validated_data.get("name")
        )
        companyuser = User.objects.create(
            username=make_username('Company', 'itself', company.name),
            first_name='Company', last_name='itself',
            email='info@{}-company-itself.com'.format(slugify(company.name))
        )
        shareholder = Shareholder.objects.create(user=companyuser, company=company, number='0')
        Position.objects.create(
            bought_at=datetime.datetime.now(),
            buyer=shareholder, count=validated_data.get("count"), value=validated_data.get("face_value")
        )
        Operator.objects.create(user=user, company=company)

        return validated_data


class OperatorSerializer(serializers.HyperlinkedModelSerializer):
    company = CompanySerializer(many=False, read_only=True)

    class Meta:
        model = Operator
        fields = ('id', 'company')


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    """ list of countries selectable """

    class Meta:
        model = Country
        fields = ('iso_code', 'name')


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    """ serialize additional user data """
    country = CountrySerializer(many=False)

    class Meta:
        model = UserProfile
        fields = ('street', 'city', 'province', 'postal_code', 'country', 'birthday', 'company_name')


class UserWithEmailOnlySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('email',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    operator_set = OperatorSerializer(many=True, read_only=True)
    userprofile = UserProfileSerializer(many=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'operator_set', 'userprofile')

    def create(self, validated_data):

        if validated_data.get('user').get('userprofile'):
            userprofile_data = validated_data.pop('userprofile')
            userprofile = UserProfile.objects.create(**userprofile_data)
        else:
            raise ValidationError('Missing User Profile data')

        if validated_data.get('user').get('userprofile').get('country'):
            country_data = validated_data.get('user').get('userprofile').get('country')
            country = Country.objects.create(**country_data)
        else:
            raise ValidationError('Missing country data')

        validated_data['user']['userprofile'] = userprofile
        validated_data['user']['userprofile']['country'] = country

        user = User.objects.create(**validated_data)

        return user


class ShareholderSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(many=False)
    company = CompanySerializer(many=False,  read_only=True)

    class Meta:
        model = Shareholder
        fields = ('pk', 'user', 'number', 'company', 'share_percent', 'share_count', 'share_value')

    def create(self, validated_data):

        # existing or new user
        user = self.context.get("request").user

        # FIXME: assuming one company per user
        company = user.operator_set.all()[0].company

        # get unique username
        username = make_username(
            validated_data.get("user").get("first_name"),
            validated_data.get("user").get("last_name"),
            validated_data.get("user").get("email")
        )

        # save user/-profile
        profile_data = validated_data.get("user").get("userprofile")
        country_data = profile_data.get("country")
        country, created = Country.objects.get_or_create(
            iso_code=country_data.get("iso_code"),
            defaults={
                "name": country_data.get("name"),
                "iso_code": country_data.get("iso_code"),
            })
        shareholder_user, created = User.objects.get_or_create(
            email=validated_data.get("user").get("email"),
            defaults={
                "username": username,
                "first_name": validated_data.get("user").get("first_name"),
                "last_name": validated_data.get("user").get("last_name"),
            })

        profile, created = UserProfile.objects.get_or_create(
            user=shareholder_user,
            defaults={
                "company_name": profile_data.get("company_name"),
                "street": profile_data.get("street"),
                "postal_code": profile_data.get("postal_code"),
                "province": profile_data.get("province"),
                "city": profile_data.get("city"),
                "country": country,
                "birthday": profile_data.get("birthday"),
                "user": shareholder_user,
            })

        if not created:
            if not shareholder_user.first_name:
                shareholder_user.first_name = validated_data.get("user").get("first_name")
            if not shareholder_user.last_name:
                shareholder_user.last_name = validated_data.get("user").get("last_name")
            shareholder_user.save()

        # save shareholder
        shareholder, created = Shareholder.objects.get_or_create(
            user=shareholder_user,
            company=company,
            defaults={"number": validated_data.get("number")},
        )

        return shareholder


class PositionSerializer(serializers.HyperlinkedModelSerializer):
    buyer = ShareholderSerializer(many=False, required=False)
    seller = ShareholderSerializer(many=False, required=False)
    bought_at = serializers.DateTimeField()  # e.g. 2015-06-02T23:00:00.000Z

    class Meta:
        model = Position
        fields = ('pk', 'buyer', 'seller', 'bought_at', 'count', 'value')
        validators = [DependedFieldsValidator(fields=('seller', 'buyer'))]

    def create(self, validated_data):
        """ adding a new position and handling nested data for buyer
        and seller """

        # prepare data
        kwargs = {}
        user = self.context.get("request").user
        company = user.operator_set.all()[0].company

        if validated_data.get("seller") and validated_data.get("buyer"):
            buyer = Shareholder.objects.get(
                company=company,
                user__email=validated_data.get("buyer").get("user").get("email")
            )
            seller = Shareholder.objects.get(
                company=company,
                user__email=validated_data.get("seller").get("user").get("email")
            )
            kwargs.update({"seller": seller})

        else:
            buyer = Shareholder.objects.get(
                company=company,
                user__first_name='Company',
                user__last_name='itself',
            )
            company.share_count = company.share_count + validated_data.get("count")
            company.save()

        kwargs.update({
            "buyer": buyer,
            "bought_at": validated_data.get("bought_at"),
            "value": validated_data.get("value"),
            "count": validated_data.get("count"),
        })

        position = Position.objects.create(**kwargs)

        return position
