from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class OutputFormat(str, Enum):
    SINGLE = "single"
    PER_PRODUCT = "per_product"
    SPLIT_60K = "split_60k"

class DeviceAction(BaseModel):
    name: str
    action: str  # "add" or "remove"

class DeviceAttributeInfo(BaseModel):
    device: str
    attribute_value: Optional[str] = None
    size_category: Optional[str] = None

class ProcessRequest(BaseModel):
    file_id: str
    devices_to_add: Optional[List[str]] = []
    devices_to_remove: Optional[List[str]] = []
    output_format: OutputFormat = OutputFormat.SINGLE
    add_position: Optional[str] = "start"  # "start", "end", "after", "custom", or "final_order"
    after_device: Optional[str] = None
    custom_device_order: Optional[List[str]] = None  # カスタム順序（並び替え機能）
    insert_index: Optional[int] = None  # カスタム順序での挿入位置
    device_brand: Optional[str] = None  # 機種ブランド
    device_attributes: Optional[List[DeviceAttributeInfo]] = None  # 機種固有の属性情報
    reset_all_devices: Optional[bool] = False  # 全機種削除して再定義

class ProcessingOptions(BaseModel):
    maintain_column_order: bool = True
    encoding: str = "shift_jis"
    max_variations_per_attribute: int = 40
    max_skus_per_product: int = 400

class ProductInfo(BaseModel):
    product_id: str
    product_name: str
    variation_count: int
    sku_count: int

class ValidationResult(BaseModel):
    valid: bool
    errors: Optional[List[str]] = []
    warnings: Optional[List[str]] = []

class CSVUploadResponse(BaseModel):
    file_id: str
    devices: List[str]
    products: List[ProductInfo]
    row_count: int
    column_count: int

class ProcessResponse(BaseModel):
    success: bool
    output_files: List[str]
    total_rows: int
    sku_count: int