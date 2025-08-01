import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import AutoSaveProgress from '../AutoSaveProgress'

const theme = createTheme()

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
)

describe('AutoSaveProgress', () => {
  const mockOnManualSave = jest.fn()
  const mockOnRetry = jest.fn()

  beforeEach(() => {
    mockOnManualSave.mockClear()
    mockOnRetry.mockClear()
  })

  test('プログレス情報が正しく表示される', () => {
    render(
      <TestWrapper>
        <AutoSaveProgress
          currentProgress={75}
          totalTasks={8}
          completedTasks={6}
        />
      </TestWrapper>
    )

    expect(screen.getByText('6/8 タスク (75%)')).toBeInTheDocument()
    expect(screen.getByText('進捗状況')).toBeInTheDocument()
  })

  test('自動保存が有効な場合の表示', () => {
    render(
      <TestWrapper>
        <AutoSaveProgress
          autoSaveEnabled={true}
          saveInterval={30}
        />
      </TestWrapper>
    )

    expect(screen.getByText('自動保存')).toBeInTheDocument()
  })

  test('手動保存ボタンが正常に動作する', async () => {
    render(
      <TestWrapper>
        <AutoSaveProgress onManualSave={mockOnManualSave} />
      </TestWrapper>
    )

    // 詳細を表示
    const infoButton = screen.getByLabelText('詳細を表示')
    fireEvent.click(infoButton)

    await waitFor(() => {
      const saveButton = screen.getByLabelText('今すぐ保存')
      fireEvent.click(saveButton)
      expect(mockOnManualSave).toHaveBeenCalled()
    })
  })

  test('自動保存のカウントダウンが表示される', async () => {
    render(
      <TestWrapper>
        <AutoSaveProgress
          autoSaveEnabled={true}
          saveInterval={5}
        />
      </TestWrapper>
    )

    // 詳細を表示
    const infoButton = screen.getByLabelText('詳細を表示')
    fireEvent.click(infoButton)

    await waitFor(() => {
      expect(screen.getByText(/\d+秒後/)).toBeInTheDocument()
    })
  })

  test('保存状態の変化が正しく表示される', async () => {
    render(
      <TestWrapper>
        <AutoSaveProgress saveInterval={2} />
      </TestWrapper>
    )

    // 2秒後に自動保存が開始されることを確認
    await waitFor(() => {
      expect(screen.getByText('保存中...')).toBeInTheDocument()
    }, { timeout: 3000 })

    // 保存完了状態になることを確認
    await waitFor(() => {
      expect(screen.getByText('保存完了')).toBeInTheDocument()
    }, { timeout: 2000 })
  })

  test('エラー状態とリトライ機能', async () => {
    // Math.randomをモックしてエラーを発生させる
    const originalRandom = Math.random
    Math.random = jest.fn(() => 0.05) // 10%未満でエラー発生

    render(
      <TestWrapper>
        <AutoSaveProgress 
          saveInterval={1}
          onRetry={mockOnRetry}
        />
      </TestWrapper>
    )

    // エラーが発生することを確認
    await waitFor(() => {
      expect(screen.getByText('保存失敗')).toBeInTheDocument()
    }, { timeout: 3000 })

    // リトライボタンが表示されることを確認
    await waitFor(() => {
      const retryButton = screen.getByLabelText('再試行')
      expect(retryButton).toBeInTheDocument()
      fireEvent.click(retryButton)
      expect(mockOnRetry).toHaveBeenCalled()
    })

    // Math.randomを元に戻す
    Math.random = originalRandom
  })

  test('最終保存時刻の表示', async () => {
    render(
      <TestWrapper>
        <AutoSaveProgress saveInterval={1} />
      </TestWrapper>
    )

    // 詳細を表示
    const infoButton = screen.getByLabelText('詳細を表示')
    fireEvent.click(infoButton)

    // 初期状態では未保存
    expect(screen.getByText('未保存')).toBeInTheDocument()

    // 保存後に時刻が表示されることを確認
    await waitFor(() => {
      expect(screen.getByText(/\d+秒前|\d+:\d+/)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  test('プログレスバーが正しく動作する', () => {
    render(
      <TestWrapper>
        <AutoSaveProgress currentProgress={60} />
      </TestWrapper>
    )

    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toBeInTheDocument()
    expect(progressBar).toHaveAttribute('aria-valuenow', '60')
  })

  test('ADHD配慮のヒントが表示される', () => {
    render(
      <TestWrapper>
        <AutoSaveProgress currentProgress={50} />
      </TestWrapper>
    )

    expect(screen.getByText(/進捗は自動的に保存されます/)).toBeInTheDocument()
    expect(screen.getByText(/一つずつタスクに集中しましょう/)).toBeInTheDocument()
  })

  test('完了時にヒントが非表示になる', () => {
    render(
      <TestWrapper>
        <AutoSaveProgress currentProgress={100} />
      </TestWrapper>
    )

    expect(screen.queryByText(/進捗は自動的に保存されます/)).not.toBeInTheDocument()
  })

  test('詳細情報の表示・非表示切り替え', () => {
    render(
      <TestWrapper>
        <AutoSaveProgress />
      </TestWrapper>
    )

    const infoButton = screen.getByLabelText('詳細を表示')
    
    // 初期状態では詳細は非表示
    expect(screen.queryByText('最終保存')).not.toBeInTheDocument()

    // クリックで詳細を表示
    fireEvent.click(infoButton)
    expect(screen.getByText('最終保存')).toBeInTheDocument()

    // 再度クリックで非表示
    fireEvent.click(infoButton)
    expect(screen.queryByText('最終保存')).not.toBeInTheDocument()
  })

  test('BIZ UDGothicフォントが適用されている', () => {
    render(
      <TestWrapper>
        <AutoSaveProgress />
      </TestWrapper>
    )

    const title = screen.getByText('進捗状況')
    const styles = window.getComputedStyle(title)
    
    expect(styles.fontFamily).toContain('BIZ UDGothic')
  })

  test('保存状態に応じた色分けが正しく適用される', async () => {
    render(
      <TestWrapper>
        <AutoSaveProgress saveInterval={1} />
      </TestWrapper>
    )

    // 保存中の色
    await waitFor(() => {
      const savingChip = screen.getByText('保存中...')
      expect(savingChip.closest('.MuiChip-root')).toHaveStyle({
        backgroundColor: '#FFC85720'
      })
    }, { timeout: 2000 })

    // 保存完了の色
    await waitFor(() => {
      const savedChip = screen.getByText('保存完了')
      expect(savedChip.closest('.MuiChip-root')).toHaveStyle({
        backgroundColor: '#4ECDC420'
      })
    }, { timeout: 2000 })
  })

  test('自動保存無効時の動作', () => {
    render(
      <TestWrapper>
        <AutoSaveProgress autoSaveEnabled={false} />
      </TestWrapper>
    )

    // 詳細を表示
    const infoButton = screen.getByLabelText('詳細を表示')
    fireEvent.click(infoButton)

    // 次回自動保存の表示がないことを確認
    expect(screen.queryByText(/次回自動保存/)).not.toBeInTheDocument()
  })
})