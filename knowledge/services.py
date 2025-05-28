"""
知识图谱服务模块

提供知识图谱的查询功能，包括：
- 获取完整图谱数据
- 获取节点详情
- 获取相关节点
"""

import logging
import json
from typing import Dict, List, Optional, Any
from django.core.cache import cache
from neo4j import Driver
from backend.connections import get_neo4j_driver

logger = logging.getLogger(__name__)

class KnowledgeGraphService:
    """知识图谱服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.driver = get_neo4j_driver()
        self.cache_timeout = 3600  # 缓存过期时间：1小时
        
        # 缓存键前缀
        self.CACHE_PREFIX = "knowledge:graph:"
        self.NODE_CACHE_PREFIX = f"{self.CACHE_PREFIX}node:"
        self.RELATION_CACHE_PREFIX = f"{self.CACHE_PREFIX}relation:"
        self.GRAPH_CACHE_KEY = f"{self.CACHE_PREFIX}full"
    
    def is_connected(self) -> bool:
        """检查Neo4j连接状态"""
        return self.driver is not None
    
    def get_full_graph(self) -> Dict[str, List]:
        """获取完整的知识图谱数据"""
        # 尝试从缓存获取
        cached_data = cache.get(self.GRAPH_CACHE_KEY)
        if cached_data:
            return json.loads(cached_data)
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n)
                    OPTIONAL MATCH (n)-[r]->(m)
                    RETURN DISTINCT 
                        n.name as name,
                        labels(n)[0] as label,
                        n.color as color,
                        n.alias as alias,
                        n.pathogen as pathogen, 
                        n.symptoms as symptoms,
                        n.treatment as treatment,
                        type(r) as relationship,
                        m.name as target
                """)
                
                nodes = {}
                links = []
                
                for record in result:
                    # 处理节点
                    node_id = record['name']
                    if node_id not in nodes:
                        node = self._create_node_dict(record)
                        nodes[node_id] = node
                    
                    # 处理关系
                    if record['relationship'] and record['target']:
                        links.append({
                            'source': node_id,
                            'target': record['target'],
                            'type': record['relationship']
                        })
                
                graph_data = {
                    'nodes': list(nodes.values()),
                    'links': links
                }
                
                # 缓存结果
                cache.set(self.GRAPH_CACHE_KEY, json.dumps(graph_data), self.cache_timeout)
                
                return graph_data
                
        except Exception as e:
            logger.error(f"获取图谱数据失败: {str(e)}")
            raise
    
    def get_node_details(self, node_id: str) -> Optional[Dict]:
        """获取节点详细信息"""
        # 尝试从缓存获取
        cache_key = f"{self.NODE_CACHE_PREFIX}{node_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n {name: $name})
                    OPTIONAL MATCH (n)-[r]->(m)
                    RETURN n, 
                           collect(distinct {rel: type(r), target: m.name}) as relations
                """, name=node_id)
                
                record = result.single()
                if not record:
                    return None
                
                node = record['n']
                relations = record['relations']
                
                node_data = {
                    'id': node['name'],
                    'name': node['name'],
                    'type': list(node.labels)[0],
                    'properties': dict(node),
                    'relations': relations
                }
                
                # 缓存结果
                cache.set(cache_key, json.dumps(node_data), self.cache_timeout)
                
                return node_data
                
        except Exception as e:
            logger.error(f"获取节点详情失败: {str(e)}")
            raise
    
    def get_related_nodes(self, node_id: str, relation_type: Optional[str] = None) -> List[Dict]:
        """获取相关节点"""
        cache_key = f"{self.RELATION_CACHE_PREFIX}{node_id}:{relation_type or 'all'}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        try:
            with self.driver.session() as session:
                query = """
                    MATCH (n {name: $name})
                    OPTIONAL MATCH (n)-[r]->(m)
                    WHERE $relation_type IS NULL OR type(r) = $relation_type
                    RETURN m, type(r) as relation_type
                """
                
                result = session.run(query, name=node_id, relation_type=relation_type)
                
                related_nodes = []
                for record in result:
                    if record['m']:
                        node = record['m']
                        related_nodes.append({
                            'id': node['name'],
                            'name': node['name'],
                            'type': list(node.labels)[0],
                            'relation_type': record['relation_type']
                        })
                
                # 缓存结果
                cache.set(cache_key, json.dumps(related_nodes), self.cache_timeout)
                
                return related_nodes
                
        except Exception as e:
            logger.error(f"获取相关节点失败: {str(e)}")
            raise
    
    def _create_node_dict(self, record: Any) -> Dict:
        """从Neo4j记录创建节点字典"""
        node = {
            'id': record['name'],
            'name': record['name'],
            'type': record['label'].lower(),
            'color': record['color']
        }
        
        # 为Disease节点添加描述信息
        if record['label'] == 'Disease':
            description = []
            if record['alias']:
                description.append(f"别名: {record['alias']}")
            if record['pathogen']:
                description.append(f"病原: {record['pathogen']}")
            if record['symptoms']:
                description.append(f"症状: {record['symptoms']}")
            if record['treatment']:
                description.append(f"防治: {record['treatment']}")
            
            if description:
                node['description'] = '\n'.join(description)
            
            node['details'] = {
                'alias': record['alias'] or '',
                'pathogen': record['pathogen'] or '',
                'symptoms': record['symptoms'] or '',
                'treatment': record['treatment'] or ''
            }
        
        return node 

    def get_disease_subgraph(self, disease_name: str) -> Dict[str, List]:
        """
        获取病害节点及其所有直接关联的非病害节点子图
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (d:Disease {name: $disease_name})-[r]-(n)
                    WHERE NOT n:Disease
                    RETURN d, r, n
                """, disease_name=disease_name)
                
                nodes = {}
                links = []
                for record in result:
                    d = record['d']
                    n = record['n']
                    r = record['r']
                    # 病害节点
                    nodes[d['name']] = {
                        'id': d['name'],
                        'name': d['name'],
                        'type': 'disease',
                        'color': '#2C3E50'
                    }
                    # 非病害节点
                    n_type = list(n.labels)[0].lower() if n.labels else 'unknown'
                    nodes[n['name']] = {
                        'id': n['name'],
                        'name': n['name'],
                        'type': n_type,
                        'color': self._get_node_color(n_type)
                    }
                    links.append({
                        'source': d['name'],
                        'target': n['name'],
                        'type': r.type
                    })
                return {
                    'nodes': list(nodes.values()),
                    'links': links
                }
        except Exception as e:
            logger.error(f"获取病害子图失败: {str(e)}")
            raise

    def _normalize_label(self, node_type: str) -> str:
        """将前端传来的 node_type 转换为 Neo4j 标准标签"""
        label_map = {
            'disease': 'Disease',
            'plantpart': 'PlantPart',
            'region': 'Region',
            'weather': 'Weather',
            'growthstage': 'GrowthStage',
        }
        return label_map.get(node_type.lower(), node_type.capitalize())

    def get_node_subgraph(self, node_name: str, node_type: str) -> Dict[str, List]:
        """
        获取非病害节点及其所有直接关联的病害节点子图
        """
        try:
            with self.driver.session() as session:
                label = self._normalize_label(node_type)
                cypher = f"""
                    MATCH (n:{label} {{name: $node_name}})-[r]-(d:Disease)
                    RETURN n, r, d
                """
                result = session.run(cypher, node_name=node_name)
                nodes = {}
                links = []
                for record in result:
                    n = record['n']
                    d = record['d']
                    r = record['r']
                    n_type = list(n.labels)[0].lower() if n.labels else 'unknown'
                    nodes[n['name']] = {
                        'id': n['name'],
                        'name': n['name'],
                        'type': n_type,
                        'color': self._get_node_color(n_type)
                    }
                    nodes[d['name']] = {
                        'id': d['name'],
                        'name': d['name'],
                        'type': 'disease',
                        'color': '#2C3E50'
                    }
                    links.append({
                        'source': n['name'],
                        'target': d['name'],
                        'type': r.type
                    })
                return {
                    'nodes': list(nodes.values()),
                    'links': links
                }
        except Exception as e:
            logger.error(f"获取节点子图失败: {str(e)}")
            raise

    def _get_node_color(self, node_type: str) -> str:
        color_map = {
            'disease': '#2C3E50',
            'weather': '#3498DB',
            'region': '#E67E22',
            'plantpart': '#27AE60',
            'growthstage': '#E67E22',
            # 其他类型...
        }
        return color_map.get(node_type, '#888888') 