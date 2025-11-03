"""
日志配置工具
统一管理应用日志
"""

import logging
import os
import functools  # 新增导入
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = None, level: str = 'INFO') -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name or 'drug_recognition')

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 确保日志目录存在
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 文件处理器 - 应用日志
    # 应用主日志
    app_log_file = os.path.join(log_dir, 'app.log')
    app_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setLevel(log_level)
    app_handler.setFormatter(formatter)
    logger.addHandler(app_handler)

    # 文件处理器 - 错误日志
    error_log_file = os.path.join(log_dir, 'error.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # 文件处理器 - 访问日志
    access_log_file = os.path.join(log_dir, 'access.log')
    access_handler = RotatingFileHandler(
        access_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(formatter)
    logger.addHandler(access_handler)

    # OCR服务专用日志（单独记录OCR调用细节）
    ocr_log_file = os.path.join(log_dir, 'ocr.log')
    ocr_handler = RotatingFileHandler(
        ocr_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    ocr_handler.setLevel(logging.INFO)
    ocr_handler.setFormatter(formatter)
    logger.addHandler(ocr_handler)

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(name or 'drug_recognition')


class LoggerMixin:
    """日志混入类，为其他类提供日志功能"""

    @property
    def logger(self):
        """获取日志记录器"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


def log_function_call(func):
    """
    函数调用日志装饰器

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数
    """
    @functools.wraps(func)  # 新增：保留原函数元数据
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.info(f"调用函数: {func.__name__}, 参数: args={args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            logger.info(f"函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {str(e)}")
            raise

    return wrapper


def log_api_call(func):
    """
    API调用日志装饰器

    Args:
        func: 要装饰的API函数

    Returns:
        装饰后的函数
    """
    @functools.wraps(func)  # 新增：保留原函数元数据，解决Flask端点冲突
    def wrapper(*args, **kwargs):
        logger = get_logger('api')
        logger.info(f"API调用开始: {func.__name__}")

        try:
            result = func(*args, **kwargs)
            logger.info(f"API {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.error(f"API {func.__name__} 执行失败: {str(e)}")
            raise

    return wrapper


def log_ocr_call(func):
    """
    OCR服务专用日志装饰器
    """
    @functools.wraps(func)  # 新增：保留原函数元数据
    def wrapper(*args, **kwargs):
        logger = get_logger('ocr')
        logger.info(f"OCR服务调用: {func.__name__}")

        try:
            result = func(*args, **kwargs)
            logger.info(f"OCR服务 {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.error(f"OCR服务 {func.__name__} 执行失败: {str(e)}")
            raise

    return wrapper


# 创建默认日志记录器
default_logger = setup_logger()