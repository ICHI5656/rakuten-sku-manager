import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  PhoneIphone as PhoneIcon,
  Smartphone as SmartphoneIcon,
  Tablet as TabletIcon,
  Devices as DevicesIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

interface Device {
  id: number;
  brand: string;
  device_name: string;
  attribute_value: string;
  size_category: string;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

interface Brand {
  id: string;
  name: string;
  name_jp: string;
  display_order: number;
  device_count: number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`brand-tabpanel-${index}`}
      aria-labelledby={`brand-tab-${index}`}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const getBrandIcon = (brand: string) => {
  switch (brand) {
    case 'iPhone':
      return <PhoneIcon />;
    case 'Galaxy':
    case 'Xperia':
    case 'AQUOS':
      return <SmartphoneIcon />;
    case 'Google Pixel':
    case 'HUAWEI':
    case 'arrows':
      return <TabletIcon />;
    default:
      return <DevicesIcon />;
  }
};

export default function ProductAttributes8DatabaseV2() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [selectedBrand, setSelectedBrand] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(50);
  const [totalDevices, setTotalDevices] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSize, setSelectedSize] = useState('');
  const [sizes, setSizes] = useState<string[]>([]);
  
  // Dialog states
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editingDevice, setEditingDevice] = useState<Device | null>(null);
  
  // Form data
  const [formData, setFormData] = useState({
    brand: '',
    device_name: '',
    attribute_value: '',
    size_category: '',
    usage_count: 0
  });

  // Statistics
  const [stats, setStats] = useState<any>({
    total_devices: 0,
    by_brand: [],
    by_size: [],
    popular_devices: []
  });

  useEffect(() => {
    fetchBrands();
    fetchSizes();
    fetchStats();
  }, []);

  useEffect(() => {
    if (brands.length > 0) {
      fetchDevices();
    }
  }, [selectedBrand, page, rowsPerPage, searchTerm, selectedSize, brands]);

  const fetchBrands = async () => {
    try {
      const response = await fetch('/api/product-attributes/brands');
      const data = await response.json();
      setBrands(data.brands);
    } catch (error) {
      console.error('Error fetching brands:', error);
    }
  };

  const fetchDevices = async () => {
    if (brands.length === 0) return;
    
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page + 1),
        limit: String(rowsPerPage),
        ...(brands[selectedBrand] && { brand: brands[selectedBrand].id }),
        ...(searchTerm && { search: searchTerm }),
        ...(selectedSize && { size_category: selectedSize })
      });

      const response = await fetch(`/api/product-attributes/devices?${params}`);
      const data = await response.json();
      
      // APIは配列を直接返すように修正されたので、配列として処理
      if (Array.isArray(data)) {
        setDevices(data);
        setTotalDevices(data.length);
      } else {
        // 念のため旧形式もサポート
        setDevices(data.devices || []);
        setTotalDevices(data.total || 0);
      }
    } catch (error) {
      console.error('Error fetching devices:', error);
      setDevices([]);
      setTotalDevices(0);
    } finally {
      setLoading(false);
    }
  };

  const fetchSizes = async () => {
    try {
      const response = await fetch('/api/product-attributes/sizes');
      const data = await response.json();
      setSizes(data.sizes.map((s: any) => s.size));
    } catch (error) {
      console.error('Error fetching sizes:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/product-attributes/stats');
      const data = await response.json();
      setStats(data || {
        total_devices: 0,
        by_brand: [],
        by_size: [],
        popular_devices: []
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
      setStats({
        total_devices: 0,
        by_brand: [],
        by_size: [],
        popular_devices: []
      });
    }
  };

  const handleAddDevice = async () => {
    try {
      const response = await fetch('/api/product-attributes/devices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setOpenAddDialog(false);
        setFormData({
          brand: '',
          device_name: '',
          attribute_value: '',
          size_category: '',
          usage_count: 0
        });
        fetchDevices();
        fetchBrands();
      } else {
        const errorData = await response.json();
        console.error('Failed to save device:', errorData);
        alert(`エラー: ${JSON.stringify(errorData.detail || errorData)}`);
      }
    } catch (error) {
      console.error('Error adding device:', error);
      alert('デバイスの追加中にエラーが発生しました');
    }
  };

  const handleUpdateDevice = async () => {
    if (!editingDevice) return;

    try {
      const response = await fetch(`/api/product-attributes/devices/${editingDevice.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setOpenEditDialog(false);
        setEditingDevice(null);
        setFormData({
          brand: '',
          device_name: '',
          attribute_value: '',
          size_category: '',
          usage_count: 0
        });
        fetchDevices();
      }
    } catch (error) {
      console.error('Error updating device:', error);
    }
  };

  const handleDeleteDevice = async (id: number) => {
    if (!confirm('このデバイスを削除してもよろしいですか？')) return;

    try {
      const response = await fetch(`/api/product-attributes/devices/${id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        fetchDevices();
        fetchBrands();
      }
    } catch (error) {
      console.error('Error deleting device:', error);
    }
  };

  const handleExport = async () => {
    try {
      const brand = brands[selectedBrand]?.id;
      const url = brand 
        ? `/api/product-attributes/export-csv?brand=${brand}`
        : '/api/product-attributes/export-csv';
      
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `product_attributes_${brand || 'all'}_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      console.error('Error exporting CSV:', error);
    }
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/product-attributes/import-csv', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        alert(`インポート完了: ${result.imported}件追加, ${result.skipped}件スキップ`);
        fetchDevices();
        fetchBrands();
      }
    } catch (error) {
      console.error('Error importing CSV:', error);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch('/api/product-attributes/template-csv');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'product_attributes_template.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      console.error('Error downloading template:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        商品属性（値）8 データベース管理
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                総デバイス数
              </Typography>
              <Typography variant="h5">
                {stats?.total_devices || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                ブランド数
              </Typography>
              <Typography variant="h5">
                {brands?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                サイズカテゴリ数
              </Typography>
              <Typography variant="h5">
                {sizes?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                最多ブランド
              </Typography>
              <Typography variant="h5">
                {stats?.by_brand?.[0]?.brand || '-'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ mb: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenAddDialog(true)}
        >
          新規追加
        </Button>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={handleExport}
        >
          CSVエクスポート
        </Button>
        <Button
          variant="outlined"
          startIcon={<UploadIcon />}
          component="label"
        >
          CSVインポート
          <input
            type="file"
            hidden
            accept=".csv"
            onChange={handleImport}
          />
        </Button>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={handleDownloadTemplate}
        >
          テンプレート
        </Button>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => {
            fetchDevices();
            fetchBrands();
            fetchStats();
          }}
        >
          更新
        </Button>
      </Box>

      {/* Search and Filter */}
      <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
        <TextField
          placeholder="デバイス検索..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
          }}
          sx={{ flexGrow: 1, maxWidth: 400 }}
        />
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>サイズ</InputLabel>
          <Select
            value={selectedSize}
            label="サイズ"
            onChange={(e) => setSelectedSize(e.target.value)}
          >
            <MenuItem value="">
              <em>すべて</em>
            </MenuItem>
            {sizes.map(size => (
              <MenuItem key={size} value={size}>
                {size}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        {(searchTerm || selectedSize) && (
          <Button
            startIcon={<ClearIcon />}
            onClick={() => {
              setSearchTerm('');
              setSelectedSize('');
            }}
          >
            クリア
          </Button>
        )}
      </Box>

      {/* Brand Tabs */}
      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs
          value={selectedBrand}
          onChange={(_, newValue) => {
            setSelectedBrand(newValue);
            setPage(0);
          }}
          variant="scrollable"
          scrollButtons="auto"
        >
          {Array.isArray(brands) && brands.map((brand, index) => (
            <Tab
              key={brand.id}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {getBrandIcon(brand.id)}
                  <span>{brand.name_jp || brand.name}</span>
                  <Chip size="small" label={brand.device_count || 0} />
                </Box>
              }
            />
          ))}
        </Tabs>

        {Array.isArray(brands) && brands.map((brand, index) => (
          <TabPanel key={brand.id} value={selectedBrand} index={index}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>デバイス名</TableCell>
                    <TableCell>属性値</TableCell>
                    <TableCell>サイズカテゴリ</TableCell>
                    <TableCell align="center">使用回数</TableCell>
                    <TableCell align="center">操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        <CircularProgress />
                      </TableCell>
                    </TableRow>
                  ) : devices.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        データがありません
                      </TableCell>
                    </TableRow>
                  ) : (
                    devices.map(device => (
                      <TableRow key={device.id}>
                        <TableCell>{device.device_name}</TableCell>
                        <TableCell>{device.attribute_value}</TableCell>
                        <TableCell>
                          <Chip
                            label={device.size_category}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell align="center">{device.usage_count}</TableCell>
                        <TableCell align="center">
                          <Tooltip title="編集">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setEditingDevice(device);
                                setFormData({
                                  brand: device.brand,
                                  device_name: device.device_name,
                                  attribute_value: device.attribute_value,
                                  size_category: device.size_category,
                                  usage_count: device.usage_count
                                });
                                setOpenEditDialog(true);
                              }}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="削除">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDeleteDevice(device.id)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={totalDevices}
              page={page}
              onPageChange={(_, newPage) => setPage(newPage)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
              rowsPerPageOptions={[25, 50, 100, 200]}
            />
          </TabPanel>
        ))}
      </Paper>

      {/* Add Dialog */}
      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>新規デバイス追加</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <FormControl fullWidth>
              <InputLabel>ブランド</InputLabel>
              <Select
                value={formData.brand}
                label="ブランド"
                onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
              >
                {brands.map(brand => (
                  <MenuItem key={brand.id} value={brand.name}>
                    {brand.name_jp}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="デバイス名"
              fullWidth
              value={formData.device_name}
              onChange={(e) => setFormData({ ...formData, device_name: e.target.value })}
            />
            <TextField
              label="属性値"
              fullWidth
              value={formData.attribute_value}
              onChange={(e) => setFormData({ ...formData, attribute_value: e.target.value })}
            />
            <TextField
              label="サイズカテゴリ"
              fullWidth
              value={formData.size_category}
              onChange={(e) => setFormData({ ...formData, size_category: e.target.value })}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddDialog(false)}>キャンセル</Button>
          <Button onClick={handleAddDevice} variant="contained">追加</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={openEditDialog} onClose={() => setOpenEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>デバイス編集</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <FormControl fullWidth>
              <InputLabel>ブランド</InputLabel>
              <Select
                value={formData.brand}
                label="ブランド"
                onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
              >
                {brands.map(brand => (
                  <MenuItem key={brand.id} value={brand.name}>
                    {brand.name_jp}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="デバイス名"
              fullWidth
              value={formData.device_name}
              onChange={(e) => setFormData({ ...formData, device_name: e.target.value })}
            />
            <TextField
              label="属性値"
              fullWidth
              value={formData.attribute_value}
              onChange={(e) => setFormData({ ...formData, attribute_value: e.target.value })}
            />
            <TextField
              label="サイズカテゴリ"
              fullWidth
              value={formData.size_category}
              onChange={(e) => setFormData({ ...formData, size_category: e.target.value })}
            />
            <TextField
              label="使用回数"
              type="number"
              fullWidth
              value={formData.usage_count}
              onChange={(e) => setFormData({ ...formData, usage_count: parseInt(e.target.value) || 0 })}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditDialog(false)}>キャンセル</Button>
          <Button onClick={handleUpdateDevice} variant="contained">更新</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}