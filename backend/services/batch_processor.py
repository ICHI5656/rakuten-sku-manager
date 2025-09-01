"""
Batch processor for handling multiple CSV files
"""
import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor

from .csv_processor import CSVProcessor
from .device_manager import DeviceManager
from .rakuten_processor import RakutenCSVProcessor
from .validator import Validator

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Handle batch processing of multiple CSV files"""
    
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.csv_processor = CSVProcessor()
        self.device_manager = DeviceManager()
        self.rakuten_processor = RakutenCSVProcessor(state_dir / "sku_counters.json")
        self.validator = Validator()
        self.batch_status = {}
        
    def create_batch_id(self) -> str:
        """Create unique batch ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S_batch")
    
    def get_batch_status(self, batch_id: str) -> Dict:
        """Get current batch processing status"""
        return self.batch_status.get(batch_id, {
            'status': 'not_found',
            'message': 'Batch ID not found'
        })
    
    async def process_batch_files(
        self,
        file_paths: List[Path],
        devices_to_add: Optional[List[str]] = None,
        devices_to_remove: Optional[List[str]] = None,
        output_format: str = 'single',
        apply_to_all: bool = True
    ) -> Dict:
        """
        Process multiple CSV files in batch
        
        Args:
            file_paths: List of CSV file paths to process
            devices_to_add: Devices to add (applied to all files if apply_to_all=True)
            devices_to_remove: Devices to remove (applied to all files if apply_to_all=True)
            output_format: Output format for each file
            apply_to_all: Whether to apply device changes to all files
        
        Returns:
            Batch processing result with file outcomes
        """
        batch_id = self.create_batch_id()
        
        # Initialize batch status
        self.batch_status[batch_id] = {
            'status': 'processing',
            'total_files': len(file_paths),
            'processed_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'results': [],
            'start_time': datetime.now().isoformat()
        }
        
        results = []
        all_devices = []  # Use list to maintain order
        seen_devices = set()  # Track seen devices
        
        # First pass: collect all unique devices from all files
        if apply_to_all and devices_to_add:
            logger.info(f"Collecting devices from {len(file_paths)} files")
            for file_path in file_paths:
                try:
                    df = self.csv_processor.read_csv(file_path)
                    file_devices = self.device_manager.extract_devices(df)
                    # Add devices maintaining order
                    for device in file_devices:
                        if device not in seen_devices:
                            all_devices.append(device)
                            seen_devices.add(device)
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")
        
        # Merge new devices with existing devices (maintain order)
        if apply_to_all and devices_to_add:
            for device in devices_to_add:
                if device not in seen_devices:
                    all_devices.append(device)
                    seen_devices.add(device)
            final_devices_to_add = all_devices
        else:
            final_devices_to_add = devices_to_add
        
        # Process each file
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for file_path in file_paths:
                future = executor.submit(
                    self._process_single_file,
                    file_path,
                    final_devices_to_add if apply_to_all else devices_to_add,
                    devices_to_remove if apply_to_all else None,
                    output_format,
                    batch_id
                )
                futures.append((file_path, future))
            
            # Collect results
            for file_path, future in futures:
                try:
                    result = future.result(timeout=300)  # 5 min timeout per file
                    results.append(result)
                    
                    if result['status'] == 'success':
                        self.batch_status[batch_id]['successful_files'] += 1
                    else:
                        self.batch_status[batch_id]['failed_files'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    results.append({
                        'file': str(file_path.name),
                        'status': 'error',
                        'message': str(e)
                    })
                    self.batch_status[batch_id]['failed_files'] += 1
                
                self.batch_status[batch_id]['processed_files'] += 1
        
        # Update final status
        self.batch_status[batch_id].update({
            'status': 'completed',
            'results': results,
            'end_time': datetime.now().isoformat(),
            'all_devices': all_devices if apply_to_all else None  # all_devices is already a list
        })
        
        logger.info(f"Batch {batch_id} completed with {len(results)} results")
        logger.info(f"Batch status stored: {batch_id} -> {self.batch_status[batch_id]['status']}")
        
        return self.batch_status[batch_id]
    
    def _process_single_file(
        self,
        file_path: Path,
        devices_to_add: Optional[List[str]],
        devices_to_remove: Optional[List[str]],
        output_format: str,
        batch_id: str
    ) -> Dict:
        """Process a single file in the batch"""
        try:
            logger.info(f"Processing file: {file_path.name}")
            
            # Read CSV
            df = self.csv_processor.read_csv(file_path)
            
            # Process with Rakuten processor
            if devices_to_add or devices_to_remove:
                df = self.rakuten_processor.process_csv(
                    df,
                    devices_to_add=devices_to_add,
                    devices_to_remove=devices_to_remove
                )
            
            # Validate
            validation_result = self.validator.validate_dataframe(df)
            if not validation_result['valid']:
                return {
                    'file': str(file_path.name),
                    'status': 'validation_failed',
                    'errors': validation_result['errors']
                }
            
            # Save output to the same directory as input file
            output_dir = file_path.parent
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"{file_path.stem}_processed_{timestamp}.csv"
            
            self.csv_processor.save_csv(df, output_file)
            
            return {
                'file': str(file_path.name),
                'status': 'success',
                'output_file': str(output_file.name),
                'output_path': str(output_file),  # フルパスを追加
                'rows': len(df),
                'devices_added': len(devices_to_add) if devices_to_add else 0,
                'devices_removed': len(devices_to_remove) if devices_to_remove else 0
            }
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return {
                'file': str(file_path.name),
                'status': 'error',
                'message': str(e)
            }
    
    async def process_folder(
        self,
        folder_path: Path,
        devices_to_add: Optional[List[str]] = None,
        devices_to_remove: Optional[List[str]] = None,
        recursive: bool = False
    ) -> Dict:
        """
        Process all CSV files in a folder
        
        Args:
            folder_path: Path to folder containing CSV files
            devices_to_add: Devices to add to all files
            devices_to_remove: Devices to remove from all files
            recursive: Whether to search recursively
        
        Returns:
            Batch processing result
        """
        # Find all CSV files
        if recursive:
            csv_files = list(folder_path.rglob("*.csv"))
        else:
            csv_files = list(folder_path.glob("*.csv"))
        
        if not csv_files:
            return {
                'status': 'error',
                'message': 'No CSV files found in the specified folder'
            }
        
        logger.info(f"Found {len(csv_files)} CSV files in {folder_path}")
        
        # Process all files
        return await self.process_batch_files(
            csv_files,
            devices_to_add=devices_to_add,
            devices_to_remove=devices_to_remove,
            apply_to_all=True
        )
    
    def cleanup_old_batches(self, days: int = 7):
        """Clean up old batch results older than specified days"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        
        for batch_id in list(self.batch_status.keys()):
            batch_info = self.batch_status[batch_id]
            if 'start_time' in batch_info:
                start_time = datetime.fromisoformat(batch_info['start_time']).timestamp()
                if start_time < cutoff_time:
                    del self.batch_status[batch_id]
                    logger.info(f"Cleaned up old batch: {batch_id}")