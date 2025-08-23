export interface ProcessRequest {
  file_id: string;
  devices_to_add: string[];
  devices_to_remove: string[];
  output_format: string;
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