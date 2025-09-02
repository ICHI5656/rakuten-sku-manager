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
  id?: number;
  device_name: string;
  brand: string;
  attribute_value: string;
  size?: string;
  size_category?: string;
  usage_count?: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
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
  const [snackbar, setSnackbar] = useState({ 
    open: false, 
    message: '', 
    severity: 'success' as 'success' | 'error' 
  });
  const [stats, setStats] = useState({ 
    brands: 0, 
    devices: 0, 
    totalValues: 0 
  });

  // 統計情報の取得
  const fetchStats = async () => {
    try {
      const [brandResponse, deviceResponse] = await Promise.all([
        fetch('/api/database/stats'),
        fetch('/api/product-attributes/stats')
      ]);
      
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
        // APIがオブジェクトの配列を返す場合、brand_nameを抽出
        const brandNames = data.map((item: any) => 
          typeof item === 'string' ? item : item.brand_name
        );
        setBrands(brandNames);
        if (brandNames.length > 0 && !selectedBrand) {
          setSelectedBrand(brandNames[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch brands:', error);
      showSnackbar('ブランド一覧の取得に失敗しました', 'error');
    }
  };

  // デバイス一覧の取得
  const fetchDevices = async () => {
    try {
      const response = await fetch('/api/product-attributes/devices');
      if (response.ok) {
        const data = await response.json();
        setDevices(data);
      }
    } catch (error) {
      console.error('Failed to fetch devices:', error);
      showSnackbar('デバイス一覧の取得に失敗しました', 'error');
    }
  };

  // 初期データロード
  useEffect(() => {
    fetchStats();
    fetchBrands();
    fetchDevices();
  }, []);

  // スナックバー表示
  const showSnackbar = (message: string, severity: 'success' | 'error' = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  // タブ変更処理
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // ブランド値追加
  const handleAddBrandValue = async () => {
    try {
      const response = await fetch('/api/database/brand-values', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newBrandValue)
      });
      
      if (response.ok) {
        showSnackbar('ブランド値を追加しました');
        setOpenAddDialog(false);
        setNewBrandValue({ brand_name: '', row_index: 0, attribute_value: '' });
        fetchBrands();
      } else {
        showSnackbar('追加に失敗しました', 'error');
      }
    } catch (error) {
      showSnackbar('エラーが発生しました', 'error');
    }
  };

  // デバイス追加
  const handleAddDevice = async () => {
    try {
      const response = await fetch('/api/product-attributes/devices', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newDevice)
      });
      
      if (response.ok) {
        showSnackbar('デバイスを追加しました');
        setOpenAddDialog(false);
        setNewDevice({ brand: '', device_name: '', attribute_value: '', size_category: '' });
        fetchDevices();
        fetchStats();
      } else {
        showSnackbar('追加に失敗しました', 'error');
      }
    } catch (error) {
      showSnackbar('エラーが発生しました', 'error');
    }
  };

  // エクスポート処理
  const handleExport = async (type: 'brand' | 'device') => {
    try {
      const endpoint = type === 'brand' 
        ? '/api/database/export' 
        : '/api/product-attributes/export';
      
      const response = await fetch(endpoint);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = type === 'brand' 
          ? 'brand_database.xlsx' 
          : 'device_attributes.xlsx';
        a.click();
        window.URL.revokeObjectURL(url);
        showSnackbar('エクスポートが完了しました');
      }
    } catch (error) {
      showSnackbar('エクスポートに失敗しました', 'error');
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            データベース統合管理
          </Typography>
          
          <Grid container spacing={2} sx={{ mt: 2 }}>
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
                    総属性値数
                  </Typography>
                  <Typography variant="h5">
                    {stats.totalValues}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="ブランドDB管理" />
            <Tab label="商品属性データベース" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>ブランド選択</InputLabel>
              <Select
                value={selectedBrand}
                onChange={(e) => setSelectedBrand(e.target.value)}
                label="ブランド選択"
              >
                {brands.map(brand => (
                  <MenuItem key={brand} value={brand}>
                    {brand}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Box>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setOpenAddDialog(true)}
                sx={{ mr: 1 }}
              >
                追加
              </Button>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={() => handleExport('brand')}
              >
                エクスポート
              </Button>
            </Box>
          </Box>

          <Typography variant="h6" sx={{ mt: 3 }}>
            ブランド一覧
          </Typography>
          <Box sx={{ mt: 2 }}>
            {brands.map(brand => (
              <Chip
                key={brand}
                label={brand}
                sx={{ m: 0.5 }}
                color={brand === selectedBrand ? 'primary' : 'default'}
                onClick={() => setSelectedBrand(brand)}
              />
            ))}
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="h6">
              デバイス属性管理
            </Typography>
            
            <Box>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setOpenAddDialog(true)}
                sx={{ mr: 1 }}
              >
                デバイス追加
              </Button>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={() => handleExport('device')}
              >
                エクスポート
              </Button>
            </Box>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>デバイス名</TableCell>
                  <TableCell>ブランド</TableCell>
                  <TableCell>属性値</TableCell>
                  <TableCell>サイズカテゴリ</TableCell>
                  <TableCell>使用回数</TableCell>
                  <TableCell>操作</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {devices.slice(0, 10).map(device => (
                  <TableRow key={device.id}>
                    <TableCell>{device.device_name}</TableCell>
                    <TableCell>{device.brand}</TableCell>
                    <TableCell>{device.attribute_value}</TableCell>
                    <TableCell>{device.size_category || '-'}</TableCell>
                    <TableCell>{device.usage_count || 0}</TableCell>
                    <TableCell>
                      <IconButton size="small">
                        <EditIcon />
                      </IconButton>
                      <IconButton size="small">
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* 追加ダイアログ */}
        <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)}>
          <DialogTitle>
            {tabValue === 0 ? 'ブランド値追加' : 'デバイス追加'}
          </DialogTitle>
          <DialogContent>
            {tabValue === 0 ? (
              <Box sx={{ pt: 2 }}>
                <TextField
                  fullWidth
                  label="ブランド名"
                  value={newBrandValue.brand_name}
                  onChange={(e) => setNewBrandValue({...newBrandValue, brand_name: e.target.value})}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="属性値"
                  value={newBrandValue.attribute_value}
                  onChange={(e) => setNewBrandValue({...newBrandValue, attribute_value: e.target.value})}
                />
              </Box>
            ) : (
              <Box sx={{ pt: 2 }}>
                <TextField
                  fullWidth
                  label="デバイス名"
                  value={newDevice.device_name}
                  onChange={(e) => setNewDevice({...newDevice, device_name: e.target.value})}
                  sx={{ mb: 2 }}
                />
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>ブランド</InputLabel>
                  <Select
                    value={newDevice.brand}
                    onChange={(e) => setNewDevice({...newDevice, brand: e.target.value})}
                    label="ブランド"
                  >
                    {brands.map(brand => (
                      <MenuItem key={brand} value={brand}>
                        {brand}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <TextField
                  fullWidth
                  label="属性値"
                  value={newDevice.attribute_value}
                  onChange={(e) => setNewDevice({...newDevice, attribute_value: e.target.value})}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="サイズカテゴリ"
                  value={newDevice.size_category}
                  onChange={(e) => setNewDevice({...newDevice, size_category: e.target.value})}
                />
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenAddDialog(false)}>
              キャンセル
            </Button>
            <Button 
              onClick={tabValue === 0 ? handleAddBrandValue : handleAddDevice} 
              variant="contained"
            >
              追加
            </Button>
          </DialogActions>
        </Dialog>

        {/* スナックバー */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({...snackbar, open: false})}
        >
          <Alert 
            onClose={() => setSnackbar({...snackbar, open: false})} 
            severity={snackbar.severity}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Paper>
    </Container>
  );
};

export default DatabaseIntegrationPage;