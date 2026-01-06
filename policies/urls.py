from django.urls import path
from policies.views import PolicyCreateView, PolicyRollbackView, PolicyVersionCreateView

urlpatterns = [
    path("policies/", PolicyCreateView.as_view()),
    path("policies/<uuid:policy_id>/versions/", PolicyVersionCreateView.as_view()),
    path("policies/<uuid:policy_id>/rollback/<uuid:version_id>/",PolicyRollbackView.as_view()),

]
