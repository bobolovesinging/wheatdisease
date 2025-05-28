"""
连接管理模块

提供各种外部服务的连接管理，包括：
- Neo4j数据库连接
- OpenAI API客户端
- Redis连接
- MySQL连接
"""

import logging
from neo4j import GraphDatabase
from openai import OpenAI
import redis
import mysql.connector
from django.conf import settings

logger = logging.getLogger(__name__)

# 全局连接实例
_neo4j_driver = None
_openai_client = None
_redis_client = None
_mysql_conn = None

def get_neo4j_driver():
    """获取Neo4j数据库连接"""
    global _neo4j_driver
    if _neo4j_driver is None:
        try:
            _neo4j_driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            logger.info("Neo4j连接成功")
        except Exception as e:
            logger.error(f"Neo4j连接失败: {str(e)}")
    return _neo4j_driver

def get_openai_client():
    """获取API客户端"""
    global _openai_client
    if _openai_client is None:
        try:
            _openai_client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
            logger.info("API客户端初始化成功")
        except Exception as e:
            logger.error(f"API客户端初始化失败: {str(e)}")
    return _openai_client

def get_redis_client():
    """获取Redis连接"""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
    return _redis_client

def get_mysql_conn():
    """获取MySQL连接"""
    global _mysql_conn
    if _mysql_conn is None:
        try:
            _mysql_conn = mysql.connector.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DB
            )
            logger.info("MySQL连接成功")
        except Exception as e:
            logger.error(f"MySQL连接失败: {str(e)}")
    return _mysql_conn

def close_all_connections():
    """关闭所有连接"""
    global _neo4j_driver, _redis_client, _mysql_conn
    
    if _neo4j_driver:
        try:
            _neo4j_driver.close()
            logger.info("Neo4j connection closed")
        except Exception as e:
            logger.error(f"Error closing Neo4j connection: {str(e)}")
    
    if _redis_client:
        try:
            _redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {str(e)}")
    
    if _mysql_conn:
        try:
            _mysql_conn.close()
            logger.info("MySQL connection closed")
        except Exception as e:
            logger.error(f"Error closing MySQL connection: {str(e)}") 