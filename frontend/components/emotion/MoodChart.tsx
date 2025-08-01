import React from 'react';
import { Box, Typography, styled } from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export interface MoodEntry {
  date: Date;
  mood: number;
  note?: string;
}

export interface MoodChartProps {
  data: MoodEntry[];
  period?: 'week' | 'month' | 'year';
  showAverage?: boolean;
  showTrend?: boolean;
  height?: number;
  title?: string;
}

const StyledChartContainer = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  borderRadius: '12px',
  padding: theme.spacing(2),
  border: `1px solid ${theme.palette.divider}`,
}));

const moodColors = {
  1: '#f44336', // とても悪い
  2: '#ff9800', // 悪い
  3: '#9e9e9e', // 普通
  4: '#4caf50', // 良い
  5: '#2196f3', // とても良い
};

const moodLabels = {
  1: 'とても悪い',
  2: '悪い',
  3: '普通',
  4: '良い',
  5: 'とても良い',
};

export const MoodChart: React.FC<MoodChartProps> = ({
  data,
  period = 'week',
  showAverage = true,
  showTrend = true,
  height = 300,
  title = '気分の推移',
}) => {
  const formatDate = (date: Date): string => {
    switch (period) {
      case 'week':
        return date.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' });
      case 'month':
        return date.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' });
      case 'year':
        return date.toLocaleDateString('ja-JP', { year: 'numeric', month: 'short' });
      default:
        return date.toLocaleDateString('ja-JP');
    }
  };

  const sortedData = [...data].sort((a, b) => a.date.getTime() - b.date.getTime());
  
  const labels = sortedData.map(entry => formatDate(entry.date));
  const moodValues = sortedData.map(entry => entry.mood);
  
  // 平均値の計算
  const average = moodValues.length > 0 
    ? moodValues.reduce((sum, mood) => sum + mood, 0) / moodValues.length 
    : 0;

  // トレンドライン（簡単な線形回帰）
  const calculateTrend = (values: number[]): number[] => {
    if (values.length < 2) return values;
    
    const n = values.length;
    const sumX = values.reduce((sum, _, i) => sum + i, 0);
    const sumY = values.reduce((sum, y) => sum + y, 0);
    const sumXY = values.reduce((sum, y, i) => sum + i * y, 0);
    const sumXX = values.reduce((sum, _, i) => sum + i * i, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    return values.map((_, i) => slope * i + intercept);
  };

  const trendValues = showTrend ? calculateTrend(moodValues) : [];

  const datasets = [
    {
      label: '気分',
      data: moodValues,
      borderColor: '#2196f3',
      backgroundColor: 'rgba(33, 150, 243, 0.1)',
      pointBackgroundColor: moodValues.map(mood => moodColors[mood as keyof typeof moodColors]),
      pointBorderColor: moodValues.map(mood => moodColors[mood as keyof typeof moodColors]),
      pointRadius: 6,
      pointHoverRadius: 8,
      tension: 0.3,
      fill: true,
    },
  ];

  if (showAverage && moodValues.length > 0) {
    datasets.push({
      label: '平均',
      data: new Array(moodValues.length).fill(average),
      borderColor: '#ff9800',
      backgroundColor: 'transparent',
      pointRadius: 0,
      borderDash: [5, 5],
      tension: 0,
      fill: false,
    } as any);
  }

  if (showTrend && trendValues.length > 0) {
    datasets.push({
      label: 'トレンド',
      data: trendValues,
      borderColor: '#9c27b0',
      backgroundColor: 'transparent',
      pointRadius: 0,
      borderDash: [10, 5],
      tension: 0,
      fill: false,
    } as any);
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const value = context.parsed.y;
            const moodLabel = moodLabels[value as keyof typeof moodLabels];
            const entry = sortedData[context.dataIndex];
            
            let label = `${context.dataset.label}: ${moodLabel} (${value})`;
            if (entry?.note) {
              label += `\nメモ: ${entry.note}`;
            }
            return label;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        min: 0.5,
        max: 5.5,
        ticks: {
          stepSize: 1,
          callback: (value: any) => {
            return moodLabels[value as keyof typeof moodLabels] || value;
          },
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
    },
    elements: {
      point: {
        hoverBorderWidth: 3,
      },
    },
  };

  const chartData = {
    labels,
    datasets,
  };

  return (
    <StyledChartContainer>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      
      {moodValues.length > 0 && (
        <Box mb={2}>
          <Typography variant="body2" color="textSecondary">
            平均気分: {moodLabels[Math.round(average) as keyof typeof moodLabels]} ({average.toFixed(1)})
          </Typography>
        </Box>
      )}
      
      <Box height={height}>
        {moodValues.length > 0 ? (
          <Line data={chartData} options={options} />
        ) : (
          <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            height="100%"
            color="text.secondary"
          >
            <Typography>データがありません</Typography>
          </Box>
        )}
      </Box>
    </StyledChartContainer>
  );
};