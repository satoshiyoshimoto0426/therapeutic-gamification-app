using UnityEngine;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Dungeon
{
    /// <summary>
    /// ダンジョンの部屋を表すクラス
    /// </summary>
    public class Room
    {
        public int x;          // 部屋の左下X座標
        public int y;          // 部屋の左下Y座標
        public int width;      // 部屋の幅
        public int height;     // 部屋の高さ

        public List<Vector2Int> floorTiles = new List<Vector2Int>();

        public Room(int x, int y, int width, int height)
        {
            this.x = x;
            this.y = y;
            this.width = width;
            this.height = height;

            // 床タイルのリストを生成
            GenerateFloorTiles();
        }

        /// <summary>
        /// 床タイルのリストを生成
        /// </summary>
        private void GenerateFloorTiles()
        {
            floorTiles.Clear();

            for (int ix = x; ix < x + width; ix++)
            {
                for (int iy = y; iy < y + height; iy++)
                {
                    floorTiles.Add(new Vector2Int(ix, iy));
                }
            }
        }

        /// <summary>
        /// 部屋の中心座標を取得
        /// </summary>
        public Vector2Int GetCenter()
        {
            return new Vector2Int(x + width / 2, y + height / 2);
        }

        /// <summary>
        /// 部屋内のランダムな位置を取得
        /// </summary>
        public Vector2Int GetRandomPosition()
        {
            int randomX = Random.Range(x, x + width);
            int randomY = Random.Range(y, y + height);
            return new Vector2Int(randomX, randomY);
        }

        /// <summary>
        /// 指定座標が部屋内かチェック
        /// </summary>
        public bool Contains(int checkX, int checkY)
        {
            return checkX >= x && checkX < x + width &&
                   checkY >= y && checkY < y + height;
        }

        /// <summary>
        /// 指定座標が部屋内かチェック（Vector2Int版）
        /// </summary>
        public bool Contains(Vector2Int position)
        {
            return Contains(position.x, position.y);
        }

        /// <summary>
        /// 部屋の面積を取得
        /// </summary>
        public int GetArea()
        {
            return width * height;
        }

        /// <summary>
        /// 別の部屋との距離を計算（中心間の距離）
        /// </summary>
        public float DistanceTo(Room other)
        {
            Vector2Int thisCenter = GetCenter();
            Vector2Int otherCenter = other.GetCenter();
            return Vector2Int.Distance(thisCenter, otherCenter);
        }

        /// <summary>
        /// 部屋が重なっているかチェック
        /// </summary>
        public bool Overlaps(Room other)
        {
            return !(x + width <= other.x ||
                     other.x + other.width <= x ||
                     y + height <= other.y ||
                     other.y + other.height <= y);
        }

        /// <summary>
        /// 部屋の境界を取得
        /// </summary>
        public Bounds GetBounds()
        {
            Vector3 center = new Vector3(x + width / 2f, 0, y + height / 2f);
            Vector3 size = new Vector3(width, 1, height);
            return new Bounds(center, size);
        }

        /// <summary>
        /// デバッグ用の文字列表現
        /// </summary>
        public override string ToString()
        {
            return $"Room(x:{x}, y:{y}, w:{width}, h:{height})";
        }
    }
}
