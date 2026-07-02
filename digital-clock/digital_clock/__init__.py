"""
Digital Clock with Multiple Time Zones
ساعة رقمية تعرض الوقت الحالي في مناطق زمنية مختلفة
"""

__version__ = "1.0.0"
__author__ = "AhmedElsakaVip"

from .core.clock import DigitalClock
from .core.timezone_manager import TimezoneManager
from .core.display import ClockDisplay
from .utils.config import ClockConfig

__all__ = [
    'DigitalClock',
    'TimezoneManager',
    'ClockDisplay',
    'ClockConfig',
]
