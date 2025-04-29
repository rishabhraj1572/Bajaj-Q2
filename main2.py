import cv2
import pytesseract
import re
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'Tess\tesseract.exe'

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not load image")
    
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text(image):
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config)
    return text

def is_out_of_range(test_value, reference_range):
    """Determine if test_value is outside the reference_range."""
    try:
        
        if '-' in test_value:
            return True 
        
        test_value = float(test_value)
        if not reference_range:
            return True
        ref_min, ref_max = map(float, reference_range.split('-'))
        return not (ref_min <= test_value <= ref_max)
    except (ValueError, TypeError):
        return True 

def parse_lab_results(text):
    results = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        print(f"LINE: {line}") 

        match = re.search(r'^(.*?)\s*(\d+\.\d+)\s*([a-zA-Z/%]*)\s*([0-9.\-–]*\s*[-]?\s*[0-9.\-–]*)', line)
        if match:
            test_name = match.group(1).strip()
            test_value = match.group(2).strip()
            unit = match.group(3).strip() if match.group(3) else ""
            ref_range = match.group(4).strip() if match.group(4) else ""

            ref_range = ref_range.replace('–', '-').strip()

            out_of_range = is_out_of_range(test_value, ref_range)

            results.append({
                "test_name": test_name,
                "test_value": test_value,
                "bio_reference_range": ref_range,
                "test_unit": unit,
                "lab_test_out_of_range": out_of_range
            })
    return results

def process_lab_image(image_path):
    try:
        preprocessed_img = preprocess_image(image_path)
        extracted_text = extract_text(preprocessed_img)
        print("----- OCR TEXT -----")
        print(extracted_text)
        lab_results = parse_lab_results(extracted_text)
        return {
            "is_success": True,
            "data": lab_results
        }
    except Exception as e:
        print(f"Error processing image: {e}")
        return {
            "is_success": False,
            "data": []
        }