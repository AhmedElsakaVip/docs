"""Utility functions for digital clock"""

import logging
from datetime import datetime, timedelta
from typing import Optional


logger = logging.getLogger(__name__)


def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO) -> None:
    """
    إعداد نظام تسجيل السجلات
    
    Args:
        log_file: مسار ملف السجل (اختياري)
        level: مستوى تسجيل الأحداث
    """
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # معالج وحدة التحكم
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.setLevel(level)
    
    # معالج الملف (إذا تم توفيره)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def calculate_time_until(target_hour: int, target_minute: int = 0) -> timedelta:
    """
    حساب الوقت المتبقي حتى وقت معين
    
    Args:
        target_hour: الساعة المستهدفة
        target_minute: الدقيقة المستهدفة
    
    Returns:
        الفرق الزمني
    """
    now = datetime.now()
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    if target <= now:
        target += timedelta(days=1)
    
    return target - now


def format_timedelta(td: timedelta) -> str:
    """
    تنسيق الفرق الزمني
    
    Args:
        td: الفرق الزمني
    
    Returns:
        نص منسق
    """
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def is_business_hours(hour: int) -> bool:
    """
    التحقق من ما إذا كان الوقت ضمن ساعات العمل (9 صباحاً - 5 مساءً)
    
    Args:
        hour: الساعة
    
    Returns:
        True إذا كان ضمن ساعات العمل
    """
    return 9 <= hour < 17


def get_time_period_name(hour: int) -> str:
    """
    الحصول على اسم فترة الوقت
    
    Args:
        hour: الساعة
    
    Returns:
        اسم الفترة
    """
    if 5 <= hour < 12:
        return "صباح"
    elif 12 <= hour < 17:
        return "ظهيرة"
    elif 17 <= hour < 19:
        return "مساء"
    else:
        return "ليل"
