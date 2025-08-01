import React from 'react';
import { Box, Typography, LinearProgress, Grid, Chip, Avatar } from '@mui/material';
import { styled } from '@mui/material/styles';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import EmojiEmotionsIcon from '@mui/icons-material/EmojiEmotions';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';

const StatBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  marginBottom: theme.spacing(2),
}));

const StatIcon = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: 48,
  height: 48,
  borderRadius: '50%',
  marginRight: theme.spacing(2),
}));

interface DashboardSummaryProps {
  userName: string;
  level: number;
  xp: number;
  xpToNextLevel: number;
  tasksCompleted: number;
  currentStreak: number;
  moodAverage: number;
  companionName: string;
  companionLevel: number;
}

const DashboardSummary: React.FC<DashboardSummaryProps> = ({
  userName,
  level,
  xp,
  xpToNextLevel,
  tasksCompleted,
  currentStreak,
  moodAverage,
  companionName,
  companionLevel,
}) => {
  const xpProgress = (xp / xpToNextLevel) * 100;
  
  // Convert mood average (1-5) to emoji and color
  const getMoodEmoji = (mood: number) => {
    if (mood >= 4.5) return { emoji: '😄', color: '#4caf50' };
    if (mood >= 3.5) return { emoji: '🙂', color: '#8bc34a' };
    if (mood >= 2.5) return { emoji: '😐', color: '#ffeb3b' };
    if (mood >= 1.5) return { emoji: '😕', color: '#ff9800' };
    return { emoji: '😢', color: '#f44336' };
  };
  
  const moodInfo = getMoodEmoji(moodAverage);
  
  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Avatar 
          sx={{ 
            width: 64, 
            height: 64, 
            bgcolor: 'primary.main',
            fontSize: '1.5rem',
            mr: 2 
          }}
        >
          {userName.charAt(0).toUpperCase()}
        </Avatar>
        <Box>
          <Typography variant="h5" component="h1" sx={{ fontWeight: 'bold' }}>
            こんにちは、{userName}さん
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
            <Chip 
              label={`レベル ${level}`} 
              color="primary" 
              size="small" 
              sx={{ mr: 1 }} 
            />
            <Typography variant="body2" color="text.secondary">
              次のレベルまで: {xp}/{xpToNextLevel} XP
            </Typography>
          </Box>
        </Box>
      </Box>
      
      <LinearProgress 
        variant="determinate" 
        value={xpProgress} 
        sx={{ 
          height: 8, 
          borderRadius: 4,
          mb: 3,
          '& .MuiLinearProgress-bar': {
            borderRadius: 4,
          }
        }} 
      />
      
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <StatBox>
            <StatIcon sx={{ bgcolor: 'rgba(25, 118, 210, 0.1)' }}>
              <CheckCircleIcon color="primary" />
            </StatIcon>
            <Box>
              <Typography variant="body2" color="text.secondary">
                完了タスク
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {tasksCompleted}
              </Typography>
            </Box>
          </StatBox>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatBox>
            <StatIcon sx={{ bgcolor: 'rgba(245, 124, 0, 0.1)' }}>
              <LocalFireDepartmentIcon sx={{ color: '#f57c00' }} />
            </StatIcon>
            <Box>
              <Typography variant="body2" color="text.secondary">
                現在の連続達成
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {currentStreak}日
              </Typography>
            </Box>
          </StatBox>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatBox>
            <StatIcon sx={{ bgcolor: `rgba(${parseInt(moodInfo.color.slice(1, 3), 16)}, ${parseInt(moodInfo.color.slice(3, 5), 16)}, ${parseInt(moodInfo.color.slice(5, 7), 16)}, 0.1)` }}>
              <EmojiEmotionsIcon sx={{ color: moodInfo.color }} />
            </StatIcon>
            <Box>
              <Typography variant="body2" color="text.secondary">
                平均気分
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {moodInfo.emoji} {moodAverage.toFixed(1)}/5
              </Typography>
            </Box>
          </StatBox>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatBox>
            <StatIcon sx={{ bgcolor: 'rgba(156, 39, 176, 0.1)' }}>
              <TrendingUpIcon sx={{ color: '#9c27b0' }} />
            </StatIcon>
            <Box>
              <Typography variant="body2" color="text.secondary">
                {companionName}との絆
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                レベル {companionLevel}
              </Typography>
            </Box>
          </StatBox>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardSummary;