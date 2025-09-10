export interface ProcessRequest {
  file_id: string;
  devices_to_add: string[];
  devices_to_remove: string[];
  output_format: string;
  add_position?: 'start' | 'end' | 'after' | 'custom' | 'final_order';
  after_device?: string;
  custom_device_order?: string[];
  insert_index?: number;
  device_brand?: string;
  device_attributes?: Array<{
    device: string;
    attribute_value?: string;
    size_category?: string;
  }>;
  anve_mode?: boolean;
  auto_fill_alt_text?: boolean;
}

export interface ProcessResponse {
  success: boolean;
  output_files: string[];
  total_rows: number;
  sku_count: number;
}

export interface UploadResponse {
  file_id: string;
  devices: string[];
  products: ProductInfo[];
  product_devices?: Record<string, string[]>;
  row_count: number;
  column_count: number;
}

export interface ProductInfo {
  product_id: string;
  product_name: string;
  variation_count: number;
  sku_count: number;
}