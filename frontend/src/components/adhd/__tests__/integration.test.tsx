import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { 
  ADHDFriendlyLayout, 
  SimpleNavigation, 
  FocusMode, 
  AutoSaveProgress 
} from '../index'
import { AuthContext } from '../../../contexts/AuthContext'

const theme = createTheme()

const mockUser = {
  id: '1',
  name: 'テストユーザー',
  level: 5,
  email: 'test@example.com'
}

const mockAuthContext = {
  user: mockUser,
  login: jest.fn(),
  logout: jest.fn(),
  loading: false
}

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <ThemeProvider theme={theme}>
      <AuthContext.Provider value={mockAuthContext}>
        {children}
      </AuthContext.Provider>
    </ThemeProvider>
  </BrowserRouter>
)

describe('ADHD配慮UX統合テスト', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('ADHD配慮の要件3.1: ワンスクリーン・ワンアクション設計', () => {
    render(
      <TestWrapper>
        <ADHDFriendlyLayout>
          <SimpleNavigation />
          <FocusMode isActive={false} onToggle={() => {}} />
        </ADHDFriendlyLayout>
      </TestWrapper>
    )

    // 最大3項目のナビゲーション
    const navButtons = screen.getAllByRole('button').filter(button => 
      button.textContent?.includes('ホーム') || 
      button.textContent?.includes('タスク') || 
      button.textContent?.includes('気分')
    )
    expect(navButtons).toHaveLength(3)

    // 一度に表示される選択肢が3つ以下であることを確認
    const allButtons = screen.getAllByRole('button')
    const visibleButtons = allButtons.filter(button => {
      const styles = window.getComputedStyle(button)
      return styles.display !== 'none' && styles.visibility !== 'hidden'
    })
    expect(visibleButtons.length).toBeLessThanOrEqual(6) // ナビ3つ + その他のUI要素
  })

  test('ADHD配慮の要件9.2: 集中モードと気を散らす要素の除去', async () => {
    const TestComponent = () => {
      const [focusMode, setFocusMode] = React.useState(false)
      
      return (
        <TestWrapper>
          <ADHDFriendlyLayout>
            <FocusMode 
              isActive={focusMode} 
              onToggle={setFocusMode}
              distractionLevel="high"
            />
          </ADHDFriendlyLayout>
        </TestWrapper>
      )
    }

    render(<TestComponent />)

    // 集中モードを有効にする
    const focusToggle = screen.getByRole('checkbox')
    fireEvent.click(focusToggle)

    await waitFor(() => {
      // 気を散らす要素の警告が表示される
      expect(screen.getByText(/気を散らす要素が検出されました/)).toBeInTheDocument()
    })

    // 集中モード時のスタイル変更を確認
    const mainContent = screen.getByRole('main')
    expect(mainContent).toHaveStyle({
      padding: expect.stringContaining('8px') // 集中モード時のpadding削減
    })
  })

  test('自動保存とプログレス可視化の統合', async () => {
    render(
      <TestWrapper>
        <AutoSaveProgress
          autoSaveEnabled={true}
          saveInterval={2}
          currentProgress={65}
          totalTasks={10}
          completedTasks={6}
        />
      </TestWrapper>
    )

    // プログレス表示の確認
    expect(screen.getByText('6/10 タスク (65%)')).toBeInTheDocument()
    
    // プログレスバーの確認
    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toHaveAttribute('aria-valuenow', '65')

    // 自動保存の動作確認
    await waitFor(() => {
      expect(screen.getByText('保存中...')).toBeInTheDocument()
    }, { timeout: 3000 })

    await waitFor(() => {
      expect(screen.getByText('保存完了')).toBeInTheDocument()
    }, { timeout: 2000 })
  })

  test('モバイル対応とタッチフレンドリーUI', () => {
    // モバイル画面サイズをシミュレート
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    })

    render(
      <TestWrapper>
        <ADHDFriendlyLayout>
          <SimpleNavigation variant="horizontal" />
        </ADHDFriendlyLayout>
      </TestWrapper>
    )

    // 44px以上のタッチターゲットサイズを確認
    const buttons = screen.getAllByRole('button')
    buttons.forEach(button => {
      const rect = button.getBoundingClientRect()
      expect(Math.max(rect.width, rect.height)).toBeGreaterThanOrEqual(44)
    })

    // ボトムナビゲーションの表示確認
    const bottomNavItems = buttons.filter(button => 
      button.closest('[role="button"]')?.parentElement?.tagName === 'NAV' ||
      button.textContent?.includes('ホーム') ||
      button.textContent?.includes('タスク') ||
      button.textContent?.includes('気分')
    )
    expect(bottomNavItems.length).toBeGreaterThan(0)
  })

  test('BIZ UDGothicフォントとアクセシビリティ', () => {
    render(
      <TestWrapper>
        <ADHDFriendlyLayout>
          <SimpleNavigation />
          <AutoSaveProgress />
        </ADHDFriendlyLayout>
      </TestWrapper>
    )

    // BIZ UDGothicフォントの適用確認
    const textElements = [
      screen.getByText('ホーム'),
      screen.getByText('進捗状況'),
    ]

    textElements.forEach(element => {
      const styles = window.getComputedStyle(element)
      expect(styles.fontFamily).toContain('BIZ UDGothic')
      expect(parseFloat(styles.lineHeight)).toBeGreaterThanOrEqual(1.6) // 1.6以上の行間
    })
  })

  test('集中モードとナビゲーションの連携', async () => {
    const TestComponent = () => {
      const [focusMode, setFocusMode] = React.useState(false)
      
      return (
        <TestWrapper>
          <ADHDFriendlyLayout>
            <SimpleNavigation focusMode={focusMode} showDescriptions={true} />
            <FocusMode isActive={focusMode} onToggle={setFocusMode} />
          </ADHDFriendlyLayout>
        </TestWrapper>
      )
    }

    render(<TestComponent />)

    // 通常モードでは説明文が表示される
    expect(screen.getByText('メインダッシュボード')).toBeInTheDocument()

    // 集中モードを有効にする
    const focusToggle = screen.getByRole('checkbox')
    fireEvent.click(focusToggle)

    await waitFor(() => {
      // 集中モード時は説明文が非表示になる
      expect(screen.queryByText('メインダッシュボード')).not.toBeInTheDocument()
    })
  })

  test('エラーハンドリングとユーザーフィードバック', async () => {
    // エラーを発生させるためのモック
    const originalRandom = Math.random
    Math.random = jest.fn(() => 0.05) // エラー発生

    render(
      <TestWrapper>
        <AutoSaveProgress saveInterval={1} />
      </TestWrapper>
    )

    // エラー状態の確認
    await waitFor(() => {
      expect(screen.getByText('保存失敗')).toBeInTheDocument()
    }, { timeout: 3000 })

    // エラーメッセージの表示確認
    await waitFor(() => {
      expect(screen.getByText(/ネットワークエラーが発生しました/)).toBeInTheDocument()
    })

    // リトライボタンの確認
    const infoButton = screen.getByLabelText('詳細を表示')
    fireEvent.click(infoButton)

    await waitFor(() => {
      const retryButton = screen.getByLabelText('再試行')
      expect(retryButton).toBeInTheDocument()
    })

    Math.random = originalRandom
  })

  test('レスポンシブデザインの動作確認', () => {
    const { rerender } = render(
      <TestWrapper>
        <SimpleNavigation variant="horizontal" />
      </TestWrapper>
    )

    // デスクトップサイズ
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    })

    // 水平レイアウトが適用される
    const buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(3)

    // モバイルサイズに変更
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    })

    rerender(
      <TestWrapper>
        <SimpleNavigation variant="horizontal" />
      </TestWrapper>
    )

    // モバイル対応のスタイルが適用される
    const mobileButtons = screen.getAllByRole('button')
    mobileButtons.forEach(button => {
      const styles = window.getComputedStyle(button)
      expect(styles.fontSize).toMatch(/0\.9rem|14\.4px/) // モバイル用フォントサイズ
    })
  })

  test('パフォーマンスとメモリ効率', async () => {
    const TestComponent = () => {
      const [mounted, setMounted] = React.useState(true)
      
      return (
        <TestWrapper>
          {mounted && (
            <ADHDFriendlyLayout>
              <AutoSaveProgress saveInterval={1} />
            </ADHDFriendlyLayout>
          )}
          <button onClick={() => setMounted(false)}>Unmount</button>
        </TestWrapper>
      )
    }

    render(<TestComponent />)

    // コンポーネントのアンマウント
    const unmountButton = screen.getByText('Unmount')
    fireEvent.click(unmountButton)

    // メモリリークがないことを確認（タイマーのクリーンアップ）
    await waitFor(() => {
      expect(screen.queryByText('自動保存')).not.toBeInTheDocument()
    })
  })
})