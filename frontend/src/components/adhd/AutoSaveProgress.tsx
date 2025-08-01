import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Fade,
  CircularProgress,
  Alert,
  Collapse,
} from '@mui/material'
import {
  Save as SaveIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material'

interface AutoSaveProgressProps {
  autoSaveEnabled?: boolean
  saveInterval?: number // 秒
  currentProgress?: number // 0-100
  totalTasks?: number
  completedTasks?: number
  onManualSave?: () => void
  onRetry?: () => void
}

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'

const AutoSaveProgress: React.FC<AutoSaveProgressProps> = ({
  autoSaveEnabled = true,
  saveInterval = 30,
  currentProgress = 0,
  totalTasks = 0,
  completedTasks = 0,
  onManualSave,
  onRetry
}) => {
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle')
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [nextSaveIn, setNextSaveIn] = useState(saveInterval)
  const [showDetails, setShowDetails] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  // 自動保存タイマー
  useEffect(() => {
    if (!autoSaveEnabled) return

    const interval = setInterval(() => {
      setNextSaveIn(prev => {
        if (prev <= 1) {
          performAutoSave()
          return saveInterval
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [autoSaveEnabled, saveInterval])

  // 自動保存実行
  const performAutoSave = async () => {
    if (saveStatus === 'saving') return

    setSaveStatus('saving')
    setSaveError(null)

    try {
      // 実際の保存処理をシミュレート
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // ランダムにエラーを発生させる（デモ用）
      if (Math.random() < 0.1) {
        throw new Error('ネットワークエラーが発生しました')
      }

      setSaveStatus('saved')
      setLastSaved(new Date())
      
      // 2秒後にアイドル状態に戻る
      setTimeout(() => {
        setSaveStatus('idle')
      }, 2000)
    } catch (error) {
      setSaveStatus('error')
      setSaveError(error instanceof Error ? error.message : '保存に失敗しました')
    }
  }

  // 手動保存
  const handleManualSave = () => {
    if (onManualSave) {
      onManualSave()
    } else {
      performAutoSave()
    }
  }

  // リトライ
  const handleRetry = () => {
    if (onRetry) {
      onRetry()
    } else {
      performAutoSave()
    }
  }

  // 保存状態のアイコンと色を取得
  const getSaveStatusIcon = () => {
    switch (saveStatus) {
      case 'saving':
        return <CircularProgress size={16} />
      case 'saved':
        return <CheckIcon sx={{ color: '#4ECDC4', fontSize: '1rem' }} />
      case 'error':
        return <ErrorIcon sx={{ color: '#ff6b6b', fontSize: '1rem' }} />
      default:
        return <SaveIcon sx={{ color: 'text.secondary', fontSize: '1rem' }} />
    }
  }

  const getSaveStatusColor = () => {
    switch (saveStatus) {
      case 'saving': return '#FFC857'
      case 'saved': return '#4ECDC4'
      case 'error': return '#ff6b6b'
      default: return '#e0e0e0'
    }
  }

  const getSaveStatusText = () => {
    switch (saveStatus) {
      case 'saving': return '保存中...'
      case 'saved': return '保存完了'
      case 'error': return '保存失敗'
      default: return '自動保存'
    }
  }

  const formatLastSaved = () => {
    if (!lastSaved) return '未保存'
    const now = new Date()
    const diff = Math.floor((now.getTime() - lastSaved.getTime()) / 1000)
    
    if (diff < 60) return `${diff}秒前`
    if (diff < 3600) return `${Math.floor(diff / 60)}分前`
    return lastSaved.toLocaleTimeString('ja-JP', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <Paper
      elevation={1}
      sx={{
        p: 2,
        backgroundColor: 'background.paper',
        border: `1px solid ${getSaveStatusColor()}30`,
        borderRadius: 2,
      }}
    >
      {/* ヘッダー */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TimelineIcon sx={{ color: 'text.secondary' }} />
          <Typography 
            variant="h6" 
            sx={{ 
              fontFamily: 'BIZ UDGothic, sans-serif',
              fontWeight: 600
            }}
          >
            進捗状況
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            icon={getSaveStatusIcon()}
            label={getSaveStatusText()}
            size="small"
            sx={{
              backgroundColor: `${getSaveStatusColor()}20`,
              color: getSaveStatusColor(),
              fontFamily: 'BIZ UDGothic, sans-serif',
            }}
          />
          
          <Tooltip title="詳細を表示">
            <IconButton
              size="small"
              onClick={() => setShowDetails(!showDetails)}
            >
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* メインプログレス */}
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography 
            variant="body2" 
            sx={{ 
              fontFamily: 'BIZ UDGothic, sans-serif',
              color: 'text.secondary'
            }}
          >
            今日の進捗
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              fontFamily: 'BIZ UDGothic, sans-serif',
              fontWeight: 600
            }}
          >
            {completedTasks}/{totalTasks} タスク ({currentProgress}%)
          </Typography>
        </Box>
        
        <LinearProgress
          variant="determinate"
          value={currentProgress}
          sx={{
            height: 8,
            borderRadius: 4,
            backgroundColor: '#e0e0e0',
            '& .MuiLinearProgress-bar': {
              backgroundColor: '#4ECDC4',
              borderRadius: 4,
            }
          }}
        />
      </Box>

      {/* エラー表示 */}
      <Collapse in={saveStatus === 'error'}>
        <Alert 
          severity="error" 
          sx={{ mb: 2, fontFamily: 'BIZ UDGothic, sans-serif' }}
          action={
            <IconButton
              color="inherit"
              size="small"
              onClick={handleRetry}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          }
        >
          {saveError}
        </Alert>
      </Collapse>

      {/* 詳細情報 */}
      <Collapse in={showDetails}>
        <Box sx={{ pt: 1, borderTop: '1px solid #e0e0e0' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography 
              variant="caption" 
              sx={{ 
                fontFamily: 'BIZ UDGothic, sans-serif',
                color: 'text.secondary'
              }}
            >
              最終保存
            </Typography>
            <Typography 
              variant="caption" 
              sx={{ 
                fontFamily: 'BIZ UDGothic, sans-serif',
                fontWeight: 500
              }}
            >
              {formatLastSaved()}
            </Typography>
          </Box>
          
          {autoSaveEnabled && saveStatus !== 'saving' && (
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography 
                variant="caption" 
                sx={{ 
                  fontFamily: 'BIZ UDGothic, sans-serif',
                  color: 'text.secondary'
                }}
              >
                次回自動保存
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  fontFamily: 'BIZ UDGothic, sans-serif',
                  fontWeight: 500
                }}
              >
                {nextSaveIn}秒後
              </Typography>
            </Box>
          )}
          
          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
            <Tooltip title="今すぐ保存">
              <IconButton
                size="small"
                onClick={handleManualSave}
                disabled={saveStatus === 'saving'}
                sx={{
                  backgroundColor: '#4ECDC420',
                  '&:hover': {
                    backgroundColor: '#4ECDC430',
                  }
                }}
              >
                <SaveIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            
            {saveStatus === 'error' && (
              <Tooltip title="再試行">
                <IconButton
                  size="small"
                  onClick={handleRetry}
                  sx={{
                    backgroundColor: '#FFC85720',
                    '&:hover': {
                      backgroundColor: '#FFC85730',
                    }
                  }}
                >
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Box>
      </Collapse>

      {/* ADHD配慮のヒント */}
      <Fade in={currentProgress > 0 && currentProgress < 100}>
        <Box 
          sx={{ 
            mt: 2,
            p: 1,
            backgroundColor: '#4ECDC410',
            borderRadius: 1,
            border: '1px solid #4ECDC430'
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
            💡 進捗は自動的に保存されます。安心して一つずつタスクに集中しましょう。
          </Typography>
        </Box>
      </Fade>
    </Paper>
  )
}

export default AutoSaveProgress