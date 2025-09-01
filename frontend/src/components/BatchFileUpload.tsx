import React, { useState, useCallback, useRef } from 'react';
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
  ListItemSecondaryAction,
  IconButton,
  Button,
  Chip,
  Card,
  CardContent,
  Stack,
  Divider,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import FolderIcon from '@mui/icons-material/Folder';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { uploadBatchCSV } from '../services/api';

interface BatchFileUploadProps {
  onUploadSuccess: (batchId: string, files: any[], allDevices: string[], allProductDevices?: Record<string, string[]>) => void;
}

interface FileInfo {
  file: File;
  id: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
  result?: any;
}

const BatchFileUpload: React.FC<BatchFileUploadProps> = ({ onUploadSuccess }) => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [includeSubfolders, setIncludeSubfolders] = useState(false);
  const folderInputRef = useRef<HTMLInputElement>(null);

  const addFiles = (newFiles: File[]) => {
    const csvFiles = newFiles.filter(f => f.name.endsWith('.csv'));
    const fileInfos: FileInfo[] = csvFiles.map(file => ({
      file,
      id: `${Date.now()}_${Math.random()}`,
      status: 'pending'
    }));
    
    setFiles(prev => [...prev, ...fileInfos]);
  };

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    addFiles(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: true
  });

  const handleFolderSelect = () => {
    folderInputRef.current?.click();
  };

  const handleFolderChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = event.target.files;
    if (fileList) {
      const filesArray = Array.from(fileList);
      addFiles(filesArray);
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setError('');

    try {
      // Prepare files for upload
      const formData = new FormData();
      files.forEach(fileInfo => {
        formData.append('files', fileInfo.file);
      });

      // Upload all files
      const result = await uploadBatchCSV(formData);
      
      setUploadResult(result);
      
      // Update file statuses
      setFiles(prev => prev.map(f => ({
        ...f,
        status: result.errors?.find((e: any) => e.file === f.file.name) ? 'error' : 'success'
      })));

      setTimeout(() => {
        console.log('BatchFileUpload - all_devices from API:', JSON.stringify(result.all_devices, null, 2));
        console.log('BatchFileUpload - all_product_devices from API:', result.all_product_devices);
        onUploadSuccess(result.batch_id, result.uploaded_files, result.all_devices, result.all_product_devices);
      }, 1500);
      
    } catch (err: any) {
      setError(err.message || 'バッチアップロードに失敗しました');
      setFiles(prev => prev.map(f => ({ ...f, status: 'error' })));
    } finally {
      setUploading(false);
    }
  };

  const clearAll = () => {
    setFiles([]);
    setUploadResult(null);
    setError('');
  };

  return (
    <Box>
      {!uploadResult ? (
        <>
          <Paper
            {...getRootProps()}
            sx={{
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'divider',
              transition: 'all 0.3s ease',
              mb: 2
            }}
          >
            <input {...getInputProps()} />
            <CloudUploadIcon sx={{ fontSize: 48, color: 'action.disabled', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive
                ? '複数のCSVファイルをドロップしてください'
                : '複数のCSVファイルをドラッグ＆ドロップ'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              またはクリックしてファイルを選択
            </Typography>
          </Paper>

          <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              startIcon={<FolderIcon />}
              onClick={handleFolderSelect}
            >
              フォルダから選択
            </Button>
            <FormControlLabel
              control={
                <Checkbox
                  checked={includeSubfolders}
                  onChange={(e) => setIncludeSubfolders(e.target.checked)}
                />
              }
              label="サブフォルダも含む"
            />
          </Stack>

          <input
            ref={folderInputRef}
            type="file"
            multiple
            webkitdirectory=""
            directory=""
            style={{ display: 'none' }}
            onChange={handleFolderChange}
            accept=".csv"
          />

          {files.length > 0 && (
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                  <Typography variant="h6">
                    選択されたファイル ({files.length}個)
                  </Typography>
                  <Button 
                    variant="text" 
                    color="error" 
                    onClick={clearAll}
                    size="small"
                  >
                    すべてクリア
                  </Button>
                </Stack>
                
                <List dense sx={{ maxHeight: 300, overflow: 'auto' }}>
                  {files.map(fileInfo => (
                    <ListItem key={fileInfo.id}>
                      <ListItemText
                        primary={fileInfo.file.name}
                        secondary={`${(fileInfo.file.size / 1024).toFixed(2)} KB`}
                      />
                      {fileInfo.status === 'success' && (
                        <CheckCircleIcon color="success" sx={{ mr: 2 }} />
                      )}
                      {fileInfo.status === 'error' && (
                        <ErrorIcon color="error" sx={{ mr: 2 }} />
                      )}
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => removeFile(fileInfo.id)}
                          disabled={uploading}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>

                <Divider sx={{ my: 2 }} />

                <Button
                  variant="contained"
                  fullWidth
                  onClick={handleUpload}
                  disabled={uploading || files.length === 0}
                  startIcon={<CloudUploadIcon />}
                >
                  {files.length}個のファイルをアップロード
                </Button>
              </CardContent>
            </Card>
          )}

          {uploading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="body2" align="center" sx={{ mt: 1 }}>
                バッチアップロード中...
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
            <Typography variant="h6">バッチアップロード完了</Typography>
          </Box>
          
          <List>
            <ListItem>
              <ListItemText 
                primary="バッチID" 
                secondary={uploadResult.batch_id} 
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="アップロード成功" 
                secondary={`${uploadResult.uploaded_files?.length || 0} ファイル`} 
              />
            </ListItem>
            {uploadResult.errors?.length > 0 && (
              <ListItem>
                <ListItemText 
                  primary="エラー" 
                  secondary={`${uploadResult.errors.length} ファイル`} 
                />
              </ListItem>
            )}
            <ListItem>
              <ListItemText 
                primary="検出された全機種数" 
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Chip 
                      label={`${uploadResult.all_devices?.length || 0} 機種`} 
                      color="primary" 
                    />
                  </Box>
                } 
              />
            </ListItem>
          </List>
          
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            次のステップで全ファイルに適用する機種の追加・削除を設定します...
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

// Add type declarations for directory attributes
declare module 'react' {
  interface HTMLAttributes<T> extends AriaAttributes, DOMAttributes<T> {
    webkitdirectory?: string;
    directory?: string;
  }
}

export default BatchFileUpload;