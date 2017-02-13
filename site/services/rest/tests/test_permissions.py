
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

from rest_framework.views import APIView

from project.generators import OperatorGenerator, UserGenerator
from project.tests.mixins import StripeTestCaseMixin, SubscriptionTestMixin

from ..permissions import IsOperatorPermission, HasSubscriptionPermission


class IsOperatorPermissionTestCase(TestCase):

    def setUp(self):
        super(IsOperatorPermissionTestCase, self).setUp()

        self.factory = RequestFactory()
        self.permission = IsOperatorPermission()

    def test_has_permission(self):
        view = APIView()

        req = self.factory.get('/')
        req.user = AnonymousUser()

        # not authenticated
        self.assertFalse(self.permission.has_permission(req, view))

        req.user = UserGenerator().generate()
        # authenticated but no operator
        self.assertFalse(self.permission.has_permission(req, view))

        # add operator for user
        OperatorGenerator().generate(user=req.user)
        # user is authenticated and operator
        self.assertTrue(self.permission.has_permission(req, view))


class HasSubscriptionPermissionTestCase(StripeTestCaseMixin,
                                        SubscriptionTestMixin, TestCase):

    def setUp(self):
        super(HasSubscriptionPermissionTestCase, self).setUp()

        self.factory = RequestFactory()
        self.permission = HasSubscriptionPermission()

    def test_has_permission(self):
        view = APIView()

        req = self.factory.get('/')
        req.user = AnonymousUser()

        # no company
        self.assertFalse(self.permission.has_permission(req, view))

        # add company operator
        operator = OperatorGenerator().generate()
        req.user = operator.user

        # no plan/subscription
        self.assertFalse(self.permission.has_permission(req, view))

        # add company subscription
        self.add_subscription(operator.company)

        # no subscription features on view defined
        self.assertTrue(self.permission.has_permission(req, view))

        view.subscription_features = ['foo']

        # feature not in plan features
        self.assertFalse(self.permission.has_permission(req, view))

        view.subscription_features = ['shareholders']

        plans = settings.DJSTRIPE_PLANS.copy()
        plans['test']['features']['shareholders'] = {}
        with self.settings(DJSTRIPE_PLANS=plans):
            self.assertTrue(self.permission.has_permission(req, view))

        view.action = 'bar'
        # view action has no validator
        self.assertTrue(self.permission.has_permission(req, view))

        plans['test']['features']['shareholders'] = {
            'max': 2,
            'validators': {
                'bar': [
                    'company.validators.features.'
                    'ShareholderCreateMaxCountValidator'
                ]
            }
        }
        with self.settings(DJSTRIPE_PLANS=plans):
            self.assertTrue(self.permission.has_permission(req, view))

        plans['test']['features']['shareholders']['max'] = 0
        with self.settings(DJSTRIPE_PLANS=plans):
            self.assertFalse(self.permission.has_permission(req, view))

    def test_get_object_permission(self):
        # TODO: add real tests after logic is determined in permission
        req = self.factory.get('/')
        view = APIView()
        self.assertTrue(self.permission.has_object_permission(req, view))

    def test_get_company(self):
        req = self.factory.get('/')
        self.assertIsNone(self.permission._get_company(req))

        req.user = AnonymousUser()
        self.assertIsNone(self.permission._get_company(req))

        req.user = UserGenerator().generate()
        self.assertIsNone(self.permission._get_company(req))

        operator = OperatorGenerator().generate(user=req.user)
        self.assertIsNotNone(self.permission._get_company(req))
        self.assertEqual(self.permission._get_company(req), operator.company)

        # add another operator
        operator2 = OperatorGenerator().generate(user=operator.user)
        company = self.permission._get_company(req)
        self.assertIsNotNone(company)
        self.assertEqual(company, operator.company)
        self.assertNotEqual(company, operator2.company)