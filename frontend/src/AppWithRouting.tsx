import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Container,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  useMediaQuery,
  useTheme,
  Chip
} from '@mui/material';
import {
  Home as HomeIcon,
  Storage as StorageIcon,
  Dashboard as DashboardIcon,
  Menu as MenuIcon,
  Upload as UploadIcon,
  DataObject as DataObjectIcon,
  Inventory as InventoryIcon,
  IntegrationInstructions as IntegrationIcon
} from '@mui/icons-material';
import App from './App';
import DatabaseManager from './pages/DatabaseManager';
import ProductAttributes8DatabaseV2 from './pages/ProductAttributes8DatabaseV2';
import DatabaseIntegrationPageFixed from './pages/DatabaseIntegrationPageFixed';
import ProcessingPage from './pages/ProcessingPage';
import BatchProcessPage from './pages/BatchProcessPage';
import UploadPage from './pages/UploadPage';
import ProcessOptionsPage from './pages/ProcessOptionsPage';

function Navigation() {
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);
  
  const menuItems = [
    { 
      path: '/', 
      label: 'CSV処理', 
      icon: <UploadIcon />,
      description: 'CSVファイルの処理とSKU管理'
    },
    {
      path: '/processing',
      label: '処理センター（開発中）',
      icon: <DashboardIcon />,
      description: 'バッチ処理・オプション管理'
    },
    { 
      path: '/database', 
      label: 'ブランドDB', 
      icon: <StorageIcon />,
      description: 'デバイス・ブランド管理'
    },
    { 
      path: '/product-attributes', 
      label: '商品属性管理', 
      icon: <DataObjectIcon />,
      description: '商品属性（値）8 データベース'
    },
    { 
      path: '/db-integration', 
      label: '統合管理', 
      icon: <IntegrationIcon />,
      description: '統合データベース管理'
    }
  ];

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const drawer = (
    <Box sx={{ width: 250 }}>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <InventoryIcon color="primary" />
        <Typography variant="h6" color="primary">
          楽天SKU Manager
        </Typography>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              component={Link}
              to={item.path}
              selected={location.pathname === item.path}
              onClick={() => setDrawerOpen(false)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: theme.palette.action.selected,
                  borderLeft: `4px solid ${theme.palette.primary.main}`,
                  '& .MuiListItemIcon-root': {
                    color: theme.palette.primary.main,
                  },
                },
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText 
                primary={item.label} 
                secondary={item.description}
                secondaryTypographyProps={{
                  fontSize: '0.75rem',
                  sx: { opacity: 0.7 }
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
  
  return (
    <>
      <AppBar 
        position="sticky" 
        elevation={1}
        sx={{ 
          backgroundColor: 'background.paper',
          color: 'text.primary',
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Toolbar sx={{ minHeight: { xs: 56, sm: 64 } }}>
          {isMobile && (
            <IconButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexGrow: 1 }}>
            <InventoryIcon color="primary" sx={{ fontSize: 28 }} />
            <Typography 
              variant="h6" 
              component="div" 
              sx={{ 
                fontWeight: 600,
                background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              楽天SKU管理システム
            </Typography>
            <Chip 
              label="v2.0" 
              size="small" 
              color="primary" 
              variant="outlined"
              sx={{ ml: 1 }}
            />
          </Box>
          
          {!isMobile && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              {menuItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Button
                    key={item.path}
                    component={Link}
                    to={item.path}
                    startIcon={item.icon}
                    variant={isActive ? 'contained' : 'text'}
                    color={isActive ? 'primary' : 'inherit'}
                    sx={{
                      px: 2,
                      borderRadius: 2,
                      textTransform: 'none',
                      fontWeight: isActive ? 600 : 400,
                      '&:hover': {
                        backgroundColor: isActive 
                          ? theme.palette.primary.dark
                          : theme.palette.action.hover,
                      },
                    }}
                  >
                    {item.label}
                  </Button>
                );
              })}
            </Box>
          )}
        </Toolbar>
      </AppBar>
      
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
}

export default function AppWithRouting() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <Navigation />
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/processing" element={<ProcessingPage />} />
          <Route path="/batch" element={<BatchProcessPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/process-options" element={<ProcessOptionsPage />} />
          <Route path="/database" element={<DatabaseManager />} />
          <Route path="/product-attributes" element={<ProductAttributes8DatabaseV2 />} />
          <Route path="/db-integration" element={<DatabaseIntegrationPageFixed />} />
        </Routes>
      </Box>
    </Router>
  );
}