"""
百度云OCR服务封装
专为药品识别优化的OCR服务
"""
import os
import requests
import base64
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from utils.logger import get_logger
from utils.logger import log_ocr_call

logger = get_logger(__name__)


class BaiduOCRService:
    """百度云OCR服务封装类"""

    def __init__(self, config: Dict):
        """
        初始化OCR服务

        Args:
            config: OCR配置字典，包含api_key, secret_key, token_url, ocr_url
        """
        self.api_key = config['api_key']
        self.secret_key = config['secret_key']
        self.token_url = config['token_url']
        self.ocr_url = config['ocr_url']

        # 全局变量存储access_token
        self._access_token = None
        self._token_expire_time = None

        logger.info("百度云OCR服务初始化完成")

    def get_access_token(self) -> Optional[str]:
        """
        获取百度云OCR的access_token

        Returns:
            str: access_token，失败返回None
        """
        # 检查token是否过期（百度云token有效期为30天）
        if (self._access_token and
                self._token_expire_time and
                datetime.now() < self._token_expire_time):
            return self._access_token

        try:
            # 请求获取access_token
            params = {
                'grant_type': 'client_credentials',
                'client_id': self.api_key,
                'client_secret': self.secret_key
            }

            response = requests.post(self.token_url, params=params, timeout=10)
            result = response.json()

            if 'access_token' in result:
                self._access_token = result['access_token']
                # 设置token过期时间（提前1小时刷新）
                self._token_expire_time = datetime.now() + timedelta(days=29, hours=23)
                logger.info("百度云OCR token获取成功")
                return self._access_token
            else:
                logger.error(f"获取百度云OCR token失败: {result}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"获取百度云OCR token网络异常: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取百度云OCR token异常: {str(e)}")
            return None

    @log_ocr_call
    def recognize_text(self, image_path: str, options: Dict = None, force_call: bool = False) -> Dict:
        """
        使用百度云OCR识别图片中的文字

        Args:
            image_path: 图片路径
            options: OCR识别选项
            force_call: 强制调用OCR（用于调试，忽略前置图像分析结果）
        """
        try:
            # ========== 新增：强制调用逻辑（调试用） ==========
            if force_call:
                logger.warning("⚠️ 已触发强制OCR调用（调试模式）")
            else:
                # 模拟图像分析结果（若实际流程中需依赖has_drug_info，需同步修改）
                logger.info("图像分析结果：假设has_drug_info为true，允许OCR调用")

            # 原有图片验证逻辑
            if not os.path.exists(image_path):
                logger.error(f"图片文件不存在: {image_path}")
                return {
                    'success': False,
                    'error': '图片文件不存在',
                    'error_code': 'FILE_NOT_FOUND'
                }

            file_size = os.path.getsize(image_path)
            logger.info(f"OCR处理图片: {image_path}, 大小: {file_size} 字节")

            if file_size == 0:
                logger.error("图片文件为空")
                return {
                    'success': False,
                    'error': '图片文件为空',
                    'error_code': 'EMPTY_FILE'
                }

            # 获取access_token
            access_token = self.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'error': '无法获取百度云OCR访问令牌',
                    'error_code': 'TOKEN_ERROR'
                }

            # 读取图片并转换为base64
            with open(image_path, 'rb') as f:
                image_data = f.read()

            image_base64 = base64.b64encode(image_data).decode('utf-8')
            logger.info(f"图片Base64编码完成，长度: {len(image_base64)} 字符")

            # 默认OCR参数
            default_options = {
                'language_type': 'CHN_ENG',  # 中英文混合
                'detect_direction': 'true',  # 检测图像朝向
                'paragraph': 'true',  # 输出段落信息
                'probability': 'true'  # 返回识别结果中每一行的置信度
            }

            if options:
                default_options.update(options)

            # 调用百度云OCR API
            ocr_url = f"{self.ocr_url}?access_token={access_token}"
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'image': image_base64,
                **default_options
            }

            response = requests.post(ocr_url, headers=headers, data=data, timeout=30)
            result = response.json()

            if 'words_result' in result:
                logger.info(f"百度云OCR识别成功，识别到{result.get('words_result_num', 0)}个文字块")
                # ========== 新增：记录调用详情到日志 ==========
                logger.info(f"百度OCR调用详情：{json.dumps(result, ensure_ascii=False)}")
                return {
                    'success': True,
                    'text_blocks': result['words_result'],
                    'words_result_num': result['words_result_num'],
                    'raw_result': result,
                    'token_info': self.get_token_info()  # 新增：返回token状态
                }
            else:
                error_msg = result.get('error_msg', 'OCR识别失败')
                error_code = result.get('error_code', 'UNKNOWN_ERROR')
                logger.error(f"百度云OCR识别失败: {error_msg} (代码: {error_code})")
                return {
                    'success': False,
                    'error': error_msg,
                    'error_code': error_code,
                    'raw_result': result  # 新增：返回原始错误
                }

        except FileNotFoundError:
            logger.error(f"图片文件不存在: {image_path}")
            return {
                'success': False,
                'error': '图片文件不存在',
                'error_code': 'FILE_NOT_FOUND'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"百度云OCR网络异常: {str(e)}")
            return {
                'success': False,
                'error': f'网络连接异常: {str(e)}',
                'error_code': 'NETWORK_ERROR'
            }
        except Exception as e:
            logger.error(f"百度云OCR识别异常: {str(e)}")
            return {
                'success': False,
                'error': f'OCR服务异常: {str(e)}',
                'error_code': 'SERVICE_ERROR'
            }

    @log_ocr_call
    def recognize_text_from_base64(self, image_base64: str, options: Dict = None) -> Dict:
        """
        从Base64图片数据识别文字

        Args:
            image_base64: Base64编码的图片数据
            options: OCR识别选项

        Returns:
            Dict: 识别结果
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'error': '无法获取百度云OCR访问令牌',
                    'error_code': 'TOKEN_ERROR'
                }

            # 默认OCR参数
            default_options = {
                'language_type': 'CHN_ENG',
                'detect_direction': 'true',
                'paragraph': 'true',
                'probability': 'true'
            }

            if options:
                default_options.update(options)

            # 调用百度云OCR API
            ocr_url = f"{self.ocr_url}?access_token={access_token}"
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'image': image_base64,
                **default_options
            }

            response = requests.post(ocr_url, headers=headers, data=data, timeout=30)
            result = response.json()

            if 'words_result' in result:
                logger.info(f"百度云OCR Base64识别成功，识别到{result.get('words_result_num', 0)}个文字块")
                return {
                    'success': True,
                    'text_blocks': result['words_result'],
                    'words_result_num': result['words_result_num'],
                    'raw_result': result
                }
            else:
                error_msg = result.get('error_msg', 'OCR识别失败')
                error_code = result.get('error_code', 'UNKNOWN_ERROR')
                logger.error(f"百度云OCR Base64识别失败: {error_msg} (代码: {error_code})")
                return {
                    'success': False,
                    'error': error_msg,
                    'error_code': error_code
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"百度云OCR Base64网络异常: {str(e)}")
            return {
                'success': False,
                'error': f'网络连接异常: {str(e)}',
                'error_code': 'NETWORK_ERROR'
            }
        except Exception as e:
            logger.error(f"百度云OCR Base64识别异常: {str(e)}")
            return {
                'success': False,
                'error': f'OCR服务异常: {str(e)}',
                'error_code': 'SERVICE_ERROR'
            }

    def is_token_valid(self) -> bool:
        """
        检查当前token是否有效

        Returns:
            bool: token是否有效
        """
        return (self._access_token is not None and
                self._token_expire_time is not None and
                datetime.now() < self._token_expire_time)

    def get_token_info(self) -> Dict:
        """
        获取token信息

        Returns:
            Dict: token信息
        """
        return {
            'has_token': self._access_token is not None,
            'is_valid': self.is_token_valid(),
            'expire_time': self._token_expire_time.isoformat() if self._token_expire_time else None
        }
