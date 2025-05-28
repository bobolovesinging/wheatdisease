"""
聊天应用的视图处理模块

提供与聊天功能相关的所有视图逻辑，包括：
- 处理流式响应请求
- 管理对话历史记录
- 实现流式响应（打字机效果）
- 提供API连接测试功能
- 与知识图谱交互
- 意图识别
"""

# Django REST framework相关导入
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer, BaseRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# Django相关导入
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

# Python标准库导入
import time
import json
import logging
import random
import traceback

# 导入服务
from .services import Neo4jService, IntentService
from backend.connections import get_openai_client
from .session import SessionManager
from .utils import keyword_manager

# 配置日志
logger = logging.getLogger(__name__)

WELCOME_MESSAGE = "您好，需要我什么帮助吗？请告诉我小麦的发病情况，包括：\n1. 从哪个部位开始发病\n2. 发病时的气象条件\n3. 发病的生育期\n4. 小麦的种植区"

# 全局单例
neo4j_service = Neo4jService()
session_manager = SessionManager()
intent_service = IntentService()

@method_decorator(csrf_exempt, name='dispatch')
class ChatAPI(viewsets.ViewSet):
    """聊天API视图集：处理与聊天相关的所有请求"""
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        """初始化ChatAPI实例"""
        super().__init__(*args, **kwargs)
        self.client = get_openai_client()
        self.neo4j_service = neo4j_service
        logger.debug("API/Neo4j实例初始化完成")

    @action(detail=False, methods=['get'], authentication_classes=[], permission_classes=[])
    def stream_chat(self, request):
        """处理流式响应请求"""
        logger.debug(f"收到stream_chat请求: {dict(request.GET)}")
        
        # 支持token从GET参数获取，自动识别用户
        token = request.GET.get('token')
        if token:
            try:
                validated = JWTAuthentication().get_validated_token(token)
                user = JWTAuthentication().get_user(validated)
                request.user = user
            except Exception as e:
                logger.warning(f"JWT token 解析失败: {e}")
                request.user = None
        
        if not self.client:
            logger.error("API客户端未初始化")
            return StreamingHttpResponse(
                "data: Error: API client not initialized\n\n",
                content_type='text/event-stream'
            )
        
        try:
            message = request.GET.get('message')
            session_id = request.GET.get('session_id', 'default')
            logger.debug(f"处理消息: {message}, 会话ID: {session_id}, 用户ID: {getattr(request.user, 'id', '匿名')}")
            
            if not message:
                logger.warning("接收到空消息")
                return StreamingHttpResponse(
                    "data: Error: Message is required\n\n",
                    content_type='text/event-stream'
                )

            # 获取历史对话并构建消息列表
            history = session_manager.get_history(session_id, request)
            messages = self.build_messages(message, history)
            logger.debug(f"构建的消息列表长度: {len(messages)}")

            response = StreamingHttpResponse(
                streaming_content=self._generate_stream_response(messages, session_id, message, request),
                content_type='text/event-stream'
            )
            
            # 设置响应头
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Headers'] = '*'
            
            return response
                
        except Exception as e:
            logger.error(f"stream_chat处理异常: {str(e)}", exc_info=True)
            return StreamingHttpResponse(
                f"data: Error: {str(e)}\n\n",
                content_type='text/event-stream'
            )

    @action(detail=False, methods=['post'])
    def create_session(self, request):
        """创建新会话"""
        try:
            user = request.user
            session_id = session_manager.create_session(getattr(user, 'id', None))
            logger.info(f"创建新会话成功 - 用户ID: {getattr(user, 'id', None)}, 会话ID: {session_id}")
            return JsonResponse({
                'status': 'success',
                'session_id': session_id
            })
        except Exception as e:
            logger.error(f"创建会话失败: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def add_message(self, request):
        """添加消息到历史记录"""
        try:
            user = request.user
            session_id = request.data.get('session_id')
            role = request.data.get('role', 'user')
            content = request.data.get('content')
            
            # 过滤欢迎语
            if content and content.strip() == WELCOME_MESSAGE.strip():
                return JsonResponse({'status': 'success'})
                
            if not session_id or not content:
                return JsonResponse({'status': 'error', 'message': 'session_id和content必填'}, status=400)
                
            history = session_manager.get_history(session_id, request)
            history.append({
                'role': role,
                'content': content,
                'timestamp': time.time()
            })
            
            # 限制历史记录长度
            if len(history) > 50:
                history = history[-50:]
                
            session_manager.save_history(session_id, request, history)
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            logger.error(f"添加消息失败: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def get_session_list(self, request):
        """获取会话列表"""
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 3))
            offset = (page - 1) * size
            
            sessions = session_manager.get_all_sessions(request, count=size, offset=offset)
            logger.info(f"获取会话列表成功 - 会话数: {len(sessions)}")
            
            return JsonResponse({'status': 'success', 'sessions': sessions})
            
        except Exception as e:
            logger.error(f"获取会话列表失败: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def get_history(self, request):
        """获取会话历史记录"""
        try:
            user = request.user
            session_id = request.GET.get('session_id')
            
            if not session_id:
                return JsonResponse({'status': 'error', 'message': 'session_id必填'}, status=400)
                
            history = session_manager.get_history(session_id, request)
            return JsonResponse({'status': 'success', 'messages': history})
            
        except Exception as e:
            logger.error(f"获取历史记录失败: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def save_symptoms(self, request):
        """保存症状信息"""
        try:
            user = request.user
            session_id = request.data.get('session_id')
            symptoms = request.data.get('symptoms')
            
            if not session_id or symptoms is None:
                return JsonResponse({'status': 'error', 'message': 'session_id和symptoms必填'}, status=400)
                
            session_manager.save_symptoms(session_id, request, symptoms)
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            logger.error(f"保存症状失败: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def get_symptoms(self, request):
        """获取症状信息"""
        try:
            user = request.user
            session_id = request.GET.get('session_id')
            
            if not session_id:
                return JsonResponse({'status': 'error', 'message': 'session_id必填'}, status=400)
                
            symptoms = session_manager.get_symptoms(session_id, request)
            return JsonResponse({'status': 'success', 'symptoms': symptoms})
            
        except Exception as e:
            logger.error(f"获取症状失败: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def clear_history(self, request):
        """清除会话历史记录"""
        try:
            user = request.user
            session_id = request.data.get('session_id')
            
            if not session_id:
                return JsonResponse({'status': 'error', 'message': 'session_id必填'}, status=400)
                
            session_manager.clear_session(session_id, user.id)
            logger.info(f"已清除会话 {session_id} 的所有信息")
            
            return JsonResponse({'status': 'success', 'message': '已清除历史记录和症状信息'})
            
        except Exception as e:
            logger.error(f"清除历史记录失败: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def _generate_stream_response(self, messages, session_id, original_message, request):
        """生成流式响应内容"""
        try:
            yield "data: 正在分析您的问题...\n\n"
            
            # 首先进行意图识别
            intent = intent_service.recognize_intent(original_message)
            logger.info(f"识别到的意图: {intent_service.get_intent_description(intent)}")
            
            # 处理基础意图
            if intent in ['greeting', 'farewell', 'thanks']:
                response_text = self._handle_basic_intent(intent)
                yield from self._stream_text(response_text)
                yield "data: [DONE]\n\n"
                return
            
            # 如果是诊断意图，则提取症状信息
            if intent == 'diagnosis':
                # 提取症状信息
                symptoms = keyword_manager.extract_symptoms(original_message)
                logger.info(f"从消息中提取的症状: {symptoms}")

                # 合并历史症状
                history_symptoms = session_manager.get_symptoms(session_id, request)
                if history_symptoms:
                    for k, v in history_symptoms.items():
                        if k not in symptoms or not symptoms[k]:
                            symptoms[k] = v
                logger.info(f"合并后症状: {symptoms}")
                
                if symptoms:
                    # 保存合并后的症状
                    session_manager.save_symptoms(session_id, request, symptoms)
                    
                    # 显示已收集的信息
                    summary = self._summarize_collected_symptoms(symptoms)
                    yield from self._stream_text(summary)
                    yield "data: \\n\\n\n\n"
                    
                    # 查询匹配的病害
                    if self.neo4j_service.is_connected():
                        diseases = self.neo4j_service.query_disease(symptoms)
                        diagnosis = self._build_diagnosis_response(diseases, symptoms)
                        yield from self._stream_text(diagnosis)
                    
                    # 保存对话历史
                    self._save_conversation_history(session_id, request, original_message, diagnosis)
                    
                    yield "data: [DONE]\n\n"
                    return
            
            # 如果不是诊断意图或没有提取到症状，使用API处理
            logger.debug(f"准备请求API: model={settings.OPENAI_MODEL}, messages={messages}")
            try:
                response = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    stream=False
                )
            except Exception as e:
                logger.error(f"API非流式请求异常: {str(e)}\n{traceback.format_exc()}")
                yield f"data: Error: API非流式请求异常 - {str(e)}\n\n"
                return
                
            response_text = response.choices[0].message.content
            logger.info(f"API返回内容: {response_text}")
            if not response_text:
                response_text = "很抱歉，暂时无法理解您的问题，请补充更多描述。"
                
            yield from self._stream_text(response_text)
            
            # 保存对话历史
            self._save_conversation_history(session_id, request, original_message, response_text)
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"生成响应时发生错误: {str(e)}\n{traceback.format_exc()}")
            yield f"data: Error: 服务器内部错误 - {str(e)}\n\n"

    def _handle_basic_intent(self, intent):
        """处理基础意图（问候、告别、感谢）"""
        responses = {
            'greeting': "您好！我是小麦病害诊断助手，很高兴为您服务。",
            'farewell': "再见！如果还有其他问题，随时都可以问我。",
            'thanks': "不客气！如果还有其他问题，我很乐意继续帮助您。"
        }
        return responses.get(intent, "抱歉，我没有理解您的意思。")

    def _stream_text(self, text):
        """流式输出文本"""
        for char in text:
            if char == '\n':
                yield "data: \\n\n\n"
            else:
                yield f"data: {char}\n\n"
            time.sleep(0.05)

    def _save_conversation_history(self, session_id, request, user_message, assistant_message):
        """保存对话历史"""
        history = session_manager.get_history(session_id, request)
        history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': time.time()
        })
        history.append({
            'role': 'assistant',
            'content': assistant_message,
            'timestamp': time.time()
        })
        if len(history) > 50:
            history = history[-50:]
        session_manager.save_history(session_id, request, history)

    def build_messages(self, message, history):
        """构建发送给AI的消息列表"""
        return [
            {
                "role": "system",
                "content": """你是一个专业的小麦病害诊断助手。请遵循以下步骤进行诊断：
                1. 仔细分析用户描述的症状
                2. 列出可能的病害类型及其特征
                3. 给出诊断结果的可信度评估
                4. 提供具体的防治建议
                5. 如果症状描述不够清晰，请询问更多细节,例如从哪个部位开始发病，发病气象条件，发病的生育期，发病的种植区等
                
                请使用专业但易懂的语言，必要时解释专业术语。"""
            }
        ] + history + [{"role": "user", "content": message}]

    def _summarize_collected_symptoms(self, symptoms):
        """总结已收集的症状信息"""
        if not symptoms:
            return "目前还没有收集到任何症状信息。"
            
        summary = "目前已经收集到的信息："
        info = []
        
        if 'plant_part' in symptoms:
            info.append(f"发病部位：{symptoms['plant_part']}")
        if 'weather' in symptoms:
            info.append(f"气象条件：{symptoms['weather']}")
        if 'growth_stage' in symptoms:
            info.append(f"生育期：{symptoms['growth_stage']}")
        if 'region' in symptoms:
            info.append(f"种植区：{symptoms['region']}")
            
        if info:
            summary += "\n" + "，".join(info)
            
        # 添加缺失信息提示
        missing = []
        if 'plant_part' not in symptoms:
            missing.append("发病部位")
        if 'weather' not in symptoms:
            missing.append("气象条件")
        if 'growth_stage' not in symptoms:
            missing.append("生育期")
        if 'region' not in symptoms:
            missing.append("种植区")
            
        if missing:
            summary += f"\n\n还需要补充：{', '.join(missing)}"
                
        return summary

    def _build_diagnosis_response(self, diseases, collected_symptoms):
        """构建诊断回复"""
        def format_symptom_value(value):
            """格式化症状值，处理单个值或多个值的情况"""
            if isinstance(value, list):
                return "、".join(value)
            return value

        if not diseases:
            missing_info = []
            if 'plant_part' not in collected_symptoms:
                missing_info.append("发病部位")
            if 'weather' not in collected_symptoms:
                missing_info.append("气象条件")
            if 'growth_stage' not in collected_symptoms:
                missing_info.append("生育期")
            if 'region' not in collected_symptoms:
                missing_info.append("种植区")
            
            response = "根据您提供的信息："
            info = []
            for category, value in collected_symptoms.items():
                if category == 'plant_part':
                    info.append(f"发病部位：{format_symptom_value(value)}")
                elif category == 'weather':
                    info.append(f"气象条件：{format_symptom_value(value)}")
                elif category == 'growth_stage':
                    info.append(f"生育期：{format_symptom_value(value)}")
                elif category == 'region':
                    info.append(f"种植区：{format_symptom_value(value)}")
            
            if info:
                response += "\n" + "，".join(info)
            
            if missing_info:
                response += f"\n\n暂时无法确定具体病害。请补充{'、'.join(missing_info)}等信息，以便我更准确地判断。"
            else:
                response += "\n\n暂时没有找到完全匹配的病害。请补充更多具体的症状表现，以便我更准确地判断。"
            return response
        
        if len(diseases) == 1:
            # 只有一个匹配的病害，提供详细信息
            disease = diseases[0]
            response = "根据您提供的信息："
            info = []
            for category, value in collected_symptoms.items():
                if category == 'plant_part':
                    info.append(f"发病部位：{format_symptom_value(value)}")
                elif category == 'weather':
                    info.append(f"气象条件：{format_symptom_value(value)}")
                elif category == 'growth_stage':
                    info.append(f"生育期：{format_symptom_value(value)}")
                elif category == 'region':
                    info.append(f"种植区：{format_symptom_value(value)}")
            response += "\n" + "，".join(info)
            response += f"\n\n诊断结果为{disease['name']}。"
            response += f"\n病害特征：{disease['description']}"
            response += f"\n防治建议：{disease['control_method']}"
            if 'prevention' in disease:
                response += f"\n预防措施：{disease['prevention']}"
            return response
        
        # 多个可能的病害，列出简要信息
        response = "根据目前掌握的信息："
        info = []
        for category, value in collected_symptoms.items():
            if category == 'plant_part':
                info.append(f"发病部位：{format_symptom_value(value)}")
            elif category == 'weather':
                info.append(f"气象条件：{format_symptom_value(value)}")
            elif category == 'growth_stage':
                info.append(f"生育期：{format_symptom_value(value)}")
            elif category == 'region':
                info.append(f"种植区：{format_symptom_value(value)}")
        response += "\n" + "，".join(info)
        response += "\n\n可能的病害有："
        
        # 按匹配度排序疾病列表
        for i, disease in enumerate(diseases, 1):
            response += f"\n{i}. {disease['name']}"
            response += f"\n   主要特征: {disease['description'][:100]}..."
        
        response += "\n\n请补充更多信息，以便我更准确地判断。"
        return response

    class SSERenderer(BaseRenderer):
        media_type = 'text/event-stream'
        format = 'sse'
        
        def render(self, data, accepted_media_type=None, renderer_context=None):
            return data
            
    renderer_classes = [SSERenderer] 