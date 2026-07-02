# Digital Clock - ساعة رقمية متعددة المناطق الزمنية

A beautiful and feature-rich digital clock application that displays the current time across multiple time zones.

## 🌟 Features

### ⏰ Core Features
- 🕐 **Digital Time Display** - Display time in 24/7 or 12-hour format
- 🌍 **Multiple Time Zones** - Support for 400+ time zones worldwide
- 🗓️ **Date Display** - Show date in various formats (Arabic/English)
- 📊 **Time Information** - Display UTC offset, DST status
- 🎨 **Beautiful UI** - Clean and modern interface with icons

### 🛠️ Advanced Features
- 🔄 **Real-time Updates** - Continuous time synchronization
- 🔍 **Time Zone Search** - Search for specific time zones
- 📈 **Time Comparison** - Compare times between zones
- 🌐 **Multi-language** - Support for Arabic and English
- 📌 **Custom Time Zones** - Add your own time zones
- ⚙️ **Configuration** - Customizable settings and preferences

## 📦 Requirements

```bash
Python 3.8+
pytz>=2023.3
```

## 🚀 Installation

```bash
git clone https://github.com/AhmedElsakaVip/digital-clock.git
cd digital-clock
pip install -r requirements.txt
```

## 💻 Quick Start

### Basic Usage

```python
from digital_clock import DigitalClock

# Create a clock instance
clock = DigitalClock()

# Get current time in all zones
print(clock.get_formatted_output())

# Get time in specific zone
time_cairo = clock.get_current_time('Africa/Cairo')
print(f"Cairo time: {time_cairo}")
```

### Add Custom Time Zone

```python
clock.add_timezone('My City', 'Asia/Dubai')

# Remove a timezone
clock.remove_timezone('My City')
```

### Display Time

```python
from digital_clock import ClockDisplay

# Get formatted display
display = ClockDisplay.format_clock_widget(
    'Africa/Cairo',
    'Cairo',
    show_date=True,
    show_offset=True
)
print(display)
```

### Time Comparison

```python
# Compare times between two zones
comparison = ClockDisplay.format_comparison(
    'Africa/Cairo',
    'America/New_York',
    'Cairo',
    'New York'
)
print(comparison)
```

## 📖 API Documentation

### DigitalClock Class

```python
class DigitalClock:
    def add_timezone(name: str, timezone: str) -> bool
    def remove_timezone(name: str) -> bool
    def get_current_time(timezone_str: str, format_str: str) -> str
    def get_all_times(format_str: str) -> Dict
    def get_formatted_output(format_str: str) -> str
    def get_time_difference(tz1: str, tz2: str) -> str
    def is_dst_active(timezone_str: str) -> bool
    def list_available_timezones() -> List[str]
    def search_timezones(keyword: str) -> List[str]
```

### ClockDisplay Class

```python
class ClockDisplay:
    @staticmethod
    def get_digital_time(timezone_str: str, format_12h: bool) -> str
    @staticmethod
    def get_analog_time(timezone_str: str) -> str
    @staticmethod
    def get_formatted_date(timezone_str: str, arabic: bool) -> str
    @staticmethod
    def format_clock_widget(...) -> str
    @staticmethod
    def format_table_display(times_dict: Dict) -> str
    @staticmethod
    def get_time_status(timezone_str: str) -> str
    @staticmethod
    def format_comparison(...) -> str
```

### TimezoneManager Class

```python
class TimezoneManager:
    def add_custom_timezone(name: str, timezone: str) -> bool
    def get_all_timezones() -> Dict[str, str]
    def convert_time(time_str: str, from_tz: str, to_tz: str) -> str
    def get_time_offset(timezone_str: str) -> str
    def get_dst_info(timezone_str: str) -> Dict
    def list_timezones_by_region(region: str) -> List[str]
    def search_timezone(keyword: str) -> List[str]
```

## 🎨 Supported Time Zones

The application includes built-in support for popular time zones:

**Middle East & North Africa:**
- Egypt, Saudi Arabia, UAE, Kuwait, Qatar, etc.

**Europe:**
- London, Paris, Berlin, Rome, Istanbul, Moscow, etc.

**Asia:**
- Tokyo, Shanghai, Dubai, Bangkok, Singapore, etc.

**Americas:**
- New York, Los Angeles, Chicago, Toronto, Mexico, etc.

**Oceania:**
- Sydney, Melbourne, Auckland, etc.

## ⚙️ Configuration

Create a `config.json` file to customize settings:

```json
{
  "default_timezones": {
    "مصر": "Africa/Cairo",
    "السعودية": "Asia/Riyadh"
  },
  "time_format_24h": true,
  "language": "ar",
  "show_date": true,
  "show_timezone": true,
  "use_icons": true,
  "update_interval": 1000
}
```

## 📊 Example Output

```
⏰ الساعة الرقمية متعددة المناطق الزمنية
================================================================================
المنطقة الزمنية              الوقت         التاريخ                الإزاحة
--------------------------------------------------------------------------------
مصر                    14:30:45      2026-07-02            UTC+02:00
السعودية               15:30:45      2026-07-02            UTC+03:00
الإمارات               16:30:45      2026-07-02            UTC+04:00
لندن                   13:30:45      2026-07-02            UTC+01:00
نيويورك                08:30:45      2026-07-02            UTC-04:00
================================================================================
```

## 🔧 Advanced Examples

### Monitor Time Until Event

```python
from digital_clock.utils import calculate_time_until, format_timedelta

# Time until 5 PM
time_left = calculate_time_until(17, 0)
print(f"Time until 5 PM: {format_timedelta(time_left)}")
```

### Check Business Hours

```python
from digital_clock.utils import is_business_hours
from datetime import datetime

current_hour = datetime.now().hour
if is_business_hours(current_hour):
    print("Currently in business hours")
```

### Get Time Period

```python
from digital_clock.utils import get_time_period_name
from datetime import datetime

hour = datetime.now().hour
period = get_time_period_name(hour)
print(f"Current period: {period}")  # e.g., "صباح" (Morning)
```

## 📝 File Structure

```
digital-clock/
├── digital_clock/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── clock.py          # Main clock logic
│   │   ├── timezone_manager.py # Timezone management
│   │   └── display.py        # Display formatting
│   └── utils/
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       └── helpers.py        # Utility functions
├── examples/
│   ├── basic_example.py
│   ├── comparison_example.py
│   └── advanced_example.py
├── tests/
│   ├── test_clock.py
│   └── test_display.py
├── requirements.txt
├── setup.py
├── README.md
└── LICENSE
```

## 🧪 Testing

```bash
pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**AhmedElsakaVip**
- GitHub: [@AhmedElsakaVip](https://github.com/AhmedElsakaVip)
- Email: contact@example.com

## 🙏 Acknowledgments

- PyTZ for timezone support
- Python community for inspiration

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ by AhmedElsakaVip**
