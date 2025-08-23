import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Typography,
  Paper,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  Chip
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { uploadCSV } from '../services/api';

interface FileUploadProps {
  onUploadSuccess: (fileId: string, devices: string[], productDevices?: Record<string, string[]>) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    const file = acceptedFiles[0];
    if (!file.name.endsWith('.csv')) {
      setError('CSVファイルのみアップロード可能です');
      return;
    }

    setUploading(true);
    setError('');
    
    try {
      const result = await uploadCSV(file);
      console.log('Upload result:', result);
      console.log('product_devices:', result.product_devices);
      setUploadResult(result);
      setTimeout(() => {
        onUploadSuccess(result.file_id, result.devices, result.product_devices);
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'アップロードに失敗しました');
    } finally {
      setUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    maxFiles: 1
  });

  return (
    <Box>
      {!uploadResult ? (
        <>
          <Paper
            {...getRootProps()}
            sx={{
              p: 6,
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'divider',
              transition: 'all 0.3s ease'
            }}
          >
            <input {...getInputProps()} />
            <CloudUploadIcon sx={{ fontSize: 64, color: 'action.disabled', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive
                ? 'ファイルをドロップしてください'
                : 'CSVファイルをドラッグ＆ドロップ'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              またはクリックしてファイルを選択
            </Typography>
            <Typography variant="caption" display="block" sx={{ mt: 2 }}>
              対応形式: 楽天RMS仕様CSV (Shift-JIS)
            </Typography>
          </Paper>

          {uploading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="body2" align="center" sx={{ mt: 1 }}>
                アップロード中...
              </Typography>
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </>
      ) : (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <CheckCircleIcon color="success" sx={{ mr: 1 }} />
            <Typography variant="h6">アップロード完了</Typography>
          </Box>
          
          <List>
            <ListItem>
              <ListItemText 
                primary="ファイルID" 
                secondary={uploadResult.file_id} 
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="行数" 
                secondary={`${uploadResult.row_count} 行`} 
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="列数" 
                secondary={`${uploadResult.column_count} 列`} 
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="検出された機種数" 
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Chip label={`${uploadResult.devices.length} 機種`} color="primary" />
                  </Box>
                } 
              />
            </ListItem>
          </List>
          
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            次のステップで機種の追加・削除を設定します...
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default FileUpload;