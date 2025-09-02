import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Container
} from '@mui/material';
import {
  Home as HomeIcon,
  Storage as StorageIcon,
  Dashboard as DashboardIcon
} from '@mui/icons-material';
import App from './App';
import DatabaseManager from './pages/DatabaseManager';
import ProductAttributes8DatabaseV2 from './pages/ProductAttributes8DatabaseV2';
import DatabaseIntegrationPageFixed from './pages/DatabaseIntegrationPageFixed';

function Navigation() {
  const location = useLocation();
  
  return (
    <AppBar position="static" sx={{ mb: 3 }}>
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="home"
          component={Link}
          to="/"
          sx={{ mr: 2 }}
        >
          <HomeIcon />
        </IconButton>
        
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          楽天SKU管理システム
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            color="inherit" 
            component={Link} 
            to="/"
            startIcon={<DashboardIcon />}
            variant={location.pathname === '/' ? 'outlined' : 'text'}
          >
            SKU処理
          </Button>
          <Button 
            color="inherit" 
            component={Link} 
            to="/database"
            startIcon={<StorageIcon />}
            variant={location.pathname === '/database' ? 'outlined' : 'text'}
          >
            ブランドDB
          </Button>
          <Button 
            color="inherit" 
            component={Link} 
            to="/product-attributes"
            startIcon={<DashboardIcon />}
            variant={location.pathname === '/product-attributes' ? 'outlined' : 'text'}
          >
            商品属性8
          </Button>
          <Button 
            color="inherit" 
            component={Link} 
            to="/db-integration"
            startIcon={<StorageIcon />}
            variant={location.pathname === '/db-integration' ? 'outlined' : 'text'}
          >
            統合管理
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default function AppWithRouting() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <Navigation />
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/database" element={<DatabaseManager />} />
          <Route path="/product-attributes" element={<ProductAttributes8DatabaseV2 />} />
          <Route path="/db-integration" element={<DatabaseIntegrationPageFixed />} />
        </Routes>
      </Box>
    </Router>
  );
}