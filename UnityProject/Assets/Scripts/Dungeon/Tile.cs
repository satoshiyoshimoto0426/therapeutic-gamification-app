using UnityEngine;

namespace KokoroNoBoukensha.Dungeon
{
    /// <summary>
    /// ダンジョンのタイル情報を保持するクラス
    /// </summary>
    public class Tile
    {
        public int x;
        public int y;
        public TileType type;
        public bool isWalkable;
        public bool isExplored;  // プレイヤーが訪れたか
        public bool isVisible;   // 現在見えているか

        public Tile(int x, int y, TileType type)
        {
            this.x = x;
            this.y = y;
            this.type = type;
            this.isWalkable = (type == TileType.Floor || type == TileType.StairsUp || type == TileType.StairsDown);
            this.isExplored = false;
            this.isVisible = false;
        }

        /// <summary>
        /// 移動可能かチェック
        /// </summary>
        public bool IsWalkable()
        {
            return isWalkable && type != TileType.Wall;
        }

        /// <summary>
        /// 階段かチェック
        /// </summary>
        public bool IsStairs()
        {
            return type == TileType.StairsDown || type == TileType.StairsUp;
        }

        /// <summary>
        /// タイルの座標を取得
        /// </summary>
        public Vector2Int GetPosition()
        {
            return new Vector2Int(x, y);
        }

        /// <summary>
        /// タイルの世界座標を取得
        /// </summary>
        public Vector3 GetWorldPosition()
        {
            return new Vector3(x, 0, y);
        }
    }

    /// <summary>
    /// タイルの種類
    /// </summary>
    public enum TileType
    {
        Floor,        // 床（移動可能）
        Wall,         // 壁（移動不可）
        StairsUp,     // 上り階段（前の階へ）
        StairsDown,   // 下り階段（次の階へ）
        Trap,         // トラップ
        Door          // 扉（将来実装予定）
    }
}
