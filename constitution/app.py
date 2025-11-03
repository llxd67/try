"""
药品识别助手 - Flask应用主入口
专为视障人群优化的药品识别服务
"""

from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv('.env')

# 导入配置
try:
    from config import config
    print("✅ 使用config.py配置文件")
except ImportError:
    print("⚠️  config.py未找到，使用默认配置")
    # 创建默认配置
    class DefaultConfig:
        BAIDU_API_KEY = os.getenv('BAIDU_API_KEY')
        BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY')
        BAIDU_TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'
        BAIDU_OCR_URL = 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic'

        @property
        def baidu_ocr_config(self):
            return {
                'api_key': self.BAIDU_API_KEY,
                'secret_key': self.BAIDU_SECRET_KEY,
                'token_url': self.BAIDU_TOKEN_URL,
                'ocr_url': self.BAIDU_OCR_URL
            }

    config = DefaultConfig()

# 导入服务
from services.ocr_service import BaiduOCRService
from services.drug_extractor import DrugInfoExtractor
from services.image_processor import ImageProcessor
from utils.logger import setup_logger

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置应用
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = 'tmp'

# 设置日志
logger = setup_logger('app', 'INFO')

# 初始化服务
ocr_service = BaiduOCRService(config.baidu_ocr_config)
drug_extractor = DrugInfoExtractor()
image_processor = ImageProcessor()


# 注册API路由
from api.routes import api_bp
app.register_blueprint(api_bp)


# 应用初始化函数
def initialize_app():
    """应用初始化"""
    logger.info("药品识别助手启动")
    logger.info(f"配置信息: OCR服务已配置, 图像处理已配置")

    # 确保临时目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logger.info(f"临时目录已创建: {app.config['UPLOAD_FOLDER']}")


if __name__ == '__main__':
    """启动应用"""
    # app.run(host='0.0.0.0', port=5000, debug=True)
    try:
        # 在启动前进行初始化
        initialize_app()
        
        logger.info("正在启动药品识别助手...")
        app.run(
            host=config.HOST if hasattr(config, 'HOST') else '0.0.0.0',
            port=config.PORT if hasattr(config, 'PORT') else 5000,
            debug=config.DEBUG if hasattr(config, 'DEBUG') else False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")
        raise