import os
import django
from neo4j import GraphDatabase 
import logging

# 首先设置Django环境 
# 设置环境变量 DJANGO_SETTINGS_MODULE
# 告诉Django在哪里找到项目的配置文件（settings.py）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# 然后再导入settings
from django.conf import settings 

# 配置日志
logger = logging.getLogger(__name__)

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

if __name__ == '__main__':
    # 以下为测试代码，仅在直接运行本文件时执行
    import logging
    logging.basicConfig(level=logging.INFO)
    try:
        from backend.connections import get_neo4j_driver
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run('RETURN 1 AS test')
            assert result.single()['test'] == 1
        logging.info('✓ Neo4j连接和基本查询测试通过!')
    except Exception as e:
        logging.error(f'Neo4j测试失败: {e}')