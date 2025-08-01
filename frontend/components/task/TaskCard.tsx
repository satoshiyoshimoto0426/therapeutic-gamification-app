import React from 'react';
import { Box, Typography, IconButton, Chip, styled } from '@mui/material';
import { motion } from 'framer-motion';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import TimerIcon from '@mui/icons-material/Timer';
import RepeatIcon from '@mui/icons-material/Repeat';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import GroupIcon from '@mui/icons-material/Group';

export interface Task {
  id: string;
  title: string;
  description?: string;
  type: 'routine' | 'one-shot' | 'skill-up' | 'social';
  difficulty: 1 | 2 | 3 | 4 | 5;
  estimatedTime?: number; // minutes
  xpReward: number;
  completed: boolean;
  dueDate?: Date;
  tags?: string[];
  pomodoroSessions?: number;
}

export interface TaskCardProps {
  task: Task;
  onToggleComplete: (taskId: string) => void;
  onStartPomodoro?: (taskId: string) => void;
  showXP?: boolean;
  showTime?: boolean;
  showTags?: boolean;
  compact?: boolean;
  animated?: boolean;
}

const taskTypeConfig = {
  routine: {
    icon: <RepeatIcon />,
    color: '#4CAF50',
    label: 'ルーティン',
  },
  'one-shot': {
    icon: <CheckCircleIcon />,
    color: '#2196F3',
    label: 'ワンショット',
  },
  'skill-up': {
    icon: <TrendingUpIcon />,
    color: '#FF9800',
    label: 'スキルアップ',
  },
  social: {
    icon: <GroupIcon />,
    color: '#9C27B0',
    label: 'ソーシャル',
  },
};

const difficultyStars = (difficulty: number) => '★'.repeat(difficulty) + '☆'.repeat(5 - difficulty);

const StyledTaskCard = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'completed' && prop !== 'compact',
})(
  ({
    theme,
    completed = false,
    compact = false,
  }: {
    theme: any;
    completed?: boolean;
    compact?: boolean;
  }) => ({
    backgroundColor: theme.palette.background.paper,
    borderRadius: '12px',
    border: `1px solid ${theme.palette.divider}`,
    padding: compact ? theme.spacing(1.5) : theme.spacing(2),
    transition: 'all 0.2s ease',
    opacity: completed ? 0.7 : 1,
    position: 'relative',
    overflow: 'hidden',
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
    },
    ...(completed && {
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `linear-gradient(45deg, transparent 40%, ${theme.palette.success.main}20 50%, transparent 60%)`,
        pointerEvents: 'none',
      },
    }),
  })
);

const TaskHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'flex-start',
  justifyContent: 'space-between',
  marginBottom: theme.spacing(1),
}));

const TaskContent = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(1),
  flex: 1,
}));

const TaskMeta = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  flexWrap: 'wrap',
  marginTop: theme.spacing(1),
}));

const XPChip = styled(Chip)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  fontWeight: 'bold',
  '& .MuiChip-icon': {
    color: 'inherit',
  },
}));

const TypeChip = styled(Chip, {
  shouldForwardProp: (prop) => prop !== 'taskType',
})(
  ({
    theme,
    taskType,
  }: {
    theme: any;
    taskType: 'routine' | 'one-shot' | 'skill-up' | 'social';
  }) => ({
    backgroundColor: `${taskTypeConfig[taskType].color}20`,
    color: taskTypeConfig[taskType].color,
    border: `1px solid ${taskTypeConfig[taskType].color}40`,
    '& .MuiChip-icon': {
      color: 'inherit',
    },
  })
);

const MotionTaskCard = motion(StyledTaskCard);

export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onToggleComplete,
  onStartPomodoro,
  showXP = true,
  showTime = true,
  showTags = true,
  compact = false,
  animated = true,
}) => {
  const typeConfig = taskTypeConfig[task.type];
  const isOverdue = task.dueDate && new Date() > task.dueDate && !task.completed;

  const cardContent = (
    <>
      <TaskHeader>
        <TaskContent>
          <Box display="flex" alignItems="center" gap={1}>
            <IconButton
              size="small"
              onClick={() => onToggleComplete(task.id)}
              color={task.completed ? 'success' : 'default'}
            >
              {task.completed ? <CheckCircleIcon /> : <RadioButtonUncheckedIcon />}
            </IconButton>
            <Typography
              variant={compact ? 'body2' : 'h6'}
              sx={{
                textDecoration: task.completed ? 'line-through' : 'none',
                color: task.completed ? 'text.secondary' : 'text.primary',
              }}
            >
              {task.title}
            </Typography>
          </Box>
          
          {task.description && !compact && (
            <Typography variant="body2" color="text.secondary" ml={5}>
              {task.description}
            </Typography>
          )}
        </TaskContent>
        
        {onStartPomodoro && !task.completed && (
          <IconButton
            size="small"
            onClick={() => onStartPomodoro(task.id)}
            color="primary"
          >
            <TimerIcon />
          </IconButton>
        )}
      </TaskHeader>

      <TaskMeta>
        <TypeChip
          icon={typeConfig.icon}
          label={typeConfig.label}
          size="small"
          taskType={task.type}
        />
        
        <Chip
          label={difficultyStars(task.difficulty)}
          size="small"
          variant="outlined"
        />
        
        {showXP && (
          <XPChip
            label={`${task.xpReward} XP`}
            size="small"
          />
        )}
        
        {showTime && task.estimatedTime && (
          <Chip
            icon={<TimerIcon />}
            label={`${task.estimatedTime}分`}
            size="small"
            variant="outlined"
          />
        )}
        
        {task.pomodoroSessions && task.pomodoroSessions > 0 && (
          <Chip
            label={`🍅 ${task.pomodoroSessions}`}
            size="small"
            variant="outlined"
          />
        )}
        
        {isOverdue && (
          <Chip
            label="期限切れ"
            size="small"
            color="error"
          />
        )}
      </TaskMeta>
      
      {showTags && task.tags && task.tags.length > 0 && (
        <Box display="flex" gap={0.5} flexWrap="wrap" mt={1}>
          {task.tags.map((tag) => (
            <Chip
              key={tag}
              label={tag}
              size="small"
              variant="outlined"
              sx={{ fontSize: '0.7rem', height: 20 }}
            />
          ))}
        </Box>
      )}
    </>
  );

  if (animated) {
    return (
      <MotionTaskCard
        completed={task.completed}
        compact={compact}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, x: -100 }}
        transition={{ duration: 0.3 }}
        whileHover={{ scale: 1.02 }}
        layout
      >
        {cardContent}
      </MotionTaskCard>
    );
  }

  return (
    <StyledTaskCard completed={task.completed} compact={compact}>
      {cardContent}
    </StyledTaskCard>
  );
};