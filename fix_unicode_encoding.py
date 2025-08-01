#!/usr/bin/env python3
"""
UNICODE文字エンコーディング問題修正スクリプト
[UNICODE_XXXX] 形式の文字を適切な日本語文字に変換
"""

import os
import re
import glob
from typing import Dict, List

# UNICODE文字マッピング（よく使われるもの）
UNICODE_MAPPING = {
    # コメント・説明系
    'コア': 'コア',
    'アプリ': 'アプリ',
    'ログ': 'ログ',
    '設定': '設定',
    '共有': '共有',
    'プレビュー': 'プレイヤー',
    'ユーザー': 'ユーザー',
    'レベル': 'レベル',
    'システム': 'システム',
    'ゲーム': 'ゲーム',
    'エラー': 'エラー',
    'ヘルパー': 'ヘルパー',
    'タスク': 'タスク',
    '気分': '気分',
    'バリデーション': 'バリデーション',
    'デフォルト': 'デフォルト',
    '係数': '係数',
    '支援': '支援',
    '基本': '基本',
    '計算': '計算',
    'プレビュー': 'プレビュー',
    '入力': '入力',
    '内部': '内部',
    '一般': '一般',
    '起動': '起動',
    '管理': '管理',
    'モデル': 'モデル',
    '治療': '治療',
    '自動': '自動',
    'カスタム': 'カスタム',
    '文字': '文字',
    'ストーリー': 'ストーリー',
    '物語': '物語',
    '総合': '総合',
    '安全': '安全',
    '検証': '検証',
    '信頼': '信頼',
    'リスト': 'リスト',
    'ビジネス': 'ビジネス',
    '実装': '実装',
    'こ': 'この',
    'メイン': 'メイン',
    '使用': '使用',
    'システム': 'システム',
    '準拠': '準拠',
    
    # 日本語の基本文字
    '死': '死',
    '消': '消',
    'い': 'い',
    '傷': '傷',
    'だ': 'だ',
    'も': 'も',
    '限': '限',
    '耐': '耐',
    '終': '終',
    '誰': '誰',
    'み': 'み',
    '嫌': '嫌',
    '憎': '憎',
    '許': '許',
    '価': '価',
    '意': '意',
    '無': '無',
    '成': '成',
    '希': '希',
    'つ': 'つ',
    '理': '理',
    '勇': '勇',
    '挑': '挑',
    '学': '学',
    '発': '発',
    '創': '創',
    '表': '表',
    
    # その他よく使われる文字
    'で': 'で',
    'か': 'か',
    'の': 'の',
    'を': 'を',
    'に': 'に',
    'が': 'が',
    'と': 'と',
    'し': 'し',
    'て': 'て',
    'す': 'す',
    'る': 'る',
    'ん': 'ん',
    'あ': 'あ',
    'え': 'え',
    'お': 'お',
    'き': 'き',
    'く': 'く',
    'け': 'け',
    'こ': 'こ',
    'さ': 'さ',
    'た': 'た',
    'な': 'な',
    'は': 'は',
    'ま': 'ま',
    'や': 'や',
    'ら': 'ら',
    'わ': 'わ',
}

def find_files_with_unicode_issues(directory: str = ".") -> List[str]:
    """UNICODE文字を含むファイルを検索"""
    files_with_issues = []
    
    # Python ファイルを検索
    for pattern in ["**/*.py", "**/*.md", "**/*.txt"]:
        for file_path in glob.glob(os.path.join(directory, pattern), recursive=True):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '[UNICODE_' in content:
                        files_with_issues.append(file_path)
            except Exception as e:
                print(f"⚠️ ファイル読み込みエラー {file_path}: {e}")
    
    return files_with_issues

def fix_unicode_in_file(file_path: str) -> bool:
    """ファイル内のUNICODE文字を修正"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # UNICODE文字を置換
        for unicode_char, replacement in UNICODE_MAPPING.items():
            content = content.replace(unicode_char, replacement)
        
        # 未知のUNICODE文字を検出
        unknown_unicode = re.findall(r'\[UNICODE_[A-F0-9]+\]', content)
        if unknown_unicode:
            print(f"⚠️ 未知のUNICODE文字が見つかりました in {file_path}: {set(unknown_unicode)}")
            # 未知の文字は削除または適切な文字に置換
            for unknown in set(unknown_unicode):
                content = content.replace(unknown, '?')  # プレースホルダー
        
        # 変更があった場合のみファイルを更新
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ ファイル修正エラー {file_path}: {e}")
        return False

def create_backup(file_path: str):
    """ファイルのバックアップを作成"""
    backup_path = file_path + '.backup'
    try:
        with open(file_path, 'r', encoding='utf-8') as original:
            with open(backup_path, 'w', encoding='utf-8') as backup:
                backup.write(original.read())
        print(f"📋 バックアップ作成: {backup_path}")
    except Exception as e:
        print(f"⚠️ バックアップ作成失敗 {file_path}: {e}")

def main():
    print("🔧 UNICODE文字エンコーディング問題修正開始")
    print("="*50)
    
    # 問題のあるファイルを検索
    print("🔍 UNICODE文字を含むファイルを検索中...")
    problem_files = find_files_with_unicode_issues()
    
    if not problem_files:
        print("✅ UNICODE文字の問題は見つかりませんでした")
        return
    
    print(f"📋 {len(problem_files)} 個のファイルに問題が見つかりました:")
    for file_path in problem_files[:10]:  # 最初の10個を表示
        print(f"  - {file_path}")
    
    if len(problem_files) > 10:
        print(f"  ... および {len(problem_files) - 10} 個の追加ファイル")
    
    # 修正実行の確認
    response = input("\n🤔 これらのファイルを修正しますか？ (y/N): ")
    if response.lower() != 'y':
        print("❌ 修正をキャンセルしました")
        return
    
    # ファイルを修正
    print("\n🔧 ファイル修正中...")
    fixed_count = 0
    
    for file_path in problem_files:
        print(f"📝 修正中: {file_path}")
        
        # バックアップ作成
        create_backup(file_path)
        
        # 修正実行
        if fix_unicode_in_file(file_path):
            fixed_count += 1
            print(f"✅ 修正完了: {file_path}")
        else:
            print(f"⚠️ 変更なし: {file_path}")
    
    print(f"\n🎉 修正完了: {fixed_count}/{len(problem_files)} ファイル")
    
    # 検証
    print("\n🔍 修正結果を検証中...")
    remaining_issues = find_files_with_unicode_issues()
    
    if remaining_issues:
        print(f"⚠️ まだ {len(remaining_issues)} 個のファイルに問題があります")
        for file_path in remaining_issues[:5]:
            print(f"  - {file_path}")
    else:
        print("✅ すべてのUNICODE文字問題が解決されました！")
    
    print("\n💡 次のステップ:")
    print("1. 修正されたファイルの動作確認")
    print("2. バックアップファイル（*.backup）の削除")
    print("3. サービスの起動テスト")

if __name__ == "__main__":
    main()