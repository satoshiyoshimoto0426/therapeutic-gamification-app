import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import KPIDashboard from '../KPIDashboard';

// モックデータ
const mockDashboardData = {
  overall_health_score: 0.75,
  critical_metrics: {
    d1_retention: {
      name: 'D1リテンション率',
      current_value: 0.42,
      target_value: 0.45,
      unit: '%',
      trend: 'up',
      achievement_rate: 93.3
    },
    d7_continuation_rate: {
      name: '7日継続率 (ACTION以上)',
      current_value: 0.23,
      target_value: 0.25,
      unit: '%',
      trend: 'stable',
      achievement_rate: 92.0
    },
    d21_habituation_rate: {
      name: '21日習慣化達成率',
      current_value: 0.11,
      target_value: 0.12,
      unit: '%',
      trend: 'up',
      achievement_rate: 91.7
    },
    arpmau: {
      name: 'ARPMAU (月間平均収益)',
      current_value: 320,
      target_value: 350,
      unit: '¥',
      trend: 'up',
      achievement_rate: 91.4
    }
  },
  active_alerts: [
    {
      alert_id: 'alert-1',
      metric_name: 'D1リテンション率',
      severity: 'high',
      message: 'D1リテンション率が閾値を下回りました',
      created_at: '2025-07-27T12:00:00Z'
    }
  ],
  total_users: 1250,
  last_updated: '2025-07-27T12:00:00Z',
  summary_insights: [
    'D1リテンション率の改善が必要です',
    '収益化施策の強化を検討してください'
  ]
};

// fetch のモック
global.fetch = jest.fn();

describe('KPIDashboard', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  it('ローディング状態を正しく表示する', () => {
    (fetch as jest.Mock).mockImplementation(() => new Promise(() => {})); // 永続的なpending状態
    
    render(<KPIDashboard />);
    
    expect(screen.getByText('KPI ダッシュボード')).toBeInTheDocument();
    // ローディングスケルトンの確認
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('エラー状態を正しく表示する', async () => {
    (fetch as jest.Mock).mockRejectedValue(new Error('API Error'));
    
    render(<KPIDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });

  it('ダッシュボードデータを正しく表示する', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockDashboardData
    });
    
    render(<KPIDashboard />);
    
    await waitFor(() => {
      // ヘッダー情報
      expect(screen.getByText('KPI ダッシュボード')).toBeInTheDocument();
      expect(screen.getByText('健康度: 75.0%')).toBeInTheDocument();
      
      // 重要指標
      expect(screen.getByText('D1リテンション率')).toBeInTheDocument();
      expect(screen.getByText('42.0%')).toBeInTheDocument();
      expect(screen.getByText('目標: 45.0%')).toBeInTheDocument();
      
      expect(screen.getByText('7日継続率 (ACTION以上)')).toBeInTheDocument();
      expect(screen.getByText('23.0%')).toBeInTheDocument();
      
      expect(screen.getByText('21日習慣化達成率')).toBeInTheDocument();
      expect(screen.getByText('11.0%')).toBeInTheDocument();
      
      expect(screen.getByText('ARPMAU (月間平均収益)')).toBeInTheDocument();
      expect(screen.getByText('¥320')).toBeInTheDocument();
      
      // サマリー統計
      expect(screen.getByText('1,250')).toBeInTheDocument(); // 総ユーザー数
      expect(screen.getByText('1')).toBeInTheDocument(); // アクティブアラート数
    });
  });

  it('アクティブアラートを正しく表示する', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockDashboardData
    });
    
    render(<KPIDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('アクティブアラート')).toBeInTheDocument();
      expect(screen.getByText('HIGH')).toBeInTheDocument();
      expect(screen.getByText('D1リテンション率が閾値を下回りました')).toBeInTheDocument();
    });
  });

  it('システム洞察を正しく表示する', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockDashboardData
    });
    
    render(<KPIDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('システム洞察')).toBeInTheDocument();
      expect(screen.getByText('D1リテンション率の改善が必要です')).toBeInTheDocument();
      expect(screen.getByText('収益化施策の強化を検討してください')).toBeInTheDocument();
    });
  });

  it('健康度スコアに応じて適切な色とアイコンを表示する', async () => {
    // 健康な状態（0.8以上）
    const healthyData = { ...mockDashboardData, overall_health_score: 0.85 };
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => healthyData
    });
    
    render(<KPIDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('健康度: 85.0%')).toBeInTheDocument();
      // 緑色のテキストクラスが適用されているかチェック
      const healthElement = screen.getByText('健康度: 85.0%');
      expect(healthElement).toHaveClass('text-green-600');
    });
  });

  it('警告状態の健康度スコアを正しく表示する', async () => {
    // 警告状態（0.6-0.8）
    const warningData = { ...mockDashboardData, overall_health_score: 0.65 };
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => warningData
    });
    
    render(<KPIDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('健康度: 65.0%')).toBeInTheDocument();
      const healthElement = screen.getByText('健康度: 65.0%');
      expect(healthElement).toHaveClass('text-yellow-600');
    });
  });

  it('危険状態の健康度スコアを正しく表示する', async () => {
    // 危険状態（0.6未満）
    const criticalData = { ...mockDashboardData, overall_health_score: 0.45 };
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => criticalData
    });
    
    render(<KPIDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('健康度: 45.0%')).toBeInTheDocument();
      const healthElement = screen.getByText('健康度: 45.0%');
      expect(healthElement).toHaveClass('text-red-600');
    });
  });

  it('アラートがない場合はアラートセクションを表示しない', async () => {
    const noAlertsData = { ...mockDashboardData, active_alerts: [] };
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => noAlertsData
    });
    
    render(<KPIDashboard />);
    
    await waitFor(() => {
      // アクティブアラートのカードが表示されないことを確認
      const alertCards = screen.queryAllByText('アクティブアラート');
      // ヘッダー部分の統計表示は残るが、詳細カードは表示されない
      expect(alertCards.length).toBeLessThanOrEqual(1);
    });
  });

  it('値のフォーマットが正しく動作する', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockDashboardData
    });
    
    render(<KPIDashboard />);
    
    await waitFor(() => {
      // パーセンテージ表示
      expect(screen.getByText('42.0%')).toBeInTheDocument();
      expect(screen.getByText('23.0%')).toBeInTheDocument();
      
      // 通貨表示
      expect(screen.getByText('¥320')).toBeInTheDocument();
      expect(screen.getByText('目標: ¥350')).toBeInTheDocument();
      
      // カウント表示
      expect(screen.getByText('1,250')).toBeInTheDocument();
    });
  });
});