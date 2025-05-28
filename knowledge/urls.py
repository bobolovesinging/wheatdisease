from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KnowledgeGraphAPI

router = DefaultRouter()
router.register(r'', KnowledgeGraphAPI, basename='knowledge')

urlpatterns = [
    path('', include(router.urls)),
] 