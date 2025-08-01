import React from 'react';
import { Box, Typography, styled } from '@mui/material';
import { motion } from 'framer-motion';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import StarIcon from '@mui/icons-material/Star';
import DiamondIcon from '@mui/icons-material/Diamond';

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon?: React.ReactNode;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  unlockedAt?: Date;
  progress?: {
    current: number;
    total: number;
  };
}

export interface AchievementBadgeProps {
  achievement: Achievement;
  size?: 'small' | 'medium' | 'large';
  showProgress?: boolean;
  showDescription?: boolean;
  animated?: boolean;
  onClick?: () => void;
}

const rarityColors = {
  common: '#9E9E9E',
  rare: '#2196F3',
  epic: '#9C27B0',
  legendary: '#FF9800',
};

const rarityIcons = {
  common: <StarIcon />,
  rare: <EmojiEventsIcon />,
  epic: <DiamondIcon />,
  legendary: <DiamondIcon />,
};

const StyledBadgeContainer = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'size' && prop !== 'rarity' && prop !== 'unlocked',
})(
  ({
    theme,
    size = 'medium',
    rarity = 'common',
    unlocked = false,
  }: {
    theme: any;
    size?: 'small' | 'medium' | 'large';
    rarity?: 'common' | 'rare' | 'epic' | 'legendary';
    unlocked?: boolean;
  }) => {
    const sizeMap = {
      small: {
        width: 80,
        height: 80,
        iconSize: 24,
        titleSize: '0.75rem',
        descSize: '0.625rem',
      },
      medium: {
        width: 120,
        height: 120,
        iconSize: 32,
        titleSize: '0.875rem',
        descSize: '0.75rem',
      },
      large: {
        width: 160,
        height: 160,
        iconSize: 48,
        titleSize: '1rem',
        descSize: '0.875rem',
      },
    };

    const config = sizeMap[size];
    const rarityColor = rarityColors[rarity];

    return {
      width: config.width,
      height: config.height,
      borderRadius: '50%',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      background: unlocked
        ? `linear-gradient(135deg, ${rarityColor}20, ${rarityColor}40)`
        : theme.palette.grey[100],
      border: `3px solid ${unlocked ? rarityColor : theme.palette.grey[300]}`,
      opacity: unlocked ? 1 : 0.6,
      '&:hover': {
        transform: 'scale(1.05)',
        boxShadow: unlocked
          ? `0 8px 25px ${rarityColor}40`
          : '0 4px 12px rgba(0, 0, 0, 0.1)',
      },
      '& .achievement-icon': {
        fontSize: config.iconSize,
        color: unlocked ? rarityColor : theme.palette.grey[400],
        marginBottom: theme.spacing(0.5),
      },
      '& .achievement-title': {
        fontSize: config.titleSize,
        fontWeight: 600,
        textAlign: 'center',
        color: unlocked ? theme.palette.text.primary : theme.palette.text.disabled,
        lineHeight: 1.2,
      },
      '& .achievement-description': {
        fontSize: config.descSize,
        textAlign: 'center',
        color: theme.palette.text.secondary,
        marginTop: theme.spacing(0.5),
        lineHeight: 1.2,
      },
    };
  }
);

const ProgressRing = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'progress' && prop !== 'size' && prop !== 'rarity',
})(
  ({
    theme,
    progress = 0,
    size = 'medium',
    rarity = 'common',
  }: {
    theme: any;
    progress?: number;
    size?: 'small' | 'medium' | 'large';
    rarity?: 'common' | 'rare' | 'epic' | 'legendary';
  }) => {
    const sizeMap = {
      small: 76,
      medium: 116,
      large: 156,
    };

    const ringSize = sizeMap[size];
    const strokeWidth = 4;
    const radius = (ringSize - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const strokeDasharray = circumference;
    const strokeDashoffset = circumference - (progress / 100) * circumference;
    const rarityColor = rarityColors[rarity];

    return {
      position: 'absolute',
      top: -2,
      left: -2,
      width: ringSize + 4,
      height: ringSize + 4,
      '& svg': {
        width: '100%',
        height: '100%',
        transform: 'rotate(-90deg)',
      },
      '& .progress-ring': {
        fill: 'none',
        stroke: rarityColor,
        strokeWidth,
        strokeLinecap: 'round',
        strokeDasharray,
        strokeDashoffset,
        transition: 'stroke-dashoffset 0.8s ease',
        filter: `drop-shadow(0 0 4px ${rarityColor}60)`,
      },
    };
  }
);

const UnlockAnimation = styled(motion.div)({
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  pointerEvents: 'none',
});

const MotionBadge = motion(StyledBadgeContainer);

export const AchievementBadge: React.FC<AchievementBadgeProps> = ({
  achievement,
  size = 'medium',
  showProgress = true,
  showDescription = false,
  animated = true,
  onClick,
}) => {
  const isUnlocked = !!achievement.unlockedAt;
  const progress = achievement.progress
    ? (achievement.progress.current / achievement.progress.total) * 100
    : 100;

  const badgeContent = (
    <>
      {showProgress && achievement.progress && !isUnlocked && (
        <ProgressRing progress={progress} size={size} rarity={achievement.rarity} />
      )}
      
      <Box className="achievement-icon">
        {achievement.icon || rarityIcons[achievement.rarity]}
      </Box>
      
      <Typography className="achievement-title">
        {achievement.title}
      </Typography>
      
      {showDescription && (
        <Typography className="achievement-description">
          {achievement.description}
        </Typography>
      )}
      
      {showProgress && achievement.progress && !isUnlocked && (
        <Typography variant="caption" color="textSecondary" mt={0.5}>
          {achievement.progress.current}/{achievement.progress.total}
        </Typography>
      )}
      
      {isUnlocked && animated && (
        <UnlockAnimation
          initial={{ scale: 0, rotate: 0 }}
          animate={{ scale: [0, 1.2, 1], rotate: [0, 180, 360] }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <StarIcon sx={{ fontSize: 32, color: rarityColors[achievement.rarity] }} />
        </UnlockAnimation>
      )}
    </>
  );

  if (animated) {
    return (
      <MotionBadge
        size={size}
        rarity={achievement.rarity}
        unlocked={isUnlocked}
        onClick={onClick}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        {badgeContent}
      </MotionBadge>
    );
  }

  return (
    <StyledBadgeContainer
      size={size}
      rarity={achievement.rarity}
      unlocked={isUnlocked}
      onClick={onClick}
    >
      {badgeContent}
    </StyledBadgeContainer>
  );
};