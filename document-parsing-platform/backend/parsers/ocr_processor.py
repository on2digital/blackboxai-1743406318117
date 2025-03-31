import pytesseract
import cv2
import numpy as np
from PIL import Image
from typing import Optional, List
import logging

class OCRProcessor:
    def __init__(self, languages: List[str] = ['eng'], config: Optional[str] = None):
        """
        Initialize OCR processor with specified languages and Tesseract config
        
        Args:
            languages: List of language codes (e.g., ['eng', 'ben'])
            config: Additional Tesseract config parameters
        """
        self.languages = self._validate_languages(languages)
        self.config = config or '--oem 3 --psm 6'
        self.logger = logging.getLogger(__name__)
        
        # Bangla handwriting specific parameters
        self.bangla_config = {
            'preprocessing': {
                'threshold': True,
                'denoise': True,
                'deskew': True
            },
            'tesseract': {
                'config': '--oem 1 --psm 6'  # LSTM mode for better handwriting recognition
            }
        }

    def process_image(self, image: np.ndarray) -> str:
        """
        Perform OCR on an image with preprocessing
        
        Args:
            image: Input image as numpy array (OpenCV format)
            
        Returns:
            Extracted text
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
            # Apply preprocessing
            processed = self._preprocess_image(image)
            
            # Determine if we need special handling for Bangla
            use_bangla_config = 'ben' in self.languages
            
            # Perform OCR
            custom_config = self.bangla_config['tesseract']['config'] if use_bangla_config else self.config
            lang_param = '+'.join(self.languages)
            
            return pytesseract.image_to_string(
                processed,
                lang=lang_param,
                config=custom_config
            )
            
        except Exception as e:
            self.logger.error(f"OCR processing failed: {str(e)}")
            return ""

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Apply image preprocessing to improve OCR accuracy
        
        Args:
            image: Input grayscale image
            
        Returns:
            Preprocessed image
        """
        # Apply adaptive thresholding
        processed = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Denoising
        processed = cv2.fastNlMeansDenoising(processed, h=10)
        
        # Deskew (if needed)
        if self._needs_deskew(processed):
            processed = self._deskew_image(processed)
            
        return processed

    def _needs_deskew(self, image: np.ndarray) -> bool:
        """
        Detect if image needs deskewing
        """
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is not None:
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
                if abs(angle) > 0.5:  # Only consider significant angles
                    angles.append(angle)
                    
            if angles:
                median_angle = np.median(angles)
                return abs(median_angle) > 0.5
                
        return False

    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Deskew the input image
        """
        # Find all lines in the image
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            angles.append(angle)
            
        median_angle = np.median(angles)
        
        # Rotate the image to deskew
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), 
                                flags=cv2.INTER_CUBIC, 
                                borderMode=cv2.BORDER_REPLICATE)
        
        return rotated

    def _validate_languages(self, languages: List[str]) -> List[str]:
        """
        Validate and normalize language codes
        """
        valid_langs = []
        for lang in languages:
            lang = lang.lower().strip()
            if lang == 'bn' or lang == 'bangla':
                valid_langs.append('ben')  # Tesseract uses 'ben' for Bengali
            elif lang in pytesseract.get_languages():
                valid_langs.append(lang)
            else:
                self.logger.warning(f"Unsupported language code: {lang}")
                
        return valid_langs if valid_langs else ['eng']  # Default to English

    @staticmethod
    def load_image(file_path: str) -> Optional[np.ndarray]:
        """
        Load image from file path
        """
        try:
            image = cv2.imread(file_path)
            if image is not None:
                return image
        except Exception as e:
            logging.error(f"Failed to load image: {str(e)}")
        return None

if __name__ == '__main__':
    # Example usage
    processor = OCRProcessor(languages=['eng', 'ben'])
    image = OCRProcessor.load_image('sample.png')
    if image is not None:
        text = processor.process_image(image)
        print("Extracted Text:")
        print(text)