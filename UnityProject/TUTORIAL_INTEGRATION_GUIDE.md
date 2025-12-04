# チュートリアルシステム統合ガイド

「心の冒険者」Unity 3Dローグライクゲームのチュートリアルシステム統合手順

## 📋 目次

1. [概要](#概要)
2. [実装済みコンポーネント](#実装済みコンポーネント)
3. [既存スクリプトへの統合](#既存スクリプトへの統合)
4. [UIセットアップ](#uiセットアップ)
5. [テスト方法](#テスト方法)

---

## 概要

チュートリアルシステムは、プレイヤーにゲームの基本操作を段階的に教えるシステムです。

### 主要機能

- ✅ 17ステップのインタラクティブチュートリアル
- ✅ UI要素のハイライト表示
- ✅ ワールド/UIオブジェクトへのポインター表示
- ✅ タイプライターテキスト表示
- ✅ スキップ機能
- ✅ 進行状況の保存/ロード
- ✅ 完了報酬システム

---

## 実装済みコンポーネント

### 1. TutorialManager.cs (18,190 bytes)
チュートリアルの中核システム

**機能**:
- 17ステップのチュートリアルフロー
- ステップ進行管理
- アクション検知
- 進行状況保存/ロード
- 完了報酬付与

### 2. TutorialUI.cs (7,942 bytes)
チュートリアルUI表示システム

**機能**:
- ステップ情報表示
- タイプライターエフェクト
- フェードイン/アウト
- 次へ/スキップボタン

### 3. TutorialHighlight.cs (5,050 bytes)
UI要素ハイライトシステム

**機能**:
- UI要素を強調表示
- パルスアニメーション
- 半透明オーバーレイ

### 4. TutorialPointer.cs (5,995 bytes)
ポインター表示システム

**機能**:
- 3D/UIオブジェクトを指し示す
- バウンスアニメーション
- ワールド座標追従

### 5. TutorialTrigger.cs (3,636 bytes)
アクション検知トリガー

**機能**:
- プレイヤーアクションを検知
- TutorialManagerに通知

---

## 既存スクリプトへの統合

### 1. Player.cs への統合

`Player.cs` の各アクションメソッドにトリガー呼び出しを追加します。

#### 移動検知

```csharp
// Player.cs の Move() メソッド内に追加

public void Move(Vector2Int direction)
{
    // 既存の移動処理...
    
    // チュートリアルトリガー
    if (direction != Vector2Int.zero)
    {
        Tutorial.TutorialTrigger.NotifyMove();
        
        // 斜め移動の場合
        if (Mathf.Abs(direction.x) == 1 && Mathf.Abs(direction.y) == 1)
        {
            Tutorial.TutorialTrigger.NotifyMoveDiagonal();
        }
    }
}
```

#### 攻撃検知

```csharp
// Player.cs の Attack() メソッド内に追加

public void Attack(Enemy enemy)
{
    // 既存の攻撃処理...
    
    // チュートリアルトリガー
    Tutorial.TutorialTrigger.NotifyAttack();
}
```

#### アイテム拾得検知

```csharp
// Player.cs の PickupItem() メソッド内に追加

public void PickupItem(Item item)
{
    // 既存のアイテム取得処理...
    
    // チュートリアルトリガー
    Tutorial.TutorialTrigger.NotifyPickupItem();
}
```

### 2. InventoryUI.cs への統合

#### インベントリ開く検知

```csharp
// InventoryUI.cs の Show() メソッド内に追加

public void Show()
{
    // 既存のUI表示処理...
    
    // チュートリアルトリガー
    Tutorial.TutorialTrigger.NotifyOpenInventory();
}
```

#### アイテム使用検知

```csharp
// InventoryUI.cs の UseItem() メソッド内に追加

private void UseItem(Item item)
{
    // 既存のアイテム使用処理...
    
    // チュートリアルトリガー
    Tutorial.TutorialTrigger.NotifyUseItem();
}
```

### 3. EquipmentManager.cs への統合

#### 装備変更検知

```csharp
// EquipmentManager.cs の EquipItem() メソッド内に追加

public void EquipItem(Equipment equipment)
{
    // 既存の装備処理...
    
    // チュートリアルトリガー
    Tutorial.TutorialTrigger.NotifyEquipItem();
}
```

### 4. GachaUI.cs への統合

#### ガチャ画面開く検知

```csharp
// GachaUI.cs の ShowGachaScreen() メソッド内に追加

public void ShowGachaScreen()
{
    // 既存のUI表示処理...
    
    // チュートリアルトリガー
    Tutorial.TutorialTrigger.NotifyOpenGacha();
}
```

### 5. Enemy.cs への統合

#### 敵撃破検知

```csharp
// Enemy.cs の Die() メソッド内に追加

public void Die()
{
    // 既存の死亡処理...
    
    // チュートリアルトリガー
    Tutorial.TutorialTrigger.NotifyDefeatEnemy();
}
```

### 6. DungeonGenerator.cs への統合

#### 階段発見検知

```csharp
// Player.cs で階段に到達した時

private void OnTriggerEnter(Collider other)
{
    if (other.CompareTag("Stairs"))
    {
        // 既存の階段処理...
        
        // チュートリアルトリガー
        Tutorial.TutorialTrigger.NotifyFindStairs();
    }
}
```

---

## UIセットアップ

### 1. Canvas階層構造

```
Canvas
├── TutorialSystem (GameObject)
│   ├── TutorialManager (TutorialManager.cs)
│   ├── TutorialPanel (UI Panel)
│   │   ├── Background (Image - 半透明黒)
│   │   ├── ContentPanel (Panel)
│   │   │   ├── CharacterIcon (Image)
│   │   │   ├── TitleText (TextMeshProUGUI)
│   │   │   ├── DescriptionText (TextMeshProUGUI)
│   │   │   ├── ProgressText (TextMeshProUGUI)
│   │   │   └── ButtonGroup (Horizontal Layout Group)
│   │   │       ├── NextButton (Button)
│   │   │       ├── SkipButton (Button)
│   │   │       └── CloseButton (Button)
│   ├── HighlightSystem (GameObject)
│   │   ├── HighlightOverlay (Image - 全画面)
│   │   └── HighlightFrame (Image - 枠線)
│   └── PointerSystem (GameObject)
│       └── PointerIcon (Image - 矢印)
```

### 2. TutorialPanel設定

#### 推奨設定

**TutorialPanel (Panel)**
- Anchor: Center
- Width: 800
- Height: 400
- Position: (0, 0, 0)

**Background (Image)**
- Color: (0, 0, 0, 200) - 半透明黒
- Material: UI/Default

**ContentPanel (Panel)**
- Padding: 20px
- Background: White or Light Gray

**TitleText (TextMeshProUGUI)**
- Font Size: 32
- Font Style: Bold
- Color: Black or Dark Blue
- Alignment: Center

**DescriptionText (TextMeshProUGUI)**
- Font Size: 20
- Color: Dark Gray
- Alignment: Left
- Auto Size: ✗
- Word Wrapping: ✓

**ProgressText (TextMeshProUGUI)**
- Font Size: 16
- Color: Gray
- Alignment: Right

**Buttons (Button)**
- Width: 150
- Height: 50
- Font Size: 18

### 3. HighlightSystem設定

**HighlightOverlay (Image)**
- Anchor: Stretch (全画面)
- Color: (0, 0, 0, 180) - 半透明黒
- Raycast Target: ✗

**HighlightFrame (Image)**
- Sprite: UI/Skin/UISprite (or custom frame sprite)
- Color: (255, 255, 0, 128) - 半透明黄色
- Image Type: Sliced
- Width/Height: Dynamic (ターゲットに合わせる)

### 4. PointerSystem設定

**PointerIcon (Image)**
- Sprite: 矢印画像（下向き）
- Color: (255, 255, 0, 255) - 黄色
- Width: 64
- Height: 64
- Pivot: (0.5, 1.0) - 上中央

### 5. TutorialManagerコンポーネント設定

Inspectorで以下を設定:

```
Tutorial Manager (Script)
├─ Tutorial Settings
│  ├─ Tutorial Enabled: ✓
│  ├─ Auto Start Tutorial: ✓
│  └─ Allow Skip: ✓
├─ UI References
│  ├─ Tutorial UI: TutorialPanel (TutorialUI.cs)
│  ├─ Highlight System: HighlightSystem (TutorialHighlight.cs)
│  └─ Pointer System: PointerSystem (TutorialPointer.cs)
└─ Tutorial Steps: (自動生成済み)
```

---

## セットアップ手順

### Step 1: UIプレハブ作成

1. Canvas作成（既にある場合はスキップ）
2. 上記の階層構造でGameObject/UI要素を作成
3. 各コンポーネントをアタッチ
4. Inspector で参照を設定

### Step 2: ハイライトターゲット登録

```csharp
// GameManager.cs の Start() 内など、初期化時に実行

void RegisterTutorialTargets()
{
    TutorialHighlight highlight = TutorialManager.Instance.highlightSystem;
    
    if (highlight != null)
    {
        // HUD要素
        highlight.RegisterTarget("HUD", hudPanel.GetComponent<RectTransform>());
        highlight.RegisterTarget("HungerBar", hungerBar.GetComponent<RectTransform>());
        
        // インベントリ
        highlight.RegisterTarget("InventoryButton", inventoryButton.GetComponent<RectTransform>());
        highlight.RegisterTarget("InventorySlot", inventorySlot.GetComponent<RectTransform>());
        
        // ガチャ
        highlight.RegisterTarget("GachaButton", gachaButton.GetComponent<RectTransform>());
    }
}
```

### Step 3: トリガー統合

上記「既存スクリプトへの統合」セクションの手順に従って、各スクリプトにトリガー呼び出しを追加。

### Step 4: テスト

1. Play ボタンを押す
2. チュートリアルが自動的に開始されることを確認
3. 各ステップの指示に従ってアクションを実行
4. ハイライト・ポインターが正しく表示されることを確認

---

## トラブルシューティング

### Q: チュートリアルが表示されない

**A**: 以下を確認:
1. TutorialManager.tutorialEnabled が true
2. TutorialManager.autoStartTutorial が true
3. PlayerPrefs で TutorialCompleted が 0 (未完了)

### Q: ハイライトが表示されない

**A**: 
1. HighlightSystem の highlightTargets にターゲットが登録されているか確認
2. ターゲットの RectTransform が null でないか確認
3. Canvas の Render Mode を確認

### Q: ポインターが追従しない

**A**:
1. Main Camera が正しく設定されているか確認
2. Canvas の Render Mode が Screen Space - Overlay または Camera の場合、適切に設定されているか確認

### Q: トリガーが発火しない

**A**:
1. TutorialTrigger.Notify***() が正しく呼ばれているか Debug.Log で確認
2. TutorialManager.IsTutorialActive が true か確認
3. 現在のステップの requiredAction が正しいか確認

---

## デバッグ用コマンド

### チュートリアルリセット

```csharp
// コンソールまたはデバッグボタンから実行
TutorialManager.Instance.ResetTutorial();
```

### 特定ステップへジャンプ

```csharp
// TutorialManager.cs に追加（デバッグ用）
public void JumpToStep(int stepIndex)
{
    currentStepIndex = stepIndex;
    ShowCurrentStep();
}
```

### 現在の状態を確認

```csharp
Debug.Log($"Tutorial Active: {TutorialManager.Instance.IsTutorialActive}");
Debug.Log($"Tutorial Completed: {TutorialManager.Instance.IsTutorialCompleted}");
Debug.Log($"Current Step: {TutorialManager.Instance.CurrentStepIndex}");
```

---

## カスタマイズ

### 新しいステップを追加

```csharp
// TutorialManager.cs の InitializeTutorialSteps() 内に追加

tutorialSteps.Add(new TutorialStep
{
    stepId = "custom_step",
    title = "カスタムステップ",
    description = "ここに説明を記述",
    stepType = TutorialStepType.Action,
    requiredAction = TutorialAction.CustomAction, // 新しいActionを定義
    highlightUI = "CustomUIElement",
    showPointer = true,
    pointerTarget = "CustomTarget"
});
```

### 新しいアクションタイプを追加

```csharp
// TutorialManager.cs の TutorialAction enum に追加

public enum TutorialAction
{
    // ... 既存のアクション
    CustomAction  // 新しいアクション
}

// TutorialTrigger.cs に対応するメソッドを追加

public static void NotifyCustomAction()
{
    if (TutorialManager.Instance != null && TutorialManager.Instance.IsTutorialActive)
    {
        TutorialManager.Instance.OnActionPerformed(TutorialAction.CustomAction);
    }
}
```

---

## 次のステップ

1. ✅ チュートリアルシステム実装完了
2. ⏳ UIデザインのブラッシュアップ
3. ⏳ 多言語対応（日本語・英語）
4. ⏳ アニメーションの追加
5. ⏳ サウンドエフェクト追加

---

**作成日**: 2025-12-04  
**バージョン**: 1.0  
**関連スクリプト**:
- `TutorialManager.cs`
- `TutorialUI.cs`
- `TutorialHighlight.cs`
- `TutorialPointer.cs`
- `TutorialTrigger.cs`
