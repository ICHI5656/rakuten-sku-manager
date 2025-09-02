import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const TestDatabasePage: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Database Integration Test Page
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Typography>
            This is a test page to verify routing works correctly.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default TestDatabasePage;