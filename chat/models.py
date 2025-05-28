from django.db import models
from users.models import User

class ChatMessage(models.Model):
    """
    聊天记录模型 ：暂未使用，用于后续扩展（比如需要做消息检索、统计、数据分析等）
    
    字段说明:
    - id: 主键
    - user: 关联的用户
    - message: 消息内容
    - role: 消息发送者角色（user/assistant）
    - created_at: 消息创建时间
    """
    ROLE_CHOICES = (
        ('user', '用户'),
        ('assistant', '助手'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name='用户'
    )
    message = models.TextField(verbose_name='消息内容')
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='消息角色'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = '聊天记录'
        verbose_name_plural = verbose_name
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.user.account} - {self.role} - {self.created_at}' 