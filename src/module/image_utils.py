import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

class ImageUtils:
    @staticmethod
    def cv_to_qimage(cv_img):
        """
        Convert OpenCV image (numpy array) to QImage
        
        Args:
            cv_img: OpenCV image in BGR or RGB format
            
        Returns:
            QImage object
        """
        # Ensure RGB format (OpenCV uses BGR by default)
        if len(cv_img.shape) == 3 and cv_img.shape[2] == 3:
            if isinstance(cv_img[0, 0, 0], np.uint8):
                # Already in RGB format (we assume the input is RGB in this module)
                rgb_img = cv_img
                height, width, channels = rgb_img.shape
                bytes_per_line = channels * width
                return QImage(rgb_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # Fallback for other formats
        return QImage()
    
    @staticmethod
    def cv_to_pixmap(cv_img):
        """
        Convert OpenCV image to QPixmap
        
        Args:
            cv_img: OpenCV image
            
        Returns:
            QPixmap object
        """
        return QPixmap.fromImage(ImageUtils.cv_to_qimage(cv_img))
    
    @staticmethod
    def scale_pixmap_to_widget(pixmap, widget, keep_aspect_ratio=True):
        """
        Scale a QPixmap to fit in a widget
        
        Args:
            pixmap: QPixmap to scale
            widget: Target widget (should have width() and height() methods)
            keep_aspect_ratio: Whether to maintain aspect ratio
            
        Returns:
            Scaled QPixmap
        """
        if pixmap.isNull():
            return pixmap
            
        target_width = widget.width()
        target_height = widget.height()
        
        if keep_aspect_ratio:
            return pixmap.scaled(
                target_width,
                target_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        else:
            return pixmap.scaled(
                target_width,
                target_height,
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
    
    @staticmethod
    def display_image_in_widget(cv_img, widget, keep_aspect_ratio=True):
        """
        Display an OpenCV image in a Qt widget
        
        Args:
            cv_img: OpenCV image
            widget: Target widget (QLabel or compatible)
            keep_aspect_ratio: Whether to maintain aspect ratio
        """
        if cv_img is None:
            widget.clear()
            return
            
        qimage = ImageUtils.cv_to_qimage(cv_img)
        pixmap = QPixmap.fromImage(qimage)
        scaled_pixmap = ImageUtils.scale_pixmap_to_widget(pixmap, widget, keep_aspect_ratio)
        widget.setPixmap(scaled_pixmap)
    
    @staticmethod
    def get_color_for_class(class_id):
        """
        Generate a consistent color for a class ID
        
        Args:
            class_id: Class identifier (int or hashable)
            
        Returns:
            Tuple of (R, G, B) values
        """
        # Ensure consistent colors by setting seed with class_id
        np.random.seed(hash(class_id) if not isinstance(class_id, int) else class_id)
        return tuple(map(int, np.random.randint(0, 255, 3)))
    
    @staticmethod
    def convert_rgb_to_bgr(image):
        """
        Convert RGB image to BGR (for saving with OpenCV)
        
        Args:
            image: RGB image
            
        Returns:
            BGR image
        """
        if image is None or len(image.shape) != 3:
            return image
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def convert_bgr_to_rgb(image):
        """
        Convert BGR image to RGB (for display)
        
        Args:
            image: BGR image
            
        Returns:
            RGB image
        """
        if image is None or len(image.shape) != 3:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    @staticmethod
    def draw_bounding_box(image, bbox, label, confidence, color=None):
        """
        Draw a bounding box with label on an image
        
        Args:
            image: OpenCV image to draw on
            bbox: [x1, y1, x2, y2] bounding box coordinates
            label: Class label
            confidence: Detection confidence
            color: (R, G, B) tuple or None to auto-generate
            
        Returns:
            Image with bounding box drawn
        """
        if image is None or bbox is None:
            return image
            
        # Make a copy to avoid modifying the original
        draw_img = image.copy()
        
        # Get color based on class if not provided
        if color is None:
            color = ImageUtils.get_color_for_class(label)
        
        # Extract coordinates
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        
        # Draw rectangle
        cv2.rectangle(draw_img, (x1, y1), (x2, y2), color, 2)
        
        # Prepare label
        text = f"{label}: {confidence:.2f}"
        font_scale = 0.5
        thickness = 1
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )
        
        # Draw label background
        cv2.rectangle(
            draw_img, 
            (x1, y1 - text_height - 5), 
            (x1 + text_width, y1), 
            color, 
            -1
        )
        
        # Draw text
        cv2.putText(
            draw_img,
            text,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA
        )
        
        return draw_img