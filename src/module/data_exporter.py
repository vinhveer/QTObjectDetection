import os
import json
import shutil
import cv2
import pandas as pd
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QProgressDialog, QFileDialog, QProgressBar
from PySide6.QtCore import Qt

# Define constants for save prompt types
SAVE_TO_CONFIGURED_PATH = 0  # Save to pre-configured path
SAVE_WITH_PROMPT = 1         # Prompt user to select path before saving


class DataExporter:
    """
    A class to handle exporting detection data, including images and metadata.
    
    This class manages the export of detection results, including original images,
    bounding box visualizations, and detection metadata in both JSON and Excel formats.
    
    Attributes:
        settings: Application settings object containing save_path and save_prompt_type
        last_export_path: String storing the last used export path
    """

    def __init__(self, settings):
        """
        Initialize DataExporter class
        
        Args:
            settings: Application settings object with save_path and save_prompt_type
        """
        self.settings = settings
        self.last_export_path = None
        
    def get_destination_directory(self, title="Select directory to save data", source_type="camera"):
        """
        Get destination directory based on settings or user selection
        
        Args:
            title: Dialog window title if prompt is shown
            source_type: Type of source ("camera" or "picture")
            
        Returns:
            str: Selected directory path or None if canceled
        """
        # Check if we should use the configured path
        if (hasattr(self.settings, 'save_prompt_type') and 
            self.settings.save_prompt_type == SAVE_TO_CONFIGURED_PATH):
            if hasattr(self.settings, 'save_path') and self.settings.save_path:
                # Use the pre-configured path but create a subdirectory with the required format
                base_path = self.settings.save_path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                subfolder_name = f"detect_with_{source_type}_{timestamp}"
                full_path = os.path.join(base_path, subfolder_name)
                
                # Create the directory
                try:
                    os.makedirs(full_path, exist_ok=True)
                    return full_path
                except Exception as e:
                    QMessageBox.warning(
                        None,
                        "Warning",
                        f"Could not create directory: {str(e)}. Please select a directory manually."
                    )
            else:
                QMessageBox.warning(
                    None,
                    "Warning",
                    "No save path configured in settings. Please select a directory."
                )
        
        # Show dialog to select directory
        directory = QFileDialog.getExistingDirectory(
            None,
            title,
            self.last_export_path or (
                self.settings.save_path if hasattr(self.settings, 'save_path') else ""
            ),
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
            bool: True if successful, False if failed
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
            str: Base filename with timestamp
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
            dict: Dictionary with destination paths
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
            dict: Dictionary with saved file paths
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
            str: Path to saved JSON file
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
            str: Path to saved Excel file
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
            dict: Dictionary with paths to saved files or None if canceled
        """
        # Check if valid data exists
        required_frames = ['original', 'binding_box', 'warm_up']
        if any(frames.get(f) is None for f in required_frames) or not detections:
            QMessageBox.warning(None, "Error", "No frame or detection data to save!")
            return None

        # Get destination directory based on save_prompt_type
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

            QMessageBox.information(
                None,
                "Success", 
                f"Frame exported to:\n{root_dir}"
            )
                
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
            dict: Dictionary with export info or None if canceled
        """
        # Check if data exists
        if not frame_data.get('images') or not frame_data.get('detections'):
            QMessageBox.warning(None, "Error", "No detection data to save!")
            return None

        # Get destination directory based on save_prompt_type
        root_dir = self.get_destination_directory("Select directory for all frames export")
        if not root_dir:
            return None

        try:
            # Create a custom progress dialog
            progress = QProgressDialog(None)
            progress.setWindowTitle("Saving Progress")
            progress.setLabelText("Initializing...")
            progress.setCancelButtonText("Cancel")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            
            # Set size and style
            progress.setMinimumWidth(400)  # Wider dialog
            progress.setMinimumHeight(100)  # Taller dialog
            
            # Style the progress bar
            progress_bar = progress.findChild(QProgressBar)
            if progress_bar:
                progress_bar.setTextVisible(True)  # Show percentage
                progress_bar.setFormat("%v/%m (%p%)")  # Custom format
                
            # Set range
            total_frames = len(frame_data['images'])
            progress.setRange(0, total_frames)
            
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
                progress.setLabelText(
                    f"Processing frame {i+1} of {total_frames}\n"
                    f"Saving to: {root_dir}"
                )
                
                # Extract frame information
                timestamp = frame_info['timestamp']
                detections = frame_info['detections']
                base_filename = f"detection_{timestamp}"
                
                try:
                    # Copy image files
                    paths = self.copy_image_files(frame_info, root_dir, base_filename)
                    all_paths['image_paths'].append(paths)
                    
                    # Save JSON and Excel data
                    json_path = self.save_json_data(
                        root_dir,
                        base_filename,
                        timestamp,
                        detections
                    )
                    all_paths['json_paths'].append(json_path)
                    
                    excel_path = self.save_excel_data(
                        root_dir,
                        base_filename,
                        detections
                    )
                    all_paths['excel_paths'].append(excel_path)
                    
                except Exception as e:
                    print(f"Error processing frame {i+1}: {str(e)}")
                    continue

            progress.setValue(total_frames)
            
            if not progress.wasCanceled():
                # Create metadata file with export information
                metadata = {
                    'export_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'exported_by': 'vinhveer',  # Using the current user's login
                    'total_frames': total_frames,
                    'export_location': root_dir,
                    'frames_processed': len(all_paths['json_paths']),
                    'successful_exports': {
                        'images': len(all_paths['image_paths']),
                        'json_files': len(all_paths['json_paths']),
                        'excel_files': len(all_paths['excel_paths'])
                    }
                }
                
                # Save metadata to JSON file
                metadata_path = os.path.join(root_dir, 'export_metadata.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=4)
                
                QMessageBox.information(
                    None, 
                    "Success", 
                    f"All frames exported to:\n{root_dir}\n\n"
                    f"Total frames processed: {total_frames}\n"
                    f"Export completed at: {metadata['export_timestamp']}"
                )
                
                return {
                    'root_dir': root_dir,
                    'paths': all_paths,
                    'frame_count': total_frames,
                    'metadata': metadata,
                    'metadata_path': metadata_path
                }
            else:
                QMessageBox.warning(
                    None,
                    "Export Canceled",
                    f"Export was canceled. {len(all_paths['json_paths'])} frames were processed."
                )
                return None
                
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error exporting frames: {str(e)}")
            return None

    def get_export_statistics(self, export_result):
        """
        Generate statistics about the export operation
        
        Args:
            export_result: Dictionary containing export results
            
        Returns:
            dict: Dictionary containing export statistics
        """
        if not export_result:
            return None
            
        try:
            stats = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_frames': export_result['frame_count'],
                'files_generated': {
                    'images': len(export_result['paths']['image_paths']),
                    'json': len(export_result['paths']['json_paths']),
                    'excel': len(export_result['paths']['excel_paths'])
                },
                'export_location': export_result['root_dir'],
                'success_rate': (
                    len(export_result['paths']['json_paths']) / 
                    export_result['frame_count'] * 100
                ) if export_result['frame_count'] > 0 else 0
            }
            
            return stats
            
        except Exception as e:
            print(f"Error generating export statistics: {str(e)}")
            return None