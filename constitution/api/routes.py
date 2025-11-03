"""
药品识别API路由
专为视障人群优化的药品识别服务
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from datetime import datetime
import os
import cv2
import numpy as np
from dotenv import load_dotenv  # 新增：加载.env文件

# 导入服务层
from services.ocr_service import BaiduOCRService
from services.drug_extractor import DrugInfoExtractor
from services.image_processor import ImageProcessor
from utils.logger import get_logger, log_api_call  # 新增：日志装饰器

# 加载.env文件（优先加载项目根目录的.env）
load_dotenv()

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 初始化服务（从环境变量读取密钥，移除硬编码）
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

ocr_service = BaiduOCRService(config.baidu_ocr_config)
drug_extractor = DrugInfoExtractor()
image_processor = ImageProcessor()
logger = get_logger(__name__)


@api_bp.route('/health', methods=['GET'])
@cross_origin()
@log_api_call  # 新增：API调用日志装饰器
def health_check():
    """健康检查接口"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'Drug Recognition API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'features': {
                'ocr': 'enabled',
                'drug_extraction': 'enabled',
                'image_processing': 'enabled',
                'light_detection': 'enabled'
            }
        })
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '服务异常'
        }), 500


@api_bp.route('/analyze-image', methods=['POST'])
@cross_origin()
@log_api_call
def analyze_image():
    """
    图像分析接口 - 检测光线和内容质量
    为视障用户提供拍照指导
    """
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传图片文件',
                'error_code': 'NO_IMAGE'
            }), 400

        image_file = request.files['image']

        # 保存临时文件
        temp_image_path = image_processor.save_temp_image(image_file)
        if not temp_image_path:
            return jsonify({
                'success': False,
                'error': '图片保存失败',
                'error_code': 'SAVE_FAILED'
            }), 500

        try:
            # 1. 光线检测
            light_analysis = analyze_lighting(temp_image_path)

            # 2. 图像质量检测
            quality_analysis = analyze_image_quality(temp_image_path)

            # 3. 内容预检测（快速OCR）
            content_analysis = quick_content_analysis(temp_image_path)

            # 4. 生成拍照指导
            guidance = generate_photo_guidance(light_analysis, quality_analysis, content_analysis)

            return jsonify({
                'success': True,
                'analysis': {
                    'lighting': light_analysis,
                    'quality': quality_analysis,
                    'content': content_analysis,
                    'guidance': guidance
                }
            })

        finally:
            # 清理临时文件
            image_processor.cleanup_temp_files(temp_image_path)

    except Exception as e:
        logger.error(f"图像分析异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'图像分析失败: {str(e)}',
            'error_code': 'ANALYSIS_ERROR'
        }), 500


@api_bp.route('/recognize', methods=['POST'])
@cross_origin()
@log_api_call
def recognize_drug():
    """
    药品识别主接口
    支持图片上传和药品信息提取
    专为视障人群优化，包含语音播报指导
    """
    logger.info("收到药品识别请求")
    logger.info(f"请求方法: {request.method}")
    logger.info(f"请求头: {dict(request.headers)}")
    logger.info(f"请求文件: {list(request.files.keys())}")

    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            logger.error("请求中没有图片文件")
            return jsonify({
                'success': False,
                'error': '没有上传图片文件',
                'error_code': 'NO_IMAGE',
                'voice_guidance': '请重新拍照'
            }), 400

        image_file = request.files['image']
        logger.info(f"收到图片文件: {image_file.filename}")

        # 验证文件
        if not image_file.filename:
            logger.error("文件名为空")
            return jsonify({
                'success': False,
                'error': '文件名为空',
                'error_code': 'EMPTY_FILENAME',
                'voice_guidance': '请重新拍照'
            }), 400

        # 检查文件格式
        allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp'}
        file_ext = image_file.filename.lower().split('.')[-1] if '.' in image_file.filename else ''
        if file_ext not in allowed_extensions:
            logger.error(f"不支持的文件格式: {file_ext}")
            return jsonify({
                'success': False,
                'error': f'不支持的文件格式: {file_ext}，支持格式: {", ".join(allowed_extensions)}',
                'error_code': 'INVALID_FORMAT',
                'voice_guidance': '请使用正确的图片格式'
            }), 400

        # 保存临时文件
        temp_image_path = image_processor.save_temp_image(image_file)
        if not temp_image_path:
            return jsonify({
                'success': False,
                'error': '图片保存失败',
                'error_code': 'SAVE_FAILED',
                'voice_guidance': '拍照失败，请重试'
            }), 500

        logger.info(f"图片保存成功: {temp_image_path}")
        logger.info(f"文件存在: {os.path.exists(temp_image_path)}")
        logger.info(f"文件大小: {os.path.getsize(temp_image_path)} 字节")

        try:
            # 1. 图像预处理
            processed_image_path = image_processor.preprocess_image(temp_image_path)
            logger.info("图像预处理完成")

            # 2. OCR文字识别（强制调用，忽略前置内容检测）
            logger.info("开始OCR识别...")
            ocr_result = ocr_service.recognize_text(processed_image_path, force_call=True)

            if not ocr_result.get('success'):
                logger.error(f"OCR识别失败: {ocr_result.get('error')}，错误码: {ocr_result.get('error_code')}")
                return jsonify({
                    'success': False,
                    'error': ocr_result.get('error', 'OCR识别失败'),
                    'error_code': ocr_result.get('error_code', 'OCR_FAILED'),
                    'voice_guidance': '识别失败，请重试'
                }), 500

            # 3. 药品信息提取
            drug_info = drug_extractor.extract_drug_info(ocr_result)

            # 4. 验证药品信息完整性
            validation_result = validate_drug_info(drug_info)

            # 5. 构建响应
            response_data = {
                'success': True,
                'drug_info': drug_info,
                'ocr_confidence': ocr_result.get('words_result_num', 0),
                'processing_time': datetime.now().isoformat(),
                'image_processed': processed_image_path != temp_image_path,
                'validation': validation_result,
                'voice_guidance': generate_voice_guidance(drug_info, validation_result),
                'raw_ocr_result': ocr_result.get('raw_result')  # 新增：返回OCR原始结果
            }

            logger.info(f"药品识别成功: {drug_info.get('drug_name', '未知药品')}")
            return jsonify(response_data)

        finally:
            # 清理临时文件
            image_processor.cleanup_temp_files(temp_image_path, processed_image_path)

    except Exception as e:
        logger.error(f"药品识别异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}',
            'error_code': 'INTERNAL_ERROR',
            'voice_guidance': '识别出错，请重试'
        }), 500


@api_bp.route('/recognize/base64', methods=['POST'])
@cross_origin()
@log_api_call
def recognize_drug_base64():
    """
    支持Base64图片的药品识别接口
    适用于微信小程序等场景
    """
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': '缺少图片数据',
                'error_code': 'NO_IMAGE_DATA'
            }), 400

        # 处理Base64图片
        temp_image_path = image_processor.save_base64_image(data['image'])
        if not temp_image_path:
            return jsonify({
                'success': False,
                'error': '图片数据无效',
                'error_code': 'INVALID_IMAGE_DATA'
            }), 400

        try:
            # 图像预处理
            processed_image_path = image_processor.preprocess_image(temp_image_path)

            # OCR识别（强制调用）
            ocr_result = ocr_service.recognize_text(processed_image_path, force_call=True)

            if not ocr_result.get('success'):
                return jsonify({
                    'success': False,
                    'error': ocr_result.get('error', 'OCR识别失败'),
                    'error_code': 'OCR_FAILED'
                }), 500

            # 药品信息提取
            drug_info = drug_extractor.extract_drug_info(ocr_result)

            return jsonify({
                'success': True,
                'drug_info': drug_info,
                'ocr_confidence': ocr_result.get('words_result_num', 0),
                'processing_time': datetime.now().isoformat(),
                'raw_ocr_result': ocr_result.get('raw_result')
            })

        finally:
            # 清理临时文件
            image_processor.cleanup_temp_files(temp_image_path, processed_image_path)

    except Exception as e:
        logger.error(f"Base64药品识别异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}',
            'error_code': 'INTERNAL_ERROR'
        }), 500


def analyze_lighting(image_path: str) -> dict:
    """
    分析图像光线条件

    Args:
        image_path: 图片路径

    Returns:
        dict: 光线分析结果
    """
    try:
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            return {'status': 'error', 'message': '无法读取图片'}

        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 计算平均亮度
        mean_brightness = np.mean(gray)

        # 计算亮度标准差（对比度）
        brightness_std = np.std(gray)

        # 判断光线条件
        if mean_brightness < 80:
            light_condition = 'dark'
            message = '当前光线不足，三秒后自动开启闪光灯，请注意保护眼睛'
            need_flash = True
        elif mean_brightness < 120:
            light_condition = 'dim'
            message = '光线较暗，建议调整角度或开启闪光灯'
            need_flash = False
        elif mean_brightness > 200:
            light_condition = 'bright'
            message = '光线充足，可以开始拍照'
            need_flash = False
        else:
            light_condition = 'good'
            message = '光线条件良好，可以开始拍照'
            need_flash = False

        return {
            'status': 'success',
            'light_condition': light_condition,
            'brightness': float(mean_brightness),
            'contrast': float(brightness_std),
            'message': message,
            'need_flash': need_flash
        }

    except Exception as e:
        logger.error(f"光线分析失败: {str(e)}")
        return {'status': 'error', 'message': f'光线分析失败: {str(e)}'}


def analyze_image_quality(image_path: str) -> dict:
    """
    分析图像质量

    Args:
        image_path: 图片路径

    Returns:
        dict: 图像质量分析结果
    """
    try:
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            return {'status': 'error', 'message': '无法读取图片'}

        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 计算拉普拉斯方差（清晰度）
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # 计算图像尺寸
        height, width = gray.shape
        total_pixels = height * width

        # 判断图像质量
        if laplacian_var < 100:
            quality = 'blurry'
            message = '图像模糊，请保持稳定重新拍照'
        elif laplacian_var < 200:
            quality = 'fair'
            message = '图像质量一般，建议重新拍照'
        elif total_pixels < 100000:  # 小于100万像素
            quality = 'low_resolution'
            message = '图像分辨率较低，请靠近药品标签拍照'
        else:
            quality = 'good'
            message = '图像质量良好'

        return {
            'status': 'success',
            'quality': quality,
            'sharpness': float(laplacian_var),
            'resolution': total_pixels,
            'message': message
        }

    except Exception as e:
        logger.error(f"图像质量分析失败: {str(e)}")
        return {'status': 'error', 'message': f'图像质量分析失败: {str(e)}'}


def quick_content_analysis(image_path: str) -> dict:
    """
    快速内容分析 - 检测是否包含药品信息

    Args:
        image_path: 图片路径

    Returns:
        dict: 内容分析结果
    """
    try:
        # 使用快速OCR进行内容检测
        ocr_result = ocr_service.recognize_text(image_path, force_call=True)  # 强制调用OCR
        
        if not ocr_result.get('success'):
            return {
                'status': 'error',
                'message': '无法识别图片内容',
                'has_drug_info': False
            }
        
        # 提取文本
        text_blocks = ocr_result.get('text_blocks', [])
        full_text = ' '.join([block['words'] for block in text_blocks])
        
        # 检测药品关键词
        drug_keywords = ['片', '胶囊', '颗粒', '丸', '口服液', '注射液', '用法', '用量', '有效期', '生产日期']
        found_keywords = [keyword for keyword in drug_keywords if keyword in full_text]
        
        # 检测关键信息
        has_drug_name = any(keyword in full_text for keyword in ['片', '胶囊', '颗粒', '丸', '口服液', '注射液'])
        has_usage = any(keyword in full_text for keyword in ['用法', '服用', '口服', '外用'])
        has_dosage = any(keyword in full_text for keyword in ['用量', '剂量', '一次', '一日'])
        has_expiry = any(keyword in full_text for keyword in ['有效期', '失效期', '生产日期'])
        
        # 判断是否包含药品信息
        has_drug_info = has_drug_name and (has_usage or has_dosage)
        
        if has_drug_info:
            message = '检测到药品信息，开始识别，保持不动'
        else:
            message = '未检测到药品信息，请对准药品标签重新拍照'
        
        return {
            'status': 'success',
            'has_drug_info': has_drug_info,
            'found_keywords': found_keywords,
            'has_drug_name': has_drug_name,
            'has_usage': has_usage,
            'has_dosage': has_dosage,
            'has_expiry': has_expiry,
            'message': message,
            'text_length': len(full_text)
        }
        
    except Exception as e:
        logger.error(f"内容分析失败: {str(e)}")
        return {
            'status': 'error',
            'message': f'内容分析失败: {str(e)}',
            'has_drug_info': False
        }


def validate_drug_info(drug_info: dict) -> dict:
    """
    验证药品信息完整性
    专为视障人群设计，确保包含必要信息
    
    Args:
        drug_info: 药品信息字典
        
    Returns:
        dict: 验证结果
    """
    required_fields = {
        'drug_name': '药品名称',
        'dosage': '用法用量', 
        'usage': '使用方法',
        'manufacturer': '生产厂家'
    }
    
    missing_fields = []
    present_fields = []
    
    for field, field_name in required_fields.items():
        if drug_info.get(field) and drug_info[field].strip():
            present_fields.append(field_name)
        else:
            missing_fields.append(field_name)
    
    # 计算完整性评分
    completeness_score = len(present_fields) / len(required_fields) * 100
    
    # 判断是否需要重新拍照
    need_retake = completeness_score < 50  # 低于50%需要重拍
    
    return {
        'completeness_score': completeness_score,
        'present_fields': present_fields,
        'missing_fields': missing_fields,
        'need_retake': need_retake,
        'is_complete': completeness_score >= 75  # 75%以上认为完整
    }


def generate_voice_guidance(drug_info: dict, validation_result: dict) -> str:
    """
    生成语音播报指导
    
    Args:
        drug_info: 药品信息
        validation_result: 验证结果
        
    Returns:
        str: 语音播报内容
    """
    if validation_result['need_retake']:
        missing_fields = validation_result['missing_fields']
        if len(missing_fields) >= 3:
            return "请变换药品另一个面，当前面信息不完整"
        elif '药品名称' in missing_fields:
            return "请对准药品名称部分重新拍照"
        elif '用法用量' in missing_fields:
            return "请对准用法用量部分重新拍照"
        else:
            return "请调整角度重新拍照"
    
    # 信息完整，播报药品信息
    voice_text = ""
    
    if drug_info.get('drug_name'):
        voice_text += f"药品名称：{drug_info['drug_name']}。"
    
    if drug_info.get('dosage'):
        voice_text += f"用法用量：{drug_info['dosage']}。"
    
    if drug_info.get('usage'):
        voice_text += f"使用方法：{drug_info['usage']}。"
    
    if drug_info.get('manufacturer'):
        voice_text += f"生产厂家：{drug_info['manufacturer']}。"
    
    if drug_info.get('expiry_date'):
        voice_text += f"有效期：{drug_info['expiry_date']}。"
    
    return voice_text if voice_text else "识别完成，但信息不完整"


def generate_photo_guidance(light_analysis: dict, quality_analysis: dict, content_analysis: dict) -> dict:
    """
    生成拍照指导
    
    Args:
        light_analysis: 光线分析结果
        quality_analysis: 图像质量分析结果
        content_analysis: 内容分析结果
        
    Returns:
        dict: 拍照指导
    """
    guidance = {
        'action': 'continue',  # continue, retake, flash
        'message': '',
        'voice_guidance': '',
        'wait_time': 0
    }
    
    # 光线不足，需要闪光灯
    if light_analysis.get('need_flash'):
        guidance.update({
            'action': 'flash',
            'message': light_analysis.get('message', ''),
            'voice_guidance': '当前光线不足，三秒后自动开启闪光灯，请注意保护眼睛',
            'wait_time': 3
        })
        return guidance
    
    # 图像质量不好，需要重拍
    if quality_analysis.get('quality') in ['blurry', 'low_resolution']:
        guidance.update({
            'action': 'retake',
            'message': quality_analysis.get('message', ''),
            'voice_guidance': quality_analysis.get('message', ''),
            'wait_time': 0
        })
        return guidance
    
    # 没有检测到药品信息
    if not content_analysis.get('has_drug_info'):
        guidance.update({
            'action': 'retake',
            'message': content_analysis.get('message', ''),
            'voice_guidance': content_analysis.get('message', ''),
            'wait_time': 0
        })
        return guidance
    
    # 一切正常，可以识别
    guidance.update({
        'action': 'continue',
        'message': '图像质量良好，开始识别',
        'voice_guidance': '开始识别，请保持不动',
        'wait_time': 0
    })
    
    return guidance


@api_bp.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({
        'success': False,
        'error': '文件过大，请上传小于16MB的图片',
        'error_code': 'FILE_TOO_LARGE'
    }), 413


@api_bp.errorhandler(400)
def bad_request(e):
    """请求错误处理"""
    return jsonify({
        'success': False,
        'error': '请求参数错误',
        'error_code': 'BAD_REQUEST'
    }), 400