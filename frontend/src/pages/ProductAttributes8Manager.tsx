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
  CardContent
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Smartphone as SmartphoneIcon,
  Category as CategoryIcon
} from '@mui/icons-material';

// Brand categories
const BRANDS = [
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
  device_name: string;
  attribute_value: string;
  size_category: string;
  brand: string;
}

const ProductAttributes8Manager: React.FC = () => {
  const [selectedBrand, setSelectedBrand] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Data state
  const [devices, setDevices] = useState<DeviceData[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  
  // Add dialog state
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [formData, setFormData] = useState<AddDeviceForm>({
    device_name: '',
    attribute_value: '',
    size_category: '[L]',
    brand: 'iphone'
  });

  // Load devices by brand
  const loadDevices = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const brand = BRANDS[selectedBrand].id;
      const response = await fetch(
        `/api/multi-database/product_attributes_8/devices-by-brand?brand=${brand}&limit=${rowsPerPage}&offset=${page * rowsPerPage}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to load devices');
      }
      
      const data = await response.json();
      setDevices(data.devices || []);
      setTotalCount(data.total || 0);
    } catch (error) {
      console.error('Error loading devices:', error);
      // Fallback to loading all devices
      try {
        const response = await fetch(
          `/api/multi-database/product_attributes_8/data?table=attribute_mappings&limit=${rowsPerPage}`
        );
        
        if (!response.ok) {
          throw new Error('Failed to load data');
        }
        
        const data = await response.json();
        
        // Filter by brand
        const brandName = BRANDS[selectedBrand].name.toLowerCase();
        const filtered = (data.data || []).filter((item: any) => {
          const deviceName = (item.device_name || '').toLowerCase();
          const attrValue = (item.attribute_value || '').toLowerCase();
          
          if (brandName === 'iphone') {
            return deviceName.includes('iphone') || attrValue.includes('iphone');
          } else if (brandName === 'xperia') {
            return deviceName.includes('xperia') || deviceName.includes('so-') || attrValue.includes('xperia');
          } else if (brandName === 'aquos') {
            return deviceName.includes('aquos') || deviceName.includes('sh-') || attrValue.includes('aquos');
          } else if (brandName === 'galaxy') {
            return deviceName.includes('galaxy') || deviceName.includes('sc-') || attrValue.includes('galaxy');
          } else if (brandName === 'pixel') {
            return deviceName.includes('pixel') || attrValue.includes('pixel');
          } else if (brandName === 'huawei') {
            return deviceName.includes('huawei') || deviceName.includes('mate') || attrValue.includes('huawei');
          } else if (brandName === 'arrows') {
            return deviceName.includes('arrows') || deviceName.includes('m0') || attrValue.includes('arrows');
          } else {
            // その他 - exclude all known brands
            return !deviceName.includes('iphone') && !deviceName.includes('xperia') && 
                   !deviceName.includes('aquos') && !deviceName.includes('galaxy') &&
                   !deviceName.includes('pixel') && !deviceName.includes('huawei') &&
                   !deviceName.includes('arrows');
          }
        });
        
        setDevices(filtered);
        setTotalCount(filtered.length);
      } catch (fallbackError) {
        setError('データの読み込みに失敗しました');
      }
    } finally {
      setLoading(false);
    }
  };

  // Load devices when brand or pagination changes
  useEffect(() => {
    loadDevices();
  }, [selectedBrand, page, rowsPerPage]);

  const handleBrandChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedBrand(newValue);
    setPage(0); // Reset to first page when changing brands
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
      device_name: '',
      attribute_value: '',
      size_category: '[L]',
      brand: BRANDS[selectedBrand].id
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
    if (!formData.device_name || !formData.attribute_value) {
      setError('デバイス名と属性値は必須です');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/multi-database/product_attributes_8/add-device', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          size_category: formData.size_category,
          variation_item_choice_2: formData.device_name,
          product_attribute_8: formData.attribute_value
        })
      });

      if (!response.ok) {
        throw new Error('Failed to add device');
      }

      setSuccess('デバイスを追加しました');
      handleCloseAddDialog();
      loadDevices(); // Reload the data
    } catch (error) {
      setError('デバイスの追加に失敗しました');
    } finally {
      setLoading(false);
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
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <SmartphoneIcon sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
          <Typography variant="h4">
            商品属性（値）8 管理
          </Typography>
        </Box>

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
                      <TableCell>ID</TableCell>
                      <TableCell>device_name</TableCell>
                      <TableCell>attribute_value</TableCell>
                      <TableCell>size_category</TableCell>
                      <TableCell align="center">usage_count</TableCell>
                      <TableCell>created_at</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {devices.map((device, index) => (
                      <TableRow key={device.id || index} hover>
                        <TableCell>{device.id || page * rowsPerPage + index + 1}</TableCell>
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
                      </TableRow>
                    ))}
                    {devices.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
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
                labelDisplayedRows={({ from, to, count }) => `${from}-${to} of ${count}`}
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
                  value={formData.device_name}
                  onChange={handleFormChange('device_name')}
                  placeholder="例: iPhone16 ProMax"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="attribute_value (商品属性（値）8)"
                  value={formData.attribute_value}
                  onChange={handleFormChange('attribute_value')}
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
              disabled={loading || !formData.device_name || !formData.attribute_value}
            >
              追加
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

export default ProductAttributes8Manager;