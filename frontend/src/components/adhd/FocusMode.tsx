import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Switch,
  FormControlLabel,
  Chip,
  LinearProgress,
  Fade,
  Collapse,
  Alert,
  useTheme,
} from '@mui/material'
import {
  FocusMode as FocusIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Timer as TimerIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
} from '@mui/icons-material'

interface FocusModeProps {
  isActive: boolean
  onToggle: (active: boolean) => void
  currentTask?: {
    title: string
    progress: number
    timeRemaining?: number
  }
  distractionLevel?: 'low' | 'medium' | 'high'
}

const FocusMode: React.FC<FocusModeProps> = ({
  isActive,
  onToggle,
  currentTask,
  distractionLevel = 'low'
}) => {
  const theme = useTheme()
  const [hideDistractions, setHideDistractions] = useState(isActive)
  const [showProgress, setShowProgress] = useState(true)
  const [focusTime, setFocusTime] = useState(0)
  const [showWarning, setShowWarning] = useState(false)

  // 集中時間をカウント
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isActive) {
      interval = setInterval(() => {
        setFocusTime(prev => prev + 1)
      }, 1000)
    } else {
      setFocusTime(0)
    }
    return () => clearInterval(interval)
  }, [isActive])

  // 気を散らす要素の検出
  useEffect(() => {
    if (isActive && distractionLevel === 'high') {
      setShowWarning(true)
      const timer = setTimeout(() => setShowWarning(false), 5000)
      return () => clearTimeout(timer)
    }
  }, [isActive, distractionLevel])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getDistractionColor = () => {
    switch (distractionLevel) {
      case 'high': return '#ff6b6b'
      case 'medium': return '#FFC857'
      case 'low': return '#4ECDC4'
      default: return '#4ECDC4'
    }
  }

  const getDistractionText = () => {
    switch (distractionLevel) {
      case 'high': return '注意散漫'
      case 'medium': return '軽度の散漫'
      case 'low': return '集中中'
      default: return '集中中'
    }
  }

  return (
    <Paper
      elevation={isActive ? 3 : 1}
      sx={{
        p: 2,
        backgroundColor: isActive ? '#f8f9fa' : 'background.paper',
        border: isActive ? `2px solid ${theme.palette.primary.main}` : '1px solid #e0e0e0',
        borderRadius: 2,
        transition: 'all 0.3s ease',
      }}
    >
      {/* 集中モードヘッダー */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FocusIcon 
            sx={{ 
              color: isActive ? theme.palette.primary.main : 'text.secondary',
              fontSize: '1.5rem'
            }} 
          />
          <Typography 
            variant="h6" 
            sx={{ 
              fontFamily: 'BIZ UDGothic, sans-serif',
              fontWeight: 600,
              color: isActive ? theme.palette.primary.main : 'text.primary'
            }}
          >
            集中モード
          </Typography>
          {isActive && (
            <Chip
              icon={<TimerIcon />}
              label={formatTime(focusTime)}
              size="small"
              color="primary"
              variant="outlined"
            />
          )}
        </Box>
        
        <FormControlLabel
          control={
            <Switch
              checked={isActive}
              onChange={(e) => onToggle(e.target.checked)}
              color="primary"
            />
          }
          label=""
          sx={{ m: 0 }}
        />
      </Box>

      {/* 警告メッセージ */}
      <Collapse in={showWarning}>
        <Alert 
          severity="warning" 
          sx={{ mb: 2, fontFamily: 'BIZ UDGothic, sans-serif' }}
          onClose={() => setShowWarning(false)}
        >
          気を散らす要素が検出されました。集中を維持するために不要な要素を非表示にします。
        </Alert>
      </Collapse>

      {/* 集中モード設定 */}
      <Fade in={isActive}>
        <Box>
          {/* 現在のタスク表示 */}
          {currentTask && (
            <Box sx={{ mb: 2 }}>
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  fontFamily: 'BIZ UDGothic, sans-serif',
                  mb: 1,
                  color: 'text.secondary'
                }}
              >
                現在のタスク
              </Typography>
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 1.5,
                  backgroundColor: 'background.default',
                  border: `1px solid ${theme.palette.primary.main}20`
                }}
              >
                <Typography 
                  variant="body1" 
                  sx={{ 
                    fontFamily: 'BIZ UDGothic, sans-serif',
                    fontWeight: 500,
                    mb: 1
                  }}
                >
                  {currentTask.title}
                </Typography>
                {showProgress && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={currentTask.progress}
                      sx={{ 
                        flexGrow: 1,
                        height: 6,
                        borderRadius: 3,
                        backgroundColor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: theme.palette.primary.main,
                          borderRadius: 3,
                        }
                      }}
                    />
                    <Typography variant="caption" sx={{ minWidth: 40 }}>
                      {currentTask.progress}%
                    </Typography>
                  </Box>
                )}
                {currentTask.timeRemaining && (
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      color: 'text.secondary',
                      display: 'block',
                      mt: 0.5
                    }}
                  >
                    残り時間: {formatTime(currentTask.timeRemaining)}
                  </Typography>
                )}
              </Paper>
            </Box>
          )}

          {/* 集中状態インジケーター */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography 
              variant="body2" 
              sx={{ 
                fontFamily: 'BIZ UDGothic, sans-serif',
                color: 'text.secondary'
              }}
            >
              集中状態
            </Typography>
            <Chip
              label={getDistractionText()}
              size="small"
              sx={{
                backgroundColor: `${getDistractionColor()}20`,
                color: getDistractionColor(),
                fontFamily: 'BIZ UDGothic, sans-serif',
                fontWeight: 500,
              }}
            />
          </Box>

          {/* 設定オプション */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={hideDistractions}
                  onChange={(e) => setHideDistractions(e.target.checked)}
                  size="small"
                />
              }
              label={
                <Typography 
                  variant="body2" 
                  sx={{ fontFamily: 'BIZ UDGothic, sans-serif' }}
                >
                  気を散らす要素を非表示
                </Typography>
              }
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={showProgress}
                  onChange={(e) => setShowProgress(e.target.checked)}
                  size="small"
                />
              }
              label={
                <Typography 
                  variant="body2" 
                  sx={{ fontFamily: 'BIZ UDGothic, sans-serif' }}
                >
                  プログレス表示
                </Typography>
              }
            />
          </Box>

          {/* 集中のヒント */}
          <Box 
            sx={{ 
              mt: 2,
              p: 1.5,
              backgroundColor: `${theme.palette.info.main}10`,
              borderRadius: 1,
              border: `1px solid ${theme.palette.info.main}30`
            }}
          >
            <Typography 
              variant="caption" 
              sx={{ 
                fontFamily: 'BIZ UDGothic, sans-serif',
                color: 'text.secondary',
                lineHeight: 1.6
              }}
            >
              💡 集中のコツ: 一度に一つのことに集中し、25分間隔で休憩を取りましょう。
            </Typography>
          </Box>
        </Box>
      </Fade>
    </Paper>
  )
}

export default FocusMode