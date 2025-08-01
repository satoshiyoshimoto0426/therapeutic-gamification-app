import React from 'react';
import { Box, Typography, LinearProgress, styled } from '@mui/material';
import { motion } from 'framer-motion';

export interface XPBarProps {
  currentXP: number;
  nextLevelXP: number;
  level: number;
  showLevel?: boolean;
  showNumbers?: boolean;
  animated?: boolean;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'small' | 'medium' | 'large';
}

const StyledXPContainer = styled(Box)(({ theme }) => ({
  width: '100%',
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(1),
}));

const StyledXPProgress = styled(LinearProgress, {
  shouldForwardProp: (prop) => prop !== 'size',
})(
  ({
    theme,
    size = 'medium',
  }: {
    theme: any;
    size?: 'small' | 'medium' | 'large';
  }) => {
    const sizeMap = {
      small: 6,
      medium: 10,
      large: 14,
    };

    const height = sizeMap[size];

    return {
      height,
      borderRadius: height / 2,
      backgroundColor: theme.palette.grey[200],
      '& .MuiLinearProgress-bar': {
        borderRadius: height / 2,
        background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
        boxShadow: `0 0 10px ${theme.palette.primary.main}40`,
      },
    };
  }
);

const LevelBadge = styled(Box)(({ theme }) => ({
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  minWidth: 32,
  height: 32,
  borderRadius: '50%',
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  fontWeight: 'bold',
  fontSize: '0.875rem',
  boxShadow: `0 2px 8px ${theme.palette.primary.main}40`,
}));

const MotionBox = motion(Box);

export const XPBar: React.FC<XPBarProps> = ({
  currentXP,
  nextLevelXP,
  level,
  showLevel = true,
  showNumbers = true,
  animated = true,
  color = 'primary',
  size = 'medium',
}) => {
  const progress = (currentXP / nextLevelXP) * 100;

  const progressBar = (
    <StyledXPProgress
      variant="determinate"
      value={progress}
      color={color}
      size={size}
    />
  );

  return (
    <StyledXPContainer>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        {showLevel && (
          <Box display="flex" alignItems="center" gap={1}>
            <LevelBadge>
              {level}
            </LevelBadge>
            <Typography variant="body2" fontWeight="medium">
              Level {level}
            </Typography>
          </Box>
        )}
        {showNumbers && (
          <Typography variant="body2" color="textSecondary">
            {currentXP} / {nextLevelXP} XP
          </Typography>
        )}
      </Box>
      
      {animated ? (
        <MotionBox
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={{ transformOrigin: 'left' }}
        >
          {progressBar}
        </MotionBox>
      ) : (
        progressBar
      )}
      
      {showNumbers && (
        <Box display="flex" justifyContent="space-between">
          <Typography variant="caption" color="textSecondary">
            {Math.round(progress)}% to next level
          </Typography>
          <Typography variant="caption" color="textSecondary">
            {nextLevelXP - currentXP} XP needed
          </Typography>
        </Box>
      )}
    </StyledXPContainer>
  );
};