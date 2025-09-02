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
  Card,
  CardContent,
  Grid,
  IconButton,
  Tooltip,
  SelectChangeEvent,
  Snackbar,
  InputAdornment
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  Storage as StorageIcon,
  TableChart as TableChartIcon,
  QueryStats as QueryStatsIcon,
  Close as CloseIcon
} from '@mui/icons-material';

interface DatabaseInfo {
  type: string;
  path: string;
  size?: number;
  exists: boolean;
}

interface DatabaseStats {
  [key: string]: any;
}

interface TableData {
  table: string;
  columns: string[];
  data: any[];
  total_count: number;
  returned_count: number;
}

interface SearchResult {
  table: string;
  data: any;
}

const MultiDatabaseManager: React.FC = () => {
  const [databases, setDatabases] = useState<DatabaseInfo[]>([]);
  const [selectedDb, setSelectedDb] = useState<string>('brand_attributes');
  const [currentTab, setCurrentTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Stats state
  const [stats, setStats] = useState<DatabaseStats | null>(null);

  // Table data state
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [tableData, setTableData] = useState<TableData | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  // Search state
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);

  // Query state
  const [sqlQuery, setSqlQuery] = useState('');
  const [queryResults, setQueryResults] = useState<any>(null);

  // Load available databases
  const loadDatabases = async () => {
    try {
      const response = await fetch('/api/multi-database/databases');
      if (!response.ok) throw new Error('Failed to load databases');
      const data = await response.json();
      setDatabases(data);
    } catch (error) {
      setError('データベース一覧の取得に失敗しました');
      console.error(error);
    }
  };

  // Load database stats
  const loadStats = async () => {
    if (!selectedDb) return;
    setLoading(true);
    try {
      const response = await fetch(`/api/multi-database/${selectedDb}/stats`);
      if (!response.ok) throw new Error('Failed to load stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      setError('統計情報の取得に失敗しました');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Load table list
  const loadTables = async () => {
    if (!selectedDb) return;
    setLoading(true);
    try {
      const response = await fetch(`/api/multi-database/${selectedDb}/data`);
      if (!response.ok) throw new Error('Failed to load tables');
      const data = await response.json();
      setTables(data.tables || []);
      if (data.tables && data.tables.length > 0) {
        setSelectedTable(data.tables[0]);
      }
    } catch (error) {
      setError('テーブル一覧の取得に失敗しました');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Load table data
  const loadTableData = async () => {
    if (!selectedDb || !selectedTable) return;
    setLoading(true);
    try {
      const response = await fetch(
        `/api/multi-database/${selectedDb}/data?table=${selectedTable}&limit=${rowsPerPage}&offset=${page * rowsPerPage}`
      );
      if (!response.ok) throw new Error('Failed to load table data');
      const data = await response.json();
      setTableData(data);
    } catch (error) {
      setError('テーブルデータの取得に失敗しました');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Search in database
  const handleSearch = async () => {
    if (!selectedDb || !searchTerm) return;
    setLoading(true);
    try {
      const response = await fetch(
        `/api/multi-database/${selectedDb}/search?search_term=${encodeURIComponent(searchTerm)}`
      );
      if (!response.ok) throw new Error('Search failed');
      const data = await response.json();
      setSearchResults(data.results || []);
      setSuccess(`${data.total_found}件の結果が見つかりました`);
    } catch (error) {
      setError('検索に失敗しました');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Execute SQL query
  const handleExecuteQuery = async () => {
    if (!selectedDb || !sqlQuery) return;
    setLoading(true);
    try {
      const response = await fetch(`/api/multi-database/${selectedDb}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: sqlQuery })
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Query execution failed');
      }
      const data = await response.json();
      setQueryResults(data);
      setSuccess(`クエリが実行されました: ${data.row_count}行`);
    } catch (error: any) {
      setError(`クエリエラー: ${error.message}`);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Export database
  const handleExport = async () => {
    if (!selectedDb) return;
    try {
      window.open(`/api/multi-database/${selectedDb}/export`, '_blank');
      setSuccess('データベースのエクスポートを開始しました');
    } catch (error) {
      setError('エクスポートに失敗しました');
      console.error(error);
    }
  };

  // Initialize
  useEffect(() => {
    loadDatabases();
  }, []);

  // Load data when database changes
  useEffect(() => {
    if (selectedDb) {
      loadStats();
      loadTables();
    }
  }, [selectedDb]);

  // Load table data when table changes
  useEffect(() => {
    if (selectedTable) {
      loadTableData();
    }
  }, [selectedTable, page, rowsPerPage]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleDbChange = (event: SelectChangeEvent) => {
    setSelectedDb(event.target.value);
    setPage(0);
  };

  const handleTableChange = (event: SelectChangeEvent) => {
    setSelectedTable(event.target.value);
    setPage(0);
  };

  const formatBytes = (bytes?: number) => {
    if (!bytes) return 'N/A';
    const kb = bytes / 1024;
    const mb = kb / 1024;
    if (mb > 1) return `${mb.toFixed(2)} MB`;
    if (kb > 1) return `${kb.toFixed(2)} KB`;
    return `${bytes} B`;
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 3 }}>
        <Typography variant="h4" gutterBottom>
          マルチデータベース管理
        </Typography>

        {/* Database Selector */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>データベース選択</InputLabel>
                <Select
                  value={selectedDb}
                  onChange={handleDbChange}
                  label="データベース選択"
                  startAdornment={<StorageIcon sx={{ mr: 1, color: 'action.active' }} />}
                >
                  {databases.map((db) => (
                    <MenuItem key={db.type} value={db.type} disabled={!db.exists}>
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                        <Typography sx={{ flexGrow: 1 }}>
                          {db.type === 'brand_attributes' ? 'ブランド属性' : '商品属性8'}
                        </Typography>
                        {db.exists ? (
                          <Chip label={formatBytes(db.size)} size="small" color="primary" />
                        ) : (
                          <Chip label="未作成" size="small" color="default" />
                        )}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={8}>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <Button
                  startIcon={<RefreshIcon />}
                  onClick={() => {
                    loadDatabases();
                    loadStats();
                    loadTables();
                  }}
                >
                  更新
                </Button>
                <Button
                  startIcon={<DownloadIcon />}
                  onClick={handleExport}
                  variant="outlined"
                >
                  エクスポート
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs value={currentTab} onChange={handleTabChange}>
            <Tab label="統計情報" icon={<QueryStatsIcon />} iconPosition="start" />
            <Tab label="テーブル表示" icon={<TableChartIcon />} iconPosition="start" />
            <Tab label="検索" icon={<SearchIcon />} iconPosition="start" />
            <Tab label="SQLクエリ" icon={<StorageIcon />} iconPosition="start" />
          </Tabs>
        </Paper>

        {/* Tab Contents */}
        {currentTab === 0 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              データベース統計
            </Typography>
            {loading ? (
              <CircularProgress />
            ) : stats ? (
              <Grid container spacing={3}>
                {Object.entries(stats).map(([key, value]) => (
                  <Grid item xs={12} md={6} lg={4} key={key}>
                    <Card>
                      <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                          {key.replace(/_/g, ' ').toUpperCase()}
                        </Typography>
                        {Array.isArray(value) ? (
                          <Box>
                            {value.map((item, idx) => (
                              <Box key={idx} sx={{ mb: 1 }}>
                                {Object.entries(item).map(([k, v]) => (
                                  <Typography key={k} variant="body2">
                                    {k}: {String(v)}
                                  </Typography>
                                ))}
                              </Box>
                            ))}
                          </Box>
                        ) : (
                          <Typography variant="h4">{String(value)}</Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Alert severity="info">統計情報がありません</Alert>
            )}
          </Paper>
        )}

        {currentTab === 1 && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ mb: 2 }}>
              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel>テーブル選択</InputLabel>
                <Select
                  value={selectedTable}
                  onChange={handleTableChange}
                  label="テーブル選択"
                >
                  {tables.map((table) => (
                    <MenuItem key={table} value={table}>
                      {table}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            {loading ? (
              <CircularProgress />
            ) : tableData ? (
              <>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        {tableData.columns.map((col) => (
                          <TableCell key={col}>{col}</TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {tableData.data.map((row, idx) => (
                        <TableRow key={idx}>
                          {tableData.columns.map((col) => (
                            <TableCell key={col}>
                              {row[col] !== null ? String(row[col]) : 'NULL'}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                <TablePagination
                  component="div"
                  count={tableData.total_count}
                  page={page}
                  onPageChange={(e, newPage) => setPage(newPage)}
                  rowsPerPage={rowsPerPage}
                  onRowsPerPageChange={(e) => {
                    setRowsPerPage(parseInt(e.target.value, 10));
                    setPage(0);
                  }}
                  labelRowsPerPage="行数:"
                />
              </>
            ) : (
              <Alert severity="info">テーブルを選択してください</Alert>
            )}
          </Paper>
        )}

        {currentTab === 2 && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                label="検索キーワード"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={handleSearch} disabled={!searchTerm}>
                        <SearchIcon />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            </Box>

            {loading ? (
              <CircularProgress />
            ) : searchResults.length > 0 ? (
              <Box>
                {searchResults.map((result, idx) => (
                  <Card key={idx} sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="subtitle1" color="primary" gutterBottom>
                        テーブル: {result.table}
                      </Typography>
                      <Box sx={{ pl: 2 }}>
                        {Object.entries(result.data).map(([key, value]) => (
                          <Typography key={key} variant="body2">
                            <strong>{key}:</strong> {String(value)}
                          </Typography>
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            ) : searchTerm ? (
              <Alert severity="info">検索結果がありません</Alert>
            ) : (
              <Alert severity="info">検索キーワードを入力してください</Alert>
            )}
          </Paper>
        )}

        {currentTab === 3 && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                multiline
                rows={6}
                label="SQLクエリ (SELECTのみ)"
                value={sqlQuery}
                onChange={(e) => setSqlQuery(e.target.value)}
                placeholder="SELECT * FROM table_name LIMIT 10"
              />
              <Button
                variant="contained"
                onClick={handleExecuteQuery}
                disabled={!sqlQuery || loading}
                sx={{ mt: 2 }}
              >
                実行
              </Button>
            </Box>

            {loading ? (
              <CircularProgress />
            ) : queryResults ? (
              <>
                <Alert severity="success" sx={{ mb: 2 }}>
                  {queryResults.row_count}行が返されました
                </Alert>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        {queryResults.columns.map((col: string) => (
                          <TableCell key={col}>{col}</TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {queryResults.data.slice(0, 100).map((row: any, idx: number) => (
                        <TableRow key={idx}>
                          {queryResults.columns.map((col: string) => (
                            <TableCell key={col}>
                              {row[col] !== null ? String(row[col]) : 'NULL'}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                {queryResults.row_count > 100 && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    最初の100行のみ表示しています
                  </Alert>
                )}
              </>
            ) : (
              <Alert severity="info">SQLクエリを入力して実行してください</Alert>
            )}
          </Paper>
        )}

        {/* Error/Success Messages */}
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

export default MultiDatabaseManager;