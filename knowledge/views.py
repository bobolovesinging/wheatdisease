"""
知识图谱API视图集

提供知识图谱的查询接口，包括：
- 获取完整图谱数据
- 获取节点详情
- 获取相关节点
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import logging

from .services import KnowledgeGraphService

logger = logging.getLogger(__name__)

class KnowledgeGraphAPI(viewsets.ViewSet):
    """知识图谱API视图集"""
    
    authentication_classes = []
    permission_classes = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = KnowledgeGraphService()
    
    @action(detail=False, methods=['GET'])
    def graph(self, request):
        """获取完整的知识图谱数据"""
        try:
            if not self.service.is_connected():
                return Response(
                    {'error': 'Neo4j数据库未连接,请检查Neo4j是否启动'},
                    status=500
                )
                
            graph_data = self.service.get_full_graph()
            return Response(graph_data)
                
        except Exception as e:
            logger.error(f"获取图谱数据失败: {str(e)}")
            return Response(
                {'error': f'获取图谱数据失败: {str(e)}'},
                status=500
            )

    @action(detail=False, methods=['GET'])
    def node_details(self, request):
        """获取节点详细信息"""
        try:
            node_id = request.GET.get('id')
            if not node_id:
                return Response({'error': '节点ID不能为空'}, status=400)
            
            node_data = self.service.get_node_details(node_id)
            if not node_data:
                return Response({'error': '节点不存在'}, status=404)
                
            return Response(node_data)
                
        except Exception as e:
            logger.error(f"获取节点详情失败: {str(e)}")
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['GET'])
    def related_nodes(self, request):
        """获取相关节点"""
        try:
            node_id = request.GET.get('id')
            relation_type = request.GET.get('type')
            
            if not node_id:
                return Response({'error': '节点ID不能为空'}, status=400)
            
            related_nodes = self.service.get_related_nodes(node_id, relation_type)
            return Response(related_nodes)
            
        except Exception as e:
            logger.error(f"获取相关节点失败: {str(e)}")
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['GET'])
    def get_disease_subgraph(self, request):
        """获取病害节点的子图"""
        disease = request.GET.get('disease')
        if not disease:
            return Response({'error': '缺少disease参数'}, status=400)
        try:
            data = self.service.get_disease_subgraph(disease)
            return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['GET'])
    def get_node_subgraph(self, request):
        """获取非病害节点的子图"""
        node = request.GET.get('node')
        node_type = request.GET.get('type')
        if not node or not node_type:
            return Response({'error': '缺少node或type参数'}, status=400)
        try:
            data = self.service.get_node_subgraph(node, node_type)
            return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=500) 