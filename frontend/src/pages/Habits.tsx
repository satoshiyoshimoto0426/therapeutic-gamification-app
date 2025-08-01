import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const Habits: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          習慣管理
        </Typography>
        <Box sx={{ mt: 3 }}>
          <Typography variant="body1" color="text.secondary">
            習慣管理機能は実装中です。
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Habits;