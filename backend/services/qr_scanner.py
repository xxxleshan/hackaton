import cv2

def scan_qr_code(image_path: str) -> str:
    image = cv2.imread(image_path)
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(image)
    if not data:
        return None
    print(data)
    return data
