import React, { useState } from 'react';
import { Box, Typography, IconButton, styled } from '@mui/material';
import { motion } from 'framer-motion';

export interface MoodOption {
  value: number;
  label: string;
  emoji: string;
  color: string;
  description?: string;
}

export interface MoodSelectorProps {
  value?: number;
  onChange: (value: number) => void;
  options?: MoodOption[];
  title?: string;
  subtitle?: string;
  size?: 'small' | 'medium' | 'large';
  animated?: boolean;
  showLabels?: boolean;
  showDescription?: boolean;
}

const defaultMoodOptions: MoodOption[] = [
  {
    value: 1,
    label: 'とても悪い',
    emoji: '😢',
    color: '#f44336',
    description: 'とても落ち込んでいる',
  },
  {
    value: 2,
    label: '悪い',
    emoji: '😞',
    color: '#ff9800',
    description: '少し気分が沈んでいる',
  },
  {
    value: 3,
    label: '普通',
    emoji: '😐',
    color: '#9e9e9e',
    description: '特に変わりなし',
  },
  {
    value: 4,
    label: '良い',
    emoji: '😊',
    color: '#4caf50',
    description: '気分が良い',
  },
  {
    value: 5,
    label: 'とても良い',
    emoji: '😄',
    color: '#2196f3',
    description: 'とても気分が良い',
  },
];

const StyledMoodContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: theme.spacing(2),
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderRadius: '16px',
  border: `1px solid ${theme.palette.divider}`,
}));

const MoodOptionsContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  flexWrap: 'wrap',
  justifyContent: 'center',
}));

const StyledMoodButton = styled(IconButton, {
  shouldForwardProp: (prop) => prop !== 'selected' && prop !== 'moodColor' && prop !== 'size',
})(
  ({
    theme,
    selected = false,
    moodColor = theme.palette.primary.main,
    size = 'medium',
  }: {
    theme: any;
    selected?: boolean;
    moodColor?: string;
    size?: 'small' | 'medium' | 'large';
  }) => {
    const sizeMap = {
      small: {
        width: 48,
        height: 48,
        fontSize: '1.5rem',
      },
      medium: {
        width: 64,
        height: 64,
        fontSize: '2rem',
      },
      large: {
        width: 80,
        height: 80,
        fontSize: '2.5rem',
      },
    };

    const buttonSize = sizeMap[size];

    return {
      ...buttonSize,
      borderRadius: '50%',
      border: `3px solid ${selected ? moodColor : 'transparent'}`,
      backgroundColor: selected ? `${moodColor}20` : theme.palette.background.default,
      transition: 'all 0.2s ease',
      '&:hover': {
        backgroundColor: `${moodColor}30`,
        transform: 'scale(1.1)',
        border: `3px solid ${moodColor}60`,
      },
      '&:active': {
        transform: 'scale(0.95)',
      },
    };
  }
);

const MoodDescription = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  minHeight: 60,
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  padding: theme.spacing(1),
}));

const MotionMoodButton = motion(StyledMoodButton);
const MotionContainer = motion(StyledMoodContainer);

export const MoodSelector: React.FC<MoodSelectorProps> = ({
  value,
  onChange,
  options = defaultMoodOptions,
  title = '今の気分はどうですか？',
  subtitle,
  size = 'medium',
  animated = true,
  showLabels = true,
  showDescription = true,
}) => {
  const [hoveredMood, setHoveredMood] = useState<MoodOption | null>(null);
  
  const selectedMood = options.find(option => option.value === value);
  const displayMood = hoveredMood || selectedMood;

  const handleMoodSelect = (moodValue: number) => {
    onChange(moodValue);
  };

  const containerContent = (
    <>
      <Box textAlign="center">
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="textSecondary">
            {subtitle}
          </Typography>
        )}
      </Box>

      <MoodOptionsContainer>
        {options.map((mood, index) => {
          const isSelected = value === mood.value;
          
          const button = (
            <StyledMoodButton
              key={mood.value}
              selected={isSelected}
              moodColor={mood.color}
              size={size}
              onClick={() => handleMoodSelect(mood.value)}
              onMouseEnter={() => setHoveredMood(mood)}
              onMouseLeave={() => setHoveredMood(null)}
            >
              <span style={{ fontSize: 'inherit' }}>{mood.emoji}</span>
            </StyledMoodButton>
          );

          if (animated) {
            return (
              <MotionMoodButton
                key={mood.value}
                selected={isSelected}
                moodColor={mood.color}
                size={size}
                onClick={() => handleMoodSelect(mood.value)}
                onMouseEnter={() => setHoveredMood(mood)}
                onMouseLeave={() => setHoveredMood(null)}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                <span style={{ fontSize: 'inherit' }}>{mood.emoji}</span>
              </MotionMoodButton>
            );
          }

          return button;
        })}
      </MoodOptionsContainer>

      {(showLabels || showDescription) && (
        <MoodDescription>
          {displayMood && (
            <>
              {showLabels && (
                <Typography
                  variant="h6"
                  sx={{ color: displayMood.color, fontWeight: 'bold' }}
                >
                  {displayMood.label}
                </Typography>
              )}
              {showDescription && displayMood.description && (
                <Typography variant="body2" color="textSecondary">
                  {displayMood.description}
                </Typography>
              )}
            </>
          )}
        </MoodDescription>
      )}
    </>
  );

  if (animated) {
    return (
      <MotionContainer
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {containerContent}
      </MotionContainer>
    );
  }

  return <StyledMoodContainer>{containerContent}</StyledMoodContainer>;
};