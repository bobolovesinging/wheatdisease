"""
会话管理模块

提供会话状态管理功能，包括：
- 会话创建和获取
- 会话历史记录管理
- 症状信息管理
"""

import time
import json
import logging
from django.core.cache import cache
from backend.connections import get_redis_client

logger = logging.getLogger(__name__)

class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        """初始化会话管理器"""
        self.redis_client = get_redis_client()
        self.key_prefix = "chat:session:"
        self.history_prefix = "chat:history:"
        self.symptoms_prefix = "chat:symptoms:"
    
    def create_session(self, user_id):
        """创建新会话"""
        try:
            timestamp = int(time.time() * 1000)
            session_id = f"{timestamp}"
            
            # 初始化会话数据
            session_data = {
                'id': session_id,
                'user_id': user_id,
                'created_at': time.time(),
                'last_active': time.time(),
                'title': '新对话',
                'history': [],
                'symptoms': {}
            }
            
            # 保存会话数据
            self._save_session(session_id, user_id, session_data)
            logger.info(f"创建新会话成功 - 用户ID: {user_id}, 会话ID: {session_id}")
            
            return session_id
        except Exception as e:
            logger.error(f"创建会话失败: {str(e)}")
            raise
    
    def get_session(self, session_id, user_id):
        """获取会话信息"""
        try:
            session_key = f"{self.key_prefix}{user_id}:{session_id}"
            session_data = cache.get(session_key)
            
            if session_data is None:
                logger.warning(f"会话不存在: {session_id}")
                return None
            
            # 更新最后活动时间
            session_data['last_active'] = time.time()
            self._save_session(session_id, user_id, session_data)
            
            return session_data
        except Exception as e:
            logger.error(f"获取会话失败: {str(e)}")
            return None
    
    def save_history(self, session_id, request, history):
        """保存会话历史记录"""
        user_id = get_user_id(request)
        try:
            history_key = f"{self.history_prefix}{user_id}:{session_id}"
            self.redis_client.set(history_key, json.dumps(history))
            logger.debug(f"保存历史记录成功 - 会话ID: {session_id}")
        except Exception as e:
            logger.error(f"保存历史记录失败: {str(e)}")
    
    def get_history(self, session_id, request):
        """获取会话历史记录"""
        user_id = get_user_id(request)
        history_key = f"{self.history_prefix}{user_id}:{session_id}"
        try:
            data = self.redis_client.get(history_key)
            logger.info(f"get_history: user_id={user_id}, session_id={session_id}, key={history_key}, data_len={len(data) if data else 0}")
            return json.loads(data) if data else []
        except Exception as e:
            logger.error(f"获取历史记录失败: {str(e)}")
            return []
    
    def save_symptoms(self, session_id, request, symptoms):
        """保存症状信息"""
        user_id = get_user_id(request)
        try:
            symptoms_key = f"{self.symptoms_prefix}{user_id}:{session_id}"
            self.redis_client.set(symptoms_key, json.dumps(symptoms))
            logger.debug(f"保存症状信息成功 - 会话ID: {session_id}")
        except Exception as e:
            logger.error(f"保存症状信息失败: {str(e)}")
    
    def get_symptoms(self, session_id, request):
        """获取症状信息"""
        user_id = get_user_id(request)
        try:
            symptoms_key = f"{self.symptoms_prefix}{user_id}:{session_id}"
            data = self.redis_client.get(symptoms_key)
            return json.loads(data) if data else {}
        except Exception as e:
            logger.error(f"获取症状信息失败: {str(e)}")
            return {}
    
    def get_all_sessions(self, request, count=3, offset=0):
        """获取用户的所有会话"""
        user_id = get_user_id(request)
        try:
            pattern = f"{self.history_prefix}{user_id}:*"
            cursor = 0
            session_ids = []
            
            while True:
                cursor, keys = self.redis_client.scan(cursor=cursor, match=pattern, count=100)
                session_ids.extend([
                    (k.decode() if isinstance(k, bytes) else k).split(":", 3)[3]
                    for k in keys
                ])
                if cursor == 0:
                    break
            
            # 按时间排序
            session_ids = sorted(session_ids, reverse=True)
            logger.info(f"get_all_sessions: 提取到 session_ids={session_ids}")
            sessions = []
            
            for session_id in session_ids[offset:offset+count]:
                history = self.get_history(session_id, request)
                logger.info(f"get_all_sessions: session_id={session_id}, history_len={len(history)}")
                if history:
                    created_at = history[0]['timestamp']
                    updated_at = history[-1]['timestamp']
                    sessions.append({
                        'id': session_id,
                        'title': '新对话',
                        'created_at': created_at,
                        'updated_at': updated_at,
                        'message_count': len(history)
                    })
            
            return sessions
        except Exception as e:
            logger.error(f"获取会话列表失败: {str(e)}")
            return []
    
    def clear_session(self, session_id, user_id):
        """清除会话数据"""
        try:
            # 删除会话数据
            session_key = f"{self.key_prefix}{user_id}:{session_id}"
            history_key = f"{self.history_prefix}{user_id}:{session_id}"
            symptoms_key = f"{self.symptoms_prefix}{user_id}:{session_id}"
            
            cache.delete(session_key)
            self.redis_client.delete(history_key)
            self.redis_client.delete(symptoms_key)
            
            logger.info(f"清除会话数据成功 - 会话ID: {session_id}")
        except Exception as e:
            logger.error(f"清除会话数据失败: {str(e)}")
    
    def _save_session(self, session_id, user_id, session_data):
        """保存会话数据"""
        try:
            session_key = f"{self.key_prefix}{user_id}:{session_id}"
            cache.set(session_key, session_data, timeout=None)
        except Exception as e:
            logger.error(f"保存会话数据失败: {str(e)}")
            raise

def get_user_id(request):
    """统一获取当前用户ID，未登录返回None"""
    user = getattr(request, 'user', None)
    return getattr(user, 'id', None) if user else None 