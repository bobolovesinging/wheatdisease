from django.urls import path, include
from rest_framework.routers import DefaultRouter
from knowledge.views import KnowledgeGraphAPI

router = DefaultRouter()
router.register(r'knowledge', KnowledgeGraphAPI, basename='knowledge')

urlpatterns = [
    path('api/', include(router.urls)),
] 