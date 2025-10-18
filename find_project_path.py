import os

# 現在のスクリプトの場所を表示
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"プロジェクトルート: {current_dir}")
print(f"\nstart_mvp_services.py が存在: {os.path.exists(os.path.join(current_dir, 'start_mvp_services.py'))}")
print(f"\nこのパスをコピーしてターミナルで使用してください:")
print(f'cd "{current_dir}"')
print(f"python start_mvp_services.py")
