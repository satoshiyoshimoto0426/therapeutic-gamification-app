#!/usr/bin/env python3
"""Task 2.2 サンプルデータ管理機能の完全テスト"""

import sys
import os

# 簡易テストを実行
print("=" * 70)
print("Task 2.2: サンプルデータ管理機能の実装テスト")
print("=" * 70)

# test_sample_quick.pyを実行
print("\n[1/2] 基本機能テストを実行中...")
exit_code = os.system("python test_sample_quick.py")
if exit_code != 0:
    print("\n❌ 基本機能テストが失敗しました")
    sys.exit(1)

# 完全なテストスイートを実行
print("\n[2/2] 完全なテストスイートを実行中...")
print("-" * 70)

from test_sample_data_management import run_all_tests

success = run_all_tests()

if success:
    print("\n" + "=" * 70)
    print("🎉 Task 2.2 の全テストが成功しました！")
    print("=" * 70)
    print("\n実装された機能:")
    print("  ✓ JSONファイルからのサンプルデータロード (load_sample_data)")
    print("  ✓ テストデータの生成機能 (generate_test_data)")
    print("  ✓ データのエクスポート/インポート機能 (export_data/import_data)")
    print("  ✓ バックアップ/復元機能 (backup_data/restore_data)")
    print("  ✓ シードデータ機能 (seed_data)")
    print("  ✓ コレクションクリア機能 (clear_collection)")
    print("  ✓ データマージ機能 (import with merge=True)")
    print("\n要件 2.3 を満たしています ✅")
    sys.exit(0)
else:
    print("\n❌ 一部のテストが失敗しました")
    sys.exit(1)
