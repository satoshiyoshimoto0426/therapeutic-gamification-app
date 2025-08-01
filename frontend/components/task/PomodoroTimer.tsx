import React, { useState, useEffect, useCallback } from 'react';
import { Box, Typography, IconButton, LinearProgress, styled } from '@mui/material';
import { motion } from 'framer-motion';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import StopIcon from '@mui/icons-material/Stop';
import SkipNextIcon from '@mui/icons-material/SkipNext';

export interface PomodoroTimerProps {
  workDuration?: number; // minutes
  breakDuration?: number; // minutes
  longBreakDuration?: number; // minutes
  sessionsUntilLongBreak?: number;
  onSessionComplete?: (type: 'work' | 'break' | 'longBreak') => void;
  onTimerStop?: () => void;
  autoStart?: boolean;
  showProgress?: boolean;
  compact?: boolean;
}

type TimerState = 'idle' | 'running' | 'paused';
type SessionType = 'work' | 'break' | 'longBreak';

const StyledTimerContainer = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'compact' && prop !== 'sessionType',
})(
  ({
    theme,
    compact = false,
    sessionType = 'work',
  }: {
    theme: any;
    compact?: boolean;
    sessionType?: SessionType;
  }) => {
    const sessionColors = {
      work: theme.palette.primary.main,
      break: theme.palette.success.main,
      longBreak: theme.palette.warning.main,
    };

    return {
      backgroundColor: theme.palette.background.paper,
      borderRadius: '16px',
      padding: compact ? theme.spacing(2) : theme.spacing(3),
      border: `2px solid ${sessionColors[sessionType]}40`,
      textAlign: 'center',
      minWidth: compact ? 200 : 300,
      boxShadow: `0 4px 20px ${sessionColors[sessionType]}20`,
    };
  }
);

const TimerDisplay = styled(Typography, {
  shouldForwardProp: (prop) => prop !== 'sessionType',
})(
  ({
    theme,
    sessionType = 'work',
  }: {
    theme: any;
    sessionType?: SessionType;
  }) => {
    const sessionColors = {
      work: theme.palette.primary.main,
      break: theme.palette.success.main,
      longBreak: theme.palette.warning.main,
    };

    return {
      fontSize: '3rem',
      fontWeight: 'bold',
      fontFamily: 'monospace',
      color: sessionColors[sessionType],
      textShadow: `0 2px 4px ${sessionColors[sessionType]}40`,
    };
  }
);

const SessionIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'center',
  gap: theme.spacing(0.5),
  marginBottom: theme.spacing(2),
}));

const SessionDot = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'active' && prop !== 'completed',
})(
  ({
    theme,
    active = false,
    completed = false,
  }: {
    theme: any;
    active?: boolean;
    completed?: boolean;
  }) => ({
    width: 12,
    height: 12,
    borderRadius: '50%',
    backgroundColor: completed
      ? theme.palette.success.main
      : active
      ? theme.palette.primary.main
      : theme.palette.grey[300],
    transition: 'all 0.2s ease',
  })
);

const ControlButtons = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'center',
  gap: theme.spacing(1),
  marginTop: theme.spacing(2),
}));

const MotionContainer = motion(StyledTimerContainer);

export const PomodoroTimer: React.FC<PomodoroTimerProps> = ({
  workDuration = 25,
  breakDuration = 5,
  longBreakDuration = 15,
  sessionsUntilLongBreak = 4,
  onSessionComplete,
  onTimerStop,
  autoStart = false,
  showProgress = true,
  compact = false,
}) => {
  const [timeLeft, setTimeLeft] = useState(workDuration * 60);
  const [timerState, setTimerState] = useState<TimerState>('idle');
  const [sessionType, setSessionType] = useState<SessionType>('work');
  const [completedSessions, setCompletedSessions] = useState(0);
  const [currentCycle, setCurrentCycle] = useState(0);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getSessionDuration = (type: SessionType): number => {
    switch (type) {
      case 'work':
        return workDuration * 60;
      case 'break':
        return breakDuration * 60;
      case 'longBreak':
        return longBreakDuration * 60;
    }
  };

  const startNextSession = useCallback(() => {
    let nextType: SessionType;
    
    if (sessionType === 'work') {
      const newCompletedSessions = completedSessions + 1;
      setCompletedSessions(newCompletedSessions);
      
      if (newCompletedSessions % sessionsUntilLongBreak === 0) {
        nextType = 'longBreak';
        setCurrentCycle(currentCycle + 1);
      } else {
        nextType = 'break';
      }
    } else {
      nextType = 'work';
    }
    
    setSessionType(nextType);
    setTimeLeft(getSessionDuration(nextType));
    
    if (autoStart) {
      setTimerState('running');
    } else {
      setTimerState('idle');
    }
  }, [sessionType, completedSessions, sessionsUntilLongBreak, currentCycle, autoStart]);

  const handleSessionComplete = useCallback(() => {
    if (onSessionComplete) {
      onSessionComplete(sessionType);
    }
    startNextSession();
  }, [sessionType, onSessionComplete, startNextSession]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (timerState === 'running' && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            handleSessionComplete();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    
    return () => clearInterval(interval);
  }, [timerState, timeLeft, handleSessionComplete]);

  const handleStart = () => {
    setTimerState('running');
  };

  const handlePause = () => {
    setTimerState('paused');
  };

  const handleStop = () => {
    setTimerState('idle');
    setTimeLeft(getSessionDuration(sessionType));
    if (onTimerStop) {
      onTimerStop();
    }
  };

  const handleSkip = () => {
    handleSessionComplete();
  };

  const progress = ((getSessionDuration(sessionType) - timeLeft) / getSessionDuration(sessionType)) * 100;

  const sessionLabels = {
    work: '作業時間',
    break: '休憩時間',
    longBreak: '長い休憩',
  };

  return (
    <MotionContainer
      compact={compact}
      sessionType={sessionType}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Typography variant="h6" color="textSecondary" gutterBottom>
        {sessionLabels[sessionType]}
      </Typography>
      
      <SessionIndicator>
        {Array.from({ length: sessionsUntilLongBreak }).map((_, index) => (
          <SessionDot
            key={index}
            active={index === (completedSessions % sessionsUntilLongBreak)}
            completed={index < (completedSessions % sessionsUntilLongBreak)}
          />
        ))}
      </SessionIndicator>
      
      <TimerDisplay sessionType={sessionType}>
        {formatTime(timeLeft)}
      </TimerDisplay>
      
      {showProgress && (
        <Box mt={2} mb={2}>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                borderRadius: 4,
              },
            }}
          />
        </Box>
      )}
      
      <ControlButtons>
        {timerState === 'idle' || timerState === 'paused' ? (
          <IconButton
            onClick={handleStart}
            color="primary"
            size="large"
            sx={{
              backgroundColor: 'primary.main',
              color: 'primary.contrastText',
              '&:hover': {
                backgroundColor: 'primary.dark',
              },
            }}
          >
            <PlayArrowIcon />
          </IconButton>
        ) : (
          <IconButton
            onClick={handlePause}
            color="primary"
            size="large"
            sx={{
              backgroundColor: 'warning.main',
              color: 'warning.contrastText',
              '&:hover': {
                backgroundColor: 'warning.dark',
              },
            }}
          >
            <PauseIcon />
          </IconButton>
        )}
        
        <IconButton
          onClick={handleStop}
          color="error"
          size="large"
          disabled={timerState === 'idle'}
        >
          <StopIcon />
        </IconButton>
        
        <IconButton
          onClick={handleSkip}
          color="secondary"
          size="large"
          disabled={timerState === 'idle'}
        >
          <SkipNextIcon />
        </IconButton>
      </ControlButtons>
      
      <Typography variant="body2" color="textSecondary" mt={2}>
        完了セッション: {completedSessions} | サイクル: {currentCycle + 1}
      </Typography>
    </MotionContainer>
  );
};