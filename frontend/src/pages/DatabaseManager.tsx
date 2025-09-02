import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  TextField,
  Tabs,
  Tab,
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Storage as StorageIcon
} from '@mui/icons-material';
import axios from 'axios';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`database-tabpanel-${index}`}
      aria-labelledby={`database-tab-${index}`}
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

interface BrandData {
  id: number;
  brand_name: string;
  brand_category: string;
  created_at: string;
}

interface BrandValue {
  id: number;
  brand_name: string;
  row_index: number;
  attribute_value: string;
  created_at: string;
}

interface DatabaseStats {
  total_brands: number;
  total_values: number;
  last_updated: string;
}

export default function DatabaseManager() {
  const [tabValue, setTabValue] = useState(0);
  const [brands, setBrands] = useState<BrandData[]>([]);
  const [brandValues, setBrandValues] = useState<BrandValue[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [editDialog, setEditDialog] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [newBrandDialog, setNewBrandDialog] = useState(false);
  const [newBrandName, setNewBrandName] = useState('');
  const [newBrandCategory, setNewBrandCategory] = useState('mobile_device');

  useEffect(() => {
    fetchBrands();
    fetchStats();
  }, []);

  const fetchBrands = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/database/brands');
      setBrands(response.data);
    } catch (err: any) {
      setError('ブランドデータの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const fetchBrandValues = async (brandName: string) => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/database/brand-values/${brandName}`);
      setBrandValues(response.data);
    } catch (err: any) {
      setError('ブランド値の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/database/stats');
      setStats(response.data);
    } catch (err: any) {
      console.error('統計情報の取得に失敗しました');
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setError('');
    setSuccess('');
  };

  const handleBrandSelect = (brandName: string) => {
    setSelectedBrand(brandName);
    fetchBrandValues(brandName);
  };

  const handleAddBrand = async () => {
    if (!newBrandName) {
      setError('ブランド名を入力してください');
      return;
    }

    try {
      await axios.post('/api/database/brands', {
        brand_name: newBrandName,
        brand_category: newBrandCategory
      });
      setSuccess('ブランドを追加しました');
      setNewBrandDialog(false);
      setNewBrandName('');
      fetchBrands();
      fetchStats();
    } catch (err: any) {
      setError('ブランドの追加に失敗しました');
    }
  };

  const handleDeleteBrand = async (brandName: string) => {
    if (!confirm(`ブランド「${brandName}」を削除しますか？`)) {
      return;
    }

    try {
      await axios.delete(`/api/database/brands/${brandName}`);
      setSuccess('ブランドを削除しました');
      fetchBrands();
      fetchStats();
    } catch (err: any) {
      setError('ブランドの削除に失敗しました');
    }
  };

  const handleEditValue = async () => {
    try {
      await axios.put(`/api/database/brand-values/${editingItem.id}`, {
        attribute_value: editingItem.attribute_value
      });
      setSuccess('値を更新しました');
      setEditDialog(false);
      if (selectedBrand) {
        fetchBrandValues(selectedBrand);
      }
    } catch (err: any) {
      setError('値の更新に失敗しました');
    }
  };

  const handleExportDatabase = async () => {
    try {
      const response = await axios.get('/api/database/export', {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `brand_database_${Date.now()}.sqlite`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setSuccess('データベースをエクスポートしました');
    } catch (err: any) {
      setError('エクスポートに失敗しました');
    }
  };

  const handleExecuteQuery = async () => {
    // SQL query execution would go here
    setError('SQL実行機能は開発中です');
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <StorageIcon sx={{ fontSize: 32, color: 'primary.main' }} />
            <Typography variant="h4" component="h1">
              データベース管理
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              startIcon={<RefreshIcon />}
              onClick={() => {
                fetchBrands();
                fetchStats();
              }}
            >
              更新
            </Button>
            <Button
              startIcon={<DownloadIcon />}
              onClick={handleExportDatabase}
              variant="outlined"
            >
              エクスポート
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        {/* Statistics Cards */}
        {stats && (
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    総ブランド数
                  </Typography>
                  <Typography variant="h4">
                    {stats.total_brands}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    総データ数
                  </Typography>
                  <Typography variant="h4">
                    {stats.total_values}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    最終更新
                  </Typography>
                  <Typography variant="h6">
                    {new Date(stats.last_updated).toLocaleString('ja-JP')}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="ブランド一覧" />
            <Tab label="ブランド値" />
            <Tab label="SQLクエリ" />
            <Tab label="インポート/エクスポート" />
          </Tabs>
        </Box>

        {/* Brands Tab */}
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
            <TextField
              size="small"
              placeholder="ブランドを検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
            <Button
              startIcon={<AddIcon />}
              variant="contained"
              onClick={() => setNewBrandDialog(true)}
            >
              新規ブランド
            </Button>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>ブランド名</TableCell>
                  <TableCell>カテゴリ</TableCell>
                  <TableCell>作成日時</TableCell>
                  <TableCell>操作</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : (
                  brands
                    .filter(brand => 
                      brand.brand_name.toLowerCase().includes(searchQuery.toLowerCase())
                    )
                    .map((brand) => (
                      <TableRow key={brand.id} hover>
                        <TableCell>{brand.id}</TableCell>
                        <TableCell>
                          <Chip 
                            label={brand.brand_name} 
                            onClick={() => {
                              setTabValue(1);
                              handleBrandSelect(brand.brand_name);
                            }}
                            color="primary"
                            variant="outlined"
                            sx={{ cursor: 'pointer' }}
                          />
                        </TableCell>
                        <TableCell>{brand.brand_category}</TableCell>
                        <TableCell>
                          {new Date(brand.created_at).toLocaleString('ja-JP')}
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteBrand(brand.brand_name)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* Brand Values Tab */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 2 }}>
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>ブランドを選択</InputLabel>
              <Select
                value={selectedBrand}
                label="ブランドを選択"
                onChange={(e) => handleBrandSelect(e.target.value)}
              >
                {brands.map((brand) => (
                  <MenuItem key={brand.id} value={brand.brand_name}>
                    {brand.brand_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {selectedBrand && (
            <>
              <Typography variant="h6" sx={{ mb: 2 }}>
                {selectedBrand} の属性値
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>行番号</TableCell>
                      <TableCell>属性値</TableCell>
                      <TableCell>作成日時</TableCell>
                      <TableCell>操作</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {brandValues.map((value) => (
                      <TableRow key={value.id}>
                        <TableCell>{value.row_index}</TableCell>
                        <TableCell>{value.attribute_value}</TableCell>
                        <TableCell>
                          {new Date(value.created_at).toLocaleString('ja-JP')}
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => {
                              setEditingItem(value);
                              setEditDialog(true);
                            }}
                          >
                            <EditIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </>
          )}
        </TabPanel>

        {/* SQL Query Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            SQLクエリ実行
          </Typography>
          <TextField
            multiline
            rows={10}
            fullWidth
            placeholder="SELECT * FROM brand_attributes;"
            variant="outlined"
            sx={{ mb: 2, fontFamily: 'monospace' }}
          />
          <Button
            variant="contained"
            onClick={handleExecuteQuery}
            startIcon={<SearchIcon />}
          >
            クエリ実行
          </Button>
        </TabPanel>

        {/* Import/Export Tab */}
        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  データベースエクスポート
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  現在のデータベースをSQLiteファイルとしてダウンロードします
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportDatabase}
                  fullWidth
                >
                  データベースをダウンロード
                </Button>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  データインポート
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Excel/CSVファイルからデータをインポートします
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<UploadIcon />}
                  fullWidth
                  disabled
                >
                  ファイルを選択（開発中）
                </Button>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>

      {/* Edit Dialog */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>属性値を編集</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="属性値"
            value={editingItem?.attribute_value || ''}
            onChange={(e) => setEditingItem({ ...editingItem, attribute_value: e.target.value })}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>キャンセル</Button>
          <Button onClick={handleEditValue} variant="contained">保存</Button>
        </DialogActions>
      </Dialog>

      {/* New Brand Dialog */}
      <Dialog open={newBrandDialog} onClose={() => setNewBrandDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>新規ブランド追加</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="ブランド名"
            value={newBrandName}
            onChange={(e) => setNewBrandName(e.target.value)}
            sx={{ mt: 2, mb: 2 }}
          />
          <FormControl fullWidth>
            <InputLabel>カテゴリ</InputLabel>
            <Select
              value={newBrandCategory}
              label="カテゴリ"
              onChange={(e) => setNewBrandCategory(e.target.value)}
            >
              <MenuItem value="mobile_device">モバイルデバイス</MenuItem>
              <MenuItem value="accessory">アクセサリー</MenuItem>
              <MenuItem value="other">その他</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewBrandDialog(false)}>キャンセル</Button>
          <Button onClick={handleAddBrand} variant="contained">追加</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}