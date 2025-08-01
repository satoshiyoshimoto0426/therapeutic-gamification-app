import React from 'react';
import { Box, Container, Grid, Paper, Typography, useTheme } from '@mui/material';
import { styled } from '@mui/material/styles';

const DashboardContainer = styled(Container)(({ theme }) => ({
  paddingTop: theme.spacing(4),
  paddingBottom: theme.spacing(4),
}));

const DashboardPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
  borderRadius: '12px',
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
  height: '100%',
  position: 'relative',
  overflow: 'hidden',
}));

interface DashboardSectionProps {
  title: string;
  children: React.ReactNode;
  gridSize?: { xs: number; sm: number; md: number; lg?: number };
  height?: string | number;
  color?: string;
}

export const DashboardSection: React.FC<DashboardSectionProps> = ({
  title,
  children,
  gridSize = { xs: 12, sm: 6, md: 4, lg: 4 },
  height = 'auto',
  color,
}) => {
  const theme = useTheme();
  
  return (
    <Grid item {...gridSize}>
      <DashboardPaper 
        sx={{
          height,
          bgcolor: color || 'background.paper',
          borderTop: color ? `4px solid ${color}` : undefined,
        }}
      >
        <Typography 
          variant="h6" 
          component="h2" 
          gutterBottom 
          sx={{ 
            fontWeight: 600,
            color: color ? theme.palette.getContrastText(color) : 'text.primary',
            mb: 2
          }}
        >
          {title}
        </Typography>
        <Box sx={{ flexGrow: 1 }}>
          {children}
        </Box>
      </DashboardPaper>
    </Grid>
  );
};

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  return (
    <DashboardContainer maxWidth="xl">
      <Grid container spacing={3}>
        {children}
      </Grid>
    </DashboardContainer>
  );
};

export default DashboardLayout;