"""
药品识别小程序 - 配置文件
专为视障人群优化的自动拍摄识别配置
"""

import os
from datetime import timedelta

class Config:
    """
    应用配置类
    针对自动拍摄场景和视障用户优化
    """
    
    # ==================== 应用信息 ====================
    APP_NAME = "药品识别助手-视障版"
    APP_VERSION = "1.0.0"
    
    # ==================== 服务器配置 ====================
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # ==================== 百度云OCR配置 ====================
    # 【必须修改】填写你的百度云OCR密钥
    BAIDU_API_KEY = os.getenv('BAIDU_API_KEY', 'qLXk73B8ErRa9QuslGZCpSRl')
    BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY', 'WU1UYgSrYkFbgCV2io1BBX4SfTW8mu5f')
    BAIDU_TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'
    BAIDU_OCR_URL = 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic'
    
    # OCR参数（适配你现有的代码）
    OCR_LANGUAGE_TYPE = 'CHN_ENG'
    OCR_DETECT_DIRECTION = True
    OCR_PARAGRAPH = True
    OCR_PROBABILITY = True
    
    # ==================== 图像处理配置 ====================
    # 针对自动拍摄优化
    MAX_IMAGE_WIDTH = 1600               # 降低分辨率提高速度
    MAX_IMAGE_HEIGHT = 1600
    CLAHE_CLIP_LIMIT = 3.0               # 增强对比度适应不同光线
    CLAHE_TILE_SIZE = (8, 8)
    
    # ==================== 文件处理配置 ====================
    UPLOAD_FOLDER = 'tmp'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # ==================== 性能配置 ====================
    OCR_TIMEOUT = 30
    MAX_RETRY_COUNT = 3
    REQUEST_TIMEOUT = 10
    
    # ==================== 日志配置 ====================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # ==================== 药品识别优化 ====================
    # 扩展药品关键词（已在你的DrugInfoExtractor中使用）
    DRUG_NAME_KEYWORDS = [
        '片', '胶囊', '颗粒', '丸', '口服液', '注射液', 
        '软膏', '滴眼液', '栓剂', '贴剂', '喷雾剂', '糖浆'
    ]
    
    # ==================== 环境配置 ====================
    
    @property
    def baidu_ocr_config(self):
        """返回百度云OCR配置字典（适配你现有的代码结构）"""
        return {
            'api_key': self.BAIDU_API_KEY,
            'secret_key': self.BAIDU_SECRET_KEY,
            'token_url': self.BAIDU_TOKEN_URL,
            'ocr_url': self.BAIDU_OCR_URL
        }

# 创建全局配置实例
config = Config()