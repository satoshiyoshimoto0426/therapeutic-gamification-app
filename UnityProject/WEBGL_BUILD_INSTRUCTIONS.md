# WebGL ビルド手順書

「心の冒険者」Unity 3DローグライクのWebGLビルド手順を説明します。

## 📋 前提条件

- Unity 2022.3 LTS がインストール済み
- WebGL Build Support モジュールがインストール済み
- プロジェクトが正常に動作すること

## 🚀 ビルド手順

### ステップ1: プロジェクト設定の確認

#### 1.1 Player Settings

```
Edit > Project Settings > Player > WebGL タブ

【Company Name】
- Kokoro no Boukensha Team

【Product Name】
- 心の冒険者

【Default Icon】
- アイコン画像を設定（512x512推奨）

【Resolution and Presentation】
- Default Canvas Width: 1280
- Default Canvas Height: 720
- Run In Background: ✓

【Other Settings】
- Color Space: Gamma（軽量）
- Auto Graphics API: ✓
- Rendering Path: Forward
- Scripting Backend: IL2CPP

【Publishing Settings】
- Compression Format: Brotli（最高圧縮）
  または Gzip（互換性重視）
- Enable Decompression Fallback: ✓
- Name Files As Hashes: ✓
- Data Caching: ✓

【Memory Size】
- Memory Size: 512 MB
  （必要に応じて 256 MB〜2048 MB）

【Optimization】
- Managed Stripping Level: High
- Enable Exceptions: None（最軽量）
- IL2CPP Code Generation: Faster runtime
```

#### 1.2 Quality Settings

```
Edit > Project Settings > Quality

デフォルトレベル: Medium

【Medium Settings】
- Pixel Light Count: 2
- Texture Quality: Half Res
- Anisotropic Textures: Per Texture
- Anti Aliasing: 2x Multi Sampling
- Soft Particles: ✗
- Realtime Reflection Probes: ✗
- Billboards Face Camera Position: ✓
- Shadows: Hard Shadows Only
- Shadow Resolution: Medium Resolution
- Shadow Projection: Close Fit
- Shadow Distance: 50
- Shadow Near Plane Offset: 3
- Shadow Cascades: No Cascades
- Particle Raycast Budget: 256
- Async Upload Time Slice: 2 ms
- Async Upload Buffer Size: 16 MB
- Async Upload Persistent Buffer: ✓
```

#### 1.3 Graphics Settings

```
Edit > Project Settings > Graphics

- Scriptable Render Pipeline Settings: None（Built-in使用）
- Camera-Relative Culling: ✗
- Transparency Sort Mode: Default
- Transparency Sort Axis: (0, 0, 1)
```

### ステップ2: アセット最適化

#### 2.1 テクスチャ最適化（重要！）

```
全テクスチャを選択:
1. Project > Assets > Search: "t:Texture2D"
2. 全て選択
3. Inspector > Platform Settings > WebGL
   - Max Size: 1024（キャラ）/ 512（UI）
   - Compression: High Quality
   - Use Crunch Compression: ✓
   - Compressor Quality: 50
4. Apply
```

#### 2.2 オーディオ最適化

```
BGM:
- Load Type: Compressed In Memory
- Compression Format: Vorbis
- Quality: 70
- Sample Rate: 44100 Hz

SFX:
- Load Type: Decompress On Load
- Compression Format: Vorbis
- Quality: 100
- Sample Rate: 22050 Hz
```

#### 2.3 3Dモデル最適化

```
1. 全FBXモデルを選択
2. Model タブ:
   - Scale Factor: 1
   - Mesh Compression: High
   - Read/Write Enabled: ✗
   - Optimize Mesh: ✓
   - Generate Colliders: ✗（不要なら）
3. Rig タブ:
   - Animation Type: Humanoid（キャラ）/ None（オブジェクト）
   - Optimize Game Objects: ✓
4. Animation タブ:
   - Anim. Compression: Optimal
```

### ステップ3: ビルド実行

#### 3.1 Build Settings

```
File > Build Settings

1. Platform: WebGL を選択
2. "Switch Platform" をクリック（初回のみ）
3. Scenes In Build:
   - [0] TitleScene
   - [1] GameScene
   - [2] DungeonScene
   （必要なシーンを追加）
4. Compression Method: Brotli
5. Development Build: ✗（本番）
   Development Build: ✓（デバッグ時）
6. Autoconnect Profiler: ✗
7. Deep Profiling: ✗
8. Script Debugging: ✗
```

#### 3.2 ビルド実行

```
1. "Build" または "Build And Run" をクリック
2. 保存先フォルダを選択（例: WebGLBuild）
3. ビルド完了を待つ（5〜15分）
```

### ステップ4: ビルド後の確認

#### 4.1 ファイル構成確認

```
WebGLBuild/
├── Build/
│   ├── WebGLBuild.data.br
│   ├── WebGLBuild.framework.js.br
│   ├── WebGLBuild.loader.js
│   └── WebGLBuild.wasm.br
├── TemplateData/
│   ├── favicon.ico
│   ├── style.css
│   └── UnityProgress.js
└── index.html
```

#### 4.2 ローカルテスト

```
方法1: Unity Build And Run（推奨）
- Build Settings > "Build And Run"
- 自動でブラウザが開く

方法2: ローカルサーバー（Python）
cd WebGLBuild
python -m http.server 8000
# ブラウザで http://localhost:8000 を開く

方法3: ローカルサーバー（Node.js）
cd WebGLBuild
npx http-server -p 8000
# ブラウザで http://localhost:8000 を開く
```

#### 4.3 確認項目

- [ ] ゲームが正常に起動する
- [ ] ローディングが10秒以内に完了
- [ ] FPSが30以上（PC）/ 20以上（モバイル）
- [ ] BGM/SEが再生される
- [ ] 全機能が動作する
- [ ] ブラウザコンソールにエラーがない
- [ ] メモリリークがない（長時間プレイ）

### ステップ5: デプロイ

#### 5.1 GitHub Pages（無料）

```bash
# WebGLBuildフォルダをgh-pagesブランチにプッシュ
cd WebGLBuild
git init
git add .
git commit -m "Deploy WebGL build"
git branch -M gh-pages
git remote add origin https://github.com/yourusername/yourrepo.git
git push -u origin gh-pages -f
```

設定:
```
GitHub Repository > Settings > Pages
- Source: Deploy from a branch
- Branch: gh-pages / (root)
- Save
```

アクセス: `https://yourusername.github.io/yourrepo/`

#### 5.2 itch.io（無料・ゲーム配信サイト）

```
1. https://itch.io でアカウント作成
2. Dashboard > Create new project
3. Project名、説明、スクリーンショットを設定
4. Kind of project: HTML
5. Upload files: WebGLBuildフォルダ全体をZIP圧縮してアップロード
6. This file will be played in the browser: ✓
7. Embed options: 
   - Viewport dimensions: 1280 x 720
   - Fullscreen button: ✓
8. Save & view page
```

#### 5.3 Vercel（無料・高速）

```bash
# Vercelにデプロイ
npm install -g vercel
cd WebGLBuild
vercel --prod
```

---

## 🐛 トラブルシューティング

### Q: ビルドサイズが大きすぎる（>100MB）

**A**: 以下を確認
1. テクスチャ圧縮が有効か
2. Unused Assets を削除（Edit > Preferences > Asset Store）
3. Audio Compression が有効か
4. Code Stripping が High か
5. Compression Format が Brotli か

### Q: ロード時間が長い（>20秒）

**A**: 以下を試す
1. Memory Size を 256 MB に下げる
2. 非同期シーンロードを実装
3. アセットバンドルを使用
4. Preload Shaders をオフ

### Q: FPSが低い（<20）

**A**: 以下を確認
1. Quality Settings を Low に変更
2. Draw Calls を確認（Stats ウィンドウ）
3. Particle 数を削減
4. Shadows を Off に
5. ObjectPool を使用

### Q: 音が再生されない

**A**: WebGLではユーザー操作後に音声初期化が必要
```csharp
// AudioManager.cs
void Start()
{
    #if UNITY_WEBGL && !UNITY_EDITOR
    // WebGL用の初期化遅延
    StartCoroutine(InitAudioOnUserInteraction());
    #endif
}
```

### Q: ブラウザで動かない

**A**: 以下を確認
1. HTTPS でホスティングされているか（HTTP ではなく）
2. CORS エラーがないか（ブラウザコンソール確認）
3. ブラウザが WebGL 2.0 をサポートしているか
4. キャッシュをクリアして再読み込み

---

## 📊 ベンチマーク目標

| 項目 | 目標値 | 許容範囲 |
|------|--------|---------|
| **ビルドサイズ** | < 50 MB | < 80 MB |
| **初回ロード** | < 10秒 | < 15秒 |
| **FPS（PC）** | 60 FPS | 30+ FPS |
| **FPS（Mobile）** | 30 FPS | 20+ FPS |
| **メモリ使用** | < 200 MB | < 400 MB |
| **Draw Calls** | < 100 | < 200 |

---

## ✅ リリースチェックリスト

### ビルド前
- [ ] 全機能がPlayModeで動作
- [ ] テクスチャ最適化完了
- [ ] オーディオ最適化完了
- [ ] Player Settings 設定完了
- [ ] Quality Settings 設定完了
- [ ] 不要なアセット削除
- [ ] Development Build OFF

### ビルド後
- [ ] ビルド成功（エラーなし）
- [ ] ビルドサイズ確認
- [ ] ローカルテスト完了
- [ ] FPS 確認
- [ ] 全機能動作確認
- [ ] モバイルブラウザテスト
- [ ] メモリリークなし

### デプロイ後
- [ ] 本番URLでアクセス可能
- [ ] 複数ブラウザでテスト（Chrome, Firefox, Safari）
- [ ] パフォーマンス計測
- [ ] ユーザーフィードバック収集
- [ ] バグ報告受付体制確立

---

## 🔗 関連ドキュメント

- `WEBGL_OPTIMIZATION_GUIDE.md` - 詳細な最適化手順
- `FINAL_OPTIMIZATION_GUIDE.md` - 最終調整ガイド
- `README.md` - プロジェクト概要

---

**最終更新**: 2025-12-04  
**バージョン**: 1.0  
**プロジェクト**: 心の冒険者 - Unity 3Dローグライク
