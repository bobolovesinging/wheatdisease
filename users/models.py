# 导入必要的模块
from django.db import models

# Django模型字段类型说明:
# models.CharField: 字符串字段,需指定max_length
# models.TextField: 长文本字段
# models.IntegerField: 整数字段
# models.FloatField: 浮点数字段
# models.DecimalField: 十进制数字段,需指定max_digits和decimal_places
# models.BooleanField: 布尔字段
# models.DateField: 日期字段
# models.DateTimeField: 日期时间字段
# models.EmailField: 邮箱字段
# models.FileField: 文件字段
# models.ImageField: 图片字段
# models.ForeignKey: 外键关联
# models.ManyToManyField: 多对多关联
# models.OneToOneField: 一对一关联
# models.AutoField: 自增字段
# models.BigAutoField: 大整数自增字段

# 常用字段参数:
# null=True/False: 是否允许为空
# blank=True/False: 是否允许为空白
# default: 默认值
# unique=True/False: 是否唯一
# verbose_name: 字段说明名
# help_text: 帮助文本
# choices: 选项
# auto_now_add: 创建时自动设置时间
# auto_now: 更新时自动设置时间
# related_name: 反向关联名称,用于反向查询（取别名）
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    用户模型类
    
    继承自Django的AbstractUser,用于扩展用户功能
    
    字段说明:
    - id: BigAutoField类型,作为主键
    - account: CharField类型,最大长度11位,用户唯一账号
    - password: CharField类型,最大长度128位,存储密码哈希值
    - role: CharField类型,用户角色,可选普通用户或管理员
    - created_time: DateTimeField类型,记录用户创建时间
    - is_active: BooleanField类型,账号是否激活
    - groups: ManyToManyField类型,关联auth.Group模型,用于用户分组
    - user_permissions: ManyToManyField类型,关联auth.Permission模型,用于权限管理
    
    Meta信息:
    - db_table: 指定数据库表名为'users'
    - verbose_name: 模型在admin后台显示的名称为'用户'
    """
    # 用户角色选项
    ROLE_CHOICES = (
        ('user', '普通用户'),
        ('admin', '管理员'),
    )
    
    # 主键字段
    id = models.BigAutoField(primary_key=True)
    
    # 用户基本信息字段
    account = models.CharField(max_length=9, unique=True, verbose_name='账号')
    password = models.CharField(max_length=128, verbose_name='密码')
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='用户角色'
    )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_active = models.BooleanField(
        default=True, 
        verbose_name='账号状态',
        help_text='指示用户是否被认为是活跃的。设为False而不是删除账号。'
    )
    
    # 用户权限相关字段
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='用户组',
        blank=True,
        help_text='用户所属的组',
        related_name='custom_user_set'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        verbose_name='用户权限',
        blank=True,
        help_text='用户的具体权限',
        related_name='custom_user_set'
    )
    
    def save(self, *args, **kwargs):
        """重写save方法,根据role自动设置权限"""
        if self.role == 'admin':
            self.is_staff = True      # 可以登录admin后台
            self.is_superuser = True  # 拥有所有权限
        super().save(*args, **kwargs)
    
    @property
    def is_admin(self):
        """判断是否为管理员"""
        return self.role == 'admin'
    
    def disable_account(self):
        """禁用账号"""
        self.is_active = False
        self.save()
    
    def enable_account(self):
        """启用账号"""
        self.is_active = True
        self.save()
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return f'{self.account}({self.get_role_display()})'