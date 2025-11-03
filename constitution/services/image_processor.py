"""
图像处理服务
负责图像预处理、保存和清理
"""

import cv2
import numpy as np
import os
import base64
import logging
from datetime import datetime
from typing import Optional, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)


class ImageProcessor:
    """图像处理服务类"""

    def __init__(self, config: dict = None):
        """
        初始化图像处理器
        
        Args:
            config: 配置字典，包含图像处理参数
        """
        # 默认配置
        self.config = {
            'max_width': 1600,
            'max_height': 1600,
            'clahe_clip_limit': 3.0,
            'clahe_tile_size': (8, 8),
            'upload_folder': 'tmp',
            'max_file_size': 16 * 1024 * 1024,  # 16MB
            'allowed_extensions': {'.png', '.jpg', '.jpeg', '.bmp'}
        }
        
        # 合并用户配置
        if config:
            self.config.update(config)
        
        # 确保上传目录存在
        self._ensure_upload_folder()
        
        logger.info("图像处理器初始化完成")

    def _ensure_upload_folder(self):
        """确保上传目录存在"""
        upload_folder = self.config['upload_folder']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            logger.info(f"创建上传目录: {upload_folder}")

    def save_temp_image(self, image_file, prefix: str = "temp") -> Optional[str]:
        """
        保存临时图片文件
        
        Args:
            image_file: 上传的图片文件
            prefix: 文件名前缀
            
        Returns:
            str: 保存的文件路径，失败返回None
        """
        try:
            # 检查文件大小
            if hasattr(image_file, 'content_length'):
                if image_file.content_length > self.config['max_file_size']:
                    logger.warning(f"文件过大: {image_file.content_length} bytes")
                    return None

            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{prefix}_{timestamp}.jpg"
            file_path = os.path.join(self.config['upload_folder'], filename)

            # 保存文件
            image_file.save(file_path)
            
            # 验证文件是否保存成功
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                logger.info(f"图片保存成功: {file_path}")
                return file_path
            else:
                logger.error(f"图片保存失败: {file_path}")
                return None

        except Exception as e:
            logger.error(f"保存图片异常: {str(e)}")
            return None

    def save_base64_image(self, image_base64: str, prefix: str = "base64") -> Optional[str]:
        """
        保存Base64图片数据
        
        Args:
            image_base64: Base64编码的图片数据
            prefix: 文件名前缀
            
        Returns:
            str: 保存的文件路径，失败返回None
        """
        try:
            # 移除data:image前缀（如果存在）
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]

            # 解码Base64数据
            image_data = base64.b64decode(image_base64)
            
            # 检查文件大小
            if len(image_data) > self.config['max_file_size']:
                logger.warning(f"Base64图片过大: {len(image_data)} bytes")
                return None

            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{prefix}_{timestamp}.jpg"
            file_path = os.path.join(self.config['upload_folder'], filename)

            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(image_data)

            # 验证文件是否保存成功
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                logger.info(f"Base64图片保存成功: {file_path}")
                return file_path
            else:
                logger.error(f"Base64图片保存失败: {file_path}")
                return None

        except Exception as e:
            logger.error(f"保存Base64图片异常: {str(e)}")
            return None

    def preprocess_image(self, image_path: str) -> str:
        """
        图像预处理函数
        
        Args:
            image_path: 原始图片路径
            
        Returns:
            str: 处理后的图片路径
        """
        try:
            # 读取图片
            img = cv2.imread(image_path)
            if img is None:
                logger.warning(f"无法读取图片: {image_path}")
                return image_path

            original_height, original_width = img.shape[:2]
            logger.info(f"原始图片尺寸: {original_width}x{original_height}")

            # 1. 调整图像大小（如果太大）
            img = self._resize_image(img)
            
            # 2. 转换为灰度图
            gray = self._convert_to_grayscale(img)
            
            # 3. 图像增强 - 对比度增强
            enhanced = self._enhance_contrast(gray)
            
            # 4. 降噪
            denoised = self._denoise_image(enhanced)
            
            # 5. 锐化（可选）
            sharpened = self._sharpen_image(denoised)

            # 保存处理后的图片
            processed_path = self._get_processed_path(image_path)
            success = cv2.imwrite(processed_path, sharpened)

            if success:
                logger.info(f"图像预处理完成: {processed_path}")
                return processed_path
            else:
                logger.error(f"保存处理后的图片失败: {processed_path}")
                return image_path

        except Exception as e:
            logger.error(f"图像预处理失败: {str(e)}")
            return image_path  # 返回原图

    def _resize_image(self, img: np.ndarray) -> np.ndarray:
        """
        调整图像大小
        
        Args:
            img: 输入图像
            
        Returns:
            np.ndarray: 调整后的图像
        """
        height, width = img.shape[:2]
        max_width = self.config['max_width']
        max_height = self.config['max_height']

        if width > max_width or height > max_height:
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            logger.info(f"图像缩放: {width}x{height} -> {new_width}x{new_height}")

        return img

    def _convert_to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """
        转换为灰度图
        
        Args:
            img: 输入图像
            
        Returns:
            np.ndarray: 灰度图像
        """
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        return gray

    def _enhance_contrast(self, gray: np.ndarray) -> np.ndarray:
        """
        增强对比度
        
        Args:
            gray: 灰度图像
            
        Returns:
            np.ndarray: 增强后的图像
        """
        clahe = cv2.createCLAHE(
            clipLimit=self.config['clahe_clip_limit'],
            tileGridSize=self.config['clahe_tile_size']
        )
        enhanced = clahe.apply(gray)
        return enhanced

    def _denoise_image(self, img: np.ndarray) -> np.ndarray:
        """
        图像降噪
        
        Args:
            img: 输入图像
            
        Returns:
            np.ndarray: 降噪后的图像
        """
        # 使用中值滤波降噪
        denoised = cv2.medianBlur(img, 3)
        return denoised

    def _sharpen_image(self, img: np.ndarray) -> np.ndarray:
        """
        图像锐化
        
        Args:
            img: 输入图像
            
        Returns:
            np.ndarray: 锐化后的图像
        """
        # 创建锐化核
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        
        # 应用锐化
        sharpened = cv2.filter2D(img, -1, kernel)
        
        # 确保像素值在有效范围内
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        return sharpened

    def _get_processed_path(self, original_path: str) -> str:
        """
        获取处理后图片的路径
        
        Args:
            original_path: 原始图片路径
            
        Returns:
            str: 处理后图片路径
        """
        base, ext = os.path.splitext(original_path)
        return f"{base}_processed{ext}"

    def cleanup_temp_files(self, *file_paths):
        """
        清理临时文件
        
        Args:
            *file_paths: 要删除的文件路径
        """
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"清理临时文件: {file_path}")
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {file_path}, 错误: {str(e)}")

    def validate_image(self, image_path: str) -> Tuple[bool, str]:
        """
        验证图片文件
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                return False, "文件不存在"

            # 检查文件大小
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                return False, "文件为空"
            
            if file_size > self.config['max_file_size']:
                return False, f"文件过大: {file_size} bytes"

            # 检查文件扩展名
            _, ext = os.path.splitext(image_path)
            if ext.lower() not in self.config['allowed_extensions']:
                return False, f"不支持的文件格式: {ext}"

            # 尝试读取图片
            img = cv2.imread(image_path)
            if img is None:
                return False, "无法读取图片文件"

            return True, ""

        except Exception as e:
            return False, f"验证图片失败: {str(e)}"

    def get_image_info(self, image_path: str) -> dict:
        """
        获取图片信息
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            dict: 图片信息
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {}

            height, width = img.shape[:2]
            file_size = os.path.getsize(image_path)
            
            return {
                'width': width,
                'height': height,
                'channels': img.shape[2] if len(img.shape) == 3 else 1,
                'file_size': file_size,
                'format': os.path.splitext(image_path)[1].lower()
            }

        except Exception as e:
            logger.error(f"获取图片信息失败: {str(e)}")
            return {}
