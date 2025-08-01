import React from 'react';
import { Box, Typography, styled } from '@mui/material';
import { motion } from 'framer-motion';

export interface CrystalAttribute {
  name: string;
  value: number;
  maxValue: number;
  color: string;
  icon?: React.ReactNode;
}

export interface CrystalGaugeProps {
  attributes: CrystalAttribute[];
  size?: 'small' | 'medium' | 'large';
  showLabels?: boolean;
  showValues?: boolean;
  animated?: boolean;
  layout?: 'grid' | 'list' | 'circular';
}

const StyledGaugeContainer = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'layout',
})(
  ({
    theme,
    layout = 'grid',
  }: {
    theme: any;
    layout?: 'grid' | 'list' | 'circular';
  }) => ({
    display: layout === 'circular' ? 'flex' : 'grid',
    ...(layout === 'grid' && {
      gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
      gap: theme.spacing(2),
    }),
    ...(layout === 'list' && {
      gridTemplateColumns: '1fr',
      gap: theme.spacing(1),
    }),
    ...(layout === 'circular' && {
      justifyContent: 'center',
      alignItems: 'center',
      position: 'relative',
      width: 200,
      height: 200,
      margin: '0 auto',
    }),
  })
);

const AttributeItem = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'size' && prop !== 'layout',
})(
  ({
    theme,
    size = 'medium',
    layout = 'grid',
  }: {
    theme: any;
    size?: 'small' | 'medium' | 'large';
    layout?: 'grid' | 'list' | 'circular';
  }) => {
    const sizeMap = {
      small: {
        padding: theme.spacing(1),
        minHeight: 60,
      },
      medium: {
        padding: theme.spacing(1.5),
        minHeight: 80,
      },
      large: {
        padding: theme.spacing(2),
        minHeight: 100,
      },
    };

    return {
      ...sizeMap[size],
      backgroundColor: theme.palette.background.paper,
      borderRadius: '12px',
      border: `1px solid ${theme.palette.divider}`,
      display: 'flex',
      flexDirection: layout === 'list' ? 'row' : 'column',
      alignItems: layout === 'list' ? 'center' : 'flex-start',
      justifyContent: 'space-between',
      transition: 'all 0.2s ease',
      '&:hover': {
        transform: 'translateY(-2px)',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
      },
    };
  }
);

const GaugeBar = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'color' && prop !== 'progress' && prop !== 'layout',
})(
  ({
    theme,
    color,
    progress,
    layout = 'grid',
  }: {
    theme: any;
    color: string;
    progress: number;
    layout?: 'grid' | 'list' | 'circular';
  }) => ({
    width: layout === 'list' ? 100 : '100%',
    height: 8,
    backgroundColor: theme.palette.grey[200],
    borderRadius: 4,
    overflow: 'hidden',
    position: 'relative',
    '&::after': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      height: '100%',
      width: `${progress}%`,
      backgroundColor: color,
      borderRadius: 4,
      transition: 'width 0.8s ease',
      boxShadow: `0 0 8px ${color}40`,
    },
  })
);

const CircularGauge = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'color' && prop !== 'progress' && prop !== 'size',
})(
  ({
    theme,
    color,
    progress,
    size = 'medium',
  }: {
    theme: any;
    color: string;
    progress: number;
    size?: 'small' | 'medium' | 'large';
  }) => {
    const sizeMap = {
      small: 40,
      medium: 60,
      large: 80,
    };

    const circleSize = sizeMap[size];
    const strokeWidth = circleSize / 10;
    const radius = (circleSize - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const strokeDasharray = circumference;
    const strokeDashoffset = circumference - (progress / 100) * circumference;

    return {
      width: circleSize,
      height: circleSize,
      position: 'relative',
      '& svg': {
        width: '100%',
        height: '100%',
        transform: 'rotate(-90deg)',
      },
      '& .background-circle': {
        fill: 'none',
        stroke: theme.palette.grey[200],
        strokeWidth,
      },
      '& .progress-circle': {
        fill: 'none',
        stroke: color,
        strokeWidth,
        strokeLinecap: 'round',
        strokeDasharray,
        strokeDashoffset,
        transition: 'stroke-dashoffset 0.8s ease',
        filter: `drop-shadow(0 0 4px ${color}40)`,
      },
    };
  }
);

const MotionAttributeItem = motion(AttributeItem);

export const CrystalGauge: React.FC<CrystalGaugeProps> = ({
  attributes,
  size = 'medium',
  showLabels = true,
  showValues = true,
  animated = true,
  layout = 'grid',
}) => {
  const renderAttribute = (attribute: CrystalAttribute, index: number) => {
    const progress = (attribute.value / attribute.maxValue) * 100;

    if (layout === 'circular') {
      return (
        <Box
          key={attribute.name}
          position="absolute"
          style={{
            transform: `rotate(${(360 / attributes.length) * index}deg) translateY(-80px)`,
          }}
        >
          <Box
            style={{
              transform: `rotate(-${(360 / attributes.length) * index}deg)`,
            }}
            display="flex"
            flexDirection="column"
            alignItems="center"
            gap={1}
          >
            <CircularGauge color={attribute.color} progress={progress} size={size} />
            {showLabels && (
              <Typography variant="caption" textAlign="center">
                {attribute.name}
              </Typography>
            )}
            {showValues && (
              <Typography variant="caption" color="textSecondary">
                {attribute.value}/{attribute.maxValue}
              </Typography>
            )}
          </Box>
        </Box>
      );
    }

    const attributeItem = (
      <AttributeItem size={size} layout={layout}>
        <Box display="flex" alignItems="center" gap={1} mb={layout === 'list' ? 0 : 1}>
          {attribute.icon}
          {showLabels && (
            <Typography variant="body2" fontWeight="medium">
              {attribute.name}
            </Typography>
          )}
          {showValues && layout === 'list' && (
            <Typography variant="body2" color="textSecondary" ml="auto">
              {attribute.value}/{attribute.maxValue}
            </Typography>
          )}
        </Box>
        
        <GaugeBar color={attribute.color} progress={progress} layout={layout} />
        
        {showValues && layout !== 'list' && (
          <Typography variant="caption" color="textSecondary" mt={1}>
            {attribute.value}/{attribute.maxValue}
          </Typography>
        )}
      </AttributeItem>
    );

    if (animated) {
      return (
        <MotionAttributeItem
          key={attribute.name}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: index * 0.1 }}
          size={size}
          layout={layout}
        >
          {attributeItem.props.children}
        </MotionAttributeItem>
      );
    }

    return <React.Fragment key={attribute.name}>{attributeItem}</React.Fragment>;
  };

  return (
    <StyledGaugeContainer layout={layout}>
      {attributes.map(renderAttribute)}
    </StyledGaugeContainer>
  );
};