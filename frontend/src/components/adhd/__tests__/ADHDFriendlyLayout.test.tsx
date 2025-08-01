import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import ADHDFriendlyLayout from '../ADHDFriendlyLayout'
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

describe('ADHDFriendlyLayout', () => {
  beforeEach(() => {
    // モックをリセット
    jest.clearAllMocks()
  })

  test('最大3項目のシンプルナビゲーションを表示する', () => {
    render(
      <TestWrapper>
        <ADHDFriendlyLayout />
      </TestWrapper>
    )

    // 3つのナビゲーション項目が表示されることを確認
    expect(screen.getByText('ホーム')).toBeInTheDocument()
    expect(screen.getByText('タスク')).toBeInTheDocument()
    expect(screen.getByText('気分')).toBeInTheDocument()

    // 4つ目以降の項目がないことを確認
    expect(screen.queryByText('ストーリー')).not.toBeInTheDocument()
    expect(screen.queryByText('コンパニオン')).not.toBeInTheDocument()
    expect(screen.queryByText('習慣')).not.toBeInTheDocument()
  })

  test('集中モードの切り替えが正常に動作する', async () => {
    render(
      <TestWrapper>
        <ADHDFriendlyLayout />
      </TestWrapper>
    )

    const focusButton = screen.getByRole('button', { name: /focus/i })
    
    // 集中モードを有効にする
    fireEvent.click(focusButton)
    
    await waitFor(() => {
      expect(screen.getByText('集中モードを開始しました')).toBeInTheDocument()
    })

    // 集中モードを無効にする
    fireEvent.click(focusButton)
    
    await waitFor(() => {
      expect(screen.getByText('集中モードを解除しました')).toBeInTheDocument()
    })
  })

  test('プログレス表示が正常に動作する', () => {
    render(
      <TestWrapper>
        <ADHDFriendlyLayout />
      </TestWrapper>
    )

    // プログレスバーが表示されることを確認
    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toBeInTheDocument()

    // 連続日数とパーセンテージが表示されることを確認
    expect(screen.getByText('7日連続')).toBeInTheDocument()
    expect(screen.getByText('65%')).toBeInTheDocument()
  })

  test('自動保存インジケーターが表示される', async () => {
    render(
      <TestWrapper>
        <ADHDFriendlyLayout />
      </TestWrapper>
    )

    // 自動保存が開始されるまで待機
    await waitFor(() => {
      const saveButton = screen.getByRole('button', { name: /save/i })
      expect(saveButton).toBeInTheDocument()
    }, { timeout: 35000 }) // 30秒の自動保存間隔 + 余裕
  })

  test('モバイル表示でボトムナビゲーションが表示される', () => {
    // モバイル表示をシミュレート
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    })
    
    render(
      <TestWrapper>
        <ADHDFriendlyLayout />
      </TestWrapper>
    )

    // ボトムナビゲーションの項目が表示されることを確認
    const bottomNavItems = screen.getAllByRole('button')
    const navItems = bottomNavItems.filter(button => 
      button.textContent?.includes('ホーム') || 
      button.textContent?.includes('タスク') || 
      button.textContent?.includes('気分')
    )
    
    expect(navItems).toHaveLength(3)
  })

  test('44px以上のタッチターゲットサイズを確保している', () => {
    render(
      <TestWrapper>
        <ADHDFriendlyLayout />
      </TestWrapper>
    )

    const buttons = screen.getAllByRole('button')
    
    buttons.forEach(button => {
      const styles = window.getComputedStyle(button)
      const minHeight = parseInt(styles.minHeight) || parseInt(styles.height)
      
      // 44px以上のタッチターゲットサイズを確認
      expect(minHeight).toBeGreaterThanOrEqual(44)
    })
  })

  test('BIZ UDGothicフォントが適用されている', () => {
    render(
      <TestWrapper>
        <ADHDFriendlyLayout />
      </TestWrapper>
    )

    const titleElement = screen.getByText('ホーム')
    const styles = window.getComputedStyle(titleElement)
    
    expect(styles.fontFamily).toContain('BIZ UDGothic')
  })

  test('集中モード時に気を散らす要素が除去される', async () => {
    render(
      <TestWrapper>
        <ADHDFriendlyLayout />
      </TestWrapper>
    )

    const focusButton = screen.getByRole('button', { name: /focus/i })
    
    // 集中モードを有効にする
    fireEvent.click(focusButton)
    
    await waitFor(() => {
      const mainContent = screen.getByRole('main')
      const styles = window.getComputedStyle(mainContent)
      
      // アニメーションが無効化されていることを確認
      expect(styles.getPropertyValue('--animation')).toBe('none')
    })
  })

  test('通知が適切に表示・非表示される', async () => {
    render(
      <TestWrapper>
        <ADHDFriendlyLayout />
      </TestWrapper>
    )

    const focusButton = screen.getByRole('button', { name: /focus/i })
    
    // 集中モードを有効にして通知を表示
    fireEvent.click(focusButton)
    
    await waitFor(() => {
      expect(screen.getByText('集中モードを開始しました')).toBeInTheDocument()
    })

    // 4秒後に通知が自動で消えることを確認
    await waitFor(() => {
      expect(screen.queryByText('集中モードを開始しました')).not.toBeInTheDocument()
    }, { timeout: 5000 })
  })
})