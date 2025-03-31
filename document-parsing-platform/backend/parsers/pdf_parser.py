import PyPDF2
import io
from typing import Dict, Any
from PIL import Image
import pytesseract
import cv2
import numpy as np
import json

class PDFParser:
    def __init__(self, ocr_languages: list = ['eng']):
        self.ocr_languages = ocr_languages
        self.handwriting_languages = ['ben']  # Bengali support

    def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse a PDF file and extract text, images, and metadata"""
        result = {
            'text': '',
            'tables': [],
            'images': [],
            'metadata': {}
        }

        try:
            with open(file_path, 'rb') as file:
                # Extract text and metadata
                pdf_reader = PyPDF2.PdfReader(file)
                result['metadata']['pages'] = len(pdf_reader.pages)
                result['metadata']['author'] = pdf_reader.metadata.get('/Author', '')
                result['metadata']['title'] = pdf_reader.metadata.get('/Title', '')
                result['metadata']['created'] = pdf_reader.metadata.get('/CreationDate', '')

                # Process each page
                for page_num, page in enumerate(pdf_reader.pages):
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        result['text'] += f"\n\n--- Page {page_num + 1} ---\n{page_text}"

                    # Extract images
                    if '/XObject' in page['/Resources']:
                        x_object = page['/Resources']['/XObject'].get_object()
                        for obj in x_object:
                            if x_object[obj]['/Subtype'] == '/Image':
                                image = self._extract_pdf_image(x_object[obj])
                                if image:
                                    ocr_text = self._perform_ocr(image)
                                    result['images'].append({
                                        'page': page_num + 1,
                                        'text': ocr_text,
                                        'base64': self._image_to_base64(image)
                                    })

            return result

        except Exception as e:
            raise Exception(f"PDF parsing failed: {str(e)}")

    def _extract_pdf_image(self, image_obj) -> Image.Image:
        """Extract image from PDF XObject"""
        try:
            if image_obj['/Filter'] == '/FlateDecode':
                data = image_obj.get_data()
                return Image.open(io.BytesIO(data))
            elif image_obj['/Filter'] == '/DCTDecode':
                return Image.open(io.BytesIO(image_obj.get_data()))
            elif image_obj['/Filter'] == '/JPXDecode':
                return Image.open(io.BytesIO(image_obj.get_data()))
        except:
            return None

    def _perform_ocr(self, image: Image.Image) -> str:
        """Perform OCR on an image with support for multiple languages"""
        try:
            # Convert to OpenCV format
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Preprocessing for better OCR
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Combine all languages (English + any handwriting languages)
            languages = '+'.join(self.ocr_languages + self.handwriting_languages)
            return pytesseract.image_to_string(thresh, lang=languages)
        except Exception as e:
            print(f"OCR failed: {str(e)}")
            return ""

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL image to base64 string"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def to_json(self, result: Dict[str, Any]) -> str:
        """Convert parsing result to JSON"""
        return json.dumps(result, indent=2)

if __name__ == '__main__':
    # Example usage
    parser = PDFParser(ocr_languages=['eng', 'ben'])
    result = parser.parse('sample.pdf')
    print(parser.to_json(result))