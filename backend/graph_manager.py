from neo4j import GraphDatabase
from django.conf import settings
import csv
from pathlib import Path
import logging
import redis

# 配置日志
logger = logging.getLogger(__name__)

_neo4j_driver = None
_neo4j_driver_initialized = False

def get_neo4j_driver():
    global _neo4j_driver, _neo4j_driver_initialized
    if _neo4j_driver is None:
        _neo4j_driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        if not _neo4j_driver_initialized:
            print("Neo4j服务初始化成功（全局单例）")
            _neo4j_driver_initialized = True
    return _neo4j_driver

class GraphConfig:
    """图谱配置类"""
    # 节点颜色配置
    NODE_COLORS = {
        'disease': '#2C3E50',    # 病害节点 - 深灰色
        'weather': '#3498DB',    # 气象节点 - 蓝色
        'growth_stage': '#9B59B6',  # 生育期节点 - 紫色
        'plant_part': '#27AE60',    # 部位节点 - 绿色
        'region': '#E67E22',        # 地区节点 - 橙色
    }
    
    # 关系类型配置
    RELATIONSHIPS = {
        'weather': 'OCCURS_IN_WEATHER',
        'growth_stage': 'OCCURS_IN_STAGE',
        'plant_part': 'AFFECTS_PART',
        'region': 'OCCURS_IN_REGION'
    }

class Neo4jError(Exception):
    """Neo4j操作相关错误"""
    pass

class GraphManager:
    """知识图谱管理类
    
    负责知识图谱的初始化、数据导入、关键词提取等核心功能
    """
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # 测试连接
            with self.driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) as count")
                count = result.single()["count"]
                logger.info(f"Neo4j连接成功，当前数据库有 {count} 个节点")
        except Exception as e:
            logger.error(f"Neo4j连接失败: {str(e)}")
            self.driver = None
        
        # Redis连接
        try:
            self.redis_client = redis.StrictRedis(
                host='127.0.0.1',
                port=6379,
                db=1,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            self.redis_client = None
        
        # 定义标准关键词集
        self.region_keywords = {
            "黑龙江", "吉林", "辽宁", "河北", "山西", "山东", "河南", "江苏", "浙江",
            "安徽", "江西", "福建", "广东", "广西", "海南", "湖北", "湖南", "四川",
            "贵州", "云南", "陕西", "甘肃", "青海", "台湾", "北京", "天津", "上海", 
            "重庆", "内蒙古", "新疆", "西藏", "宁夏", 
            "东北", "华北", "华东", "华南", 
            "华中", "西北", "西南", 
            "东北平原区", "云贵高原区", "北方干旱半干旱区", 
            "华南区", "四川盆地区", "长江中下游区", "青藏高原区", "黄土高原区", 
            "黄淮海平原区", 
            "全国各地", "南方", "北方", "西部", "东部"
        }
        
        self.plant_part_keywords = {
            "叶片", "茎秆", "根系", "麦穗", "叶鞘", "籽粒", "幼苗", "基部", "穗部",
            "节间", "叶尖", "叶缘", "叶面", "叶背", "茎基", "茎部", "穗轴", "颖壳",
            "护颖", "芒", "根冠", "根毛", "分蘖", "主茎", "种子", "胚芽", "胚根",
            "叶基", "茎节", "穗颈", "颖片", "子房", "花药", "花丝", "胚乳", "胚部"
        }
        
        self.growth_stage_keywords = {
            "全生育期", "生长全期", "全生长期", "苗期", "幼苗期", "出苗期", 
            "3-4叶期", "4-6叶期", "越冬期", "冬前", "返青期", "拔节期", 
            "分蘖期", "茎节期", "起身期", "抽穗期", "孕穗期", "开花期", 
            "扬花期", "灌浆期", "乳熟期", "成熟期", "收获期", "播种期",
            "发芽期", "生育中期", "生育后期", "抽穗扬花期", "成株期"
        }
        
        self.weather_keywords = {
            # 温度相关
            "高温", "低温", "寒潮", "倒春寒", "热浪", "冷凉", "温暖",
            # 降水相关
            "干旱", "潮湿", "阴雨", "连阴雨", "梅雨", "暴雨", "降雨", "多雨",
            # 湿度相关
            "干燥", "湿润", "高湿", "低湿",
            # 其他气象条件
            "大风", "霜冻", "积雪", "冰雹", "沙尘", "阴天", "晴天",
            # 复合条件
            "高温高湿", "低温多雨", "干旱高温"
        }

        # 定义标准关键词映射关系
        self.growth_stage_mapping = {
            "开花": "开花期",
            "抽穗": "抽穗期",
            "返青": "返青期",
            "成熟": "成熟期",
            "播种": "播种期",
            "发芽": "发芽期",
            "越冬": "越冬期",
            "拔节": "拔节期",
            "分蘖": "分蘖期",
            "灌浆": "灌浆期",
            "收获": "收获期",
            "出苗": "出苗期",
            "幼苗": "幼苗期",
            "孕穗": "孕穗期",
            "扬花": "扬花期",
            "生育中": "生育中期",
            "生育后": "生育后期",
            "全生育": "全生育期",
            "生长全": "全生育期",
            # 时间相关
            "初期": "苗期",
            "前期": "苗期",
            "中期": "生育中期",
            "后期": "生育后期",
            "末期": "成熟期",
            
            # 复合表达
            "抽穗开花": "抽穗期",
            "抽穗扬花": "抽穗期",
            "灌浆成熟": "灌浆期",
            
            # 同义表达
            ("出苗", "发苗"): "出苗期",
            ("幼苗", "小苗"): "幼苗期",
            ("成熟", "成熟时"): "成熟期",
        }

        self.plant_part_mapping = {
            # 基本映射
            "叶": "叶片",
            "茎": "茎秆",
            "根": "根系",
            "穗": "麦穗",
            "颖": "颖壳",
            "芽": "胚芽",
            "胚": "胚部",
            "花": "花药",
            
            # 扩展映射
            "心叶": "叶片",
            "老叶": "叶片",
            "基部叶片": "叶片",
            "上部叶片": "叶片",
            "新叶": "叶片",
            "旗叶": "叶片",
            "叶尖": "叶片",
            "叶基": "叶片",
            "叶鞘": "叶鞘",
            
            "茎基": "茎秆",
            "茎部": "茎秆",
            "秆": "茎秆",
            "节间": "茎秆",
            "茎节": "茎秆",
            "基部": "茎秆",
            
            "根冠": "根系",
            "根毛": "根系",
            "幼根": "根系",
            "种子根": "根系",
            
            "穗部": "麦穗",
            "穗轴": "麦穗",
            "小穗": "麦穗",
            "穗颈": "麦穗",
            
            "颖壳": "颖壳",
            "护颖": "颖壳",
            "颖片": "颖壳",
            
            "胚芽鞘": "胚芽",
            "幼芽": "胚芽",
            
            "子房": "胚部",
            "胚根": "胚部",
            "胚乳": "胚部",
            
            "花丝": "花药",
            "花器": "花药",
        }

        self.weather_mapping = {
            "温度高": "高温",
            "气温高": "高温",
            "温度低": "低温",
            "气温低": "低温",
            "降水": "降雨",
            "下雨": "降雨",
            "雨天": "阴雨",
            "干燥": "干旱",
            "湿润": "潮湿",
            # 温度组合
            ("高温", "温度高", "气温高"): "高温",
            ("低温", "温度低", "气温低"): "低温",
            
            # 降水组合
            ("降水", "下雨", "降雨"): "降雨",
            ("干旱", "干燥", "缺水"): "干旱",
            
            # 复合条件
            "高温干旱": ["高温", "干旱"],
            "低温阴雨": ["低温", "阴雨"],
        }

    def extract_keywords(self, text, keyword_set, mapping=None):
        """从文本中提取标准关键词
        
        Args:
            text (str): 待分析文本
            keyword_set (set): 标准关键词集合
            mapping (dict): 关键词映射字典
        
        Returns:
            list: 提取的标准关键词列表
        """
        if not text:
            return []
        
        keywords = set()
        text = self._clean_text(text)  # 使用清理文本方法
        
        # 1. 首先处理复合关键词（避免被单个关键词匹配影响）
        if mapping:
            for key, value in mapping.items():
                if isinstance(key, tuple):
                    continue  # 先跳过同义词组
                if isinstance(value, list) and key.lower() in text:
                    keywords.update(v for v in value if v in keyword_set)
        
        # 2. 处理标准关键词（较长的优先）
        sorted_keywords = sorted(keyword_set, key=len, reverse=True)
        for keyword in sorted_keywords:
            if keyword.lower() in text:
                keywords.add(keyword)
                # 从文本中移除已匹配的关键词，避免重复匹配
                text = text.replace(keyword.lower(), '')
        
        # 3. 处理同义词组
        if mapping:
            for key, value in mapping.items():
                if isinstance(key, tuple):
                    # 同义词组匹配时考虑上下文
                    context_words = 5  # 上下文窗口大小
                    for k in key:
                        k = k.lower()
                        if k in text:
                            # 获取关键词周围的上下文
                            start = max(0, text.find(k) - context_words)
                            end = min(len(text), text.find(k) + len(k) + context_words)
                            context = text[start:end]
                            
                            # 根据上下文确认是否为目标含义
                            if self._validate_context(context, k):
                                if isinstance(value, str) and value in keyword_set:
                                    keywords.add(value)
                                elif isinstance(value, list):
                                    keywords.update(v for v in value if v in keyword_set)
        
        # 4. 应用特殊规则
        keywords = self._apply_special_rules(keywords, text)
        
        return list(keywords)

    def _validate_context(self, context, keyword):
        """验证关键词在上下文中的有效性
        
        Args:
            context (str): 关键词周围的上下文
            keyword (str): 待验证的关键词
            
        Returns:
            bool: 是否为有效匹配
        """
        # 否定词列表
        negative_words = {'不', '没有', '无', '未'}
        
        # 检查上下文中是否有否定词
        for word in negative_words:
            if word in context:
                return False
                
        return True
        
    def _apply_special_rules(self, keywords, text):
        """应用特殊规则处理关键词
        
        Args:
            keywords (set): 已提取的关键词集合
            text (str): 原始文本
            
        Returns:
            set: 处理后的关键词集合
        """
        # 1. 处理互斥关键词
        if '高温' in keywords and '低温' in keywords:
            # 根据上下文判断保留哪个
            if text.find('高温') < text.find('低温'):
                keywords.remove('低温')
            else:
                keywords.remove('高温')
                
        # 2. 处理生育期的顺序关系
        growth_stages = {'苗期', '拔节期', '抽穗期', '灌浆期'}
        found_stages = keywords.intersection(growth_stages)
        if len(found_stages) > 1:
            # 保留文本中最先提到的生育期
            first_stage = min(found_stages, key=lambda x: text.find(x))
            keywords = {k for k in keywords if k not in growth_stages or k == first_stage}
            
        return keywords

    def close(self):
        self.driver.close()

    def init_graph(self):
        """初始化基础知识图谱数据"""
        if not self.driver:
            raise Neo4jError("Neo4j连接未初始化")
        
        try:
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    # 清空现有数据
                    tx.run("MATCH (n) DETACH DELETE n")
                    
                    csv_file = Path('static/File/小麦病害信息.csv')
                    if not csv_file.exists():
                        raise Neo4jError(f"CSV文件不存在: {csv_file}")
                    
                    processed_count = 0
                    error_count = 0
                    
                    with open(csv_file, 'r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                if self._validate_csv_data(row):
                                    self._process_disease_row(tx, row)
                                    processed_count += 1
                                else:
                                    error_count += 1
                                    logger.warning(f"跳过无效数据行: {row}")
                            except Exception as e:
                                error_count += 1
                                logger.error(f"处理数据行失败: {str(e)}")
                    
                    logger.info(f"数据导入完成: 成功 {processed_count} 条，失败 {error_count} 条")
                    return True
                
        except Exception as e:
            raise Neo4jError(f"初始化知识图谱失败: {str(e)}")

    def _process_disease_row(self, tx, row):
        """处理单行疾病数据
        
        Args:
            tx: Neo4j事务对象
            row (dict): CSV数据行
        """
        # 提取疾病名称和别名
        disease_name = row['病害名称(别名)'].split('(')[0].strip()
        alias = row['病害名称(别名)'].split('(')[1].rstrip(')') if '(' in row['病害名称(别名)'] else ''
        
        # 创建疾病节点
        tx.run("""
        MERGE (d:Disease {
            name: $name,
            alias: $alias,
            pathogen: $pathogen,
            symptoms: $symptoms,
            treatment: $treatment,
            type: 'disease',
            color: '#2C3E50'
        })
        """, {
            'name': disease_name,
            'alias': alias,
            'pathogen': row.get('病原', ''),
            'symptoms': row.get('为害特征', ''),
            'treatment': row.get('防治措施', '')
        })
        
        # 处理相关节点
        self._process_weather_nodes(tx, row, disease_name)
        self._process_growth_stage_nodes(tx, row, disease_name)
        self._process_plant_part_nodes(tx, row, disease_name)
        self._process_region_nodes(tx, row, disease_name)

    def _process_weather_nodes(self, tx, row, disease_name):
        weather_conditions = set()
        weather_conditions.update(self.extract_keywords(row.get('气象', ''), self.weather_keywords, self.weather_mapping))
        weather_conditions.update(self.extract_keywords(row.get('病原', ''), self.weather_keywords, self.weather_mapping))
        for weather in weather_conditions:
            tx.run("""
            MERGE (weather:Weather {name: $weather, type: 'weather', color: '#3498DB'})
            WITH weather
            MATCH (d:Disease {name: $disease})
            MERGE (d)-[:OCCURS_IN_WEATHER]->(weather)
            """, {'weather': weather, 'disease': disease_name})

    def _process_growth_stage_nodes(self, tx, row, disease_name):
        growth_stages = set()
        growth_stages.update(self.extract_keywords(row.get('病害发生生育期', ''), self.growth_stage_keywords, self.growth_stage_mapping))
        growth_stages.update(self.extract_keywords(row.get('为害特征', ''), self.growth_stage_keywords, self.growth_stage_mapping))
        for stage in growth_stages:
            tx.run("""
            MERGE (stage:GrowthStage {name: $stage, type: 'growth_stage', color: '#9B59B6'})
            WITH stage
            MATCH (d:Disease {name: $disease})
            MERGE (d)-[:OCCURS_IN_STAGE]->(stage)
            """, {'stage': stage, 'disease': disease_name})

    def _process_plant_part_nodes(self, tx, row, disease_name):
        plant_parts = set()
        # 从病害发生部位字段提取
        parts1 = self.extract_keywords(
            row.get('病害发生部位', ''), 
            self.plant_part_keywords,
            self.plant_part_mapping
        )
        # 从为害特征字段提取
        parts2 = self.extract_keywords(
            row.get('为害特征', ''), 
            self.plant_part_keywords,
            self.plant_part_mapping
        )
        # 合并两个来源的部位信息
        plant_parts.update(parts1)
        plant_parts.update(parts2)
        
        for part in plant_parts:
            tx.run("""
            MERGE (part:PlantPart {name: $part, type: 'plant_part', color: '#27AE60'})
            WITH part
            MATCH (d:Disease {name: $disease})
            MERGE (d)-[:AFFECTS_PART]->(part)
            """, {'part': part, 'disease': disease_name})

    def _process_region_nodes(self, tx, row, disease_name):
        regions = self.extract_keywords(row.get('发病地区', ''), self.region_keywords)
        for region in regions:
            tx.run("""
            MERGE (region:Region {name: $region, type: 'region', color: '#E67E22'})
            WITH region
            MATCH (d:Disease {name: $disease})
            MERGE (d)-[:OCCURS_IN_REGION]->(region)
            """, {'region': region, 'disease': disease_name})

    def _create_node(self, tx, label, properties):
        """创建或更新节点
        
        Args:
            tx: Neo4j事务对象
            label (str): 节点标签
            properties (dict): 节点属性
        """
        properties['type'] = label.lower()
        properties['color'] = GraphConfig.NODE_COLORS[properties['type']]
        
        query = f"""
        MERGE (n:{label} {{name: $name}})
        SET n += $properties
        RETURN n
        """
        tx.run(query, {
            'name': properties['name'],
            'properties': properties
        })

    def _create_relationship(self, tx, from_label, to_label, from_name, to_name):
        """创建关系
        
        Args:
            tx: Neo4j事务对象
            from_label (str): 起始节点标签
            to_label (str): 目标节点标签
            from_name (str): 起始节点名称
            to_name (str): 目标节点名称
        """
        rel_type = GraphConfig.RELATIONSHIPS[to_label.lower()]
        query = f"""
        MATCH (a:{from_label} {{name: $from_name}})
        MATCH (b:{to_label} {{name: $to_name}})
        MERGE (a)-[:{rel_type}]->(b)
        """
        tx.run(query, {
            'from_name': from_name,
            'to_name': to_name
        })

    def _batch_process_nodes(self, tx, label, nodes_data):
        """批量处理节点
        
        Args:
            tx: Neo4j事务对象
            label (str): 节点标签
            nodes_data (list): 节点数据列表
        """
        query = f"""
        UNWIND $nodes as node
        MERGE (n:{label} {{name: node.name}})
        SET n += node.properties
        """
        tx.run(query, {
            'nodes': [{
                'name': data['name'],
                'properties': {
                    'type': label.lower(),
                    'color': GraphConfig.NODE_COLORS[label.lower()],
                    **data
                }
            } for data in nodes_data]
        })

    def _validate_csv_data(self, row):
        """验证CSV数据行
        
        Args:
            row (dict): CSV数据行
        
        Returns:
            bool: 数据是否有效
        """
        required_fields = ['病害名称(别名)', '病原', '为害特征', '防治措施']
        return all(row.get(field) for field in required_fields)

    def _clean_text(self, text):
        """清理文本数据
        
        Args:
            text (str): 原始文本
        
        Returns:
            str: 清理后的文本
        """
        if not text:
            return ''
        return text.strip().replace('\n', ' ').replace('\r', '')

# ========== 文件底部所有直接执行的代码全部注释或删除 ===========
# 例如：
# if __name__ == "__main__":
#     ...
# 任何未被类/函数包裹的 Redis/Neo4j 连接、初始化、测试等代码全部注释或删除