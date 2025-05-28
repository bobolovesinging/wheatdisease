# Django项目的主要配置文件
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
import redis

# 构建项目根目录的绝对路径
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载环境变量
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Django安全设置
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# API配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')



# 已安装的Django应用
INSTALLED_APPS = [
    'users',  # 新增用户应用
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'backend.apps.BackendConfig',  # 添加 backend 应用
    'chat.apps.ChatConfig',  # 使用完整的应用配置路径
    'knowledge',
    'rest_framework_simplejwt',
]

# 在 INSTALLED_APPS 配置下方添加：
AUTH_USER_MODEL = 'users.User'

# 中间件配置
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS中间件（必须放在最前面）
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# CORS配置
CORS_ALLOW_ALL_ORIGINS = True  # 开发环境下先允许所有源
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
CORS_ALLOWED_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
]
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# 允许在开发环境中使用不安全的请求
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# 模板配置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # 模板引擎
        'DIRS': [os.path.join(BASE_DIR, 'templates')],               # 模板目录
        'APP_DIRS': True,                                            # 是否在应用中查找模板
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',           # 调试相关上下文
                'django.template.context_processors.request',         # 请求相关上下文
                'django.contrib.auth.context_processors.auth',        # 认证相关上下文
                'django.contrib.messages.context_processors.messages',# 消息相关上下文
            ],
        },
    },
]

# 静态文件配置
STATIC_URL = '/static/'                                  # 静态文件URL前缀
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')     # 收集的静态文件存放目录
STATICFILES_DIRS = [                                    # 额外的静态文件目录
    os.path.join(BASE_DIR, 'static'),
]

# 媒体文件配置
MEDIA_URL = '/media/'                                   # 媒体文件URL前缀
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')           # 媒体文件存放目录

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DB'),
        'USER': os.getenv('MYSQL_USER'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD'),
        'HOST': os.getenv('MYSQL_HOST'),
        'PORT': os.getenv('MYSQL_PORT'),
        'CONN_MAX_AGE': 60,  # 连接最大复用时间（秒），建议60或更高
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}

# 密码验证器
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,                           # 最小密码长度
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 国际化配置
LANGUAGE_CODE = 'zh-hans'                              # 默认语言
TIME_ZONE = 'Asia/Shanghai'                            # 时区
USE_I18N = True                                        # 是否启用国际化
USE_L10N = True                                        # 是否启用本地化
USE_TZ = True                                          # 是否使用时区

# REST Framework配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'UNAUTHENTICATED_USER': None,  # 未认证用户返回None而不是AnonymousUser
}

# 知识图谱API权限配置
KNOWLEDGE_API_PERMISSION_CLASSES = [
    'rest_framework.permissions.AllowAny',
]

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 允许的主机
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'backend', 'debug.log'),
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {  # 只配置 root logger
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        # 子 logger 不单独配置 handler，只设 level 和 propagate
        'django': {
            'level': 'INFO',
            'propagate': True,
        },
        'chat': {
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# 邮件配置（如果需要）
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@example.com'
# EMAIL_HOST_PASSWORD = 'your-password'

# Redis配置
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_DB = int(os.getenv('REDIS_DB'))

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': REDIS_PASSWORD,
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 1000,
            'CONNECTION_POOL_KWARGS': {'max_connections': 100},
            'CONNECTION_POOL_CLASS': 'redis.connection.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 100,
                'timeout': 20
            }
        }
    }
}

# URL配置
ROOT_URLCONF = 'backend.urls'  # 指定主 URL 配置文件的位置

# JWT设置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Neo4j配置
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

# 添加默认主键类型设置
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 供 backend/connections.py 直连用
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_DB = 'wheatdisease'

