import os
import json
import shutil
import cv2
import pandas as pd
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QProgressDialog, QFileDialog
from PySide6.QtCore import Qt

class DataExporter:
    def __init__(self):
        """Initialize DataExporter class"""
        self.last_export_path = None
        
    def get_destination_directory(self, title="Select directory to save data"):
        """
        Show file dialog to get destination directory from user
        
        Args:
            title: Dialog window title
            
        Returns:
            Selected directory path or None if canceled
        """
        directory = QFileDialog.getExistingDirectory(
            None,
            title,
            self.last_export_path or "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if directory:
            self.last_export_path = directory
            
        return directory
        
    def create_output_directories(self, root_dir):
        """
        Create necessary subdirectories for output data
        
        Args:
            root_dir: Root directory path
            
        Returns:
            True if successful, False if failed
        """
        try:
            subdirs = [
                'images/original',
                'images/binding_box',
                'images/warm_up',
                'data_excel',
                'data_json'
            ]
            
            for subdir in subdirs:
                full_path = os.path.join(root_dir, subdir)
                os.makedirs(full_path, exist_ok=True)
                
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to create directories: {str(e)}")
            return False
            
    def generate_base_filename(self, prefix="detection"):
        """
        Generate a base filename with timestamp
        
        Args:
            prefix: Filename prefix
            
        Returns:
            Base filename with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}"
        
    def copy_image_files(self, source_paths, root_dir, base_filename):
        """
        Copy image files to destination directory
        
        Args:
            source_paths: Dictionary with paths to source files
            root_dir: Root destination directory
            base_filename: Base filename to use
            
        Returns:
            Dictionary with destination paths
        """
        # Define destination paths
        dest_paths = {
            'original_path': os.path.join(root_dir, 'images/original', f"{base_filename}.jpg"),
            'binding_box_path': os.path.join(root_dir, 'images/binding_box', f"{base_filename}.jpg"),
            'warmup_path': os.path.join(root_dir, 'images/warm_up', f"{base_filename}.jpg")
        }

        # Map source keys to destination keys
        source_to_dest = {
            'original_path': 'original_path',
            'binding_box_path': 'binding_box_path',
            'warmup_path': 'warmup_path'
        }

        # Copy each file
        for src_key, dst_key in source_to_dest.items():
            if src_key in source_paths and source_paths[src_key]:
                shutil.copy2(source_paths[src_key], dest_paths[dst_key])
                
        return dest_paths
        
    def save_images_directly(self, images, root_dir, base_filename):
        """
        Save images directly to destination directory
        
        Args:
            images: Dictionary with image data (numpy arrays)
            root_dir: Root destination directory
            base_filename: Base filename to use
            
        Returns:
            Dictionary with saved file paths
        """
        # Define destination paths
        dest_paths = {
            'original_path': os.path.join(root_dir, 'images/original', f"{base_filename}.jpg"),
            'binding_box_path': os.path.join(root_dir, 'images/binding_box', f"{base_filename}.jpg"),
            'warmup_path': os.path.join(root_dir, 'images/warm_up', f"{base_filename}.jpg")
        }
        
        # Map image keys to destination keys
        image_to_dest = {
            'original': 'original_path',
            'binding_box': 'binding_box_path',
            'warm_up': 'warmup_path'
        }
        
        # Save each image
        for img_key, dst_key in image_to_dest.items():
            if img_key in images and images[img_key] is not None:
                # Convert RGB to BGR for OpenCV saving
                bgr_image = cv2.cvtColor(images[img_key], cv2.COLOR_RGB2BGR)
                cv2.imwrite(dest_paths[dst_key], bgr_image)
                
        return dest_paths
        
    def save_json_data(self, root_dir, base_filename, timestamp, detections, image_paths=None):
        """
        Save detection data in JSON format
        
        Args:
            root_dir: Root directory path
            base_filename: Base filename to use
            timestamp: Timestamp string
            detections: List of detection objects
            image_paths: Optional dictionary with relative paths to images
            
        Returns:
            Path to saved JSON file
        """
        json_path = os.path.join(root_dir, 'data_json', f"{base_filename}.json")
        
        # Prepare image paths if not provided
        if image_paths is None:
            image_paths = {
                'original_image': f"images/original/{base_filename}.jpg",
                'binding_box_image': f"images/binding_box/{base_filename}.jpg",
                'warm_up_image': f"images/warm_up/{base_filename}.jpg"
            }
        
        # Create JSON data structure
        json_data = {
            'timestamp': timestamp,
            'original_image': image_paths.get('original_image'),
            'binding_box_image': image_paths.get('binding_box_image'),
            'warm_up_image': image_paths.get('warm_up_image'),
            'detections': detections
        }
        
        # Write to file
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=4)
            
        return json_path
        
    def save_excel_data(self, root_dir, base_filename, detections):
        """
        Save detection data in Excel format
        
        Args:
            root_dir: Root directory path
            base_filename: Base filename to use
            detections: List of detection objects
            
        Returns:
            Path to saved Excel file
        """
        excel_path = os.path.join(root_dir, 'data_excel', f"{base_filename}.xlsx")
        
        # Create DataFrames for summary and details
        df_class = pd.DataFrame(columns=['Class', 'Count'])
        df_detail = pd.DataFrame(columns=[
            'Class', 
            'Confidence', 
            'Top', 
            'Left', 
            'Bottom', 
            'Right', 
            'Width', 
            'Height'
        ])
        
        # Process detection data
        class_counts = {}
        for det in detections:
            class_name = det['class']
            confidence = det['confidence']
            bbox = det['bbox']
            
            # Extract bounding box coordinates
            top, left = bbox[1], bbox[0]
            bottom, right = bbox[3], bbox[2]
            width = right - left
            height = bottom - top
            
            # Add to details DataFrame
            df_detail.loc[len(df_detail)] = [
                class_name, 
                confidence, 
                top, 
                left, 
                bottom, 
                right, 
                width, 
                height
            ]
            
            # Count by class
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        # Update summary DataFrame
        for class_name, count in class_counts.items():
            df_class.loc[len(df_class)] = [class_name, count]
        
        # Save to Excel file with multiple sheets
        with pd.ExcelWriter(excel_path) as writer:
            df_class.to_excel(writer, sheet_name='Class Summary', index=False)
            df_detail.to_excel(writer, sheet_name='Detection Details', index=False)
            
        return excel_path
    
    def export_single_frame(self, frames, detections):
        """
        Export a single frame with its detection data
        
        Args:
            frames: Dictionary containing 'original', 'binding_box', and 'warm_up' frames
            detections: List of detection objects
            
        Returns:
            Dictionary with paths to saved files or None if canceled
        """
        # Check if valid data exists
        required_frames = ['original', 'binding_box', 'warm_up']
        if any(frames.get(f) is None for f in required_frames) or not detections:
            QMessageBox.warning(None, "Error", "No frame or detection data to save!")
            return None

        # Let user select destination directory
        root_dir = self.get_destination_directory("Select directory for frame export")
        if not root_dir:
            return None

        try:
            # Create subdirectories
            if not self.create_output_directories(root_dir):
                return None

            # Generate timestamp and base filename
            base_filename = self.generate_base_filename()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save images directly
            paths = self.save_images_directly(frames, root_dir, base_filename)

            # Save JSON and Excel data
            json_path = self.save_json_data(root_dir, base_filename, timestamp, detections)
            excel_path = self.save_excel_data(root_dir, base_filename, detections)

            QMessageBox.information(None, "Success", 
                f"Frame exported to:\n{root_dir}")
                
            return {
                'root_dir': root_dir,
                'base_filename': base_filename,
                'json_path': json_path,
                'excel_path': excel_path,
                'image_paths': paths
            }
                
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error exporting frame: {str(e)}")
            return None
            
    def export_all_frames(self, frame_data):
        """
        Export all frames with detection data
        
        Args:
            frame_data: Dictionary with 'images' and 'detections' lists
            
        Returns:
            Dictionary with export info or None if canceled
        """
        # Check if data exists
        if not frame_data.get('images') or not frame_data.get('detections'):
            QMessageBox.warning(None, "Error", "No detection data to save!")
            return None

        # Let user select destination directory
        root_dir = self.get_destination_directory("Select directory for all frames export")
        if not root_dir:
            return None

        try:
            # Create progress dialog
            progress = QProgressDialog("Saving data...", "Cancel", 0, len(frame_data['images']), None)
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle("Saving Progress")
            progress.setMinimumDuration(0)
            
            # Create subdirectories
            if not self.create_output_directories(root_dir):
                return None

            # Store all paths
            all_paths = {
                'json_paths': [],
                'excel_paths': [],
                'image_paths': []
            }

            # Process each frame
            for i, frame_info in enumerate(frame_data['images']):
                if progress.wasCanceled():
                    break
                    
                progress.setValue(i)
                progress.setLabelText(f"Saving frame {i+1}/{len(frame_data['images'])}...")
                
                # Extract frame information
                timestamp = frame_info['timestamp']
                detections = frame_info['detections']
                base_filename = f"detection_{timestamp}"
                
                try:
                    # Copy image files
                    paths = self.copy_image_files(frame_info, root_dir, base_filename)
                    all_paths['image_paths'].append(paths)
                    
                    # Save JSON and Excel data
                    json_path = self.save_json_data(root_dir, base_filename, timestamp, detections)
                    all_paths['json_paths'].append(json_path)
                    
                    excel_path = self.save_excel_data(root_dir, base_filename, detections)
                    all_paths['excel_paths'].append(excel_path)
                    
                except Exception as e:
                    print(f"Error processing frame {i+1}: {str(e)}")
                    continue

            progress.setValue(len(frame_data['images']))
            
            if not progress.wasCanceled():
                QMessageBox.information(None, "Success", 
                    f"All frames exported to:\n{root_dir}")
                return {
                    'root_dir': root_dir,
                    'paths': all_paths,
                    'frame_count': len(frame_data['images'])
                }
            else:
                return None
                
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error exporting frames: {str(e)}")
            return None