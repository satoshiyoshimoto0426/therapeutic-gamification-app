#!/usr/bin/env python3
"""
Unicode文字エンコーディング問題の簡単修正

Windows環境でcp932エンコーディングエラーが発生している問題を修正
絵文字のみを置換し、日本語は保持する
"""

import os
import re
import glob
from typing import List, Tuple

class SimpleUnicodeEncodingFixer:
    """シンプルなUnicode文字エンコーディング修正クラス"""
    
    def __init__(self):
        # 絵文字のみを置換（日本語は保持）
        self.emoji_replacements = {
            '✓': '[OK]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '✗': '[FAIL]',
            '🚀': '[ROCKET]',
            '🧪': '[TEST]',
            '🎉': '[PARTY]',
            '📊': '[CHART]',
            '📋': '[CLIPBOARD]',
            '💡': '[BULB]',
            '🔧': '[WRENCH]',
            '🔍': '[SEARCH]',
            '🔄': '[CYCLE]',
            '📁': '[FOLDER]',
            '📦': '[PACKAGE]',
            '🚨': '[ALERT]',
            '⚠️': '[WARNING]',
            '⏰': '[CLOCK]',
            '👍': '[THUMBS_UP]',
            '🎮': '[GAME]',
        }
        
        self.fixed_files = []
        self.errors = []
    
    def fix_file(self, file_path: str) -> bool:
        """単一ファイルの修正"""
        try:
            # ファイル読み込み
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # 絵文字のみを置換
            for emoji, replacement in self.emoji_replacements.items():
                content = content.replace(emoji, replacement)
            
            # 変更があった場合のみファイルを更新
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixed_files.append(file_path)
                print(f"[OK] 修正完了: {file_path}")
                return True
            else:
                print(f"- 変更なし: {file_path}")
                return False
                
        except Exception as e:
            error_msg = f"修正失敗: {file_path} - {str(e)}"
            self.errors.append(error_msg)
            print(f"[ERROR] {error_msg}")
            return False
    
    def find_python_files(self) -> List[str]:
        """Python ファイルを検索"""
        python_files = []
        
        # services ディレクトリ内のPythonファイル
        for root, dirs, files in os.walk('services'):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def fix_all_files(self):
        """全ファイルの修正"""
        print("[WRENCH] Unicode絵文字エンコーディング問題の修正開始")
        print("=" * 60)
        
        python_files = self.find_python_files()
        print(f"対象ファイル数: {len(python_files)}")
        
        for file_path in python_files:
            self.fix_file(file_path)
        
        print("\n" + "=" * 60)
        print("修正結果サマリー:")
        print(f"  修正されたファイル: {len(self.fixed_files)}")
        print(f"  エラー: {len(self.errors)}")
        
        if self.fixed_files:
            print(f"\n修正されたファイル一覧:")
            for file_path in self.fixed_files:
                print(f"  - {file_path}")
        
        if self.errors:
            print(f"\nエラー一覧:")
            for error in self.errors:
                print(f"  - {error}")

def main():
    """メイン実行関数"""
    fixer = SimpleUnicodeEncodingFixer()
    fixer.fix_all_files()

if __name__ == "__main__":
    main()