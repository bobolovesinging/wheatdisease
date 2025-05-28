from backend.connections import get_neo4j_driver, get_redis_client, get_mysql_conn, get_openai_client

def close_neo4j_connection():
    driver = get_neo4j_driver()
    if driver:
        driver.close()

# 注册关闭函数
import atexit
atexit.register(close_neo4j_connection) 