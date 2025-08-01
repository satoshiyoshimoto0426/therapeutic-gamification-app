import React, { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  BottomNavigation,
  BottomNavigationAction,
  Fab,
  Snackbar,
  Alert,
  LinearProgress,
  useTheme,
  useMediaQuery,
  Paper,
  Chip,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Assignment as TasksIcon,
  Mood as MoodIcon,
  Menu as MenuIcon,
  FocusMode as FocusIcon,
  Save as SaveIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material'
import { useAuth } from '../../contexts/AuthContext'

// ADHD配慮：最大3項目のシンプルナビゲーション
const primaryNavItems = [
  { text: 'ホーム', icon: <DashboardIcon />, path: '/dashboard', color: '#2E3A59' },
  { text: 'タスク', icon: <TasksIcon />, path: '/tasks', color: '#FFC857' },
  { text: '気分', icon: <MoodIcon />, path: '/mood', color: '#4ECDC4' },
]

interface ADHDFriendlyLayoutProps {
  children?: React.ReactNode
}

const ADHDFriendlyLayout: React.FC<ADHDFriendlyLayoutProps> = ({ children }) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuth()
  
  // 集中モード状態
  const [focusMode, setFocusMode] = useState(false)
  
  // 自動保存状態
  const [autoSaveStatus, setAutoSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  
  // プログレス状態
  const [dailyProgress, setDailyProgress] = useState(0)
  const [currentStreak, setCurrentStreak] = useState(0)
  
  // 通知状態
  const [notification, setNotification] = useState<{
    open: boolean
    message: string
    severity: 'success' | 'info' | 'warning' | 'error'
  }>({
    open: false,
    message: '',
    severity: 'info'
  })

  // 現在のナビゲーション値を取得
  const getCurrentNavValue = () => {
    const currentItem = primaryNavItems.find(item => item.path === location.pathname)
    return currentItem ? primaryNavItems.indexOf(currentItem) : 0
  }

  // ナビゲーション変更ハンドラー
  const handleNavigationChange = (_event: React.SyntheticEvent, newValue: number) => {
    const targetPath = primaryNavItems[newValue]?.path
    if (targetPath) {
      navigate(targetPath)
    }
  }

  // 集中モード切り替え
  const toggleFocusMode = () => {
    setFocusMode(!focusMode)
    setNotification({
      open: true,
      message: focusMode ? '集中モードを解除しました' : '集中モードを開始しました',
      severity: 'info'
    })
  }

  // 自動保存シミュレーション
  useEffect(() => {
    const autoSaveInterval = setInterval(() => {
      if (autoSaveStatus === 'idle') {
        setAutoSaveStatus('saving')
        
        // 実際の保存処理をシミュレート
        setTimeout(() => {
          setAutoSaveStatus('saved')
          setLastSaved(new Date())
          
          setTimeout(() => {
            setAutoSaveStatus('idle')
          }, 2000)
        }, 1000)
      }
    }, 30000) // 30秒ごとに自動保存

    return () => clearInterval(autoSaveInterval)
  }, [autoSaveStatus])

  // プログレス更新シミュレーション
  useEffect(() => {
    // 実際の実装では、タスク完了状況から計算
    setDailyProgress(65) // 65%完了
    setCurrentStreak(7) // 7日連続
  }, [])

  // 通知を閉じる
  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }))
  }

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      minHeight: '100vh',
      backgroundColor: focusMode ? '#f8f9fa' : 'background.default',
      transition: 'background-color 0.3s ease'
    }}>
      {/* ヘッダー - 集中モード時は最小限に */}
      <AppBar 
        position="fixed" 
        elevation={focusMode ? 0 : 1}
        sx={{ 
          backgroundColor: focusMode ? 'transparent' : 'primary.main',
          backdropFilter: focusMode ? 'blur(10px)' : 'none',
        }}
      >
        <Toolbar sx={{ minHeight: { xs: 56, sm: 64 } }}>
          {/* 集中モード時は簡素化 */}
          {!focusMode && (
            <>
              <Typography 
                variant="h6" 
                component="div" 
                sx={{ 
                  flexGrow: 1,
                  fontFamily: 'BIZ UDGothic, sans-serif',
                  fontWeight: 600,
                  fontSize: { xs: '1.1rem', sm: '1.25rem' }
                }}
              >
                {primaryNavItems.find(item => item.path === location.pathname)?.text || 'ホーム'}
              </Typography>
              
              {/* プログレス表示 */}
              <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                <Chip
                  icon={<CheckIcon />}
                  label={`${currentStreak}日連続`}
                  size="small"
                  color="secondary"
                  sx={{ mr: 1, display: { xs: 'none', sm: 'flex' } }}
                />
                <Typography variant="body2" sx={{ mr: 1, display: { xs: 'none', sm: 'block' } }}>
                  {dailyProgress}%
                </Typography>
              </Box>
            </>
          )}
          
          {/* 集中モードボタン */}
          <IconButton
            color="inherit"
            onClick={toggleFocusMode}
            sx={{ 
              backgroundColor: focusMode ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              '&:hover': {
                backgroundColor: focusMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)',
              }
            }}
          >
            <FocusIcon />
          </IconButton>
        </Toolbar>
        
        {/* プログレスバー - 集中モード時は非表示 */}
        {!focusMode && (
          <LinearProgress 
            variant="determinate" 
            value={dailyProgress} 
            sx={{ 
              height: 3,
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              '& .MuiLinearProgress-bar': {
                backgroundColor: '#FFC857'
              }
            }}
          />
        )}
      </AppBar>

      {/* メインコンテンツ */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          pt: { xs: 8, sm: 9 },
          pb: { xs: 8, sm: 2 },
          px: focusMode ? 1 : 2,
          maxWidth: focusMode ? '100%' : '1200px',
          mx: 'auto',
          width: '100%',
          // ADHD配慮：気を散らす要素を除去
          '& *': focusMode ? {
            animation: 'none !important',
            transition: 'none !important',
          } : {}
        }}
      >
        {children || <Outlet />}
      </Box>

      {/* モバイル用ボトムナビゲーション - 集中モード時も表示（必要最小限） */}
      {isMobile && (
        <Paper 
          sx={{ 
            position: 'fixed', 
            bottom: 0, 
            left: 0, 
            right: 0,
            zIndex: 1000,
            opacity: focusMode ? 0.8 : 1,
            transition: 'opacity 0.3s ease'
          }} 
          elevation={focusMode ? 1 : 3}
        >
          <BottomNavigation
            value={getCurrentNavValue()}
            onChange={handleNavigationChange}
            sx={{
              height: 64,
              '& .MuiBottomNavigationAction-root': {
                minWidth: 'auto',
                padding: '6px 12px 8px',
                '&.Mui-selected': {
                  color: 'primary.main',
                },
              },
              '& .MuiBottomNavigationAction-label': {
                fontFamily: 'BIZ UDGothic, sans-serif',
                fontSize: '0.75rem',
                lineHeight: 1.2,
                '&.Mui-selected': {
                  fontSize: '0.75rem',
                },
              },
            }}
          >
            {primaryNavItems.map((item, index) => (
              <BottomNavigationAction
                key={item.path}
                label={item.text}
                icon={item.icon}
                sx={{
                  '& .MuiSvgIcon-root': {
                    fontSize: '1.5rem',
                  },
                }}
              />
            ))}
          </BottomNavigation>
        </Paper>
      )}

      {/* 自動保存インジケーター */}
      {autoSaveStatus !== 'idle' && (
        <Fab
          size="small"
          sx={{
            position: 'fixed',
            bottom: isMobile ? 80 : 16,
            right: 16,
            backgroundColor: 
              autoSaveStatus === 'saving' ? '#FFC857' :
              autoSaveStatus === 'saved' ? '#4ECDC4' : '#ff6b6b',
            color: 'white',
            '&:hover': {
              backgroundColor: 
                autoSaveStatus === 'saving' ? '#e6b34f' :
                autoSaveStatus === 'saved' ? '#45b7b8' : '#e55656',
            },
          }}
        >
          <SaveIcon fontSize="small" />
        </Fab>
      )}

      {/* 通知スナックバー */}
      <Snackbar
        open={notification.open}
        autoHideDuration={4000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseNotification} 
          severity={notification.severity}
          sx={{ 
            fontFamily: 'BIZ UDGothic, sans-serif',
            '& .MuiAlert-message': {
              lineHeight: 1.6,
            }
          }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default ADHDFriendlyLayout