import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import FocusMode from '../FocusMode'

const theme = createTheme()

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
)

describe('FocusMode', () => {
  const mockOnToggle = jest.fn()
  const mockCurrentTask = {
    title: 'テストタスク',
    progress: 65,
    timeRemaining: 1500 // 25分
  }

  beforeEach(() => {
    mockOnToggle.mockClear()
  })

  test('集中モードの切り替えが正常に動作する', () => {
    render(
      <TestWrapper>
        <FocusMode isActive={false} onToggle={mockOnToggle} />
      </TestWrapper>
    )

    const toggleSwitch = screen.getByRole('checkbox')
    fireEvent.click(toggleSwitch)

    expect(mockOnToggle).toHaveBeenCalledWith(true)
  })

  test('集中モードがアクティブ時に適切な表示になる', () => {
    render(
      <TestWrapper>
        <FocusMode 
          isActive={true} 
          onToggle={mockOnToggle}
          currentTask={mockCurrentTask}
        />
      </TestWrapper>
    )

    // 集中モードのタイトルが強調表示されることを確認
    const title = screen.getByText('集中モード')
    expect(title).toHaveStyle({ color: theme.palette.primary.main })

    // タイマーが表示されることを確認
    expect(screen.getByText(/\d+:\d+/)).toBeInTheDocument()
  })

  test('現在のタスクが正しく表示される', () => {
    render(
      <TestWrapper>
        <FocusMode 
          isActive={true} 
          onToggle={mockOnToggle}
          currentTask={mockCurrentTask}
        />
      </TestWrapper>
    )

    expect(screen.getByText('テストタスク')).toBeInTheDocument()
    expect(screen.getByText('65%')).toBeInTheDocument()
    expect(screen.getByText(/残り時間: 25:00/)).toBeInTheDocument()
  })

  test('集中時間のカウントが正常に動作する', async () => {
    render(
      <TestWrapper>
        <FocusMode isActive={true} onToggle={mockOnToggle} />
      </TestWrapper>
    )

    // 初期状態では0:00
    expect(screen.getByText('0:00')).toBeInTheDocument()

    // 1秒後に0:01になることを確認
    await waitFor(() => {
      expect(screen.getByText('0:01')).toBeInTheDocument()
    }, { timeout: 1500 })
  })

  test('気を散らす要素の検出と警告表示', async () => {
    render(
      <TestWrapper>
        <FocusMode 
          isActive={true} 
          onToggle={mockOnToggle}
          distractionLevel="high"
        />
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByText(/気を散らす要素が検出されました/)).toBeInTheDocument()
    })

    // 5秒後に警告が消えることを確認
    await waitFor(() => {
      expect(screen.queryByText(/気を散らす要素が検出されました/)).not.toBeInTheDocument()
    }, { timeout: 6000 })
  })

  test('集中状態インジケーターが正しく表示される', () => {
    const { rerender } = render(
      <TestWrapper>
        <FocusMode 
          isActive={true} 
          onToggle={mockOnToggle}
          distractionLevel="low"
        />
      </TestWrapper>
    )

    expect(screen.getByText('集中中')).toBeInTheDocument()

    rerender(
      <TestWrapper>
        <FocusMode 
          isActive={true} 
          onToggle={mockOnToggle}
          distractionLevel="high"
        />
      </TestWrapper>
    )

    expect(screen.getByText('注意散漫')).toBeInTheDocument()
  })

  test('設定オプションが正常に動作する', () => {
    render(
      <TestWrapper>
        <FocusMode isActive={true} onToggle={mockOnToggle} />
      </TestWrapper>
    )

    const hideDistractionsSwitch = screen.getByLabelText('気を散らす要素を非表示')
    const showProgressSwitch = screen.getByLabelText('プログレス表示')

    expect(hideDistractionsSwitch).toBeInTheDocument()
    expect(showProgressSwitch).toBeInTheDocument()

    // スイッチの切り替えが可能であることを確認
    fireEvent.click(hideDistractionsSwitch)
    fireEvent.click(showProgressSwitch)
  })

  test('集中のヒントが表示される', () => {
    render(
      <TestWrapper>
        <FocusMode isActive={true} onToggle={mockOnToggle} />
      </TestWrapper>
    )

    expect(screen.getByText(/集中のコツ/)).toBeInTheDocument()
    expect(screen.getByText(/25分間隔で休憩/)).toBeInTheDocument()
  })

  test('非アクティブ時は詳細情報が非表示になる', () => {
    render(
      <TestWrapper>
        <FocusMode isActive={false} onToggle={mockOnToggle} />
      </TestWrapper>
    )

    expect(screen.queryByText('現在のタスク')).not.toBeInTheDocument()
    expect(screen.queryByText('集中状態')).not.toBeInTheDocument()
    expect(screen.queryByText('気を散らす要素を非表示')).not.toBeInTheDocument()
  })

  test('プログレスバーが正しく表示される', () => {
    render(
      <TestWrapper>
        <FocusMode 
          isActive={true} 
          onToggle={mockOnToggle}
          currentTask={mockCurrentTask}
        />
      </TestWrapper>
    )

    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toBeInTheDocument()
    expect(progressBar).toHaveAttribute('aria-valuenow', '65')
  })

  test('BIZ UDGothicフォントが適用されている', () => {
    render(
      <TestWrapper>
        <FocusMode isActive={true} onToggle={mockOnToggle} />
      </TestWrapper>
    )

    const title = screen.getByText('集中モード')
    const styles = window.getComputedStyle(title)
    
    expect(styles.fontFamily).toContain('BIZ UDGothic')
  })

  test('時間フォーマットが正しく動作する', () => {
    render(
      <TestWrapper>
        <FocusMode 
          isActive={true} 
          onToggle={mockOnToggle}
          currentTask={{
            ...mockCurrentTask,
            timeRemaining: 3661 // 1時間1分1秒
          }}
        />
      </TestWrapper>
    )

    expect(screen.getByText(/残り時間: 61:01/)).toBeInTheDocument()
  })

  test('集中モード時のスタイル変更が適用される', () => {
    render(
      <TestWrapper>
        <FocusMode isActive={true} onToggle={mockOnToggle} />
      </TestWrapper>
    )

    const container = screen.getByText('集中モード').closest('[role="button"]')?.parentElement
    
    // 集中モード時のボーダーが適用されていることを確認
    expect(container).toHaveStyle({
      border: `2px solid ${theme.palette.primary.main}`
    })
  })
})