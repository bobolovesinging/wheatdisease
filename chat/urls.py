"""
聊天应用的URL配置文件

配置与聊天功能相关的所有URL路由映射。
主要功能：
- 处理流式响应请求
- 提供清空历史记录接口
- 提供API测试接口
- 提供历史对话记录接口
- 提供会话管理接口
"""

from django.urls import path
from .views import ChatAPI


urlpatterns = [
    # 流式响应接口
    path('stream_chat/', ChatAPI.as_view({
    'get': 'stream_chat'     
    }), name='chat_stream'),
    
    # 清空历史记录接口
    path('clear_history/', ChatAPI.as_view({
        'post': 'clear_history'
    }), name='clear_history'),
    
    # API测试接口
    path('test_connection/', ChatAPI.as_view({
        'get': 'test_connection'
    }), name='chat_test'),
    
    # 获取所有历史对话记录
    path('get_history/', ChatAPI.as_view({
        'get': 'get_history'
    }), name='chat_history'),
    
    # 获取特定会话的历史记录
    path('get_session_history/', ChatAPI.as_view({
        'get': 'get_session_history'
    }), name='session_history'),
    
    # 创建新会话
    path('create_session/', ChatAPI.as_view({
        'post': 'create_session'
    }), name='create_session'),
    
    # 更新会话标题
    path('update_session_title/', ChatAPI.as_view({
        'post': 'update_session_title'
    }), name='update_title'),
    
    # 获取会话列表
    path('get_session_list/', ChatAPI.as_view({
        'get': 'get_session_list'
    }), name='session_list'),
]

