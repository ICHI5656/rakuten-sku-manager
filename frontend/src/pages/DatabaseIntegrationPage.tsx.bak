import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Tabs,
  Tab,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  CloudDownload as DownloadIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

interface BrandValue {
  id?: number;
  brand_name: string;
  row_index: number;
  attribute_value: string;
}

interface DeviceAttribute {
  id: number;
  brand: string;
  device_name: string;
  attribute_value: string;
  size_category?: string;
  usage_count: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const DatabaseIntegrationPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [brands, setBrands] = useState<string[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [brandValues, setBrandValues] = useState<BrandValue[]>([]);
  const [devices, setDevices] = useState<DeviceAttribute[]>([]);
  const [editingBrandValue, setEditingBrandValue] = useState<BrandValue | null>(null);
  const [editingDevice, setEditingDevice] = useState<DeviceAttribute | null>(null);
  const [newBrandValue, setNewBrandValue] = useState<BrandValue>({
    brand_name: '',
    row_index: 0,
    attribute_value: ''
  });
  const [newDevice, setNewDevice] = useState<Partial<DeviceAttribute>>({
    brand: '',
    device_name: '',
    attribute_value: '',
    size_category: ''
  });
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openImportDialog, setOpenImportDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [stats, setStats] = useState({ brands: 0, devices: 0, totalValues: 0 });

  // 統計情報の取得
  const fetchStats = async () => {
    try {
      const brandResponse = await fetch('/api/database/stats');
      const deviceResponse = await fetch('/api/product-attributes/stats');
      
      if (brandResponse.ok && deviceResponse.ok) {
        const brandData = await brandResponse.json();
        const deviceData = await deviceResponse.json();
        
        setStats({
          brands: brandData.total_brands || 0,
          devices: deviceData.total_devices || 0,
          totalValues: brandData.total_values || 0
        });
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  // ブランド一覧の取得
  const fetchBrands = async () => {
    try {
      const response = await fetch('/api/database/brands');
      if (response.ok) {
        const data = await response.json();
        setBrands(data);
        if (data.length > 0 && !selectedBrand) {
          setSelectedBrand(data[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch brands:', error);
    }
  };

  // ブランド属性値の取得
  const fetchBrandValues = async (brand: string) => {
    try {
      const response = await fetch(`/api/database/brand-values/${brand}`);
      if (response.ok) {
        const data = await response.json();
        setBrandValues(data);
      }
    } catch (error) {
      console.error('Failed to fetch brand values:', error);
    }
  };

  // デバイス一覧の取得
  const fetchDevices = async () => {
    try {
      const response = await fetch('/api/product-attributes/devices');
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) {
          setDevices(data);
        }
      }
    } catch (error) {
      console.error('Failed to fetch devices:', error);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchBrands();
    fetchDevices();
  }, []);

  useEffect(() => {
    if (selectedBrand) {
      fetchBrandValues(selectedBrand);
    }
  }, [selectedBrand]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // ブランド属性値の追加
  const handleAddBrandValue = async () => {
    try {
      const response = await fetch('/api/database/brand-values', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newBrandValue)
      });
      
      if (response.ok) {
        setSnackbar({ open: true, message: 'ブランド属性値を追加しました', severity: 'success' });
        setOpenAddDialog(false);
        setNewBrandValue({ brand_name: '', row_index: 0, attribute_value: '' });
        fetchBrandValues(selectedBrand);
        fetchStats();
      }
    } catch (error) {
      setSnackbar({ open: true, message: 'エラーが発生しました', severity: 'error' });
    }
  };

  // ブランド属性値の更新
  const handleUpdateBrandValue = async () => {
    if (!editingBrandValue || !editingBrandValue.id) return;
    
    try {
      const response = await fetch(`/api/database/brand-values/${editingBrandValue.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingBrandValue)
      });
      
      if (response.ok) {
        setSnackbar({ open: true, message: '更新しました', severity: 'success' });
        setEditingBrandValue(null);
        fetchBrandValues(selectedBrand);
      }
    } catch (error) {
      setSnackbar({ open: true, message: 'エラーが発生しました', severity: 'error' });
    }
  };

  // ブランド属性値の削除
  const handleDeleteBrandValue = async (id: number) => {
    if (!confirm('削除してもよろしいですか？')) return;
    
    try {
      const response = await fetch(`/api/database/brand-values/${id}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setSnackbar({ open: true, message: '削除しました', severity: 'success' });
        fetchBrandValues(selectedBrand);
        fetchStats();
      }
    } catch (error) {
      setSnackbar({ open: true, message: 'エラーが発生しました', severity: 'error' });
    }
  };

  // デバイスの追加
  const handleAddDevice = async () => {
    try {
      const response = await fetch('/api/product-attributes/devices', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newDevice)
      });
      
      if (response.ok) {
        setSnackbar({ open: true, message: 'デバイスを追加しました', severity: 'success' });
        setNewDevice({ brand: '', device_name: '', attribute_value: '', size_category: '' });
        fetchDevices();
        fetchStats();
      }
    } catch (error) {
      setSnackbar({ open: true, message: 'エラーが発生しました', severity: 'error' });
    }
  };

  // データのエクスポート
  const handleExportBrandData = async () => {
    try {
      const response = await fetch('/api/database/export');
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `brand_attributes_${new Date().toISOString().split('T')[0]}.xlsx`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      setSnackbar({ open: true, message: 'エクスポートエラー', severity: 'error' });
    }
  };

  const handleExportDeviceData = async () => {
    try {
      const response = await fetch('/api/product-attributes/export');
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `device_attributes_${new Date().toISOString().split('T')[0]}.xlsx`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      setSnackbar({ open: true, message: 'エクスポートエラー', severity: 'error' });
    }
  };

  // データのインポート
  const handleImportData = async (event: React.ChangeEvent<HTMLInputElement>, type: 'brand' | 'device') => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const endpoint = type === 'brand' ? '/api/database/import' : '/api/product-attributes/import';
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        setSnackbar({ open: true, message: 'インポートが完了しました', severity: 'success' });
        if (type === 'brand') {
          fetchBrands();
          fetchBrandValues(selectedBrand);
        } else {
          fetchDevices();
        }
        fetchStats();
      }
    } catch (error) {
      setSnackbar({ open: true, message: 'インポートエラー', severity: 'error' });
    }
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          データベース統合管理
        </Typography>
        
        {/* 統計情報カード */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  ブランド数
                </Typography>
                <Typography variant="h5">
                  {stats.brands}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  デバイス数
                </Typography>
                <Typography variant="h5">
                  {stats.devices}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  属性値総数
                </Typography>
                <Typography variant="h5">
                  {stats.totalValues}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="ブランド属性管理" />
              <Tab label="デバイス管理" />
              <Tab label="インポート/エクスポート" />
            </Tabs>
          </Box>

          {/* ブランド属性管理タブ */}
          <TabPanel value={tabValue} index={0}>
            <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
              <FormControl size="small" sx={{ minWidth: 200 }}>
                <InputLabel>ブランド選択</InputLabel>
                <Select
                  value={selectedBrand}
                  onChange={(e) => setSelectedBrand(e.target.value)}
                  label="ブランド選択"
                >
                  {brands.map((brand) => (
                    <MenuItem key={brand} value={brand}>
                      {brand}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setOpenAddDialog(true)}
              >
                属性値追加
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => fetchBrandValues(selectedBrand)}
              >
                更新
              </Button>
            </Box>

            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>行番号</TableCell>
                    <TableCell>属性値</TableCell>
                    <TableCell>操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {brandValues.map((value) => (
                    <TableRow key={value.id}>
                      <TableCell>{value.row_index}</TableCell>
                      <TableCell>
                        {editingBrandValue?.id === value.id ? (
                          <TextField
                            size="small"
                            value={editingBrandValue?.attribute_value || ''}
                            onChange={(e) => {
                              if (editingBrandValue) {
                                setEditingBrandValue({
                                  ...editingBrandValue,
                                  attribute_value: e.target.value
                                })
                              }
                            }}
                            fullWidth
                          />
                        ) : (
                          value.attribute_value
                        )}
                      </TableCell>
                      <TableCell>
                        {editingBrandValue?.id === value.id ? (
                          <>
                            <IconButton size="small" onClick={handleUpdateBrandValue}>
                              <SaveIcon />
                            </IconButton>
                            <IconButton size="small" onClick={() => setEditingBrandValue(null)}>
                              <CancelIcon />
                            </IconButton>
                          </>
                        ) : (
                          <>
                            <IconButton size="small" onClick={() => setEditingBrandValue(value)}>
                              <EditIcon />
                            </IconButton>
                            <IconButton size="small" onClick={() => handleDeleteBrandValue(value.id!)}>
                              <DeleteIcon />
                            </IconButton>
                          </>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          {/* デバイス管理タブ */}
          <TabPanel value={tabValue} index={1}>
            <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
              <TextField
                size="small"
                label="デバイス名"
                value={newDevice.device_name}
                onChange={(e) => setNewDevice({ ...newDevice, device_name: e.target.value })}
              />
              <TextField
                size="small"
                label="ブランド"
                value={newDevice.brand}
                onChange={(e) => setNewDevice({ ...newDevice, brand: e.target.value })}
              />
              <TextField
                size="small"
                label="属性値"
                value={newDevice.attribute_value}
                onChange={(e) => setNewDevice({ ...newDevice, attribute_value: e.target.value })}
              />
              <TextField
                size="small"
                label="サイズカテゴリ"
                value={newDevice.size_category}
                onChange={(e) => setNewDevice({ ...newDevice, size_category: e.target.value })}
              />
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddDevice}
              >
                追加
              </Button>
            </Box>

            <TableContainer component={Paper} sx={{ maxHeight: 500 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>デバイス名</TableCell>
                    <TableCell>ブランド</TableCell>
                    <TableCell>属性値</TableCell>
                    <TableCell>サイズ</TableCell>
                    <TableCell>使用回数</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {devices.map((device) => (
                    <TableRow key={device.id}>
                      <TableCell>{device.device_name}</TableCell>
                      <TableCell>
                        <Chip label={device.brand} size="small" />
                      </TableCell>
                      <TableCell>{device.attribute_value}</TableCell>
                      <TableCell>{device.size_category || '-'}</TableCell>
                      <TableCell>{device.usage_count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          {/* インポート/エクスポートタブ */}
          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    ブランド属性データ
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                    <Button
                      variant="contained"
                      startIcon={<DownloadIcon />}
                      onClick={handleExportBrandData}
                    >
                      エクスポート
                    </Button>
                    
                    <Button
                      variant="outlined"
                      startIcon={<UploadIcon />}
                      component="label"
                    >
                      インポート
                      <input
                        type="file"
                        hidden
                        accept=".xlsx,.xls"
                        onChange={(e) => handleImportData(e, 'brand')}
                      />
                    </Button>
                  </Box>
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    デバイスデータ
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                    <Button
                      variant="contained"
                      startIcon={<DownloadIcon />}
                      onClick={handleExportDeviceData}
                    >
                      エクスポート
                    </Button>
                    
                    <Button
                      variant="outlined"
                      startIcon={<UploadIcon />}
                      component="label"
                    >
                      インポート
                      <input
                        type="file"
                        hidden
                        accept=".xlsx,.xls"
                        onChange={(e) => handleImportData(e, 'device')}
                      />
                    </Button>
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>
        </Paper>
      </Box>

      {/* 属性値追加ダイアログ */}
      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)}>
        <DialogTitle>ブランド属性値を追加</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="ブランド名"
              value={newBrandValue.brand_name}
              onChange={(e) => setNewBrandValue({ ...newBrandValue, brand_name: e.target.value })}
              fullWidth
            />
            <TextField
              label="行番号"
              type="number"
              value={newBrandValue.row_index}
              onChange={(e) => setNewBrandValue({ ...newBrandValue, row_index: parseInt(e.target.value) })}
              fullWidth
            />
            <TextField
              label="属性値"
              value={newBrandValue.attribute_value}
              onChange={(e) => setNewBrandValue({ ...newBrandValue, attribute_value: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddDialog(false)}>キャンセル</Button>
          <Button onClick={handleAddBrandValue} variant="contained">追加</Button>
        </DialogActions>
      </Dialog>

      {/* スナックバー */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default DatabaseIntegrationPage;