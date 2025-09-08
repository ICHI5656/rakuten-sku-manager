import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  CircularProgress,
  LinearProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  IconButton,
  Stack,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Autocomplete,
  Checkbox,
  FormControlLabel,
  Collapse
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  GetApp as DownloadIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  HourglassEmpty as PendingIcon,
  Delete as DeleteIcon,
  InsertDriveFile as FileIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material';

interface BatchFile {
  id: string;
  name: string;
  size: number;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress?: number;
  message?: string;
}

export default function BatchProcessPage() {
  const [files, setFiles] = useState<BatchFile[]>([]);
  const [processing, setProcessing] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [batchId, setBatchId] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  
  // デバイス管理の状態
  const [showDeviceOptions, setShowDeviceOptions] = useState(false);
  const [processMode, setProcessMode] = useState('auto');
  const [devicesToAdd, setDevicesToAdd] = useState<string[]>([]);
  const [devicesToRemove, setDevicesToRemove] = useState<string[]>([]);
  const [devicePosition, setDevicePosition] = useState('end');
  const [customDeviceOrder, setCustomDeviceOrder] = useState<string[]>([]);
  const [availableDevices, setAvailableDevices] = useState<string[]>([]);
  const [deviceBrand, setDeviceBrand] = useState('');
  const [brands, setBrands] = useState<any[]>([]);

  // ブランドリストの取得
  useEffect(() => {
    fetchBrands();
  }, []);

  // デバイスリストの取得
  useEffect(() => {
    fetchAvailableDevices();
  }, [deviceBrand]);

  const fetchBrands = async () => {
    try {
      const response = await fetch('/api/product-attributes/brands');
      if (response.ok) {
        const data = await response.json();
        setBrands(data.brands || []);
      }
    } catch (error) {
      console.error('Error fetching brands:', error);
    }
  };

  const fetchAvailableDevices = async () => {
    try {
      // ブランドに基づいてデバイスを取得
      const url = deviceBrand 
        ? `/api/product-attributes/devices?brand=${deviceBrand}`
        : '/api/product-attributes/devices';
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        const devices = data.devices || data;
        const uniqueDevices = [...new Set(devices.map((d: any) => d.device_name))].filter((d): d is string => typeof d === 'string');
        setAvailableDevices(uniqueDevices);
      }
    } catch (error) {
      console.error('Error fetching devices:', error);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      await uploadFiles(droppedFiles);
    }
  };

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFiles = Array.from(e.target.files);
      await uploadFiles(selectedFiles);
    }
  };

  const uploadFiles = async (fileList: File[]) => {
    const formData = new FormData();
    fileList.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('/api/batch-upload', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setBatchId(result.batch_id);
        
        const newFiles: BatchFile[] = result.files.map((file: any) => ({
          id: file.file_id,
          name: file.filename,
          size: file.size || 0,
          status: 'pending' as const
        }));
        
        setFiles(prev => [...prev, ...newFiles]);
        setUploadedFiles(prev => [...prev, ...result.files]);
      } else {
        console.error('Upload failed');
      }
    } catch (error) {
      console.error('Error uploading files:', error);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'processing':
        return <CircularProgress size={20} />;
      default:
        return <PendingIcon color="action" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'error':
        return 'error';
      case 'processing':
        return 'primary';
      default:
        return 'default';
    }
  };

  const startBatchProcess = async () => {
    if (!batchId) {
      alert('ファイルをアップロードしてください');
      return;
    }

    setProcessing(true);

    try {
      // Backend expects Form data, not JSON
      const formData = new FormData();
      formData.append('batch_id', batchId);
      formData.append('process_mode', processMode);
      formData.append('output_format', 'single');
      formData.append('apply_to_all', 'true');
      
      if (devicesToAdd.length > 0) {
        formData.append('devices_to_add', JSON.stringify(devicesToAdd));
      }
      if (devicesToRemove.length > 0) {
        formData.append('devices_to_remove', JSON.stringify(devicesToRemove));
      }
      if (devicePosition) {
        formData.append('add_position', devicePosition);
      }
      if (customDeviceOrder.length > 0) {
        formData.append('custom_device_order', JSON.stringify(customDeviceOrder));
      }

      const response = await fetch('/api/batch-process', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        
        // ステータスをポーリング
        const pollStatus = setInterval(async () => {
          const statusResponse = await fetch(`/api/batch-status/${batchId}`);
          if (statusResponse.ok) {
            const statusData = await statusResponse.json();
            
            // ファイルごとのステータスを更新
            setFiles(prev => prev.map(file => {
              const fileStatus = statusData.files?.find((f: any) => f.file_id === file.id);
              if (fileStatus) {
                return {
                  ...file,
                  status: fileStatus.status as any,
                  progress: fileStatus.progress || 0,
                  message: fileStatus.message
                };
              }
              return file;
            }));

            // すべて完了したらポーリングを停止
            if (statusData.status === 'completed' || statusData.status === 'error') {
              clearInterval(pollStatus);
              setProcessing(false);
            }
          }
        }, 2000); // 2秒ごとにステータスチェック

      } else {
        console.error('Batch process failed');
        setProcessing(false);
      }
    } catch (error) {
      console.error('Error starting batch process:', error);
      setProcessing(false);
    }
  };

  const downloadResults = async () => {
    if (!batchId) return;

    try {
      const response = await fetch(`/api/batch-download/${batchId}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `batch_${batchId}_results.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Error downloading results:', error);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        バッチ処理
      </Typography>

      {/* 統計カード */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', p: 1.5 }}>
              <Typography variant="h4" color="primary">
                {files.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                総ファイル数
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', p: 1.5 }}>
              <Typography variant="h4" color="success.main">
                {files.filter(f => f.status === 'completed').length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                完了
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', p: 1.5 }}>
              <Typography variant="h4" color="warning.main">
                {files.filter(f => f.status === 'processing').length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                処理中
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', p: 1.5 }}>
              <Typography variant="h4" color="error.main">
                {files.filter(f => f.status === 'error').length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                エラー
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* ファイルアップロードエリア */}
      <Paper
        sx={{
          p: 3,
          mb: 3,
          border: '2px dashed',
          borderColor: dragActive ? 'primary.main' : 'grey.400',
          backgroundColor: dragActive ? 'action.hover' : 'background.paper',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          CSVファイルをドラッグ&ドロップ
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          または
        </Typography>
        <Button
          variant="contained"
          component="label"
          startIcon={<UploadIcon />}
        >
          ファイルを選択
          <input
            type="file"
            multiple
            accept=".csv"
            hidden
            onChange={handleFileInput}
          />
        </Button>
        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
          複数ファイル選択可能 (CSV形式のみ)
        </Typography>
      </Paper>

      {/* デバイス管理オプション */}
      {files.length > 0 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              cursor: 'pointer',
              mb: showDeviceOptions ? 2 : 0
            }}
            onClick={() => setShowDeviceOptions(!showDeviceOptions)}
          >
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SettingsIcon />
              デバイス管理オプション
            </Typography>
            {showDeviceOptions ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </Box>

          <Collapse in={showDeviceOptions}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel>処理モード</InputLabel>
                  <Select
                    value={processMode}
                    label="処理モード"
                    onChange={(e) => setProcessMode(e.target.value)}
                  >
                    <MenuItem value="auto">自動検出</MenuItem>
                    <MenuItem value="same_devices">同一デバイス処理</MenuItem>
                    <MenuItem value="different_devices">個別デバイス処理</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel>デバイス配置</InputLabel>
                  <Select
                    value={devicePosition}
                    label="デバイス配置"
                    onChange={(e) => setDevicePosition(e.target.value)}
                  >
                    <MenuItem value="start">先頭に追加</MenuItem>
                    <MenuItem value="end">末尾に追加</MenuItem>
                    <MenuItem value="custom">カスタム配置</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth size="small">
                  <InputLabel>ブランドフィルター</InputLabel>
                  <Select
                    value={deviceBrand}
                    label="ブランドフィルター"
                    onChange={(e) => setDeviceBrand(e.target.value)}
                  >
                    <MenuItem value="">すべて</MenuItem>
                    {brands.map((brand) => (
                      <MenuItem key={brand.id} value={brand.id}>
                        {brand.name_jp || brand.name} ({brand.device_count}機種)
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <Autocomplete
                  multiple
                  size="small"
                  options={availableDevices}
                  value={devicesToAdd}
                  onChange={(_, newValue) => setDevicesToAdd(newValue)}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="追加するデバイス"
                      placeholder="デバイスを選択"
                    />
                  )}
                  sx={{ mb: 2 }}
                />

                <Autocomplete
                  multiple
                  size="small"
                  options={availableDevices}
                  value={devicesToRemove}
                  onChange={(_, newValue) => setDevicesToRemove(newValue)}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="削除するデバイス"
                      placeholder="デバイスを選択"
                    />
                  )}
                  sx={{ mb: 2 }}
                />

                <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
                  追加: {devicesToAdd.length}個 | 削除: {devicesToRemove.length}個
                </Alert>
              </Grid>
            </Grid>
          </Collapse>
        </Paper>
      )}

      {/* コントロールボタン */}
      {files.length > 0 && (
        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={processing ? <StopIcon /> : <PlayIcon />}
            onClick={startBatchProcess}
            disabled={files.length === 0 || processing}
          >
            {processing ? '処理中...' : 'バッチ処理開始'}
          </Button>
          <Button
            variant="outlined"
            color="success"
            startIcon={<DownloadIcon />}
            disabled={files.filter(f => f.status === 'completed').length === 0}
            onClick={downloadResults}
          >
            結果ダウンロード (ZIP)
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={() => {
              setFiles([]);
              setBatchId(null);
              setUploadedFiles([]);
            }}
            disabled={processing}
          >
            すべてクリア
          </Button>
        </Stack>
      )}

      {/* ファイルリスト */}
      {files.length > 0 && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            ファイル一覧
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <List>
            {files.map((file, index) => (
              <ListItem
                key={file.id}
                sx={{
                  mb: 1,
                  backgroundColor: 'background.paper',
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'divider'
                }}
                secondaryAction={
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Chip
                      label={file.status === 'processing' ? `${file.progress}%` : file.status}
                      color={getStatusColor(file.status) as any}
                      size="small"
                    />
                    <IconButton
                      size="small"
                      onClick={() => setFiles(prev => prev.filter(f => f.id !== file.id))}
                      disabled={file.status === 'processing'}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Stack>
                }
              >
                <ListItemIcon>
                  {getStatusIcon(file.status)}
                </ListItemIcon>
                <ListItemText
                  primary={file.name}
                  secondary={
                    <Stack spacing={0.5}>
                      <Typography variant="caption">
                        {formatFileSize(file.size)}
                      </Typography>
                      {file.status === 'processing' && file.progress !== undefined && (
                        <LinearProgress
                          variant="determinate"
                          value={file.progress}
                          sx={{ height: 4, borderRadius: 2 }}
                        />
                      )}
                      {file.message && (
                        <Typography variant="caption" color="text.secondary">
                          {file.message}
                        </Typography>
                      )}
                    </Stack>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* 空の状態 */}
      {files.length === 0 && (
        <Alert severity="info" sx={{ mt: 2 }}>
          ファイルをアップロードしてバッチ処理を開始してください
        </Alert>
      )}
    </Box>
  );
}