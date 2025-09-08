import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Stack,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  FilePresent as FileIcon,
  Delete as DeleteIcon,
  Visibility as PreviewIcon
} from '@mui/icons-material';

export default function UploadPage() {
  const [uploadedFile, setUploadedFile] = useState<any>(null);
  const [encoding, setEncoding] = useState('auto');
  const [validation, setValidation] = useState<any>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    setUploadedFile({
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: new Date(file.lastModified)
    });

    // バリデーションのシミュレーション
    setValidation({
      encoding: 'Shift-JIS',
      rows: 1234,
      columns: 15,
      products: 45,
      skus: 567,
      warnings: [
        '一部の商品管理番号が重複しています',
        'バリエーション2選択肢定義が空の行があります'
      ],
      errors: []
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        ファイルアップロード
      </Typography>

      {/* アップロードエリア */}
      <Paper
        sx={{
          p: 4,
          mb: 3,
          border: '3px dashed',
          borderColor: dragActive ? 'primary.main' : 'grey.400',
          backgroundColor: dragActive ? 'action.hover' : 'background.paper',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          minHeight: 200,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <UploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h5" gutterBottom>
          ここにCSVファイルをドロップ
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          または
        </Typography>
        <Button
          variant="contained"
          component="label"
          startIcon={<UploadIcon />}
          size="large"
        >
          ファイルを選択
          <input
            type="file"
            accept=".csv"
            hidden
            onChange={handleFileInput}
          />
        </Button>
        <Typography variant="caption" display="block" sx={{ mt: 2 }}>
          対応形式: CSV (Shift-JIS, UTF-8)
        </Typography>
      </Paper>

      {/* エンコーディング設定 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth size="small">
            <InputLabel>エンコーディング</InputLabel>
            <Select
              value={encoding}
              label="エンコーディング"
              onChange={(e) => setEncoding(e.target.value)}
            >
              <MenuItem value="auto">自動検出</MenuItem>
              <MenuItem value="shift_jis">Shift-JIS</MenuItem>
              <MenuItem value="utf8">UTF-8</MenuItem>
              <MenuItem value="utf8_bom">UTF-8 with BOM</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            size="small"
            label="最大ファイルサイズ"
            value="1GB"
            disabled
            helperText="設定により変更可能"
          />
        </Grid>
      </Grid>

      {/* アップロードされたファイル情報 */}
      {uploadedFile && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            ファイル情報
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <FileIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="ファイル名"
                    secondary={uploadedFile.name}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="サイズ"
                    secondary={formatFileSize(uploadedFile.size)}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="最終更新"
                    secondary={uploadedFile.lastModified.toLocaleString()}
                  />
                </ListItem>
              </List>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Stack spacing={2}>
                <Button
                  variant="outlined"
                  startIcon={<PreviewIcon />}
                  fullWidth
                >
                  プレビュー (先頭100行)
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  fullWidth
                  onClick={() => {
                    setUploadedFile(null);
                    setValidation(null);
                  }}
                >
                  ファイルを削除
                </Button>
              </Stack>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* バリデーション結果 */}
      {validation && (
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  ファイル分析
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText
                      primary="検出エンコード"
                      secondary={
                        <Chip
                          label={validation.encoding}
                          size="small"
                          color="success"
                        />
                      }
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="行数"
                      secondary={validation.rows.toLocaleString()}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="列数"
                      secondary={validation.columns}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="商品数"
                      secondary={validation.products}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="SKU数"
                      secondary={validation.skus}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            {validation.warnings && validation.warnings.length > 0 && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                <AlertTitle>警告</AlertTitle>
                <List dense>
                  {validation.warnings.map((warning: string, index: number) => (
                    <ListItem key={index} sx={{ py: 0 }}>
                      <ListItemIcon>
                        <WarningIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={warning} />
                    </ListItem>
                  ))}
                </List>
              </Alert>
            )}

            {validation.errors && validation.errors.length > 0 && (
              <Alert severity="error">
                <AlertTitle>エラー</AlertTitle>
                <List dense>
                  {validation.errors.map((error: string, index: number) => (
                    <ListItem key={index} sx={{ py: 0 }}>
                      <ListItemText primary={error} />
                    </ListItem>
                  ))}
                </List>
              </Alert>
            )}

            {(!validation.errors || validation.errors.length === 0) && (
              <Alert severity="success">
                <AlertTitle>検証成功</AlertTitle>
                ファイルは正常に処理可能です
              </Alert>
            )}
          </Grid>
        </Grid>
      )}

      {/* 空の状態 */}
      {!uploadedFile && (
        <Alert severity="info">
          <AlertTitle>使用方法</AlertTitle>
          <Typography variant="body2">
            1. CSVファイルをドラッグ&ドロップまたは選択<br />
            2. エンコーディングは自動検出されます<br />
            3. ファイル検証後、処理オプションを選択できます
          </Typography>
        </Alert>
      )}
    </Box>
  );
}