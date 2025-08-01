import React from 'react';
import { 
  Box, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  ListItemSecondaryAction,
  IconButton,
  Chip,
  CircularProgress,
  Checkbox,
  Tooltip,
  Divider
} from '@mui/material';
import { styled } from '@mui/material/styles';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import SchoolIcon from '@mui/icons-material/School';
import PeopleIcon from '@mui/icons-material/People';
import WorkIcon from '@mui/icons-material/Work';

const TaskItem = styled(ListItem)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius,
  marginBottom: theme.spacing(1),
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

interface Task {
  id: string;
  title: string;
  type: 'routine' | 'social' | 'skill_up' | 'work' | string;
  difficulty: number;
  completed: boolean;
  dueTime?: string;
  estimatedTime?: number;
}

interface TasksListProps {
  tasks: Task[];
  loading?: boolean;
  onTaskToggle: (taskId: string, completed: boolean) => void;
  onTaskClick?: (taskId: string) => void;
  emptyMessage?: string;
  maxItems?: number;
}

const TasksList: React.FC<TasksListProps> = ({
  tasks,
  loading = false,
  onTaskToggle,
  onTaskClick,
  emptyMessage = 'タスクはありません',
  maxItems = 5
}) => {
  // Get task icon based on type
  const getTaskIcon = (type: string) => {
    switch (type) {
      case 'routine':
        return <AccessTimeIcon />;
      case 'social':
        return <PeopleIcon color="info" />;
      case 'skill_up':
        return <SchoolIcon color="success" />;
      case 'work':
        return <WorkIcon color="warning" />;
      default:
        return <AccessTimeIcon />;
    }
  };
  
  // Get difficulty label and color
  const getDifficultyInfo = (difficulty: number) => {
    if (difficulty >= 4) return { label: '難しい', color: 'error' };
    if (difficulty >= 3) return { label: 'やや難しい', color: 'warning' };
    if (difficulty >= 2) return { label: '普通', color: 'info' };
    return { label: '簡単', color: 'success' };
  };
  
  // Display limited number of tasks
  const displayedTasks = tasks.slice(0, maxItems);
  const hasMoreTasks = tasks.length > maxItems;
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress size={32} />
      </Box>
    );
  }
  
  if (tasks.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', p: 3 }}>
        <Typography color="text.secondary">{emptyMessage}</Typography>
      </Box>
    );
  }
  
  return (
    <List disablePadding>
      {displayedTasks.map((task, index) => {
        const difficultyInfo = getDifficultyInfo(task.difficulty);
        
        return (
          <React.Fragment key={task.id}>
            <TaskItem 
              onClick={() => onTaskClick && onTaskClick(task.id)}
              sx={{ cursor: onTaskClick ? 'pointer' : 'default' }}
            >
              <ListItemIcon>
                <Checkbox
                  edge="start"
                  checked={task.completed}
                  onChange={(e) => {
                    e.stopPropagation();
                    onTaskToggle(task.id, e.target.checked);
                  }}
                  sx={{
                    '&.Mui-checked': {
                      color: 'success.main',
                    },
                  }}
                />
              </ListItemIcon>
              
              <ListItemText
                primary={
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      textDecoration: task.completed ? 'line-through' : 'none',
                      color: task.completed ? 'text.secondary' : 'text.primary',
                      fontWeight: task.completed ? 'normal' : 500,
                    }}
                  >
                    {task.title}
                  </Typography>
                }
                secondary={
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                      {getTaskIcon(task.type)}
                      <Typography variant="caption" sx={{ ml: 0.5 }}>
                        {task.type === 'routine' ? '習慣' : 
                         task.type === 'social' ? '社交' :
                         task.type === 'skill_up' ? 'スキル' :
                         task.type === 'work' ? '仕事' : task.type}
                      </Typography>
                    </Box>
                    
                    <Chip
                      icon={<FitnessCenterIcon fontSize="small" />}
                      label={difficultyInfo.label}
                      size="small"
                      color={difficultyInfo.color as any}
                      variant="outlined"
                      sx={{ height: 20, '& .MuiChip-label': { px: 1, py: 0 } }}
                    />
                    
                    {task.dueTime && (
                      <Tooltip title="期限">
                        <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
                          <AccessTimeIcon fontSize="small" color="action" />
                          <Typography variant="caption" color="text.secondary" sx={{ ml: 0.5 }}>
                            {task.dueTime}
                          </Typography>
                        </Box>
                      </Tooltip>
                    )}
                  </Box>
                }
              />
              
              <ListItemSecondaryAction>
                <IconButton edge="end" size="small" onClick={(e) => e.stopPropagation()}>
                  <MoreVertIcon fontSize="small" />
                </IconButton>
              </ListItemSecondaryAction>
            </TaskItem>
            
            {index < displayedTasks.length - 1 && (
              <Divider variant="inset" component="li" />
            )}
          </React.Fragment>
        );
      })}
      
      {hasMoreTasks && (
        <Box sx={{ textAlign: 'center', mt: 1 }}>
          <Typography variant="body2" color="primary">
            他 {tasks.length - maxItems} 件のタスク
          </Typography>
        </Box>
      )}
    </List>
  );
};

export default TasksList;