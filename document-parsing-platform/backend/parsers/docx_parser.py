from docx import Document
from docx.table import Table
from typing import Dict, Any
import json
import base64
from io import BytesIO
from PIL import Image
import pytesseract
import cv2
import numpy as np

class DOCXParser:
    def __init__(self, ocr_languages: list = ['eng']):
        self.ocr_languages = ocr_languages
        self.handwriting_languages = ['ben']  # Bengali support

    def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse a DOCX file and extract text, tables, and images"""
        result = {
            'text': '',
            'tables': [],
            'images': [],
            'metadata': {}
        }

        try:
            doc = Document(file_path)
            
            # Extract metadata
            result['metadata']['author'] = doc.core_properties.author
            result['metadata']['created'] = str(doc.core_properties.created)
            result['metadata']['modified'] = str(doc.core_properties.modified)
            
            # Process document elements
            for element in doc.element.body:
                if element.tag.endswith('p'):  # Paragraph
                    paragraph = element
                    result['text'] += self._extract_paragraph_text(paragraph) + '\n'
                
                elif element.tag.endswith('tbl'):  # Table
                    table = Table(element, doc)
                    result['tables'].append(self._extract_table_data(table))
                
                elif element.tag.endswith('drawing'):  # Image
                    image = self._extract_docx_image(element)
                    if image:
                        ocr_text = self._perform_ocr(image)
                        result['images'].append({
                            'text': ocr_text,
                            'base64': self._image_to_base64(image)
                        })

            return result

        except Exception as e:
            raise Exception(f"DOCX parsing failed: {str(e)}")

    def _extract_paragraph_text(self, paragraph) -> str:
        """Extract text from a paragraph including runs and styles"""
        text = ''
        for run in paragraph.runs:
            text += run.text
        return text.strip()

    def _extract_table_data(self, table: Table) -> list:
        """Convert DOCX table to structured data"""
        table_data = []
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                cell_text = ''
                for paragraph in cell.paragraphs:
                    cell_text += paragraph.text + '\n'
                row_data.append(cell_text.strip())
            table_data.append(row_data)
        return table_data

    def _extract_docx_image(self, element) -> Image.Image:
        """Extract image from DOCX drawing element"""
        try:
            for graphic in element.iterchildren():
                if graphic.tag.endswith('graphic'):
                    for graphic_data in graphic.iterchildren():
                        if graphic_data.tag.endswith('blip'):
                            r_id = graphic_data.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                            if r_id:
                                # In a real implementation, we'd get the image from the document's relationships
                                # This is a simplified version for demonstration
                                return None
        except:
            return None
        return None

    def _perform_ocr(self, image: Image.Image) -> str:
        """Perform OCR on an image with support for multiple languages"""
        try:
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            languages = '+'.join(self.ocr_languages + self.handwriting_languages)
            return pytesseract.image_to_string(thresh, lang=languages)
        except Exception as e:
            print(f"OCR failed: {str(e)}")
            return ""

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def to_json(self, result: Dict[str, Any]) -> str:
        """Convert parsing result to JSON"""
        return json.dumps(result, indent=2)

if __name__ == '__main__':
    # Example usage
    parser = DOCXParser(ocr_languages=['eng', 'ben'])
    result = parser.parse('sample.docx')
    print(parser.to_json(result))