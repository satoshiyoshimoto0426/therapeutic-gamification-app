import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Alert, Skeleton } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useApi } from '../contexts/ApiContext';
import { 
  DashboardLayout, 
  DashboardSection, 
  DashboardSummary,
  TasksList
} from '../components/dashboard';
import AddTaskIcon from '@mui/icons-material/AddTask';
import AutoStoriesIcon from '@mui/icons-material/AutoStories';

interface DashboardData {
  user: {
    name: string;
    level: number;
    xp: number;
    xpToNextLevel: number;
  };
  stats: {
    tasksCompleted: number;
    currentStreak: number;
    moodAverage: number;
  };
  companion: {
    name: string;
    level: number;
  };
  todayTasks: Array<{
    id: string;
    title: string;
    type: string;
    difficulty: number;
    completed: boolean;
    dueTime?: string;
  }>;
  recentAchievements: Array<{
    id: string;
    title: string;
    description: string;
    unlockedAt: string;
  }>;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { get, post } = useApi();
  
  // State for dashboard data
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Mock data for now - replace with actual API call
        const mockData: DashboardData = {
          user: {
            name: user?.name || 'ユーザー',
            level: user?.level || 1,
            xp: user?.xp || 150,
            xpToNextLevel: user?.xpToNextLevel || 200,
          },
          stats: {
            tasksCompleted: 12,
            currentStreak: 3,
            moodAverage: 3.8,
          },
          companion: {
            name: 'ユウ',
            level: 2,
          },
          todayTasks: [
            {
              id: '1',
              title: '朝の散歩',
              type: 'routine',
              difficulty: 2,
              completed: false,
              dueTime: '09:00',
            },
            {
              id: '2',
              title: '読書30分',
              type: 'skill_up',
              difficulty: 3,
              completed: true,
            },
            {
              id: '3',
              title: '友人に連絡',
              type: 'social',
              difficulty: 2,
              completed: false,
            },
          ],
          recentAchievements: [
            {
              id: '1',
              title: '3日連続達成',
              description: 'タスクを3日連続で完了しました',
              unlockedAt: '2024-01-15',
            },
          ],
        };
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setDashboardData(mockData);
        setError(null);
      } catch (err: any) {
        console.error('Failed to fetch dashboard data:', err);
        setError('ダッシュボードデータの取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [user, get]);
  
  // Handle task toggle
  const handleTaskToggle = async (taskId: string, completed: boolean) => {
    try {
      // Update local state immediately for better UX
      if (dashboardData) {
        const updatedTasks = dashboardData.todayTasks.map(task =>
          task.id === taskId ? { ...task, completed } : task
        );
        setDashboardData({
          ...dashboardData,
          todayTasks: updatedTasks,
        });
      }
      
      // Make API call to update task
      await post(`/tasks/${taskId}/toggle`, { completed });
    } catch (err) {
      console.error('Failed to toggle task:', err);
      // Revert local state on error
      if (dashboardData) {
        const revertedTasks = dashboardData.todayTasks.map(task =>
          task.id === taskId ? { ...task, completed: !completed } : task
        );
        setDashboardData({
          ...dashboardData,
          todayTasks: revertedTasks,
        });
      }
    }
  };
  
  // Handle navigation
  const handleAddTask = () => {
    navigate('/tasks');
  };
  
  const handleViewStory = () => {
    navigate('/story');
  };
  
  if (error) {
    return (
      <DashboardLayout>
        <DashboardSection title="エラー" gridSize={{ xs: 12, sm: 12, md: 12 }}>
          <Alert severity="error">{error}</Alert>
        </DashboardSection>
      </DashboardLayout>
    );
  }
  
  return (
    <DashboardLayout>
      {/* User Summary Section */}
      <DashboardSection title="" gridSize={{ xs: 12, sm: 12, md: 12 }}>
        {loading || !dashboardData ? (
          <Box>
            <Skeleton variant="rectangular" height={120} sx={{ mb: 2 }} />
            <Skeleton variant="rectangular" height={60} />
          </Box>
        ) : (
          <DashboardSummary
            userName={dashboardData.user.name}
            level={dashboardData.user.level}
            xp={dashboardData.user.xp}
            xpToNextLevel={dashboardData.user.xpToNextLevel}
            tasksCompleted={dashboardData.stats.tasksCompleted}
            currentStreak={dashboardData.stats.currentStreak}
            moodAverage={dashboardData.stats.moodAverage}
            companionName={dashboardData.companion.name}
            companionLevel={dashboardData.companion.level}
          />
        )}
      </DashboardSection>
      
      {/* Today's Tasks */}
      <DashboardSection 
        title="今日のタスク" 
        gridSize={{ xs: 12, sm: 12, md: 6 }}
        color="#1976d2"
      >
        {loading || !dashboardData ? (
          <Box>
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} variant="rectangular" height={60} sx={{ mb: 1 }} />
            ))}
          </Box>
        ) : (
          <>
            <TasksList
              tasks={dashboardData.todayTasks}
              onTaskToggle={handleTaskToggle}
              maxItems={5}
            />
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Button
                variant="outlined"
                startIcon={<AddTaskIcon />}
                onClick={handleAddTask}
                size="small"
              >
                タスクを追加
              </Button>
            </Box>
          </>
        )}
      </DashboardSection>
      
      {/* Quick Actions */}
      <DashboardSection 
        title="クイックアクション" 
        gridSize={{ xs: 12, sm: 12, md: 6 }}
        color="#9c27b0"
      >
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<AutoStoriesIcon />}
            onClick={handleViewStory}
            fullWidth
            sx={{ py: 1.5 }}
          >
            ストーリーを読む
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate('/mood')}
            fullWidth
            sx={{ py: 1.5 }}
          >
            気分を記録
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate('/companion')}
            fullWidth
            sx={{ py: 1.5 }}
          >
            ユウと会話
          </Button>
        </Box>
      </DashboardSection>
      
      {/* Recent Achievements */}
      <DashboardSection 
        title="最近の実績" 
        gridSize={{ xs: 12, sm: 12, md: 6 }}
        color="#4caf50"
      >
        {loading || !dashboardData ? (
          <Box>
            <Skeleton variant="rectangular" height={80} />
          </Box>
        ) : dashboardData.recentAchievements.length > 0 ? (
          <Box>
            {dashboardData.recentAchievements.map((achievement) => (
              <Box key={achievement.id} sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                  🏆 {achievement.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {achievement.description}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {achievement.unlockedAt}
                </Typography>
              </Box>
            ))}
          </Box>
        ) : (
          <Typography color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
            まだ実績がありません
          </Typography>
        )}
      </DashboardSection>
      
      {/* Progress Overview */}
      <DashboardSection 
        title="進捗概要" 
        gridSize={{ xs: 12, sm: 12, md: 6 }}
        color="#ff9800"
      >
        {loading || !dashboardData ? (
          <Box>
            <Skeleton variant="rectangular" height={100} />
          </Box>
        ) : (
          <Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              今週の活動サマリー
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">完了タスク</Typography>
              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                {dashboardData.stats.tasksCompleted}/20
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">連続達成</Typography>
              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                {dashboardData.stats.currentStreak}日
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">平均気分</Typography>
              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                {dashboardData.stats.moodAverage.toFixed(1)}/5
              </Typography>
            </Box>
          </Box>
        )}
      </DashboardSection>
    </DashboardLayout>
  );
};

export default Dashboard;