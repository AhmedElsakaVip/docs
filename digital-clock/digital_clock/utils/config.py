"""Clock Configuration Module"""

from dataclasses import dataclass
from typing import List, Dict
import json
from pathlib import Path


@dataclass
class ClockConfig:
    """
    تكوين الساعة الرقمية
    
    المميزات:
    - إعدادات قابلة للتخصيص
    - حفظ واستعادة الإعدادات
    - دعم تنسيقات متعددة
    """
    
    # المناطق الزمنية الافتراضية
    default_timezones: Dict[str, str] = None
    
    # تنسيق الوقت
    time_format_24h: bool = True
    time_format: str = "%H:%M:%S"
    date_format: str = "%Y-%m-%d"
    
    # اللغة
    language: str = "ar"  # ar: عربي, en: إنجليزي
    
    # الإعدادات البصرية
    show_date: bool = True
    show_timezone: bool = True
    show_offset: bool = True
    use_icons: bool = True
    
    # التحديث
    update_interval: int = 1000  # ميلي ثانية
    
    def __post_init__(self):
        """تهيئة الإعدادات الافتراضية"""
        if self.default_timezones is None:
            self.default_timezones = {
                'مصر': 'Africa/Cairo',
                'السعودية': 'Asia/Riyadh',
                'الإمارات': 'Asia/Dubai',
                'لندن': 'Europe/London',
                'نيويورك': 'America/New_York',
            }
    
    def to_dict(self) -> Dict:
        """تحويل الإعدادات إلى قاموس"""
        return {
            'default_timezones': self.default_timezones,
            'time_format_24h': self.time_format_24h,
            'time_format': self.time_format,
            'date_format': self.date_format,
            'language': self.language,
            'show_date': self.show_date,
            'show_timezone': self.show_timezone,
            'show_offset': self.show_offset,
            'use_icons': self.use_icons,
            'update_interval': self.update_interval,
        }
    
    def save(self, filepath: str) -> bool:
        """حفظ الإعدادات في ملف JSON"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"خطأ في حفظ الإعدادات: {e}")
            return False
    
    @staticmethod
    def load(filepath: str) -> 'ClockConfig':
        """تحميل الإعدادات من ملف JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ClockConfig(**data)
        except Exception as e:
            print(f"خطأ في تحميل الإعدادات: {e}")
            return ClockConfig()
