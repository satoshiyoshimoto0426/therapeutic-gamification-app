import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const Story: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          ストーリー
        </Typography>
        <Box sx={{ mt: 3 }}>
          <Typography variant="body1" color="text.secondary">
            ストーリー機能は実装中です。
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Story;