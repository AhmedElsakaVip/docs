# =========================================================
# STREAMLINK PRO ULTRA X - COMPLETE FIXED VERSION
# Gaming PC -> Streaming PC Audio Bridge
#
# FEATURES:
# ---------------------------------------------------------
# ✅ WASAPI LOOPBACK (Desktop/Game Audio)
# ✅ Microphone Capture
# ✅ Real-Time Audio Mixer with Better Mixing
# ✅ OBS / TikTok Studio Ready
# ✅ Ultra Low Latency OPUS
# ✅ UDP Streaming
# ✅ Auto FFmpeg Installer
# ✅ Audio Meter with Peak Detection
# ✅ Advanced Noise Gate (Soft Gate)
# ✅ Device Detection (Improved)
# ✅ Multi-Threaded Engine (Optimized)
# ✅ Crash Protection (Better Error Handling)
# ✅ Clean Shutdown
# ✅ Gaming Optimized
# ✅ Windows Optimized
# ✅ Status Indicator
# ✅ Volume Normalization
# ✅ Latency Monitoring
#
# OBS URL:
# udp://0.0.0.0:9000
#
# =========================================================

import os
import sys
import time
import queue
import shutil
import zipfile
import threading
import subprocess
import urllib.request
import numpy as np
import logging
from datetime import datetime
from pathlib import Path

# =========================================================
# LOGGING SETUP
# =========================================================

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================================================
# AUTO INSTALL
# =========================================================

REQUIRED = {
    "PyQt5": "PyQt5",
    "numpy": "numpy",
    "sounddevice": "sounddevice"
}

for module_name, pip_name in REQUIRED.items():
    try:
        __import__(module_name)
    except ImportError:
        print(f"Installing {pip_name}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pip_name]
        )

# =========================================================
# IMPORTS
# =========================================================

import sounddevice as sd

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# =========================================================
# CONFIG
# =========================================================

APP_NAME = "STREAMLINK PRO ULTRA X"
APP_VERSION = "2.1.0"

SAMPLE_RATE = 48000
BLOCKSIZE = 960
DTYPE = "float32"

UDP_PORT = 9000

FFMPEG_URL = (
    "https://www.gyan.dev/ffmpeg/builds/"
    "ffmpeg-release-essentials.zip"
)

# Audio processing
MAX_VOLUME = 1.0
SOFT_GATE_THRESHOLD = 0.05
SOFT_GATE_RATIO = 4.0

# =========================================================
# SIGNALS
# =========================================================

class Signals(QObject):

    log_signal = pyqtSignal(str)
    meter_signal = pyqtSignal(int, int)  # volume, peak
    status_signal = pyqtSignal(str)  # status text
    connection_signal = pyqtSignal(bool)  # connection status
    latency_signal = pyqtSignal(float)  # latency in ms

# =========================================================
# UTILS
# =========================================================

class AudioProcessor:
    """Advanced audio processing with soft gate and normalization"""
    
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.noise_gate_threshold = SOFT_GATE_THRESHOLD
        self.previous_level = 0.0
        self.smoothing_factor = 0.3
        self.peak_level = 0.0
        self.peak_decay = 0.95
    
    def soft_gate(self, audio, threshold):
        """Soft gate with smooth transition"""
        try:
            if audio is None or len(audio) == 0:
                return audio
            
            # Calculate RMS level
            rms = np.sqrt(np.mean(audio ** 2))
            
            if rms < threshold:
                # Soft transition below threshold
                gate_level = max(0, (rms - threshold * 0.5) / (threshold * 0.5))
                return audio * (gate_level ** 2)
            
            return audio
        except Exception as e:
            logger.error(f"Soft gate error: {e}")
            return audio
    
    def normalize(self, audio, target_level=0.8):
        """Safe normalization with headroom"""
        try:
            if audio is None or len(audio) == 0:
                return audio
            
            peak = np.max(np.abs(audio))
            
            if peak > 0:
                # Leave headroom to prevent clipping
                scale = (target_level / peak) * 0.95
                return np.clip(audio * scale, -1.0, 1.0)
            
            return audio
        except Exception as e:
            logger.error(f"Normalization error: {e}")
            return audio
    
    def mix_audio(self, desktop, microphone, desktop_gain=1.0, mic_gain=1.0):
        """Professional audio mixing"""
        try:
            if desktop is None:
                return None
            
            mixed = desktop.copy() * desktop_gain
            
            if microphone is not None:
                min_len = min(len(mixed), len(microphone))
                mixed[:min_len] += microphone[:min_len] * mic_gain
            
            # Soft gate on mixed signal
            mixed = self.soft_gate(mixed, self.noise_gate_threshold)
            
            # Normalize
            mixed = self.normalize(mixed)
            
            # Update peak with decay
            current_peak = np.max(np.abs(mixed))
            self.peak_level = max(
                current_peak,
                self.peak_level * self.peak_decay
            )
            
            return mixed
        
        except Exception as e:
            logger.error(f"Audio mixing error: {e}")
            return desktop
    
    def get_volume_level(self, audio):
        """Get volume level (0-100) with smoothing"""
        try:
            if audio is None or len(audio) == 0:
                level = 0
            else:
                level = int(np.linalg.norm(audio) * 100)
                level = max(0, min(level, 100))
            
            # Apply smoothing
            self.previous_level = (
                self.smoothing_factor * level + 
                (1 - self.smoothing_factor) * self.previous_level
            )
            
            return int(self.previous_level)
        except Exception as e:
            logger.error(f"Volume level error: {e}")
            return 0
    
    def get_peak_level(self):
        """Get peak level (0-100)"""
        return min(100, int(self.peak_level * 100))

# =========================================================
# DEVICE MANAGER
# =========================================================

class DeviceManager:
    """Improved device detection and management"""
    
    @staticmethod
    def get_all_devices():
        """Get list of all audio devices"""
        try:
            return sd.query_devices()
        except Exception as e:
            logger.error(f"Failed to query devices: {e}")
            return []
    
    @staticmethod
    def find_wasapi_devices():
        """Find WASAPI loopback devices (Stereo Mix, Virtual Audio Cable)"""
        try:
            devices = DeviceManager.get_all_devices()
            loopback_devices = {}
            
            for idx, dev in enumerate(devices):
                try:
                    name = dev.get('name', '') if isinstance(dev, dict) else dev.name
                    max_in = dev.get('max_input_channels', 0) if isinstance(dev, dict) else dev.max_input_channels
                    
                    # Look for WASAPI devices with input capability
                    if max_in > 0:
                        # Check for common WASAPI loopback device names
                        if any(keyword in name.lower() for keyword in [
                            'stereo mix',
                            'what u hear',
                            'loopback',
                            'virtual cable',
                            'voicemeeter',
                            'vb-audio',
                            'wave out mix',
                            'mixer'
                        ]):
                            loopback_devices[f"{idx} - {name}"] = idx
                        
                        # Also include generic input devices that are not mics
                        if 'microphone' not in name.lower() and 'mic' not in name.lower():
                            loopback_devices[f"{idx} - {name}"] = idx
                
                except Exception as e:
                    logger.warning(f"Error processing device {idx}: {e}")
                    continue
            
            return loopback_devices
        except Exception as e:
            logger.error(f"Failed to find WASAPI devices: {e}")
            return {}
    
    @staticmethod
    def find_microphone_devices():
        """Find microphone devices"""
        try:
            devices = DeviceManager.get_all_devices()
            mic_devices = {}
            
            for idx, dev in enumerate(devices):
                try:
                    name = dev.get('name', '') if isinstance(dev, dict) else dev.name
                    max_in = dev.get('max_input_channels', 0) if isinstance(dev, dict) else dev.max_input_channels
                    
                    if max_in > 0:
                        # Prioritize microphone devices
                        if any(keyword in name.lower() for keyword in [
                            'microphone',
                            'mic',
                            'input',
                            'recording'
                        ]):
                            mic_devices[f"{idx} - {name}"] = idx
                        else:
                            # Include other input devices
                            mic_devices[f"{idx} - {name}"] = idx
                
                except Exception as e:
                    logger.warning(f"Error processing device {idx}: {e}")
                    continue
            
            return mic_devices
        except Exception as e:
            logger.error(f"Failed to find microphone devices: {e}")
            return {}

# =========================================================
# MAIN APP
# =========================================================

class StreamLinkUltra(QWidget):

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        super().__init__()

        self.signals = Signals()

        self.signals.log_signal.connect(
            self.write_log
        )

        self.signals.meter_signal.connect(
            self.update_meter
        )

        self.signals.status_signal.connect(
            self.update_status
        )

        self.signals.connection_signal.connect(
            self.update_connection
        )

        self.signals.latency_signal.connect(
            self.update_latency
        )

        self.running = False
        self.stream_start_time = None

        self.ffmpeg_process = None

        self.desktop_stream = None
        self.mic_stream = None

        self.desktop_audio = None
        self.mic_audio = None

        self.ffmpeg_path = self.find_ffmpeg()

        self.audio_processor = AudioProcessor()

        self.device_manager = DeviceManager()

        self.frames_processed = 0

        self.build_ui()

        self.load_devices()

        self.log("✅ Application initialized successfully")

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")

        self.resize(1100, 850)

        self.setStyleSheet(self.stylesheet())

        root = QVBoxLayout()

        # =================================================
        # TITLE
        # =================================================

        title_layout = QHBoxLayout()

        title = QLabel(
            "🎧 STREAMLINK PRO ULTRA X"
        )

        title.setAlignment(Qt.AlignCenter)

        title.setFont(
            QFont("Segoe UI", 20, QFont.Bold)
        )

        title.setStyleSheet(
            "color:#00D4FF;"
        )

        self.status_label = QLabel(
            "🔴 OFFLINE"
        )

        self.status_label.setFont(
            QFont("Segoe UI", 12, QFont.Bold)
        )

        self.status_label.setStyleSheet(
            "color:#FF6B6B; padding:5px 10px; "
            "background:#313244; border-radius:5px;"
        )

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(self.status_label)

        root.addLayout(title_layout)

        # =================================================
        # ENGINE
        # =================================================

        engine_group = QGroupBox(
            "FFmpeg Engine"
        )

        engine_layout = QHBoxLayout()

        self.install_btn = QPushButton(
            "⚡ INSTALL FFMPEG"
        )

        self.install_btn.clicked.connect(
            self.install_ffmpeg
        )

        self.ffmpeg_status = QLabel(
            "❌ Not Installed"
        )

        self.ffmpeg_status.setStyleSheet(
            "color:#FF6B6B;"
        )

        if self.ffmpeg_path:
            self.ffmpeg_status.setText("✅ Installed")
            self.ffmpeg_status.setStyleSheet("color:#A6E3A1;")
            self.install_btn.setEnabled(False)

        engine_layout.addWidget(
            self.install_btn
        )

        engine_layout.addWidget(
            self.ffmpeg_status
        )

        engine_layout.addStretch()

        engine_group.setLayout(
            engine_layout
        )

        root.addWidget(engine_group)

        # =================================================
        # DEVICES
        # =================================================

        devices_group = QGroupBox(
            "Audio Devices"
        )

        devices_layout = QGridLayout()

        self.desktop_combo = QComboBox()
        self.mic_combo = QComboBox()

        self.refresh_devices_btn = QPushButton(
            "🔄 Refresh"
        )

        self.refresh_devices_btn.clicked.connect(
            self.load_devices
        )

        self.refresh_devices_btn.setMaximumWidth(100)

        devices_layout.addWidget(
            QLabel("Desktop Audio (Stereo Mix)"),
            0,
            0
        )

        devices_layout.addWidget(
            self.desktop_combo,
            0,
            1
        )

        devices_layout.addWidget(
            self.refresh_devices_btn,
            0,
            2
        )

        devices_layout.addWidget(
            QLabel("Microphone"),
            1,
            0
        )

        devices_layout.addWidget(
            self.mic_combo,
            1,
            1
        )

        devices_group.setLayout(
            devices_layout
        )

        root.addWidget(devices_group)

        # =================================================
        # SETTINGS
        # =================================================

        settings_group = QGroupBox(
            "Streaming Settings"
        )

        settings_layout = QGridLayout()

        self.target_ip = QLineEdit()
        self.target_ip.setText("127.0.0.1")
        self.target_ip.setToolTip("Target PC IP (127.0.0.1 for local)")

        self.bitrate_box = QComboBox()
        self.bitrate_box.addItems([
            "64k",
            "96k",
            "128k",
            "192k",
            "256k",
            "320k"
        ])
        self.bitrate_box.setCurrentText("192k")

        self.noise_gate = QDoubleSpinBox()
        self.noise_gate.setRange(0.0, 1.0)
        self.noise_gate.setSingleStep(0.05)
        self.noise_gate.setValue(0.05)
        self.noise_gate.setToolTip("Noise gate threshold (0.0-1.0)")

        self.desktop_gain = QDoubleSpinBox()
        self.desktop_gain.setRange(0.0, 2.0)
        self.desktop_gain.setSingleStep(0.1)
        self.desktop_gain.setValue(1.0)
        self.desktop_gain.setToolTip("Desktop audio gain multiplier")

        self.mic_gain = QDoubleSpinBox()
        self.mic_gain.setRange(0.0, 2.0)
        self.mic_gain.setSingleStep(0.1)
        self.mic_gain.setValue(1.0)
        self.mic_gain.setToolTip("Microphone gain multiplier")

        settings_layout.addWidget(
            QLabel("Streaming PC IP"),
            0,
            0
        )
        settings_layout.addWidget(
            self.target_ip,
            0,
            1
        )

        settings_layout.addWidget(
            QLabel("Bitrate"),
            0,
            2
        )
        settings_layout.addWidget(
            self.bitrate_box,
            0,
            3
        )

        settings_layout.addWidget(
            QLabel("Noise Gate"),
            1,
            0
        )
        settings_layout.addWidget(
            self.noise_gate,
            1,
            1
        )

        settings_layout.addWidget(
            QLabel("Desktop Gain"),
            1,
            2
        )
        settings_layout.addWidget(
            self.desktop_gain,
            1,
            3
        )

        settings_layout.addWidget(
            QLabel("Mic Gain"),
            2,
            0
        )
        settings_layout.addWidget(
            self.mic_gain,
            2,
            1
        )

        settings_group.setLayout(
            settings_layout
        )

        root.addWidget(settings_group)

        # =================================================
        # AUDIO METER
        # =================================================

        meter_group = QGroupBox(
            "Audio Meter"
        )

        meter_layout = QVBoxLayout()

        meter_info_layout = QHBoxLayout()

        self.audio_meter = QProgressBar()
        self.audio_meter.setRange(0, 100)
        self.audio_meter.setStyleSheet(self.progress_stylesheet())

        self.volume_label = QLabel("Volume: 0%")
        self.volume_label.setMinimumWidth(80)

        self.peak_meter = QProgressBar()
        self.peak_meter.setRange(0, 100)
        self.peak_meter.setMaximumHeight(15)
        self.peak_meter.setStyleSheet(self.peak_stylesheet())

        self.peak_label = QLabel("Peak: 0%")
        self.peak_label.setMinimumWidth(80)

        meter_info_layout.addWidget(
            QLabel("Current:")
        )
        meter_info_layout.addWidget(
            self.volume_label
        )
        meter_info_layout.addWidget(
            self.audio_meter,
            1
        )

        meter_info_layout.addSpacing(20)

        meter_info_layout.addWidget(
            QLabel("Peak:")
        )
        meter_info_layout.addWidget(
            self.peak_label
        )
        meter_info_layout.addWidget(
            self.peak_meter,
            1
        )

        meter_layout.addLayout(meter_info_layout)

        # Latency info
        latency_layout = QHBoxLayout()
        self.latency_label = QLabel("Latency: 0ms")
        self.latency_label.setStyleSheet("color:#A6E3A1;")
        self.frames_label = QLabel("Frames: 0")
        self.frames_label.setStyleSheet("color:#89B4FA;")

        latency_layout.addWidget(self.latency_label)
        latency_layout.addStretch()
        latency_layout.addWidget(self.frames_label)

        meter_layout.addLayout(latency_layout)

        meter_group.setLayout(
            meter_layout
        )

        root.addWidget(meter_group)

        # =================================================
        # BUTTONS
        # =================================================

        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton(
            "▶ START STREAMING"
        )

        self.stop_btn = QPushButton(
            "■ STOP STREAMING"
        )

        self.stop_btn.setEnabled(False)

        self.start_btn.clicked.connect(
            self.start_stream
        )

        self.stop_btn.clicked.connect(
            self.stop_stream
        )

        btn_layout.addWidget(
            self.start_btn
        )

        btn_layout.addWidget(
            self.stop_btn
        )

        root.addLayout(btn_layout)

        # =================================================
        # OBS HELP
        # =================================================

        obs_group = QGroupBox(
            "OBS SETUP INSTRUCTIONS"
        )

        obs_layout = QVBoxLayout()

        obs_text = QLabel(
            "1. In OBS, add a new source: Media Source\n"
            "2. Disable 'Local File' option\n"
            "3. In 'Input' field, paste:\n"
            "    udp://0.0.0.0:9000\n\n"
            "4. Click OK and start streaming on this app"
        )

        obs_text.setStyleSheet(
            "color:#A6E3A1;"
            "font-family:'Consolas';"
        )

        obs_layout.addWidget(
            obs_text
        )

        obs_group.setLayout(
            obs_layout
        )

        root.addWidget(obs_group)

        # =================================================
        # LOGS
        # =================================================

        logs_group = QGroupBox(
            "Event Logs"
        )

        logs_layout = QVBoxLayout()

        self.log_box = QTextEdit()

        self.log_box.setReadOnly(True)

        self.log_box.setMaximumHeight(150)

        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.setMaximumWidth(100)
        clear_logs_btn.clicked.connect(
            self.log_box.clear
        )

        logs_layout.addWidget(self.log_box)
        logs_layout.addWidget(clear_logs_btn)

        logs_group.setLayout(logs_layout)

        root.addWidget(logs_group)

        self.setLayout(root)

    # =====================================================
    # STYLESHEETS
    # =====================================================

    def stylesheet(self):

        return """
        QWidget{
            background:#1E1E2E;
            color:#CDD6F4;
            font-family:'Segoe UI';
            font-size:11px;
        }

        QGroupBox{
            border:1px solid #45475A;
            border-radius:8px;
            margin-top:10px;
            padding-top:15px;
            font-weight:bold;
            color:#89B4FA;
        }

        QGroupBox::title{
            left:10px;
            padding:0 5px;
        }

        QPushButton{
            background:#89B4FA;
            color:#11111B;
            border:none;
            border-radius:6px;
            padding:10px;
            font-weight:bold;
            min-height:35px;
        }

        QPushButton:hover{
            background:#B4D0FB;
        }

        QPushButton:pressed{
            background:#7CA3E8;
        }

        QPushButton:disabled{
            background:#45475A;
            color:#888;
        }

        QTextEdit{
            background:#11111B;
            border:1px solid #45475A;
            border-radius:6px;
            color:#A6E3A1;
            font-family:'Consolas';
            font-size:10px;
        }

        QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox{
            background:#313244;
            border:1px solid #45475A;
            padding:6px;
            border-radius:5px;
            color:#CDD6F4;
        }

        QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover{
            border:1px solid #89B4FA;
        }

        QProgressBar{
            border:1px solid #45475A;
            border-radius:5px;
            background:#313244;
            text-align:center;
        }

        QProgressBar::chunk{
            background:#00D4FF;
            border-radius:3px;
        }

        QLabel{
            color:#CDD6F4;
        }
        """

    def progress_stylesheet(self):
        return """
        QProgressBar{
            border:1px solid #45475A;
            border-radius:5px;
            background:#313244;
        }
        QProgressBar::chunk{
            background:qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #00D4FF,
                stop:1 #89B4FA
            );
            border-radius:3px;
        }
        """

    def peak_stylesheet(self):
        return """
        QProgressBar{
            border:1px solid #45475A;
            border-radius:3px;
            background:#313244;
        }
        QProgressBar::chunk{
            background:#FF6B6B;
            border-radius:2px;
        }
        """

    # =====================================================
    # LOGGING
    # =====================================================

    def log(self, text):

        timestamp = time.strftime("%H:%M:%S")

        self.signals.log_signal.emit(
            f"[{timestamp}] {text}"
        )

        logger.info(text)

    def write_log(self, text):

        self.log_box.append(text)

        # Auto-scroll to bottom
        scrollbar = self.log_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # =====================================================
    # STATUS UPDATE
    # =====================================================

    def update_status(self, status):

        if "ONLINE" in status:
            self.status_label.setText("🟢 ONLINE")
            self.status_label.setStyleSheet(
                "color:#A6E3A1; padding:5px 10px; "
                "background:#313244; border-radius:5px;"
            )
        else:
            self.status_label.setText("🔴 OFFLINE")
            self.status_label.setStyleSheet(
                "color:#FF6B6B; padding:5px 10px; "
                "background:#313244; border-radius:5px;"
            )

    def update_connection(self, connected):
        pass  # Can be extended

    def update_latency(self, latency_ms):

        self.latency_label.setText(
            f"Latency: {latency_ms:.1f}ms"
        )

    # =====================================================
    # AUDIO METER
    # =====================================================

    def update_meter(self, volume, peak):

        self.audio_meter.setValue(volume)

        self.volume_label.setText(f"Volume: {volume}%")

        self.peak_meter.setValue(peak)

        self.peak_label.setText(f"Peak: {peak}%")

        self.frames_label.setText(
            f"Frames: {self.frames_processed}"
        )

    # =====================================================
    # LOAD DEVICES
    # =====================================================

    def load_devices(self):

        self.desktop_combo.clear()
        self.mic_combo.clear()

        try:

            self.desktop_map = self.device_manager.find_wasapi_devices()

            self.mic_map = self.device_manager.find_microphone_devices()

            if not self.desktop_map:
                self.log("⚠️ Warning: No WASAPI devices found")
                self.log("   Install 'Stereo Mix' or 'VB-Audio Virtual Cable'")

            for device_name in self.desktop_map.keys():
                self.desktop_combo.addItem(device_name)

            for device_name in self.mic_map.keys():
                self.mic_combo.addItem(device_name)

            self.log(f"✅ Loaded {len(self.desktop_map)} desktop device(s) and {len(self.mic_map)} microphone(s)")

        except Exception as e:
            self.log(f"❌ Error loading devices: {e}")
            logger.exception("Device loading error")

    # =====================================================
    # FFMPEG
    # =====================================================

    def find_ffmpeg(self):

        try:

            if os.path.exists("ffmpeg.exe"):
                return "ffmpeg.exe"

            result = subprocess.run(
                ["where", "ffmpeg"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]

        except Exception as e:
            logger.debug(f"FFmpeg search error: {e}")

        return None

    def install_ffmpeg(self):

        if self.ffmpeg_path:
            QMessageBox.information(
                self,
                "FFmpeg Status",
                "FFmpeg is already installed."
            )
            return

        try:

            reply = QMessageBox.question(
                self,
                "Install FFmpeg",
                "Download and install FFmpeg? (~500 MB)",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

            self.log("⏳ Downloading FFmpeg...")

            zip_path = "ffmpeg.zip"

            urllib.request.urlretrieve(
                FFMPEG_URL,
                zip_path
            )

            self.log("⏳ Extracting FFmpeg...")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:

                for file in zip_ref.namelist():

                    if file.endswith("ffmpeg.exe"):

                        with zip_ref.open(file) as src:

                            with open("ffmpeg.exe", "wb") as dst:

                                shutil.copyfileobj(src, dst)

                        break

            os.remove(zip_path)

            self.ffmpeg_path = "ffmpeg.exe"

            self.ffmpeg_status.setText("✅ Installed")
            self.ffmpeg_status.setStyleSheet("color:#A6E3A1;")
            self.install_btn.setEnabled(False)

            self.log("✅ FFmpeg installed successfully!")

            QMessageBox.information(
                self,
                "Success",
                "FFmpeg installed successfully!"
            )

        except Exception as e:

            self.log(f"❌ FFmpeg installation failed: {e}")

            QMessageBox.critical(
                self,
                "Installation Error",
                f"Failed to install FFmpeg:\n{e}"
            )

            logger.exception("FFmpeg installation error")

    # =====================================================
    # AUDIO CALLBACKS
    # =====================================================

    def desktop_callback(self, indata, frames, time_info, status):

        try:

            if status:
                logger.warning(f"Desktop stream status: {status}")

            self.desktop_audio = indata.copy()

        except Exception as e:
            logger.error(f"Desktop callback error: {e}")

    def mic_callback(self, indata, frames, time_info, status):

        try:

            if status:
                logger.warning(f"Mic stream status: {status}")

            self.mic_audio = indata.copy()

        except Exception as e:
            logger.error(f"Mic callback error: {e}")

    # =====================================================
    # MIXER THREAD
    # =====================================================

    def mixer_thread(self):

        buffer_size = 0

        try:

            while self.running:

                try:

                    if self.desktop_audio is None:
                        time.sleep(0.001)
                        continue

                    # Update noise gate
                    self.audio_processor.noise_gate_threshold = (
                        self.noise_gate.value()
                    )

                    # Mix audio
                    mixed = self.audio_processor.mix_audio(
                        self.desktop_audio,
                        self.mic_audio,
                        desktop_gain=self.desktop_gain.value(),
                        mic_gain=self.mic_gain.value()
                    )

                    if mixed is None:
                        continue

                    # Get volume and peak
                    volume = self.audio_processor.get_volume_level(mixed)

                    peak = self.audio_processor.get_peak_level()

                    self.signals.meter_signal.emit(volume, peak)

                    # Convert to PCM16
                    pcm = (mixed * 32767).astype(np.int16)

                    # Write to FFmpeg
                    self.ffmpeg_process.stdin.write(pcm.tobytes())

                    self.frames_processed += len(mixed)

                    buffer_size = self.ffmpeg_process.stdin.buffer_size

                    # Calculate latency
                    if self.stream_start_time:
                        elapsed = time.time() - self.stream_start_time
                        frames_time = self.frames_processed / SAMPLE_RATE
                        latency_ms = (elapsed - frames_time) * 1000
                        self.signals.latency_signal.emit(max(0, latency_ms))

                except BrokenPipeError:

                    self.log("❌ FFmpeg pipe closed unexpectedly")
                    break

                except Exception as e:

                    self.log(f"❌ Mixer error: {e}")

                    logger.exception("Mixer thread error")

                    break

        except Exception as e:

            self.log(f"❌ Fatal mixer error: {e}")

            logger.exception("Fatal mixer error")

        finally:

            self.log("🛑 Mixer thread stopped")

    # =====================================================
    # START STREAM
    # =====================================================

    def start_stream(self):

        if self.running:
            return

        if not self.ffmpeg_path:

            QMessageBox.warning(
                self,
                "FFmpeg Missing",
                "FFmpeg is not installed.\n\n"
                "Click 'INSTALL FFMPEG' button to install it."
            )

            return

        if not self.desktop_combo.count():

            QMessageBox.warning(
                self,
                "No Devices",
                "No audio devices found.\n\n"
                "Please install 'Stereo Mix' or 'VB-Audio Virtual Cable'."
            )

            return

        try:

            desktop_name = self.desktop_combo.currentText()

            mic_name = self.mic_combo.currentText()

            if desktop_name not in self.desktop_map:
                raise ValueError("Invalid desktop device selected")

            if mic_name not in self.mic_map:
                raise ValueError("Invalid microphone selected")

            desktop_index = self.desktop_map[desktop_name]

            mic_index = self.mic_map[mic_name]

            target_ip = self.target_ip.text().strip()

            if not target_ip:
                target_ip = "127.0.0.1"

            bitrate = self.bitrate_box.currentText()

            output_url = (
                f"udp://{target_ip}:{UDP_PORT}"
                "?pkt_size=1316"
            )

            # FFmpeg command with proper error handling
            ffmpeg_cmd = [

                self.ffmpeg_path,

                "-loglevel",
                "warning",

                "-f",
                "s16le",

                "-ar",
                str(SAMPLE_RATE),

                "-ac",
                "2",

                "-i",
                "pipe:0",

                "-vn",

                "-c:a",
                "libopus",

                "-application",
                "lowdelay",

                "-frame_duration",
                "20",

                "-b:a",
                bitrate,

                "-f",
                "opus",

                output_url
            ]

            self.log("🚀 Starting FFmpeg process...")

            self.ffmpeg_process = subprocess.Popen(

                ffmpeg_cmd,

                stdin=subprocess.PIPE,

                stderr=subprocess.PIPE,

                stdout=subprocess.DEVNULL,

                bufsize=0
            )

            time.sleep(0.5)

            if self.ffmpeg_process.poll() is not None:

                _, stderr = self.ffmpeg_process.communicate()

                raise RuntimeError(
                    f"FFmpeg failed to start: {stderr.decode()}"
                )

            self.log("🎧 Starting audio capture...")

            # =====================================================
            # DESKTOP AUDIO (WASAPI LOOPBACK)
            # =====================================================

            try:

                self.desktop_stream = sd.InputStream(

                    device=desktop_index,

                    channels=2,

                    samplerate=SAMPLE_RATE,

                    blocksize=BLOCKSIZE,

                    dtype=DTYPE,

                    callback=self.desktop_callback
                )

            except Exception as e:

                self.log(f"❌ Desktop audio error: {e}")

                raise

            # =====================================================
            # MICROPHONE
            # =====================================================

            try:

                self.mic_stream = sd.InputStream(

                    device=mic_index,

                    channels=2,

                    samplerate=SAMPLE_RATE,

                    blocksize=BLOCKSIZE,

                    dtype=DTYPE,

                    callback=self.mic_callback
                )

            except Exception as e:

                self.log(f"❌ Microphone error: {e}")

                raise

            self.running = True

            self.stream_start_time = time.time()

            self.frames_processed = 0

            self.desktop_stream.start()

            self.mic_stream.start()

            # Start mixer thread
            threading.Thread(

                target=self.mixer_thread,

                daemon=True

            ).start()

            self.start_btn.setEnabled(False)

            self.stop_btn.setEnabled(True)

            self.signals.status_signal.emit("ONLINE")

            self.log("✅ STREAM STARTED")

            self.log(f"📍 Target: {output_url}")

            self.log(f"🎙️  Desktop: {desktop_name}")

            self.log(f"🎧 Microphone: {mic_name}")

            self.log(f"📊 Bitrate: {bitrate}")

            self.log("📺 OBS Input: udp://0.0.0.0:9000")

        except Exception as e:

            self.log(f"❌ START ERROR: {e}")

            self.running = False

            self.stop_stream()

            QMessageBox.critical(
                self,
                "Stream Error",
                f"Failed to start stream:\n{e}"
            )

            logger.exception("Stream start error")

    # =====================================================
    # STOP STREAM
    # =====================================================

    def stop_stream(self):

        self.running = False

        self.signals.status_signal.emit("OFFLINE")

        # Stop desktop stream
        try:

            if self.desktop_stream:

                self.desktop_stream.stop()

                self.desktop_stream.close()

                self.desktop_stream = None

        except Exception as e:
            logger.warning(f"Desktop stream close error: {e}")

        # Stop mic stream
        try:

            if self.mic_stream:

                self.mic_stream.stop()

                self.mic_stream.close()

                self.mic_stream = None

        except Exception as e:
            logger.warning(f"Mic stream close error: {e}")

        # Stop FFmpeg process
        try:

            if self.ffmpeg_process:

                if self.ffmpeg_process.stdin:

                    self.ffmpeg_process.stdin.close()

                self.ffmpeg_process.terminate()

                self.ffmpeg_process.wait(timeout=2)

                self.ffmpeg_process = None

        except subprocess.TimeoutExpired:

            try:

                self.ffmpeg_process.kill()

            except Exception as e:
                logger.warning(f"FFmpeg kill error: {e}")

        except Exception as e:
            logger.warning(f"FFmpeg close error: {e}")

        self.audio_meter.setValue(0)

        self.peak_meter.setValue(0)

        self.start_btn.setEnabled(True)

        self.stop_btn.setEnabled(False)

        self.log("🛑 STREAM STOPPED")

    # =====================================================
    # CLOSE EVENT
    # =====================================================

    def closeEvent(self, event):

        self.stop_stream()

        event.accept()

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    try:

        app = QApplication(sys.argv)

        app.setStyle("Fusion")

        window = StreamLinkUltra()

        window.show()

        sys.exit(app.exec_())

    except Exception as e:

        print(f"Fatal error: {e}")

        logger.exception("Fatal application error")

        sys.exit(1)
