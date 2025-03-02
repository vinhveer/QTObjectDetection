import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from functools import lru_cache

class ImageUtils:
    """Utility class for image processing and display operations"""
    
    _COLOR_CACHE = {}  # Class-level cache for colors
    
    @staticmethod
    def cv_to_qimage(cv_img):
        """
        Convert OpenCV image (numpy array) to QImage
        
        Args:
            cv_img: OpenCV image in BGR or RGB format
            
        Returns:
            QImage object
        """
        if cv_img is None:
            return QImage()
            
        # Check image format
        if len(cv_img.shape) == 3 and cv_img.shape[2] == 3:
            # Color image (RGB assumed)
            height, width, channels = cv_img.shape
            bytes_per_line = channels * width
            return QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        elif len(cv_img.shape) == 2:
            # Grayscale image
            height, width = cv_img.shape
            bytes_per_line = width
            return QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        
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
        if pixmap.isNull() or widget is None:
            return pixmap
            
        # Get widget dimensions
        target_width = max(widget.width(), 1)  # Prevent division by zero
        target_height = max(widget.height(), 1)
        
        # Efficient scaling using Qt's built-in methods
        scale_mode = Qt.KeepAspectRatio if keep_aspect_ratio else Qt.IgnoreAspectRatio
        return pixmap.scaled(
            target_width,
            target_height,
            scale_mode,
            Qt.SmoothTransformation
        )
    
    @staticmethod
    def display_image_in_widget(cv_img, widget, keep_aspect_ratio=True):
        """
        Display an OpenCV image in a Qt widget with optimized processing
        
        Args:
            cv_img: OpenCV image
            widget: Target widget (QLabel or compatible)
            keep_aspect_ratio: Whether to maintain aspect ratio
        """
        if cv_img is None or widget is None:
            if widget:
                widget.clear()
            return
        
        # Check if widget has a reasonable size
        if widget.width() <= 1 or widget.height() <= 1:
            # Widget not properly sized yet, set a minimum size
            widget.setMinimumSize(10, 10)
        
        # Chain conversion operations efficiently
        pixmap = ImageUtils.cv_to_pixmap(cv_img)
        if not pixmap.isNull():
            scaled_pixmap = ImageUtils.scale_pixmap_to_widget(
                pixmap, widget, keep_aspect_ratio
            )
            widget.setPixmap(scaled_pixmap)
    
    @staticmethod
    @lru_cache(maxsize=128)  # Cache results for better performance
    def get_color_for_class(class_id):
        """
        Generate a consistent color for a class ID with caching
        
        Args:
            class_id: Class identifier (int or hashable)
            
        Returns:
            Tuple of (B, G, R) values for OpenCV
        """
        # Check cache first
        if class_id in ImageUtils._COLOR_CACHE:
            return ImageUtils._COLOR_CACHE[class_id]
        
        # Generate deterministic color based on golden ratio
        hue = (((hash(class_id) if not isinstance(class_id, int) else class_id) * 0.618033988749895) % 1.0) * 360
        
        # HSV to RGB conversion (more visually distinct than random RGB)
        h = hue / 60.0
        s = 0.85  # High saturation for vivid colors
        v = 0.9   # High value for visibility
        
        hi = int(h) % 6
        f = h - int(h)
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        r, g, b = 0, 0, 0
        if hi == 0:
            r, g, b = v, t, p
        elif hi == 1:
            r, g, b = q, v, p
        elif hi == 2:
            r, g, b = p, v, t
        elif hi == 3:
            r, g, b = p, q, v
        elif hi == 4:
            r, g, b = t, p, v
        elif hi == 5:
            r, g, b = v, p, q
        
        # Convert to 0-255 range and BGR for OpenCV
        color = (int(b * 255), int(g * 255), int(r * 255))
        
        # Store in cache
        ImageUtils._COLOR_CACHE[class_id] = color
        
        return color
    
    @staticmethod
    def convert_rgb_to_bgr(image):
        """
        Convert RGB image to BGR (for saving with OpenCV)
        
        Args:
            image: RGB image
            
        Returns:
            BGR image
        """
        if image is None or len(image.shape) != 3 or image.shape[2] != 3:
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
        if image is None or len(image.shape) != 3 or image.shape[2] != 3:
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
            color: (B, G, R) tuple or None to auto-generate
            
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
        
        # Extract and validate coordinates
        x1, y1, x2, y2 = map(int, bbox[:4])
        
        # Ensure coordinates are within image boundaries
        height, width = draw_img.shape[:2]
        x1 = max(0, min(x1, width - 1))
        y1 = max(0, min(y1, height - 1))
        x2 = max(0, min(x2, width - 1))
        y2 = max(0, min(y2, height - 1))
        
        # Skip if box is invalid
        if x2 <= x1 or y2 <= y1:
            return draw_img
        
        # Draw rectangle with antialiasing
        cv2.rectangle(draw_img, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)
        
        # Prepare label with confidence
        text = f"{label}: {confidence:.2f}"
        font_scale = 0.5
        thickness = 1
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness
        )
        
        # Ensure label background stays within image
        bg_y1 = max(0, y1 - text_height - 5)
        
        # Draw label background
        cv2.rectangle(
            draw_img, 
            (x1, bg_y1), 
            (min(x1 + text_width, width - 1), y1), 
            color, 
            -1
        )
        
        # Draw text with better positioning and antialiasing
        cv2.putText(
            draw_img,
            text,
            (x1, max(y1 - 5, text_height)),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA
        )
        
        return draw_img
    
    @staticmethod
    def resize_image_with_aspect_ratio(image, target_width=None, target_height=None):
        """
        Resize image while maintaining aspect ratio
        
        Args:
            image: OpenCV image
            target_width: Desired width (if None, calculated from height)
            target_height: Desired height (if None, calculated from width)
            
        Returns:
            Resized image
        """
        if image is None:
            return None
            
        if target_width is None and target_height is None:
            return image
            
        height, width = image.shape[:2]
        
        # Calculate new dimensions
        if target_width is None:
            aspect_ratio = width / height
            target_width = int(target_height * aspect_ratio)
        elif target_height is None:
            aspect_ratio = height / width
            target_height = int(target_width * aspect_ratio)
            
        # Perform resize with better quality
        return cv2.resize(
            image, 
            (target_width, target_height), 
            interpolation=cv2.INTER_AREA if target_width < width else cv2.INTER_CUBIC
        )
    
    @staticmethod
    def add_text_overlay(image, text, position=(10, 30), font_scale=1.0, 
                        color=(255, 255, 255), thickness=2, with_background=True):
        """
        Add text overlay to an image
        
        Args:
            image: OpenCV image
            text: Text to display
            position: (x, y) position
            font_scale: Font scale
            color: Text color (B, G, R)
            thickness: Text thickness
            with_background: Whether to draw a background behind the text
            
        Returns:
            Image with text overlay
        """
        if image is None or not text:
            return image
            
        result = image.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness
        )
        
        x, y = position
        
        # Add background for better readability
        if with_background:
            bg_color = (0, 0, 0)
            cv2.rectangle(
                result,
                (x - 5, y - text_height - 5),
                (x + text_width + 5, y + 5),
                bg_color,
                -1
            )
            
        # Draw text
        cv2.putText(
            result,
            text,
            position,
            font,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )
        
        return result