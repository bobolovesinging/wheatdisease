"""
Django项目的主URL配置文件

包含项目级别的URL路由映射，将不同的URL请求分发到对应的应用。
主要功能：
- 配置管理后台路由
- 包含各个应用的URL配置
- 处理静态文件和媒体文件的路由（开发环境）
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from chat.views import ChatAPI

# 创建路由器并注册视图
router = DefaultRouter()
router.register(r'chat', ChatAPI, basename='chat')

urlpatterns = [
    # Django管理后台路由
    path('admin/', admin.site.urls),
    
    # API路由
    path('api/', include([
        path('', include(router.urls)),  # chat相关路由
        path('knowledge/', include('knowledge.urls')),  # 知识图谱相关路由
        path('users/', include('users.urls')),  # 用户相关路由
    ])),
] 