"""
工具函数模块

提供各种辅助功能，包括：
- 关键词管理
- 文本处理
"""

import logging
from typing import Dict, List, Set, Optional, Union

logger = logging.getLogger(__name__)

class KeywordManager:
    """关键词管理器：统一管理所有关键词和提取逻辑"""
    
    def __init__(self):
        """初始化关键词管理器"""
        # 定义标准关键词集
        self.plant_part_keywords = {
            "叶片", "茎秆", "根系", "麦穗", "叶鞘", "籽粒", "幼苗", "基部", "穗部",
            "节间", "叶尖", "叶缘", "叶面", "叶背", "茎基", "茎部", "穗轴", "颖壳",
            "护颖", "芒", "根冠", "根毛", "分蘖", "主茎", "种子", "胚芽", "胚根",
            "叶基", "茎节", "穗颈", "颖片", "子房", "花药", "花丝", "胚乳", "胚部"
        }
        
        self.weather_keywords = {
            # 温度相关
            "高温", "低温", "寒潮", "倒春寒", "热浪", "冷凉", "温暖",
            # 降水相关
            "干旱", "潮湿", "阴雨", "连阴雨", "梅雨", "暴雨", "降雨", "多雨",
            # 湿度相关
            "干燥", "湿润", "高湿", "低湿",
            # 其他气象条件
            "大风", "霜冻", "积雪", "冰雹", "沙尘", "阴天", "晴天",
            # 复合条件
            "高温高湿", "低温多雨", "干旱高温"
        }
        
        self.growth_stage_keywords = {
            "全生育期", "生长全期", "全生长期", "苗期", "幼苗期", "出苗期", 
            "3-4叶期", "4-6叶期", "越冬期", "冬前", "返青期", "拔节期", 
            "分蘖期", "茎节期", "起身期", "抽穗期", "孕穗期", "开花期", 
            "扬花期", "灌浆期", "乳熟期", "成熟期", "收获期", "播种期",
            "发芽期", "生育中期", "生育后期", "抽穗扬花期", "成株期"
        }
        
        self.region_keywords = {
            "黑龙江", "吉林", "辽宁", "河北", "山西", "山东", "河南", "江苏", "浙江",
            "安徽", "江西", "福建", "广东", "广西", "海南", "湖北", "湖南", "四川",
            "贵州", "云南", "陕西", "甘肃", "青海", "台湾", "北京", "天津", "上海", 
            "重庆", "内蒙古", "新疆", "西藏", "宁夏", "东北", "华北", "华东", "华南", 
            "华中", "西北", "西南", "东北平原区", "云贵高原区", "北方干旱半干旱区", 
            "华南区", "四川盆地区", "长江中下游区", "青藏高原区", "黄土高原区", 
            "黄淮海平原区", "全国各地", "南方", "北方", "西部", "东部"
        }
        
        # 定义关键词映射关系
        self.mappings = {
            'plant_part': {
                "叶": "叶片",
                "茎": "茎秆",
                "根": "根系",
                "穗": "麦穗",
                "颖": "颖壳",
                "芽": "胚芽",
                "胚": "胚部",
                "花": "花药",
                "心叶": "叶片",
                "老叶": "叶片",
                "基部叶片": "叶片",
                "上部叶片": "叶片",
                "新叶": "叶片",
                "旗叶": "叶片",
                "叶尖": "叶片",
                "叶基": "叶片",
                "叶鞘": "叶鞘",
                "茎基": "茎秆",
                "茎部": "茎秆",
                "秆": "茎秆",
                "节间": "茎秆",
                "茎节": "茎秆",
                "基部": "茎秆",
                "根冠": "根系",
                "根毛": "根系",
                "幼根": "根系",
                "种子根": "根系",
                "穗部": "麦穗",
                "穗轴": "麦穗",
                "小穗": "麦穗",
                "穗颈": "麦穗",
                "颖壳": "颖壳",
                "护颖": "颖壳",
                "颖片": "颖壳",
                "胚芽鞘": "胚芽",
                "幼芽": "胚芽",
                "子房": "胚部",
                "胚根": "胚部",
                "胚乳": "胚部",
                "花丝": "花药",
                "花器": "花药"
            },
            'weather': {
                "温度高": "高温",
                "气温高": "高温",
                "温度低": "低温",
                "气温低": "低温",
                "降水": "降雨",
                "下雨": "降雨",
                "雨天": "阴雨",
                "干燥": "干旱",
                "湿润": "潮湿",
                "高温干旱": ["高温", "干旱"],
                "低温阴雨": ["低温", "阴雨"]
            },
            'growth_stage': {
                "开花": "开花期",
                "抽穗": "抽穗期",
                "返青": "返青期",
                "成熟": "成熟期",
                "播种": "播种期",
                "发芽": "发芽期",
                "越冬": "越冬期",
                "拔节": "拔节期",
                "分蘖": "分蘖期",
                "灌浆": "灌浆期",
                "收获": "收获期",
                "出苗": "出苗期",
                "幼苗": "幼苗期",
                "孕穗": "孕穗期",
                "扬花": "扬花期",
                "生育中": "生育中期",
                "生育后": "生育后期",
                "全生育": "全生育期",
                "生长全": "全生育期",
                "初期": "苗期",
                "前期": "苗期",
                "中期": "生育中期",
                "后期": "生育后期",
                "末期": "成熟期",
                "抽穗开花": "抽穗期",
                "抽穗扬花": "抽穗期",
                "灌浆成熟": "灌浆期"
            }
        }
    
    def extract_symptoms(self, text: str) -> Dict[str, Union[str, List[str]]]:
        """
        从文本中提取症状信息
        
        Args:
            text (str): 输入文本
            
        Returns:
            Dict[str, Union[str, List[str]]]: 提取的症状信息
        """
        if not text:
            return {}
            
        # 清理文本
        text = self._clean_text(text)
        
        # 初始化结果
        symptoms = {
            'plant_part': set(),
            'weather': set(),
            'growth_stage': set(),
            'region': set()
        }
        
        # 分句处理
        sentences = []
        sentences.extend(text.split('，'))
        sentences.extend(text.split('。'))
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 提取所有症状
        for sentence in sentences:
            # 提取各类信息
            plant_parts = self._extract_keywords(sentence, self.plant_part_keywords, self.mappings['plant_part'])
            symptoms['plant_part'].update(plant_parts)
            
            weather_conditions = self._extract_keywords(sentence, self.weather_keywords, self.mappings['weather'])
            symptoms['weather'].update(weather_conditions)
            
            growth_stages = self._extract_keywords(sentence, self.growth_stage_keywords, self.mappings['growth_stage'])
            symptoms['growth_stage'].update(growth_stages)
            
            regions = self._extract_keywords(sentence, self.region_keywords)
            symptoms['region'].update(regions)
        
        # 将集合转换为列表
        result = {}
        for category, values in symptoms.items():
            if values:
                result[category] = list(values)[0] if len(values) == 1 else list(values)
        
        return result
    
    def _extract_keywords(self, text: str, keyword_set: Set[str], mapping: Optional[Dict] = None) -> Set[str]:
        """
        从文本中提取关键词
        
        Args:
            text (str): 输入文本
            keyword_set (Set[str]): 关键词集合
            mapping (Optional[Dict]): 关键词映射字典
            
        Returns:
            Set[str]: 提取的关键词集合
        """
        if not text:
            return set()
            
        found_keywords = set()
        
        # 遍历关键词集合
        for keyword in keyword_set:
            if keyword in text:
                # 如果存在映射，使用映射后的关键词
                if mapping and keyword in mapping:
                    mapped_value = mapping[keyword]
                    if isinstance(mapped_value, list):
                        found_keywords.update(mapped_value)
                    else:
                        found_keywords.add(mapped_value)
                else:
                    found_keywords.add(keyword)
        
        return found_keywords
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text (str): 输入文本
            
        Returns:
            str: 清理后的文本
        """
        if not text:
            return ""
            
        # 移除多余空白字符
        text = ' '.join(text.split())
        
        # 统一标点符号
        text = text.replace('，', '，').replace('。', '。')
        
        return text

# 创建全局关键词管理器实例
keyword_manager = KeywordManager() 