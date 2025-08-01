import React from 'react';
import { Chip as MuiChip, ChipProps as MuiChipProps, styled } from '@mui/material';

export interface ChipProps extends MuiChipProps {
  variant?: 'filled' | 'outlined' | 'soft';
  size?: 'small' | 'medium' | 'large';
}

const StyledChip = styled(MuiChip, {
  shouldForwardProp: (prop) => prop !== 'variant' && prop !== 'size',
})(
  ({
    theme,
    variant = 'filled',
    size = 'medium',
    color = 'default',
  }: {
    theme: any;
    variant?: 'filled' | 'outlined' | 'soft';
    size?: 'small' | 'medium' | 'large';
    color?: string;
  }) => {
    const getColorValue = () => {
      if (color === 'default') return theme.palette.grey[500];
      return theme.palette[color]?.main || theme.palette.grey[500];
    };

    const getLightColorValue = () => {
      if (color === 'default') return theme.palette.grey[200];
      return theme.palette[color]?.light || theme.palette.grey[200];
    };

    const getContrastColorValue = () => {
      if (color === 'default') return theme.palette.getContrastText(theme.palette.grey[500]);
      return theme.palette[color]?.contrastText || theme.palette.common.white;
    };

    const sizeStyles = {
      small: {
        height: 24,
        fontSize: '0.75rem',
        '& .MuiChip-label': {
          padding: '0 8px',
        },
      },
      medium: {
        height: 32,
        fontSize: '0.875rem',
        '& .MuiChip-label': {
          padding: '0 12px',
        },
      },
      large: {
        height: 40,
        fontSize: '1rem',
        '& .MuiChip-label': {
          padding: '0 16px',
        },
      },
    };

    return {
      borderRadius: '16px',
      fontWeight: 500,
      transition: 'all 0.2s ease',
      ...sizeStyles[size],
      ...(variant === 'soft' && {
        backgroundColor: `${getColorValue()}20`,
        color: getColorValue(),
        border: 'none',
        '&:hover': {
          backgroundColor: `${getColorValue()}30`,
        },
        '&:focus': {
          backgroundColor: `${getColorValue()}30`,
        },
      }),
      ...(variant === 'outlined' && {
        backgroundColor: 'transparent',
        color: getColorValue(),
        border: `1px solid ${getColorValue()}`,
        '&:hover': {
          backgroundColor: `${getColorValue()}10`,
        },
        '&:focus': {
          backgroundColor: `${getColorValue()}10`,
        },
      }),
      ...(variant === 'filled' && {
        backgroundColor: getColorValue(),
        color: getContrastColorValue(),
        '&:hover': {
          backgroundColor: getColorValue(),
          opacity: 0.9,
        },
        '&:focus': {
          backgroundColor: getColorValue(),
          opacity: 0.9,
        },
      }),
    };
  }
);

export const Chip: React.FC<ChipProps> = ({
  variant = 'filled',
  size = 'medium',
  ...props
}) => {
  return <StyledChip variant={variant} size={size} {...props} />;
};