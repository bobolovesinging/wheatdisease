from django.apps import AppConfig
import logging

class BackendConfig(AppConfig):
    name = 'backend'
    verbose_name = '后端服务'

    def ready(self):
        from backend.connections import get_neo4j_driver, get_redis_client, get_mysql_conn, get_openai_client
        try:
            get_neo4j_driver()
            logging.info("=== Neo4j实例初始化成功 ===")
        except Exception as e:
            logging.error(f"=== Neo4j实例初始化失败: {e} ===")
        try:
            get_redis_client()
            logging.info("=== Redis实例初始化成功 ===")
        except Exception as e:
            logging.error(f"=== Redis实例初始化失败: {e} ===")
        try:
            get_mysql_conn()
            logging.info("=== MySQL实例初始化成功 ===")
        except Exception as e:
            logging.error(f"=== MySQL实例初始化失败: {e} ===")
        try:
            get_openai_client()
            logging.info("=== OpenAI/Ark实例初始化成功 ===")
        except Exception as e:
            logging.error(f"=== OpenAI/Ark实例初始化失败: {e} ===") 