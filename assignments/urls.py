from django.urls import path
from assignments.views import AssignPolicyView

urlpatterns = [
    path(
        "devices/<uuid:device_id>/assign-policy/<uuid:policy_id>/",
        AssignPolicyView.as_view(),
    ),
]
