import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Chip,
  Grid,
  IconButton,
  Snackbar,
  SelectChangeEvent,
  Card,
  CardContent,
  Tooltip,
  LinearProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  CloudUpload as UploadIcon,
  CloudDownload as DownloadIcon,
  GetApp as GetAppIcon,
  Description as DescriptionIcon,
  Storage as DatabaseIcon,
  Clear as ClearIcon
} from '@mui/icons-material';

// Brand categories
const BRANDS = [
  { id: 'all', name: '全て', icon: '📊' },
  { id: 'iphone', name: 'iPhone', icon: '🍎' },
  { id: 'xperia', name: 'Xperia', icon: '📱' },
  { id: 'aquos', name: 'AQUOS', icon: '💧' },
  { id: 'galaxy', name: 'Galaxy', icon: '🌌' },
  { id: 'pixel', name: 'Pixel', icon: '🔷' },
  { id: 'huawei', name: 'HUAWEI', icon: '🔴' },
  { id: 'arrows', name: 'arrows', icon: '➡️' },
  { id: 'other', name: 'その他', icon: '📱' }
];

// Size options
const SIZES = ['[SS]', '[S]', '[M]', '[L]', '[LL]', '[2L]', '[3L]', '[4L]', '[i6]'];

interface DeviceData {
  id: number;
  device_name: string;
  attribute_value: string;
  size_category: string;
  usage_count: number;
  created_at: string;
}

interface AddDeviceForm {
  variation_item_choice_2: string;
  product_attribute_8: string;
  size_category: string;
}

interface Stats {
  total_devices: number;
  total_sizes: number;
  devices_by_size: { size: string; count: number }[];
  devices_by_brand: { [key: string]: number };
}

const ProductAttributes8Database: React.FC = () => {
  const [selectedBrand, setSelectedBrand] = useState(0);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  
  // Data state
  const [devices, setDevices] = useState<DeviceData[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  
  // Dialog states
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openUploadDialog, setOpenUploadDialog] = useState(false);
  const [formData, setFormData] = useState<AddDeviceForm>({
    variation_item_choice_2: '',
    product_attribute_8: '',
    size_category: '[L]'
  });

  // Load stats
  const loadStats = async () => {
    try {
      const response = await fetch('/api/product-attributes/stats');
      if (!response.ok) throw new Error('Failed to load stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  // Load devices
  const loadDevices = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const brand = BRANDS[selectedBrand].id;
      const params = new URLSearchParams({
        limit: rowsPerPage.toString(),
        offset: (page * rowsPerPage).toString()
      });
      
      if (brand !== 'all') {
        params.append('brand', brand);
      }
      
      const response = await fetch(`/api/product-attributes/devices?${params}`);
      
      if (!response.ok) {
        throw new Error('Failed to load devices');
      }
      
      const data = await response.json();
      setDevices(data.devices || []);
      setTotalCount(data.total || 0);
    } catch (error) {
      setError('データの読み込みに失敗しました');
      console.error('Error loading devices:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load data on component mount and when filters change
  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    loadDevices();
  }, [selectedBrand, page, rowsPerPage]);

  const handleBrandChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedBrand(newValue);
    setPage(0);
  };

  const handlePageChange = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleOpenAddDialog = () => {
    setFormData({
      variation_item_choice_2: '',
      product_attribute_8: '',
      size_category: '[L]'
    });
    setOpenAddDialog(true);
  };

  const handleCloseAddDialog = () => {
    setOpenAddDialog(false);
  };

  const handleFormChange = (field: keyof AddDeviceForm) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | SelectChangeEvent
  ) => {
    setFormData({
      ...formData,
      [field]: event.target.value
    });
  };

  const handleAddDevice = async () => {
    if (!formData.variation_item_choice_2 || !formData.product_attribute_8) {
      setError('デバイス名と属性値は必須です');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/product-attributes/devices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to add device');
      }

      setSuccess('デバイスを追加しました');
      handleCloseAddDialog();
      loadDevices();
      loadStats();
    } catch (error) {
      setError('デバイスの追加に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDevice = async (deviceId: number) => {
    if (!confirm('このデバイスを削除しますか？')) return;

    try {
      const response = await fetch(`/api/product-attributes/devices/${deviceId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Failed to delete device');
      }

      setSuccess('デバイスを削除しました');
      loadDevices();
      loadStats();
    } catch (error) {
      setError('デバイスの削除に失敗しました');
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/product-attributes/import-csv', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to upload file');
      }

      const result = await response.json();
      setSuccess(result.message || 'CSVファイルをインポートしました');
      setOpenUploadDialog(false);
      loadDevices();
      loadStats();
    } catch (error) {
      setError('CSVファイルのインポートに失敗しました');
    } finally {
      setUploading(false);
    }
  };

  const handleExport = () => {
    window.open('/api/product-attributes/export-csv', '_blank');
  };

  const handleDownloadTemplate = () => {
    window.open('/api/product-attributes/template-csv', '_blank');
  };

  const handleClearAll = async () => {
    if (!confirm('すべてのデータを削除しますか？この操作は取り消せません。')) return;

    try {
      const response = await fetch('/api/product-attributes/clear-all', {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Failed to clear data');
      }

      setSuccess('すべてのデータを削除しました');
      loadDevices();
      loadStats();
    } catch (error) {
      setError('データの削除に失敗しました');
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleString('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const getSizeBadgeColor = (size: string): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    if (size.includes('SS') || size.includes('S')) return 'info';
    if (size.includes('M')) return 'primary';
    if (size.includes('L') && !size.includes('LL')) return 'success';
    if (size.includes('LL') || size.includes('2L') || size.includes('3L') || size.includes('4L')) return 'warning';
    return 'default';
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <DatabaseIcon sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
            <Typography variant="h4">
              商品属性（値）8 データベース管理
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="テンプレートダウンロード">
              <IconButton onClick={handleDownloadTemplate} color="primary">
                <DescriptionIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="CSVエクスポート">
              <IconButton onClick={handleExport} color="primary">
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="データクリア">
              <IconButton onClick={handleClearAll} color="error">
                <ClearIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Statistics Cards */}
        {stats && (
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    総デバイス数
                  </Typography>
                  <Typography variant="h4">
                    {stats.total_devices}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    サイズカテゴリー
                  </Typography>
                  <Typography variant="h4">
                    {stats.total_sizes}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    ブランド別デバイス数
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                    {Object.entries(stats.devices_by_brand).map(([brand, count]) => (
                      <Chip
                        key={brand}
                        label={`${brand}: ${count}`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Brand Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={selectedBrand}
            onChange={handleBrandChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              borderBottom: 1,
              borderColor: 'divider',
              '& .MuiTab-root': {
                minHeight: 64,
                fontSize: '1rem'
              }
            }}
          >
            {BRANDS.map((brand, index) => (
              <Tab
                key={brand.id}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <span style={{ fontSize: '1.5rem' }}>{brand.icon}</span>
                    <span>{brand.name}</span>
                    {stats && brand.id !== 'all' && stats.devices_by_brand[brand.name] && (
                      <Chip label={stats.devices_by_brand[brand.name]} size="small" />
                    )}
                  </Box>
                }
              />
            ))}
          </Tabs>
        </Paper>

        {/* Actions Bar */}
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <span style={{ fontSize: '1.5rem' }}>{BRANDS[selectedBrand].icon}</span>
            {BRANDS[selectedBrand].name} デバイス一覧
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<UploadIcon />}
              onClick={() => setOpenUploadDialog(true)}
            >
              CSVインポート
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleOpenAddDialog}
            >
              デバイス追加
            </Button>
            <IconButton onClick={loadDevices} color="primary">
              <RefreshIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Data Table */}
        <Paper>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error" sx={{ m: 2 }}>
              {error}
            </Alert>
          ) : (
            <>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>id</TableCell>
                      <TableCell>device_name</TableCell>
                      <TableCell>attribute_value</TableCell>
                      <TableCell>size_category</TableCell>
                      <TableCell align="center">usage_count</TableCell>
                      <TableCell>created_at</TableCell>
                      <TableCell align="center">操作</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {devices.map((device) => (
                      <TableRow key={device.id} hover>
                        <TableCell>{device.id}</TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {device.device_name}
                          </Typography>
                        </TableCell>
                        <TableCell>{device.attribute_value}</TableCell>
                        <TableCell>
                          <Chip
                            label={device.size_category}
                            size="small"
                            color={getSizeBadgeColor(device.size_category)}
                          />
                        </TableCell>
                        <TableCell align="center">{device.usage_count || 1}</TableCell>
                        <TableCell>
                          <Typography variant="caption">
                            {formatDate(device.created_at)}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteDevice(device.id)}
                            color="error"
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                    {devices.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={7} align="center">
                          <Typography variant="body2" color="textSecondary" sx={{ py: 4 }}>
                            データがありません
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
              <TablePagination
                component="div"
                count={totalCount}
                page={page}
                onPageChange={handlePageChange}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={handleRowsPerPageChange}
                labelRowsPerPage="行数:"
                labelDisplayedRows={({ from, to, count }) => `${from}-${to} of ${count !== -1 ? count : `${to}+`}`}
              />
            </>
          )}
        </Paper>

        {/* Add Device Dialog */}
        <Dialog open={openAddDialog} onClose={handleCloseAddDialog} maxWidth="sm" fullWidth>
          <DialogTitle>新規デバイス追加</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="device_name (バリエーション項目選択肢2)"
                  value={formData.variation_item_choice_2}
                  onChange={handleFormChange('variation_item_choice_2')}
                  placeholder="例: iPhone16 ProMax"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="attribute_value (商品属性（値）8)"
                  value={formData.product_attribute_8}
                  onChange={handleFormChange('product_attribute_8')}
                  placeholder="例: iPhone 16 Pro Max"
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>size_category (サイズ)</InputLabel>
                  <Select
                    value={formData.size_category}
                    onChange={handleFormChange('size_category')}
                    label="size_category (サイズ)"
                  >
                    {SIZES.map((size) => (
                      <MenuItem key={size} value={size}>
                        {size}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseAddDialog}>キャンセル</Button>
            <Button
              onClick={handleAddDevice}
              variant="contained"
              disabled={loading || !formData.variation_item_choice_2 || !formData.product_attribute_8}
            >
              追加
            </Button>
          </DialogActions>
        </Dialog>

        {/* Upload CSV Dialog */}
        <Dialog open={openUploadDialog} onClose={() => setOpenUploadDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>CSVファイルインポート</DialogTitle>
          <DialogContent>
            <Box sx={{ py: 2 }}>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                CSVファイルには以下の列が必要です：
              </Typography>
              <ul>
                <li>サイズ</li>
                <li>バリエーション項目選択肢2</li>
                <li>商品属性（値）8</li>
              </ul>
              <Button
                variant="outlined"
                startIcon={<GetAppIcon />}
                onClick={handleDownloadTemplate}
                sx={{ mt: 2, mb: 3 }}
                fullWidth
              >
                テンプレートファイルをダウンロード
              </Button>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
                id="csv-upload"
              />
              <label htmlFor="csv-upload">
                <Button
                  variant="contained"
                  component="span"
                  startIcon={<UploadIcon />}
                  fullWidth
                  disabled={uploading}
                >
                  {uploading ? 'アップロード中...' : 'CSVファイルを選択'}
                </Button>
              </label>
              {uploading && <LinearProgress sx={{ mt: 2 }} />}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenUploadDialog(false)} disabled={uploading}>
              閉じる
            </Button>
          </DialogActions>
        </Dialog>

        {/* Success/Error Messages */}
        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={() => setError(null)}
        >
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Snackbar>

        <Snackbar
          open={!!success}
          autoHideDuration={3000}
          onClose={() => setSuccess(null)}
        >
          <Alert severity="success" onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        </Snackbar>
      </Box>
    </Container>
  );
};

export default ProductAttributes8Database;