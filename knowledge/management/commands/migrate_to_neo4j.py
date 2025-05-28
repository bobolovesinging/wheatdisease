from django.core.management.base import BaseCommand
from knowledge.views import KnowledgeGraphAPI
from neo4j import GraphDatabase
from django.conf import settings
from backend.graph_manager import GraphManager, get_neo4j_driver

class Command(BaseCommand):
    help = '将现有的图谱数据迁移到Neo4j数据库'

    def handle(self, *args, **options):
        try:
            # 先测试Neo4j连接
            driver = get_neo4j_driver()
            with driver.session() as session:
                session.run("MATCH (n) RETURN count(n) as count")
            # 连接成功后再执行迁移
            api = KnowledgeGraphAPI()
            api.load_graph_data()
            self.stdout.write(self.style.SUCCESS('数据迁移成功'))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'数据迁移失败: {str(e)}\n'
                               f'请检查Neo4j服务是否启动，以及连接配置是否正确:\n'
                               f'URI: {settings.NEO4J_URI}\n'
                               f'User: {settings.NEO4J_USER}')
            ) 