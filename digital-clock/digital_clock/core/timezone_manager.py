"""
Timezone Manager Module
مدير المناطق الزمنية
"""

import pytz
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TimezoneManager:
    """
    مدير المناطق الزمنية المتقدم
    
    المميزات:
    - إدارة المناطق الزمنية
    - تحويل الأوقات بين المناطق
    - حساب الفروقات الزمنية
    - معلومات التوقيت الصيفي
    """
    
    # المناطق الزمنية الشهيرة
    POPULAR_TIMEZONES = {
        'UTC': 'UTC',
        'GMT': 'Europe/London',
        'مصر': 'Africa/Cairo',
        'السعودية': 'Asia/Riyadh',
        'الإمارات': 'Asia/Dubai',
        'الكويت': 'Asia/Kuwait',
        'قطر': 'Asia/Qatar',
        'البحرين': 'Asia/Bahrain',
        'عمان': 'Asia/Muscat',
        'اليمن': 'Asia/Aden',
        'السودان': 'Africa/Khartoum',
        'ليبيا': 'Africa/Tripoli',
        'تونس': 'Africa/Tunis',
        'المغرب': 'Africa/Casablanca',
        'الجزائر': 'Africa/Algiers',
        'فلسطين': 'Asia/Jerusalem',
        'لبنان': 'Asia/Beirut',
        'سوريا': 'Asia/Damascus',
        'العراق': 'Asia/Baghdad',
        'الأردن': 'Asia/Amman',
        'إيران': 'Asia/Tehran',
        'باكستان': 'Asia/Karachi',
        'الهند': 'Asia/Kolkata',
        'بنغلاديش': 'Asia/Dhaka',
        'تايلاند': 'Asia/Bangkok',
        'ماليزيا': 'Asia/Kuala_Lumpur',
        'إندونيسيا': 'Asia/Jakarta',
        'الفلبين': 'Asia/Manila',
        'فيتنام': 'Asia/Ho_Chi_Minh',
        'اليابان': 'Asia/Tokyo',
        'كوريا': 'Asia/Seoul',
        'الصين': 'Asia/Shanghai',
        'هونج كونج': 'Asia/Hong_Kong',
        'سنغافورة': 'Asia/Singapore',
        'سيدني': 'Australia/Sydney',
        'ملبورن': 'Australia/Melbourne',
        'نيوزيلندا': 'Pacific/Auckland',
        'لندن': 'Europe/London',
        'باريس': 'Europe/Paris',
        'برلين': 'Europe/Berlin',
        'روما': 'Europe/Rome',
        'مدريد': 'Europe/Madrid',
        'أمستردام': 'Europe/Amsterdam',
        'إسطنبول': 'Europe/Istanbul',
        'موسكو': 'Europe/Moscow',
        'نيويورك': 'America/New_York',
        'لوس أنجلوس': 'America/Los_Angeles',
        'شيكاغو': 'America/Chicago',
        'دنفر': 'America/Denver',
        'فانكوفر': 'America/Vancouver',
        'تورونتو': 'America/Toronto',
        'مكسيكو': 'America/Mexico_City',
        'ساو باولو': 'America/Sao_Paulo',
        'بيونس آيرس': 'America/Argentina/Buenos_Aires',
    }
    
    def __init__(self):
        """تهيئة مدير المناطق الزمنية"""
        self.custom_timezones: Dict[str, str] = {}
    
    def add_custom_timezone(self, name: str, timezone: str) -> bool:
        """إضافة منطقة زمنية مخصصة"""
        try:
            pytz.timezone(timezone)
            self.custom_timezones[name] = timezone
            logger.info(f"تمت إضافة المنطقة الزمنية المخصصة: {name}")
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            logger.error(f"منطقة زمنية غير معروفة: {timezone}")
            return False
    
    def get_all_timezones(self) -> Dict[str, str]:
        """الحصول على جميع المناطق الزمنية (الشهيرة + المخصصة)"""
        all_tz = self.POPULAR_TIMEZONES.copy()
        all_tz.update(self.custom_timezones)
        return all_tz
    
    def convert_time(
        self,
        time_str: str,
        from_tz: str,
        to_tz: str,
        format_str: str = "%H:%M:%S"
    ) -> Optional[str]:
        """
        تحويل الوقت من منطقة زمنية إلى أخرى
        
        Args:
            time_str: الوقت (بصيغة HH:MM:SS)
            from_tz: المنطقة الزمنية المصدر
            to_tz: المنطقة الزمنية الهدف
            format_str: تنسيق الإخراج
        
        Returns:
            الوقت المحول أو None
        """
        try:
            from_timezone = pytz.timezone(from_tz)
            to_timezone = pytz.timezone(to_tz)
            
            # إنشاء وقت في المنطقة الزمنية المصدر
            time_parts = time_str.split(':')
            now = datetime.now(from_timezone)
            localized_time = from_timezone.localize(
                datetime(now.year, now.month, now.day,
                        int(time_parts[0]), int(time_parts[1]), int(time_parts[2]))
            )
            
            # تحويل إلى المنطقة الزمنية الهدف
            converted_time = localized_time.astimezone(to_timezone)
            
            return converted_time.strftime(format_str)
        except Exception as e:
            logger.error(f"خطأ في تحويل الوقت: {e}")
            return None
    
    def get_time_offset(self, timezone_str: str) -> Optional[str]:
        """الحصول على إزاحة المنطقة الزمنية من UTC"""
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            offset = now.utcoffset()
            
            hours, remainder = divmod(int(offset.total_seconds()), 3600)
            minutes = remainder // 60
            
            return f"UTC{hours:+03d}:{minutes:02d}"
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإزاحة: {e}")
            return None
    
    def get_dst_info(self, timezone_str: str) -> Optional[Dict]:
        """الحصول على معلومات التوقيت الصيفي"""
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            
            return {
                'timezone': timezone_str,
                'is_dst': bool(now.dst()),
                'dst_offset': str(now.dst()) if now.dst() else 'None',
                'standard_offset': str(now.utcoffset()),
            }
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات DST: {e}")
            return None
    
    def list_timezones_by_region(self, region: str) -> List[str]:
        """الحصول على جميع المناطق الزمنية في منطقة معينة"""
        return [tz for tz in pytz.all_timezones if tz.startswith(region)]
    
    def get_timezone_name_in_arabic(self, timezone_str: str) -> str:
        """الحصول على اسم المنطقة الزمنية بالعربية"""
        # قاموس الأسماء العربية
        arabic_names = {
            'Africa/Cairo': 'مصر',
            'Asia/Dubai': 'الإمارات',
            'Asia/Riyadh': 'السعودية',
            'Europe/London': 'لندن',
            'Europe/Paris': 'باريس',
            'America/New_York': 'نيويورك',
            'Asia/Tokyo': 'اليابان',
            'Australia/Sydney': 'سيدني',
        }
        
        return arabic_names.get(timezone_str, timezone_str)
    
    def search_timezone(self, keyword: str) -> List[str]:
        """البحث عن منطقة زمنية"""
        keyword = keyword.lower()
        results = []
        
        # البحث في الأسماء العربية
        for tz, name in self.POPULAR_TIMEZONES.items():
            if keyword in tz.lower() or keyword in name.lower():
                results.append(name)
        
        # البحث في جميع المناطق الزمنية
        for tz in pytz.all_timezones:
            if keyword in tz.lower() and tz not in results:
                results.append(tz)
        
        return results
