"""
药品信息提取服务
从OCR识别结果中提取药品相关信息
"""

import re
import logging
from typing import Dict, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class DrugInfoExtractor:
    """药品信息提取类"""

    def __init__(self, config: Dict = None):
        """
        初始化药品信息提取器
        
        Args:
            config: 配置字典，包含药品关键词等
        """
        # 药品知识库 - 可根据需要扩展
        self.drug_keywords = {
            'drug_names': [
                '片', '胶囊', '颗粒', '丸', '口服液', '注射液', 
                '软膏', '滴眼液', '栓剂', '贴剂', '喷雾剂', '糖浆',
                '冲剂', '散剂', '膏剂', '酊剂', '洗剂', '搽剂'
            ],
            'usage_keywords': [
                '口服', '外用', '注射', '静脉滴注', '皮下注射', 
                '肌肉注射', '静脉注射', '舌下含服', '直肠给药',
                '阴道给药', '滴眼', '滴耳', '滴鼻', '吸入'
            ],
            'dosage_keywords': [
                '一次', '一日', '每次', '每日', '用量', '剂量',
                '成人', '儿童', '老人', '孕妇', '哺乳期'
            ],
            'side_effect_keywords': [
                '不良反应', '副作用', '可能引起', '注意事项',
                '常见不良反应', '偶见', '罕见', '严重不良反应'
            ],
            'contraindication_keywords': [
                '禁忌', '禁用', '禁止', '不宜', '慎用',
                '禁忌症', '绝对禁忌', '相对禁忌'
            ],
            'allergen_keywords': [
                '过敏', '过敏反应', '过敏者禁用', '过敏体质',
                '对本品过敏者', '过敏史'
            ],
            'storage_keywords': [
                '贮藏', '保存', '储存', '存放', '密封',
                '避光', '阴凉', '干燥', '冷藏', '冷冻'
            ],
            'manufacturer_keywords': [
                '生产厂家', '生产企业', '制造商', '制药',
                '有限公司', '股份有限公司', '制药厂'
            ]
        }
        
        # 合并配置中的关键词
        if config and 'drug_keywords' in config:
            for key, value in config['drug_keywords'].items():
                if key in self.drug_keywords:
                    self.drug_keywords[key].extend(value)

        logger.info("药品信息提取器初始化完成")

    def extract_drug_info(self, ocr_result: Dict) -> Dict:
        """
        从OCR结果中提取药品信息
        
        Args:
            ocr_result: OCR识别结果
            
        Returns:
            Dict: 提取的药品信息
        """
        if not ocr_result.get('success'):
            return {
                'error': 'OCR识别失败',
                'error_code': 'OCR_FAILED'
            }

        try:
            # 提取所有文本
            full_text = self._combine_text_blocks(ocr_result['text_blocks'])
            
            if not full_text.strip():
                return {
                    'error': '未识别到任何文字',
                    'error_code': 'NO_TEXT'
                }

            # 提取各类信息
            drug_info = {
                'drug_name': self._extract_drug_name(full_text),
                'usage': self._extract_usage(full_text),
                'dosage': self._extract_dosage(full_text),
                'side_effects': self._extract_side_effects(full_text),
                'contraindications': self._extract_contraindications(full_text),
                'allergens': self._extract_allergens(full_text),
                'storage': self._extract_storage(full_text),
                'manufacturer': self._extract_manufacturer(full_text),
                'expiry_date': self._extract_expiry_date(full_text),
                'batch_number': self._extract_batch_number(full_text),
                'raw_text': full_text,  # 返回原始文本用于调试
                'confidence': self._calculate_confidence(ocr_result)
            }

            logger.info(f"药品信息提取完成: {drug_info['drug_name']}")
            return drug_info

        except Exception as e:
            logger.error(f"药品信息提取异常: {str(e)}")
            return {
                'error': f'信息提取失败: {str(e)}',
                'error_code': 'EXTRACTION_ERROR'
            }

    def _combine_text_blocks(self, text_blocks: List[Dict]) -> str:
        """
        合并所有文本块
        
        Args:
            text_blocks: OCR识别的文本块列表
            
        Returns:
            str: 合并后的完整文本
        """
        if not text_blocks:
            return ""
        
        # 按位置排序文本块
        sorted_blocks = sorted(text_blocks, key=lambda x: (
            x.get('location', {}).get('top', 0),
            x.get('location', {}).get('left', 0)
        ))
        
        return ' '.join([block['words'] for block in sorted_blocks])

    def _extract_drug_name(self, text: str) -> str:
        """
        提取药品名称
        
        Args:
            text: 完整文本
            
        Returns:
            str: 药品名称
        """
        # 方法1: 查找药品名称常见后缀
        for suffix in self.drug_keywords['drug_names']:
            pattern = r'([\u4e00-\u9fa5a-zA-Z0-9]+' + re.escape(suffix) + ')'
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        # 方法2: 查找"通用名称"、"商品名称"等关键词
        name_patterns = [
            r'通用名称[：:]?\s*([^\s，。]+)',
            r'商品名称[：:]?\s*([^\s，。]+)',
            r'药品名称[：:]?\s*([^\s，。]+)',
            r'【([^】]*)】',
            r'品名[：:]?\s*([^\s，。]+)',
            r'名称[：:]?\s*([^\s，。]+)'
        ]

        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        # 方法3: 查找第一个可能的中文药品名
        chinese_pattern = r'([\u4e00-\u9fa5]{2,8}(?:片|胶囊|颗粒|丸|口服液|注射液|软膏|滴眼液))'
        match = re.search(chinese_pattern, text)
        if match:
            return match.group(1)

        return "未知药品"

    def _extract_usage(self, text: str) -> str:
        """
        提取用法
        
        Args:
            text: 完整文本
            
        Returns:
            str: 用法信息
        """
        usage_patterns = [
            r'用法[：:]?\s*([^。]+?)(?=用量|$|。)',
            r'服用方法[：:]?\s*([^。]+)',
            r'给药途径[：:]?\s*([^。]+)',
            r'(口服|外用|静脉注射|肌肉注射|皮下注射|舌下含服|直肠给药|阴道给药|滴眼|滴耳|滴鼻|吸入)'
        ]

        results = []
        for pattern in usage_patterns:
            matches = re.findall(pattern, text)
            if matches:
                results.extend(matches)

        return '；'.join(results) if results else ""

    def _extract_dosage(self, text: str) -> str:
        """
        提取用量
        
        Args:
            text: 完整文本
            
        Returns:
            str: 用量信息
        """
        dosage_patterns = [
            r'用量[：:]?\s*([^。]+)',
            r'剂量[：:]?\s*([^。]+)',
            r'一次\s*([0-9一二三四五六七八九十]+[～~\-]?[0-9一二三四五六七八九十]*[片粒支mg毫升g])',
            r'一日\s*([0-9一二三四五六七八九十]+[～~\-]?[0-9一二三四五六七八九十]*[次回])',
            r'每次\s*([0-9一二三四五六七八九十]+[～~\-]?[0-9一二三四五六七八九十]*[片粒支mg毫升g])',
            r'每日\s*([0-9一二三四五六七八九十]+[～~\-]?[0-9一二三四五六七八九十]*[次回])'
        ]

        results = []
        for pattern in dosage_patterns:
            matches = re.findall(pattern, text)
            if matches:
                results.extend(matches)

        return '；'.join(results) if results else ""

    def _extract_side_effects(self, text: str) -> str:
        """
        提取不良反应
        
        Args:
            text: 完整文本
            
        Returns:
            str: 不良反应信息
        """
        side_effect_patterns = [
            r'不良反应[：:]?\s*([^。]+?)(?=禁忌|注意事项|$)',
            r'副作用[：:]?\s*([^。]+)',
            r'常见不良反应[：:]?\s*([^。]+)',
            r'可能引起[：:]?\s*([^。]+)'
        ]

        for pattern in side_effect_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return ""

    def _extract_contraindications(self, text: str) -> str:
        """
        提取禁忌
        
        Args:
            text: 完整文本
            
        Returns:
            str: 禁忌信息
        """
        contraindication_patterns = [
            r'禁忌[：:]?\s*([^。]+?)(?=注意事项|$)',
            r'禁用[：:]?\s*([^。]+)',
            r'禁忌症[：:]?\s*([^。]+)',
            r'不宜[：:]?\s*([^。]+)',
            r'慎用[：:]?\s*([^。]+)'
        ]

        for pattern in contraindication_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return ""

    def _extract_allergens(self, text: str) -> str:
        """
        提取过敏源
        
        Args:
            text: 完整文本
            
        Returns:
            str: 过敏源信息
        """
        allergen_patterns = [
            r'过敏[：:]?\s*([^。]+)',
            r'过敏者[^。]+',
            r'对本品过敏者[^。]+',
            r'过敏体质[^。]+'
        ]

        for pattern in allergen_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return ""

    def _extract_storage(self, text: str) -> str:
        """
        提取贮藏信息
        
        Args:
            text: 完整文本
            
        Returns:
            str: 贮藏信息
        """
        storage_patterns = [
            r'贮藏[：:]?\s*([^。]+)',
            r'保存[：:]?\s*([^。]+)',
            r'储存[：:]?\s*([^。]+)',
            r'存放[：:]?\s*([^。]+)'
        ]

        for pattern in storage_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return ""

    def _extract_manufacturer(self, text: str) -> str:
        """
        提取生产厂家信息
        
        Args:
            text: 完整文本
            
        Returns:
            str: 生产厂家信息
        """
        manufacturer_patterns = [
            r'生产厂家[：:]?\s*([^。]+)',
            r'生产企业[：:]?\s*([^。]+)',
            r'制造商[：:]?\s*([^。]+)',
            r'([^。]*(?:有限公司|股份有限公司|制药厂|制药有限公司)[^。]*)'
        ]

        for pattern in manufacturer_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return ""

    def _extract_expiry_date(self, text: str) -> str:
        """
        提取有效期信息
        
        Args:
            text: 完整文本
            
        Returns:
            str: 有效期信息
        """
        expiry_patterns = [
            r'有效期[：:]?\s*([^。]+)',
            r'失效期[：:]?\s*([^。]+)',
            r'有效期至[：:]?\s*([^。]+)',
            r'失效日期[：:]?\s*([^。]+)'
        ]

        for pattern in expiry_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return ""

    def _extract_batch_number(self, text: str) -> str:
        """
        提取批号信息
        
        Args:
            text: 完整文本
            
        Returns:
            str: 批号信息
        """
        batch_patterns = [
            r'批号[：:]?\s*([^。]+)',
            r'生产批号[：:]?\s*([^。]+)',
            r'产品批号[：:]?\s*([^。]+)'
        ]

        for pattern in batch_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return ""

    def _calculate_confidence(self, ocr_result: Dict) -> float:
        """
        计算识别置信度
        
        Args:
            ocr_result: OCR识别结果
            
        Returns:
            float: 置信度 (0-1)
        """
        if not ocr_result.get('text_blocks'):
            return 0.0
        
        # 基于识别到的文字块数量和概率计算置信度
        text_blocks = ocr_result['text_blocks']
        total_confidence = 0.0
        valid_blocks = 0
        
        for block in text_blocks:
            if 'probability' in block and block['probability']:
                try:
                    confidence = float(block['probability']['average'])
                    total_confidence += confidence
                    valid_blocks += 1
                except (ValueError, KeyError):
                    continue
        
        if valid_blocks == 0:
            return 0.5  # 默认中等置信度
        
        return min(total_confidence / valid_blocks, 1.0)
