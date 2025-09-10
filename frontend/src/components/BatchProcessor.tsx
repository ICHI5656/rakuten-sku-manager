import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  CircularProgress,
  LinearProgress,
  Divider,
  IconButton,
  Collapse,
  Stack
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import DownloadIcon from '@mui/icons-material/Download';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import FolderZipIcon from '@mui/icons-material/FolderZip';
import SaveIcon from '@mui/icons-material/Save';
import DescriptionIcon from '@mui/icons-material/Description';
import DeviceManager from './DeviceManager';

interface BatchProcessorProps {
  batchId: string;
  uploadedFiles: any[];
  allDevices: string[];
  allProductDevices?: Record<string, string[]>;
  onReset: () => void;
}

const BatchProcessor: React.FC<BatchProcessorProps> = ({
  batchId,
  uploadedFiles,
  allDevices,
  allProductDevices,
  onReset
}) => {
  const [processing, setProcessing] = useState(false);
  const [processResult, setProcessResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [devicesToAdd, setDevicesToAdd] = useState<string[]>([]);
  const [devicesToRemove, setDevicesToRemove] = useState<string[]>([]);
  const [autoFillAltText, setAutoFillAltText] = useState<boolean>(true);
  const [showDeviceManager, setShowDeviceManager] = useState(true);
  const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set());
  const [downloading, setDownloading] = useState(false);

  const handleDeviceNext = async (
    addDevices: string[],
    removeDevices: string[],
    position?: string,
    afterDevice?: string,
    customOrder?: string[],
    insertIndex?: number,
    deviceBrand?: string,
    deviceAttributes?: any[]
  ) => {
    setDevicesToAdd(addDevices);
    setDevicesToRemove(removeDevices);
    setShowDeviceManager(false);

    // Start processing
    setProcessing(true);
    setError(null);

    try {
      // Check if files have different device lists
      const deviceListPatterns = new Set();
      let hasDifferentDeviceLists = false;
      
      if (allProductDevices) {
        Object.values(allProductDevices).forEach((devices: any) => {
          const pattern = Array.isArray(devices) ? devices.sort().join(',') : '';
          deviceListPatterns.add(pattern);
        });
        hasDifferentDeviceLists = deviceListPatterns.size > 1;
      }

      const formData = new FormData();
      formData.append('batch_id', batchId);
      formData.append('devices_to_add', JSON.stringify(addDevices));
      formData.append('devices_to_remove', JSON.stringify(removeDevices));
      formData.append('output_format', 'single');
      formData.append('apply_to_all', 'true');
      formData.append('auto_fill_alt_text', autoFillAltText.toString());
      
      // Add position parameters if specified
      if (position) {
        formData.append('add_position', position);
      }
      if (afterDevice) {
        formData.append('after_device', afterDevice);
      }
      if (customOrder && customOrder.length > 0) {
        formData.append('custom_device_order', JSON.stringify(customOrder));
      }
      
      // Set process mode based on device list patterns
      const processMode = hasDifferentDeviceLists ? 'different_devices' : 'same_devices';
      formData.append('process_mode', processMode);
      
      console.log(`Batch processing with mode: ${processMode} (${deviceListPatterns.size} unique device patterns)`);

      const response = await fetch('/api/batch-process', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('バッチ処理に失敗しました');
      }

      const result = await response.json();
      setProcessResult(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setProcessing(false);
    }
  };

  const handleDownloadAll = async () => {
    setDownloading(true);
    try {
      const response = await fetch(`/api/batch-download/${batchId}`);
      if (!response.ok) {
        throw new Error('ダウンロードに失敗しました');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `batch_${batchId}_results.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setDownloading(false);
    }
  };

  const handleDownloadSingle = async (filename: string) => {
    try {
      const response = await fetch(`/api/download/${filename}`);
      if (!response.ok) {
        throw new Error('ファイルのダウンロードに失敗しました');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const toggleFileExpand = (filename: string) => {
    const newExpanded = new Set(expandedFiles);
    if (newExpanded.has(filename)) {
      newExpanded.delete(filename);
    } else {
      newExpanded.add(filename);
    }
    setExpandedFiles(newExpanded);
  };

  if (showDeviceManager && !processResult) {
    return (
      <Box>
        <Alert severity="info" sx={{ mb: 3 }}>
          <AlertTitle>バッチ処理の準備</AlertTitle>
          {uploadedFiles.length}個のCSVファイルがアップロードされました。
          機種の追加・削除を設定してください。
        </Alert>

        <DeviceManager
          devices={allDevices}
          productDevices={allProductDevices || {}}
          autoFillAltText={autoFillAltText}
          onAutoFillAltTextChange={setAutoFillAltText}
          onNext={handleDeviceNext}
          onBack={onReset}
          key="batch-device-manager"  // Add key to prevent re-rendering
        />
      </Box>
    );
  }

  if (processing) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 3 }}>
          バッチ処理中...
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {uploadedFiles.length}個のファイルを処理しています
        </Typography>
        <LinearProgress sx={{ mt: 3 }} />
      </Paper>
    );
  }

  if (processResult) {
    const successCount = processResult.results?.filter((r: any) => r.status === 'success').length || 0;
    const failCount = processResult.results?.filter((r: any) => r.status === 'error').length || 0;

    return (
      <Box>
        <Alert 
          severity={failCount === 0 ? "success" : "warning"} 
          sx={{ mb: 3 }}
        >
          <AlertTitle>バッチ処理完了</AlertTitle>
          <Stack spacing={1} sx={{ mt: 1 }}>
            <Typography variant="body2">
              処理結果: 成功 {successCount}個 / 失敗 {failCount}個
            </Typography>
            {devicesToAdd.length > 0 && (
              <Typography variant="body2">
                追加した機種: {devicesToAdd.length}個
              </Typography>
            )}
            {devicesToRemove.length > 0 && (
              <Typography variant="body2">
                削除した機種: {devicesToRemove.length}個
              </Typography>
            )}
          </Stack>
        </Alert>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              処理結果ファイル
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<FolderZipIcon />}
              onClick={handleDownloadAll}
              disabled={downloading || successCount === 0}
            >
              {downloading ? '準備中...' : 'すべてダウンロード (ZIP)'}
            </Button>
          </Box>

          <Divider sx={{ mb: 2 }} />

          <List>
            {processResult.results?.map((result: any, index: number) => (
              <React.Fragment key={index}>
                <ListItem>
                  <ListItemIcon>
                    {result.status === 'success' ? (
                      <CheckCircleIcon color="success" />
                    ) : (
                      <ErrorIcon color="error" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <DescriptionIcon fontSize="small" />
                        <Typography variant="body1">
                          {result.file}
                        </Typography>
                        {result.status === 'success' && (
                          <Chip 
                            label={`${result.rows}行`} 
                            size="small" 
                            variant="outlined"
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      result.status === 'success' ? (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            出力ファイル: {result.output_file}
                          </Typography>
                          {result.devices_added > 0 && (
                            <Chip 
                              label={`+${result.devices_added}機種`} 
                              size="small" 
                              color="success"
                              sx={{ ml: 1 }}
                            />
                          )}
                          {result.devices_removed > 0 && (
                            <Chip 
                              label={`-${result.devices_removed}機種`} 
                              size="small" 
                              color="error"
                              sx={{ ml: 1 }}
                            />
                          )}
                        </Box>
                      ) : (
                        <Typography variant="caption" color="error">
                          エラー: {result.message}
                        </Typography>
                      )
                    }
                  />
                  {result.status === 'success' && result.output_file && (
                    <>
                      <IconButton
                        onClick={() => handleDownloadSingle(result.output_file)}
                        color="primary"
                      >
                        <DownloadIcon />
                      </IconButton>
                      <IconButton
                        onClick={() => toggleFileExpand(result.file)}
                      >
                        {expandedFiles.has(result.file) ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    </>
                  )}
                </ListItem>

                <Collapse in={expandedFiles.has(result.file)} timeout="auto" unmountOnExit>
                  <Box sx={{ pl: 9, pr: 3, pb: 2 }}>
                    <Alert severity="info" variant="outlined">
                      <Typography variant="caption">
                        処理済みファイルは以下の名前で保存されました：
                      </Typography>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', mt: 1 }}>
                        {result.output_file}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        ※ ダウンロードボタンをクリックして、元のフォルダーに保存してください
                      </Typography>
                    </Alert>
                  </Box>
                </Collapse>
              </React.Fragment>
            ))}
          </List>
        </Paper>

        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button
            variant="outlined"
            onClick={onReset}
          >
            新しいバッチを処理
          </Button>

          <Alert severity="info" sx={{ flex: 1, mx: 2 }}>
            <Typography variant="body2">
              💡 ヒント: 処理済みファイルは「すべてダウンロード」ボタンでZIP形式でダウンロードし、
              元のフォルダーに展開してください。
            </Typography>
          </Alert>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Box>
    );
  }

  return null;
};

export default BatchProcessor;