import os
import django
import redis
import logging
import json
from django.conf import settings


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_redis_connection():
    """
    测试Redis连接是否正常
    """
    try:
        # 创建Redis客户端
        redis_client = redis.StrictRedis(
            host='127.0.0.1',
            port=6379,
            db=1,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        
        # 测试连接
        redis_client.ping()
        logger.info("✓ Redis连接成功!")
        
        # 测试基本操作
        # 1. 字符串操作测试
        redis_client.set('test_key', 'test_value')
        value = redis_client.get('test_key')
        assert value == 'test_value', "字符串操作测试失败"
        logger.info("✓ 字符串操作测试成功")
        
        # 2. 哈希表操作测试
        redis_client.hset('test_hash', 'field1', 'value1')
        redis_client.hset('test_hash', 'field2', 'value2')
        hash_value = redis_client.hgetall('test_hash')
        assert hash_value == {'field1': 'value1', 'field2': 'value2'}, "哈希表操作测试失败"
        logger.info("✓ 哈希表操作测试成功")
        
        # 3. 列表操作测试
        redis_client.rpush('test_list', 'item1', 'item2', 'item3')
        list_value = redis_client.lrange('test_list', 0, -1)
        assert list_value == ['item1', 'item2', 'item3'], "列表操作测试失败"
        logger.info("✓ 列表操作测试成功")
        
        # 4. JSON数据测试
        test_dict = {
            'name': 'test_session',
            'created_at': 1234567890,
            'data': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        redis_client.set('test_json', json.dumps(test_dict))
        json_value = json.loads(redis_client.get('test_json'))
        assert json_value == test_dict, "JSON数据测试失败"
        logger.info("✓ JSON数据测试成功")
        
        # 5. 过期时间测试
        redis_client.set('test_expire', 'will_expire', ex=2)  # 2秒后过期
        assert redis_client.get('test_expire') == 'will_expire', "过期时间测试失败"
        logger.info("✓ 过期时间设置测试成功")
        
        # 清理测试数据
        keys_to_delete = ['test_key', 'test_hash', 'test_list', 'test_json', 'test_expire']
        redis_client.delete(*keys_to_delete)
        logger.info("✓ 测试数据清理成功")
        
        logger.info("所有测试用例执行成功!")
        return True
        
    except redis.ConnectionError as e:
        logger.error(f"Redis连接错误: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Redis操作错误: {str(e)}")
        return False

if __name__ == '__main__':
    test_redis_connection() 