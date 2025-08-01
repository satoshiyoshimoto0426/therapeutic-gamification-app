import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  Button,
  ButtonGroup,
  Paper,
  Typography,
  useTheme,
  useMediaQuery,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Assignment as TasksIcon,
  Mood as MoodIcon,
} from '@mui/icons-material'

// ADHD配慮：最大3項目のシンプルナビゲーション
const navigationItems = [
  { 
    text: 'ホーム', 
    icon: <DashboardIcon />, 
    path: '/dashboard',
    color: '#2E3A59',
    description: 'メインダッシュボード'
  },
  { 
    text: 'タスク', 
    icon: <TasksIcon />, 
    path: '/tasks',
    color: '#FFC857',
    description: '今日のタスク管理'
  },
  { 
    text: '気分', 
    icon: <MoodIcon />, 
    path: '/mood',
    color: '#4ECDC4',
    description: '気分の記録と追跡'
  },
]

interface SimpleNavigationProps {
  variant?: 'horizontal' | 'vertical'
  showDescriptions?: boolean
  focusMode?: boolean
}

const SimpleNavigation: React.FC<SimpleNavigationProps> = ({
  variant = 'horizontal',
  showDescriptions = false,
  focusMode = false
}) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  const navigate = useNavigate()
  const location = useLocation()

  const handleNavigation = (path: string) => {
    navigate(path)
  }

  const isActive = (path: string) => location.pathname === path

  if (variant === 'vertical') {
    return (
      <Paper 
        elevation={focusMode ? 0 : 2}
        sx={{ 
          p: 2,
          backgroundColor: focusMode ? 'transparent' : 'background.paper',
          border: focusMode ? '1px solid #e0e0e0' : 'none',
        }}
      >
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {navigationItems.map((item) => (
            <Button
              key={item.path}
              variant={isActive(item.path) ? 'contained' : 'outlined'}
              startIcon={item.icon}
              onClick={() => handleNavigation(item.path)}
              fullWidth
              sx={{
                justifyContent: 'flex-start',
                minHeight: 48, // ADHD配慮：44px以上のタッチターゲット
                px: 2,
                py: 1.5,
                fontFamily: 'BIZ UDGothic, sans-serif',
                fontSize: '1rem',
                lineHeight: 1.6,
                backgroundColor: isActive(item.path) ? item.color : 'transparent',
                borderColor: item.color,
                color: isActive(item.path) ? 'white' : item.color,
                '&:hover': {
                  backgroundColor: isActive(item.path) ? item.color : `${item.color}20`,
                  borderColor: item.color,
                },
                '& .MuiButton-startIcon': {
                  marginRight: 1,
                  '& .MuiSvgIcon-root': {
                    fontSize: '1.25rem',
                  },
                },
              }}
            >
              <Box sx={{ textAlign: 'left', width: '100%' }}>
                <Typography variant="button" component="span" sx={{ display: 'block' }}>
                  {item.text}
                </Typography>
                {showDescriptions && !focusMode && (
                  <Typography 
                    variant="caption" 
                    component="span" 
                    sx={{ 
                      display: 'block',
                      opacity: 0.7,
                      fontSize: '0.75rem',
                      lineHeight: 1.2,
                      mt: 0.25
                    }}
                  >
                    {item.description}
                  </Typography>
                )}
              </Box>
            </Button>
          ))}
        </Box>
      </Paper>
    )
  }

  return (
    <Paper 
      elevation={focusMode ? 0 : 1}
      sx={{ 
        p: 1,
        backgroundColor: focusMode ? 'transparent' : 'background.paper',
        border: focusMode ? '1px solid #e0e0e0' : 'none',
      }}
    >
      <ButtonGroup
        variant="outlined"
        fullWidth={isMobile}
        orientation={isMobile ? 'vertical' : 'horizontal'}
        sx={{
          '& .MuiButtonGroup-grouped': {
            minHeight: 48, // ADHD配慮：44px以上のタッチターゲット
            border: 'none',
            '&:not(:last-of-type)': {
              borderRight: isMobile ? 'none' : '1px solid #e0e0e0',
              borderBottom: isMobile ? '1px solid #e0e0e0' : 'none',
            },
          },
        }}
      >
        {navigationItems.map((item) => (
          <Button
            key={item.path}
            startIcon={item.icon}
            onClick={() => handleNavigation(item.path)}
            sx={{
              flex: 1,
              px: 2,
              py: 1.5,
              fontFamily: 'BIZ UDGothic, sans-serif',
              fontSize: isMobile ? '0.9rem' : '1rem',
              lineHeight: 1.6,
              backgroundColor: isActive(item.path) ? `${item.color}20` : 'transparent',
              borderColor: isActive(item.path) ? item.color : '#e0e0e0',
              color: isActive(item.path) ? item.color : 'text.primary',
              '&:hover': {
                backgroundColor: `${item.color}30`,
                borderColor: item.color,
              },
              '& .MuiButton-startIcon': {
                marginRight: isMobile ? 0.5 : 1,
                '& .MuiSvgIcon-root': {
                  fontSize: isMobile ? '1.1rem' : '1.25rem',
                },
              },
            }}
          >
            <Box sx={{ textAlign: 'center' }}>
              <Typography 
                variant="button" 
                component="span" 
                sx={{ 
                  display: 'block',
                  fontSize: 'inherit',
                }}
              >
                {item.text}
              </Typography>
              {showDescriptions && !focusMode && !isMobile && (
                <Typography 
                  variant="caption" 
                  component="span" 
                  sx={{ 
                    display: 'block',
                    opacity: 0.7,
                    fontSize: '0.7rem',
                    lineHeight: 1.2,
                    mt: 0.25
                  }}
                >
                  {item.description}
                </Typography>
              )}
            </Box>
          </Button>
        ))}
      </ButtonGroup>
    </Paper>
  )
}

export default SimpleNavigation