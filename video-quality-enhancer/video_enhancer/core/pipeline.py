"""
خط المعالجة - Processing Pipeline
"""

import cv2
import numpy as np
from typing import List, Callable, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Stage:
    """مرحلة معالجة"""
    name: str
    func: Callable
    params: Dict[str, Any]


class Pipeline:
    """
    خط معالجة مخصص للفيديو
    السماح بإضافة مراحل معالجة متعددة
    """
    
    def __init__(self, device: str = 'cuda'):
        """
        إنشاء خط معالجة
        
        Args:
            device: جهاز المعالجة
        """
        self.device = device
        self.stages: List[Stage] = []
    
    def add_stage(
        self,
        stage_name: str,
        func: Callable = None,
        **params
    ) -> 'Pipeline':
        """
        إضافة مرحلة معالجة
        
        Args:
            stage_name: اسم المرحلة
            func: دالة المعالجة
            **params: معاملات المرحلة
        
        Returns:
            Pipeline: للسماح بـ chaining
        """
        
        # اختيار الدالة بناءً على الاسم إذا لم تُحدد
        if func is None:
            func = self._get_default_processor(stage_name)
        
        stage = Stage(
            name=stage_name,
            func=func,
            params=params
        )
        
        self.stages.append(stage)
        logger.info(f"✓ تمت إضافة مرحلة: {stage_name}")
        return self
    
    def _get_default_processor(self, stage_name: str) -> Callable:
        """الحصول على معالج افتراضي"""
        processors = {
            'denoise': self._denoise,
            'super_resolution': self._super_resolution,
            'color_correction': self._color_correction,
            'interpolate_fps': self._interpolate_fps,
            'hdr': self._hdr_processing,
            'sharpening': self._sharpening,
            'contrast': self._contrast_enhancement,
        }
        
        if stage_name not in processors:
            raise ValueError(f"مرحلة غير معروفة: {stage_name}")
        
        return processors[stage_name]
    
    def process(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        معالجة الفيديو عبر الخط
        
        Args:
            input_path: مسار الفيديو المدخل
            output_path: مسار الفيديو المحسّن
        
        Returns:
            معلومات المعالجة
        """
        logger.info(f"بدء المعالجة عبر الخط: {len(self.stages)} مرحلة")
        
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError(f"لا يمكن فتح الفيديو: {input_path}")
        
        # معلومات الفيديو
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # إعداد الكاتب
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            (width, height)
        )
        
        frame_num = 0
        from tqdm import tqdm
        
        with tqdm(total=frame_count, desc="معالجة الفيديو") as pbar:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # تطبيق جميع المراحل
                for stage in self.stages:
                    frame = stage.func(frame, **stage.params)
                
                out.write(frame)
                frame_num += 1
                pbar.update(1)
        
        cap.release()
        out.release()
        
        result = {
            'input': input_path,
            'output': output_path,
            'frames_processed': frame_num,
            'stages': [s.name for s in self.stages],
            'status': 'completed'
        }
        
        logger.info(f"✓ تمت المعالجة بنجاح: {frame_num} إطار")
        return result
    
    # معالجات افتراضية
    
    @staticmethod
    def _denoise(frame: np.ndarray, strength: float = 0.5, **kwargs) -> np.ndarray:
        """إزالة الضوضاء"""
        h = int(10 * strength)
        return cv2.fastNlMeansDenoisingColored(
            frame,
            h=h,
            hForColorComponents=10,
            templateWindowSize=7,
            searchWindowSize=21
        )
    
    @staticmethod
    def _super_resolution(frame: np.ndarray, scale: int = 4, **kwargs) -> np.ndarray:
        """التحسين الفائق"""
        height, width = frame.shape[:2]
        new_size = (width * scale, height * scale)
        return cv2.resize(frame, new_size, interpolation=cv2.INTER_CUBIC)
    
    @staticmethod
    def _color_correction(
        frame: np.ndarray,
        saturation: float = 1.0,
        contrast: float = 1.0,
        **kwargs
    ) -> np.ndarray:
        """تصحيح الألوان"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # تحسين التشبع
        hsv[:, :, 1] *= saturation
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        
        # تحسين الإضاءة
        hsv[:, :, 2] *= contrast
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    @staticmethod
    def _interpolate_fps(frame: np.ndarray, target_fps: int = 60, **kwargs) -> np.ndarray:
        """تحسين معدل الإطارات"""
        return frame
    
    @staticmethod
    def _hdr_processing(frame: np.ndarray, **kwargs) -> np.ndarray:
        """معالجة HDR"""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    @staticmethod
    def _sharpening(frame: np.ndarray, strength: float = 1.0, **kwargs) -> np.ndarray:
        """الشحذ"""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]]) / (1.0 + strength)
        return cv2.filter2D(frame, -1, kernel)
    
    @staticmethod
    def _contrast_enhancement(frame: np.ndarray, factor: float = 1.2, **kwargs) -> np.ndarray:
        """تحسين التباين"""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        l = cv2.convertScaleAbs(l, alpha=factor, beta=0)
        
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)