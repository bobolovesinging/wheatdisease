"""
聊天应用的服务模块

提供与Neo4j知识图谱交互的服务
"""

import os
import json
import logging
from backend.connections import get_neo4j_driver, get_openai_client, get_redis_client, get_mysql_conn
from .utils import keyword_manager

logger = logging.getLogger(__name__)

class Neo4jService:
    """Neo4j服务类，用于与Neo4j数据库交互"""
    
    def __init__(self):
        """初始化Neo4j服务（不再自行管理连接，统一用全局工厂）"""
        self.driver = get_neo4j_driver()
    
    def is_connected(self):
        """检查是否成功连接到Neo4j"""
        return self.driver is not None
    
    def extract_symptoms(self, message):
        """
        从用户消息中提取症状信息
        
        Args:
            message (str): 用户消息
        
        Returns:
            dict: 提取到的症状信息
        """
        return keyword_manager.extract_symptoms(message)
    
    def query_disease(self, symptoms):
        """
        根据症状查询可能的病害
        
        Args:
            symptoms (dict): 包含症状信息的字典
                - plant_part: 发病部位
                - weather: 发病气象条件
                - growth_stage: 发病生育期
                - region: 发病地区
        
        Returns:
            list: 可能的病害列表，每个病害包含名称、描述和防治方法
        """
        if not self.is_connected():
            logger.warning("Neo4j connection is not available")
            return []
            
        try:
            with self.driver.session() as session:
                # 构建查询条件
                match_clauses = []
                where_clauses = []
                params = {
                    'plant_part': symptoms.get('plant_part'),
                    'weather': symptoms.get('weather'),
                    'growth_stage': symptoms.get('growth_stage'),
                    'region': symptoms.get('region')
                }
                
                logger.info(f"查询参数: {params}")
                
                # 构建Cypher查询
                query = """
                MATCH (d:Disease)
                """
                
                # 添加条件匹配
                if params['plant_part']:
                    query += "MATCH (d)-[:AFFECTS_PART]->(p:PlantPart {name: $plant_part}) "
                if params['weather']:
                    query += "MATCH (d)-[:OCCURS_IN_WEATHER]->(w:Weather {name: $weather}) "
                if params['growth_stage']:
                    query += "MATCH (d)-[:OCCURS_IN_STAGE]->(s:GrowthStage {name: $growth_stage}) "
                if params['region']:
                    query += "MATCH (d)-[:OCCURS_IN_REGION]->(r:Region {name: $region}) "
                
                # 返回结果
                query += """
                RETURN d.name as name, 
                       d.alias as alias,
                       d.pathogen as pathogen,
                       d.symptoms as symptoms,
                       d.treatment as treatment,
                       count(*) as matched_symptoms,
                       1.0 as match_ratio
                LIMIT 3
                """
                
                logger.info(f"执行查询: {query}")
                logger.info(f"查询参数: {params}")
                
                result = session.run(query, params)
                logger.info(f"查询结果: {result}")
                diseases = []
                
                for record in result:
                    diseases.append({
                        'name': record['name'],
                        'alias': record.get('alias', ''),
                        'pathogen': record.get('pathogen', ''),
                        'description': record.get('symptoms', ''),
                        'control_method': record.get('treatment', ''),
                        'match_count': record['matched_symptoms']
                    })
                
                logger.info(f"Found {len(diseases)} matching diseases")
                return diseases
                
        except Exception as e:
            logger.error(f"Error querying Neo4j: {str(e)}")
            return []
    
    def get_disease_details(self, disease_name):
        """
        获取特定病害的详细信息
        
        Args:
            disease_name (str): 病害名称
        
        Returns:
            dict: 病害详细信息
        """
        if not self.is_connected():
            logger.warning("Neo4j connection is not available")
            return None
            
        try:
            with self.driver.session() as session:
                query = """
                MATCH (d:Disease {name: $name})
                RETURN d.name as name, 
                       d.alias as alias,
                       d.pathogen as pathogen,
                       d.symptoms as symptoms,
                       d.treatment as treatment
                """
                
                result = session.run(query, {'name': disease_name})
                record = result.single()
                
                if record:
                    return {
                        'name': record['name'],
                        'alias': record.get('alias', ''),
                        'pathogen': record.get('pathogen', ''),
                        'description': record.get('symptoms', ''),  # 使用symptoms作为description
                        'control_method': record.get('treatment', '')
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting disease details: {str(e)}")
            return None

class IntentService:
    """意图识别服务类，用于识别用户输入的意图"""
    
    def __init__(self):
        """初始化意图识别服务"""
        self.client = get_openai_client()
        
        # 预定义的意图类型
        self.intent_types = {
            'diagnosis': '病害诊断',
            'prevention': '防治建议',
            'knowledge': '知识查询',
            'greeting': '问候',
            'farewell': '告别',
            'thanks': '感谢',
            'unknown': '未知意图'
        }
        
        # 意图识别的提示词
        self.intent_prompt = """请分析以下用户输入的意图，并返回对应的意图类型。
        可能的意图类型包括：
        1. diagnosis - 用户想要进行小麦病害诊断，此外当出现小麦的部位、气象条件、生育期、种植区时，返回diagnosis
        2. prevention - 用户想要获取防治建议
        3. knowledge - 用户想要查询小麦病害相关知识
        4. greeting - 用户在进行问候
        5. farewell - 用户在进行告别
        6. thanks - 用户在表达感谢
        7. unknown - 无法识别的意图
        
        请只返回意图类型的英文标识，不要包含其他内容。
        
        用户输入："""
    
    def recognize_intent(self, message):
        """
        识别用户输入的意图
        
        Args:
            message (str): 用户输入的消息
            
        Returns:
            str: 识别出的意图类型
        """
        if not message:
            return 'unknown'
            
        try:
            # 使用OpenAI进行意图识别
            response = self.client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL'),
                messages=[
                    {"role": "system", "content": self.intent_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            # 获取意图类型
            intent = response.choices[0].message.content.strip().lower()
            logger.debug(f"意图识别原始返回: {response.choices[0].message.content}, 提取intent: {intent}")
            
            # 验证意图类型是否有效
            if intent in self.intent_types:
                return intent
            return 'unknown'
            
        except Exception as e:
            logger.error(f"意图识别失败: {str(e)}")
            return 'unknown'
    
    def get_intent_description(self, intent):
        """
        获取意图的中文描述
        
        Args:
            intent (str): 意图类型
            
        Returns:
            str: 意图的中文描述
        """
        return self.intent_types.get(intent, '未知意图') 