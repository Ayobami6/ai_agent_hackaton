from django.urls import path
from .views import AIAgentAPIView

urlpatterns = [
    path("agent", AIAgentAPIView.as_view(), name="agent"),
]
