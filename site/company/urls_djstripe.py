
from django.conf.urls import url


urlpatterns = [

    # HTML views
    url(
        r"^$",
        'company.views.account',
        name="account"
    ),
    url(
        r"^subscribe/$",
        'company.views.subscribe',
        name="subscribe"
    ),
    url(
        r"^confirm/(?P<plan>.+)$",
        'company.views.confirm',
        name="confirm"
    ),
    url(
        r"^change/plan/$",
        'company.views.change_plan',
        name="change_plan"
    ),
    url(
        r"^change/cards/$",
        'company.views.change_card',
        name="change_card"
    ),
    # NOTE: cancellation not allowed (free plan available)
    # url(
    #     r"^cancel/subscription/$",
    #     'company.views.cancel_subscription',
    #     name="cancel_subscription"
    # ),
    url(
        r"^history/$",
        'company.views.history',
        name="history"
    ),
    url(
        r"^invoice/(?P<pk>\d+)/$",
        'company.views.invoice',
        name="invoice"
    ),


    # Web services
    url(
        r"^a/sync/history/$",
        'company.views.sync_history',
        name="sync_history"
    ),
]