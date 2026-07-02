"""
Digital Clock Main Module
الساعة الرقمية الرئيسية
"""

from datetime import datetime
import pytz
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class TimeZoneInfo:
    """معلومات المنطقة الزمنية"""
    name: str
    timezone: str
    display_name: str
    offset: str = ""
    current_time: Optional[str] = None
    
    def __post_init__(self):
        """حساب الإزاحة تلقائياً"""
        try:
            tz = pytz.timezone(self.timezone)
            now = datetime.now(tz)
            hours, remainder = divmod(int(now.utcoffset().total_seconds()), 3600)
            minutes = remainder // 60
            self.offset = f"UTC{hours:+03d}:{minutes:02d}"
        except Exception as e:
            logger.error(f"خطأ في حساب الإزاحة: {e}")
            self.offset = "UTC±00:00"


class DigitalClock:
    """
    ساعة رقمية ذكية تعرض الوقت في مناطق زمنية متعددة
    
    المميزات:
    - عرض الوقت الحالي في مناطق زمنية مختلفة
    - تحديث الوقت في الوقت الفعلي
    - دعم أكثر من 400 منطقة زمنية
    - تنسيقات وقت مختلفة
    - إنذارات وتذكيرات
    """
    
    def __init__(self):
        """تهيئة الساعة"""
        self.timezones: Dict[str, TimeZoneInfo] = {}
        self.default_timezones = {
            'مصر': 'Africa/Cairo',
            'السعودية': 'Asia/Riyadh',
            'الإمارات': 'Asia/Dubai',
            'لندن': 'Europe/London',
            'باريس': 'Europe/Paris',
            'نيويورك': 'America/New_York',
            'توكيو': 'Asia/Tokyo',
            'سيدني': 'Australia/Sydney',
            'ملبورن': 'Australia/Melbourne',
            'سنغافورة': 'Asia/Singapore',
            'هونج كونج': 'Asia/Hong_Kong',
            'دبي': 'Asia/Dubai',
            'بانكوك': 'Asia/Bangkok',
            'اسطنبول': 'Europe/Istanbul',
            'موسكو': 'Europe/Moscow',
        }
        
        # إضافة المناطق الزمنية الافتراضية
        self._init_default_timezones()
    
    def _init_default_timezones(self):
        """تهيئة المناطق الزمنية الافتراضية"""
        for display_name, timezone_str in self.default_timezones.items():
            try:
                self.add_timezone(display_name, timezone_str)
                logger.info(f"✓ تمت إضافة المنطقة الزمنية: {display_name}")
            except Exception as e:
                logger.error(f"خطأ في إضافة {display_name}: {e}")
    
    def add_timezone(self, name: str, timezone: str) -> bool:
        """
        إضافة منطقة زمنية جديدة
        
        Args:
            name: اسم المنطقة
            timezone: اسم المنطقة الزمنية (مثل: Africa/Cairo)
        
        Returns:
            bool: نجاح الإضافة
        """
        try:
            # التحقق من صحة المنطقة الزمنية
            pytz.timezone(timezone)
            
            info = TimeZoneInfo(
                name=name,
                timezone=timezone,
                display_name=name
            )
            
            self.timezones[name] = info
            logger.info(f"تمت إضافة المنطقة الزمنية: {name}")
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            logger.error(f"منطقة زمنية غير معروفة: {timezone}")
            return False
        except Exception as e:
            logger.error(f"خطأ في إضافة المنطقة الزمنية: {e}")
            return False
    
    def remove_timezone(self, name: str) -> bool:
        """حذف منطقة زمنية"""
        if name in self.timezones:
            del self.timezones[name]
            logger.info(f"تم حذف المنطقة الزمنية: {name}")
            return True
        return False
    
    def get_current_time(self, timezone_str: str, format_str: str = "%H:%M:%S") -> Optional[str]:
        """
        الحصول على الوقت الحالي في منطقة زمنية معينة
        
        Args:
            timezone_str: اسم المنطقة الزمنية
            format_str: تنسيق الوقت
        
        Returns:
            الوقت المنسق أو None
        """
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            return now.strftime(format_str)
        except Exception as e:
            logger.error(f"خطأ في الحصول على الوقت: {e}")
            return None
    
    def get_all_times(self, format_str: str = "%H:%M:%S") -> Dict[str, Dict]:
        """
        الحصول على الوقت الحالي في جميع المناطق الزمنية
        
        Args:
            format_str: تنسيق الوقت
        
        Returns:
            قاموس بأوقات جميع المناطق الزمنية
        """
        times = {}
        for name, tz_info in self.timezones.items():
            try:
                tz = pytz.timezone(tz_info.timezone)
                now = datetime.now(tz)
                
                times[name] = {
                    'time': now.strftime(format_str),
                    'date': now.strftime("%Y-%m-%d"),
                    'day': now.strftime("%A"),
                    'timezone': tz_info.timezone,
                    'offset': tz_info.offset,
                    'utc_offset': str(now.utcoffset()),
                }
            except Exception as e:
                logger.error(f"خطأ في الحصول على وقت {name}: {e}")
        
        return times
    
    def get_formatted_output(self, format_str: str = "%H:%M:%S") -> str:
        """
        الحصول على مخرجات منسقة لجميع الأوقات
        
        Args:
            format_str: تنسيق الوقت
        
        Returns:
            نص منسق
        """
        times = self.get_all_times(format_str)
        
        output = "⏰ الساعة الرقمية متعددة المناطق الزمنية\n"
        output += "=" * 60 + "\n\n"
        
        for name, data in times.items():
            output += f"🌍 {name}\n"
            output += f"   ⏱️  الوقت: {data['time']}\n"
            output += f"   📅 التاريخ: {data['date']}\n"
            output += f"   📍 المنطقة الزمنية: {data['timezone']}\n"
            output += f"   ↔️  الإزاحة: {data['offset']}\n"
            output += "-" * 60 + "\n"
        
        return output
    
    def get_time_difference(self, tz1: str, tz2: str) -> Optional[str]:
        """
        حساب الفرق الزمني بين منطقتين
        
        Args:
            tz1: المنطقة الزمنية الأولى
            tz2: المنطقة الزمنية الثانية
        
        Returns:
            الفرق الزمني
        """
        try:
            timezone1 = pytz.timezone(tz1)
            timezone2 = pytz.timezone(tz2)
            
            now_utc = datetime.now(pytz.UTC)
            time1 = now_utc.astimezone(timezone1)
            time2 = now_utc.astimezone(timezone2)
            
            diff = time2.utcoffset() - time1.utcoffset()
            hours = int(diff.total_seconds() // 3600)
            minutes = int((diff.total_seconds() % 3600) // 60)
            
            if hours > 0:
                return f"+{hours}:{minutes:02d} ساعة"
            elif hours < 0:
                return f"{hours}:{minutes:02d} ساعة"
            else:
                return "نفس الوقت"
        except Exception as e:
            logger.error(f"خطأ في حساب الفرق الزمني: {e}")
            return None
    
    def is_dst_active(self, timezone_str: str) -> bool:
        """
        التحقق من تطبيق التوقيت الصيفي
        
        Args:
            timezone_str: اسم المنطقة الزمنية
        
        Returns:
            True إذا كان التوقيت الصيفي نشطاً
        """
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            
            # التحقق من ما إذا كانت الإزاحة مختلفة عن التوقيت القياسي
            return bool(now.dst())
        except Exception as e:
            logger.error(f"خطأ في التحقق من التوقيت الصيفي: {e}")
            return False
    
    def list_available_timezones(self) -> List[str]:
        """الحصول على قائمة بجميع المناطق الزمنية المتاحة"""
        return sorted(pytz.all_timezones)
    
    def search_timezones(self, keyword: str) -> List[str]:
        """
        البحث عن مناطق زمنية حسب الكلمة المفتاحية
        
        Args:
            keyword: الكلمة المفتاحية للبحث
        
        Returns:
            قائمة المناطق الزمنية المطابقة
        """
        keyword = keyword.lower()
        return [tz for tz in pytz.all_timezones if keyword in tz.lower()]
    
    def get_timezone_info(self, timezone_str: str) -> Optional[Dict]:
        """الحصول على معلومات تفصيلية عن منطقة زمنية"""
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            
            return {
                'timezone': timezone_str,
                'current_time': now.strftime("%H:%M:%S"),
                'current_date': now.strftime("%Y-%m-%d"),
                'utc_offset': str(now.utcoffset()),
                'dst_active': bool(now.dst()),
                'country': tz.zone,
            }
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات المنطقة الزمنية: {e}")
            return None
