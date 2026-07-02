"""
Display Module for Clock
وحدة العرض للساعة
"""

from datetime import datetime
import pytz
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ClockDisplay:
    """
    وحدة عرض الساعة الرقمية
    
    المميزات:
    - تنسيقات عرض مختلفة
    - عرض جميلة للأوقات
    - رموز وأيقونات
    - تحديث في الوقت الفعلي
    """
    
    # الرموز والأيقونات
    ICONS = {
        'clock': '⏰',
        'time': '⏱️',
        'date': '📅',
        'timezone': '🌍',
        'offset': '↔️',
        'sunrise': '🌅',
        'sunset': '🌇',
        'night': '🌙',
        'day': '☀️',
    }
    
    # الأيام بالعربية
    ARABIC_DAYS = {
        'Monday': 'الاثنين',
        'Tuesday': 'الثلاثاء',
        'Wednesday': 'الأربعاء',
        'Thursday': 'الخميس',
        'Friday': 'الجمعة',
        'Saturday': 'السبت',
        'Sunday': 'الأحد',
    }
    
    # الأشهر بالعربية
    ARABIC_MONTHS = {
        1: 'يناير',
        2: 'فبراير',
        3: 'مارس',
        4: 'أبريل',
        5: 'مايو',
        6: 'يونيو',
        7: 'يوليو',
        8: 'أغسطس',
        9: 'سبتمبر',
        10: 'أكتوبر',
        11: 'نوفمبر',
        12: 'ديسمبر',
    }
    
    @staticmethod
    def get_digital_time(timezone_str: str, format_12h: bool = False) -> str:
        """
        الحصول على الوقت الرقمي
        
        Args:
            timezone_str: اسم المنطقة الزمنية
            format_12h: استخدام التنسيق 12 ساعة
        
        Returns:
            الوقت الرقمي المنسق
        """
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            
            if format_12h:
                return now.strftime("%I:%M:%S %p")
            else:
                return now.strftime("%H:%M:%S")
        except Exception as e:
            logger.error(f"خطأ في الحصول على الوقت الرقمي: {e}")
            return "00:00:00"
    
    @staticmethod
    def get_analog_time(timezone_str: str) -> str:
        """الحصول على تمثيل تناظري للوقت (مثل العقارب)"""
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            
            hours = now.hour % 12
            minutes = now.minute
            seconds = now.second
            
            # تحويل إلى موضع العقارب
            hour_angle = (hours * 30) + (minutes * 0.5)
            minute_angle = (minutes * 6) + (seconds * 0.1)
            second_angle = seconds * 6
            
            return f"ساعة: {hour_angle:.1f}°, دقيقة: {minute_angle:.1f}°, ثانية: {second_angle:.1f}°"
        except Exception as e:
            logger.error(f"خطأ في الحصول على الوقت التناظري: {e}")
            return ""
    
    @staticmethod
    def get_formatted_date(timezone_str: str, arabic: bool = True) -> str:
        """
        الحصول على التاريخ المنسق
        
        Args:
            timezone_str: اسم المنطقة الزمنية
            arabic: استخدام الأسماء العربية
        
        Returns:
            التاريخ المنسق
        """
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            
            if arabic:
                day_name = ClockDisplay.ARABIC_DAYS.get(now.strftime("%A"), "")
                month_name = ClockDisplay.ARABIC_MONTHS.get(now.month, "")
                return f"{day_name} {now.day} {month_name} {now.year}"
            else:
                return now.strftime("%A, %B %d, %Y")
        except Exception as e:
            logger.error(f"خطأ في الحصول على التاريخ: {e}")
            return ""
    
    @staticmethod
    def format_clock_widget(
        timezone_str: str,
        timezone_name: str,
        show_date: bool = True,
        show_offset: bool = True
    ) -> str:
        """
        تنسيق عنصر واجهة الساعة
        
        Args:
            timezone_str: اسم المنطقة الزمنية
            timezone_name: الاسم المعروض للمنطقة الزمنية
            show_date: عرض التاريخ
            show_offset: عرض الإزاحة
        
        Returns:
            عنصر واجهة منسق
        """
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            
            # الحصول على الوقت الرقمي
            digital_time = now.strftime("%H:%M:%S")
            
            # بناء عنصر الواجهة
            widget = f"{ClockDisplay.ICONS['timezone']} {timezone_name}\n"
            widget += f"{ClockDisplay.ICONS['time']} {digital_time}\n"
            
            if show_date:
                date_str = ClockDisplay.get_formatted_date(timezone_str, arabic=True)
                widget += f"{ClockDisplay.ICONS['date']} {date_str}\n"
            
            if show_offset:
                hours, remainder = divmod(int(now.utcoffset().total_seconds()), 3600)
                minutes = remainder // 60
                offset_str = f"UTC{hours:+03d}:{minutes:02d}"
                widget += f"{ClockDisplay.ICONS['offset']} {offset_str}"
            
            return widget
        except Exception as e:
            logger.error(f"خطأ في تنسيق عنصر الواجهة: {e}")
            return ""
    
    @staticmethod
    def format_table_display(times_dict: Dict[str, Dict]) -> str:
        """
        تنسيق جدول لعرض أوقات متعددة
        
        Args:
            times_dict: قاموس الأوقات
        
        Returns:
            جدول منسق
        """
        output = f"{ClockDisplay.ICONS['clock']} الساعة الرقمية متعددة المناطق الزمنية\n"
        output += "=" * 80 + "\n"
        output += f"{'المنطقة الزمنية':<20} {'الوقت':<12} {'التاريخ':<20} {'الإزاحة':<15}\n"
        output += "-" * 80 + "\n"
        
        for name, data in times_dict.items():
            output += f"{name:<20} {data['time']:<12} {data['date']:<20} {data['offset']:<15}\n"
        
        output += "=" * 80
        return output
    
    @staticmethod
    def get_time_status(timezone_str: str) -> str:
        """
        الحصول على حالة الوقت (صباح/مساء/ليل)
        
        Args:
            timezone_str: اسم المنطقة الزمنية
        
        Returns:
            حالة الوقت مع الرمز
        """
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            hour = now.hour
            
            if 5 <= hour < 12:
                return f"{ClockDisplay.ICONS['sunrise']} صباح"
            elif 12 <= hour < 17:
                return f"{ClockDisplay.ICONS['day']} ظهيرة"
            elif 17 <= hour < 19:
                return f"{ClockDisplay.ICONS['sunset']} مساء"
            else:
                return f"{ClockDisplay.ICONS['night']} ليل"
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة الوقت: {e}")
            return ""
    
    @staticmethod
    def format_comparison(tz1: str, tz2: str, name1: str, name2: str) -> str:
        """
        تنسيق مقارنة بين وقتين
        
        Args:
            tz1: المنطقة الزمنية الأولى
            tz2: المنطقة الزمنية الثانية
            name1: الاسم الأول
            name2: الاسم الثاني
        
        Returns:
            مقارنة منسقة
        """
        try:
            tz_obj1 = pytz.timezone(tz1)
            tz_obj2 = pytz.timezone(tz2)
            
            now1 = datetime.now(tz_obj1)
            now2 = datetime.now(tz_obj2)
            
            output = "⏰ مقارنة الأوقات\n"
            output += "=" * 50 + "\n"
            output += f"{ClockDisplay.ICONS['timezone']} {name1}\n"
            output += f"   {now1.strftime('%H:%M:%S')} - {ClockDisplay.get_formatted_date(tz1)}\n\n"
            output += f"{ClockDisplay.ICONS['timezone']} {name2}\n"
            output += f"   {now2.strftime('%H:%M:%S')} - {ClockDisplay.get_formatted_date(tz2)}\n"
            output += "=" * 50
            
            return output
        except Exception as e:
            logger.error(f"خطأ في تنسيق المقارنة: {e}")
            return ""
