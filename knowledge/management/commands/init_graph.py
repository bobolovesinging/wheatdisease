from django.core.management.base import BaseCommand
from backend.graph_manager import GraphManager

class Command(BaseCommand):
    help = '初始化知识图谱数据'

    def handle(self, *args, **options):
        try:
            manager = GraphManager()
            manager.init_graph()
            self.stdout.write(self.style.SUCCESS('知识图谱初始化成功'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'初始化失败: {str(e)}')) 