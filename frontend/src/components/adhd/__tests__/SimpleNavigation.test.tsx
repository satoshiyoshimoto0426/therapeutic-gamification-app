import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import SimpleNavigation from '../SimpleNavigation'

const theme = createTheme()

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  </BrowserRouter>
)

// react-router-domのmock
const mockNavigate = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/dashboard' })
}))

describe('SimpleNavigation', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
  })

  test('最大3項目のナビゲーションを表示する', () => {
    render(
      <TestWrapper>
        <SimpleNavigation />
      </TestWrapper>
    )

    // 3つのナビゲーション項目が表示されることを確認
    expect(screen.getByText('ホーム')).toBeInTheDocument()
    expect(screen.getByText('タスク')).toBeInTheDocument()
    expect(screen.getByText('気分')).toBeInTheDocument()

    // 3つ以上の項目がないことを確認
    const buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(3)
  })

  test('水平レイアウトが正常に表示される', () => {
    render(
      <TestWrapper>
        <SimpleNavigation variant="horizontal" />
      </TestWrapper>
    )

    const buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(3)
    
    // 各ボタンがクリック可能であることを確認
    buttons.forEach(button => {
      expect(button).toBeEnabled()
    })
  })

  test('垂直レイアウトが正常に表示される', () => {
    render(
      <TestWrapper>
        <SimpleNavigation variant="vertical" />
      </TestWrapper>
    )

    const buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(3)
    
    // fullWidthプロパティが適用されていることを確認
    buttons.forEach(button => {
      const styles = window.getComputedStyle(button)
      expect(styles.width).toBe('100%')
    })
  })

  test('説明文が表示される', () => {
    render(
      <TestWrapper>
        <SimpleNavigation showDescriptions={true} />
      </TestWrapper>
    )

    expect(screen.getByText('メインダッシュボード')).toBeInTheDocument()
    expect(screen.getByText('今日のタスク管理')).toBeInTheDocument()
    expect(screen.getByText('気分の記録と追跡')).toBeInTheDocument()
  })

  test('集中モード時に説明文が非表示になる', () => {
    render(
      <TestWrapper>
        <SimpleNavigation showDescriptions={true} focusMode={true} />
      </TestWrapper>
    )

    expect(screen.queryByText('メインダッシュボード')).not.toBeInTheDocument()
    expect(screen.queryByText('今日のタスク管理')).not.toBeInTheDocument()
    expect(screen.queryByText('気分の記録と追跡')).not.toBeInTheDocument()
  })

  test('ナビゲーションクリックが正常に動作する', () => {
    render(
      <TestWrapper>
        <SimpleNavigation />
      </TestWrapper>
    )

    const taskButton = screen.getByText('タスク')
    fireEvent.click(taskButton)

    expect(mockNavigate).toHaveBeenCalledWith('/tasks')
  })

  test('現在のページがアクティブ状態で表示される', () => {
    // useLocationのmockを更新
    jest.doMock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate,
      useLocation: () => ({ pathname: '/tasks' })
    }))

    render(
      <TestWrapper>
        <SimpleNavigation />
      </TestWrapper>
    )

    const taskButton = screen.getByText('タスク')
    
    // アクティブ状態のスタイルが適用されていることを確認
    expect(taskButton.closest('button')).toHaveStyle({
      backgroundColor: expect.stringContaining('#FFC857')
    })
  })

  test('44px以上のタッチターゲットサイズを確保している', () => {
    render(
      <TestWrapper>
        <SimpleNavigation />
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
        <SimpleNavigation />
      </TestWrapper>
    )

    const homeButton = screen.getByText('ホーム')
    const styles = window.getComputedStyle(homeButton)
    
    expect(styles.fontFamily).toContain('BIZ UDGothic')
  })

  test('集中モード時にスタイルが変更される', () => {
    render(
      <TestWrapper>
        <SimpleNavigation focusMode={true} />
      </TestWrapper>
    )

    const container = screen.getByText('ホーム').closest('[role="button"]')?.parentElement?.parentElement
    
    // 集中モード時の透明な背景が適用されていることを確認
    expect(container).toHaveStyle({
      backgroundColor: 'transparent'
    })
  })

  test('アイコンが正しく表示される', () => {
    render(
      <TestWrapper>
        <SimpleNavigation />
      </TestWrapper>
    )

    // SVGアイコンが存在することを確認
    const icons = document.querySelectorAll('svg')
    expect(icons.length).toBeGreaterThanOrEqual(3)
  })

  test('色分けが正しく適用される', () => {
    render(
      <TestWrapper>
        <SimpleNavigation />
      </TestWrapper>
    )

    const homeButton = screen.getByText('ホーム').closest('button')
    const taskButton = screen.getByText('タスク').closest('button')
    const moodButton = screen.getByText('気分').closest('button')

    // 各ボタンに異なる色が適用されていることを確認
    expect(homeButton).toHaveStyle({ borderColor: '#2E3A59' })
    expect(taskButton).toHaveStyle({ borderColor: '#FFC857' })
    expect(moodButton).toHaveStyle({ borderColor: '#4ECDC4' })
  })
})