using UnityEngine;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Dungeon
{
    /// <summary>
    /// プロシージャルダンジョン生成システム
    /// BSP（Binary Space Partitioning）アルゴリズムを使用
    /// </summary>
    public class DungeonGenerator : MonoBehaviour
    {
        [Header("Dungeon Settings")]
        public int width = 50;
        public int height = 50;
        public int minRoomSize = 6;
        public int maxRoomSize = 15;

        [Header("Generation Settings")]
        public int maxRoomCount = 10;
        public float corridorWidth = 1f;

        [Header("Prefabs")]
        public GameObject floorTilePrefab;
        public GameObject wallTilePrefab;
        public GameObject stairsUpPrefab;
        public GameObject stairsDownPrefab;

        [Header("Spawn Settings")]
        public GameObject[] enemyPrefabs;
        public GameObject[] itemPrefabs;
        public GameObject[] trapPrefabs;

        private Tile[,] dungeonGrid;
        private List<Room> rooms = new List<Room>();
        private Room startRoom;
        private Room endRoom;
        private System.Random random;

        /// <summary>
        /// ダンジョンを生成
        /// </summary>
        public void Generate(int floor, int seed)
        {
            random = new System.Random(seed);
            
            // 既存のダンジョンをクリア
            ClearDungeon();

            // グリッド初期化
            InitializeGrid();

            // BSPで部屋を生成
            GenerateRoomsWithBSP();

            // 部屋を通路で接続
            ConnectRooms();

            // 壁を配置
            PlaceWalls();

            // 階段を配置
            PlaceStairs();

            // 敵・アイテム・トラップを配置
            SpawnEntities(floor);

            // 3Dメッシュ生成
            BuildDungeonMesh();

            Debug.Log($"[DungeonGenerator] Generated floor {floor} with {rooms.Count} rooms");
        }

        /// <summary>
        /// グリッドを初期化
        /// </summary>
        private void InitializeGrid()
        {
            dungeonGrid = new Tile[width, height];

            for (int x = 0; x < width; x++)
            {
                for (int y = 0; y < height; y++)
                {
                    dungeonGrid[x, y] = new Tile(x, y, TileType.Wall);
                }
            }
        }

        /// <summary>
        /// BSPアルゴリズムで部屋を生成
        /// </summary>
        private void GenerateRoomsWithBSP()
        {
            rooms.Clear();

            // ルートノード（全体領域）
            BSPNode rootNode = new BSPNode(0, 0, width, height);

            // 再帰的に分割
            SplitNode(rootNode, 0);

            // リーフノードから部屋を作成
            CreateRoomsFromLeaves(rootNode);

            Debug.Log($"[DungeonGenerator] Created {rooms.Count} rooms");
        }

        /// <summary>
        /// ノードを再帰的に分割
        /// </summary>
        private void SplitNode(BSPNode node, int depth)
        {
            // 最大深度または最小サイズに達したら分割停止
            if (depth >= 4 || node.width < minRoomSize * 2 || node.height < minRoomSize * 2)
            {
                return;
            }

            // 分割方向を決定（ランダム）
            bool splitHorizontally = random.Next(2) == 0;

            if (splitHorizontally)
            {
                int splitY = random.Next(node.y + minRoomSize, node.y + node.height - minRoomSize);
                node.left = new BSPNode(node.x, node.y, node.width, splitY - node.y);
                node.right = new BSPNode(node.x, splitY, node.width, node.y + node.height - splitY);
            }
            else
            {
                int splitX = random.Next(node.x + minRoomSize, node.x + node.width - minRoomSize);
                node.left = new BSPNode(node.x, node.y, splitX - node.x, node.height);
                node.right = new BSPNode(splitX, node.y, node.x + node.width - splitX, node.height);
            }

            // 再帰的に分割
            SplitNode(node.left, depth + 1);
            SplitNode(node.right, depth + 1);
        }

        /// <summary>
        /// リーフノードから部屋を作成
        /// </summary>
        private void CreateRoomsFromLeaves(BSPNode node)
        {
            if (node.left == null && node.right == null)
            {
                // リーフノード：部屋を作成
                int roomWidth = random.Next(minRoomSize, Mathf.Min(maxRoomSize, node.width - 2));
                int roomHeight = random.Next(minRoomSize, Mathf.Min(maxRoomSize, node.height - 2));
                int roomX = node.x + random.Next(1, node.width - roomWidth - 1);
                int roomY = node.y + random.Next(1, node.height - roomHeight - 1);

                Room room = new Room(roomX, roomY, roomWidth, roomHeight);
                rooms.Add(room);

                // 部屋の床を配置
                for (int x = roomX; x < roomX + roomWidth; x++)
                {
                    for (int y = roomY; y < roomY + roomHeight; y++)
                    {
                        if (x >= 0 && x < width && y >= 0 && y < height)
                        {
                            dungeonGrid[x, y].type = TileType.Floor;
                        }
                    }
                }

                node.room = room;
            }
            else
            {
                // 内部ノード：子ノードを処理
                if (node.left != null) CreateRoomsFromLeaves(node.left);
                if (node.right != null) CreateRoomsFromLeaves(node.right);
            }
        }

        /// <summary>
        /// 部屋を通路で接続
        /// </summary>
        private void ConnectRooms()
        {
            for (int i = 0; i < rooms.Count - 1; i++)
            {
                Room roomA = rooms[i];
                Room roomB = rooms[i + 1];

                Vector2Int centerA = roomA.GetCenter();
                Vector2Int centerB = roomB.GetCenter();

                // L字型の通路を作成
                CreateCorridor(centerA.x, centerA.y, centerB.x, centerA.y);
                CreateCorridor(centerB.x, centerA.y, centerB.x, centerB.y);
            }
        }

        /// <summary>
        /// 通路を作成
        /// </summary>
        private void CreateCorridor(int x1, int y1, int x2, int y2)
        {
            int minX = Mathf.Min(x1, x2);
            int maxX = Mathf.Max(x1, x2);
            int minY = Mathf.Min(y1, y2);
            int maxY = Mathf.Max(y1, y2);

            for (int x = minX; x <= maxX; x++)
            {
                for (int y = minY; y <= maxY; y++)
                {
                    if (x >= 0 && x < width && y >= 0 && y < height)
                    {
                        dungeonGrid[x, y].type = TileType.Floor;
                    }
                }
            }
        }

        /// <summary>
        /// 壁を配置
        /// </summary>
        private void PlaceWalls()
        {
            for (int x = 0; x < width; x++)
            {
                for (int y = 0; y < height; y++)
                {
                    if (dungeonGrid[x, y].type == TileType.Floor)
                    {
                        // 隣接マスをチェック
                        CheckAndPlaceWalls(x, y);
                    }
                }
            }
        }

        /// <summary>
        /// 隣接マスをチェックして壁を配置
        /// </summary>
        private void CheckAndPlaceWalls(int x, int y)
        {
            for (int dx = -1; dx <= 1; dx++)
            {
                for (int dy = -1; dy <= 1; dy++)
                {
                    int nx = x + dx;
                    int ny = y + dy;

                    if (nx >= 0 && nx < width && ny >= 0 && ny < height)
                    {
                        if (dungeonGrid[nx, ny].type == TileType.Wall)
                        {
                            // 隣接に床があれば壁として確定
                            dungeonGrid[nx, ny].type = TileType.Wall;
                        }
                    }
                }
            }
        }

        /// <summary>
        /// 階段を配置
        /// </summary>
        private void PlaceStairs()
        {
            if (rooms.Count < 2) return;

            // 開始部屋（階段上）
            startRoom = rooms[0];
            Vector2Int startPos = startRoom.GetCenter();
            dungeonGrid[startPos.x, startPos.y].type = TileType.StairsUp;

            // 終了部屋（階段下）
            endRoom = rooms[rooms.Count - 1];
            Vector2Int endPos = endRoom.GetCenter();
            dungeonGrid[endPos.x, endPos.y].type = TileType.StairsDown;

            Debug.Log($"[DungeonGenerator] Stairs placed at {startPos} and {endPos}");
        }

        /// <summary>
        /// 敵・アイテム・トラップを配置
        /// </summary>
        private void SpawnEntities(int floor)
        {
            // 敵の配置数（階層に応じて増加）
            int enemyCount = random.Next(floor * 2, floor * 4);
            SpawnEnemies(enemyCount);

            // アイテムの配置数
            int itemCount = random.Next(floor, floor * 3);
            SpawnItems(itemCount);

            // トラップの配置数
            int trapCount = random.Next(0, floor * 2);
            SpawnTraps(trapCount);
        }

        /// <summary>
        /// 敵を配置
        /// </summary>
        private void SpawnEnemies(int count)
        {
            for (int i = 0; i < count; i++)
            {
                Vector2Int pos = GetRandomFloorPosition();
                // TODO: 敵のプレハブをインスタンス化
                Debug.Log($"[DungeonGenerator] Enemy spawned at {pos}");
            }
        }

        /// <summary>
        /// アイテムを配置
        /// </summary>
        private void SpawnItems(int count)
        {
            for (int i = 0; i < count; i++)
            {
                Vector2Int pos = GetRandomFloorPosition();
                // TODO: アイテムのプレハブをインスタンス化
                Debug.Log($"[DungeonGenerator] Item spawned at {pos}");
            }
        }

        /// <summary>
        /// トラップを配置
        /// </summary>
        private void SpawnTraps(int count)
        {
            for (int i = 0; i < count; i++)
            {
                Vector2Int pos = GetRandomFloorPosition();
                dungeonGrid[pos.x, pos.y].type = TileType.Trap;
                Debug.Log($"[DungeonGenerator] Trap placed at {pos}");
            }
        }

        /// <summary>
        /// ランダムな床位置を取得
        /// </summary>
        private Vector2Int GetRandomFloorPosition()
        {
            Room room = rooms[random.Next(rooms.Count)];
            int x = random.Next(room.x, room.x + room.width);
            int y = random.Next(room.y, room.y + room.height);
            return new Vector2Int(x, y);
        }

        /// <summary>
        /// 3Dメッシュを構築
        /// </summary>
        private void BuildDungeonMesh()
        {
            // TODO: タイルごとに3Dオブジェクトを配置
            for (int x = 0; x < width; x++)
            {
                for (int y = 0; y < height; y++)
                {
                    Tile tile = dungeonGrid[x, y];
                    Vector3 position = new Vector3(x, 0, y);

                    switch (tile.type)
                    {
                        case TileType.Floor:
                            if (floorTilePrefab != null)
                            {
                                Instantiate(floorTilePrefab, position, Quaternion.identity, transform);
                            }
                            break;

                        case TileType.Wall:
                            if (wallTilePrefab != null)
                            {
                                Instantiate(wallTilePrefab, position, Quaternion.identity, transform);
                            }
                            break;

                        case TileType.StairsUp:
                            if (stairsUpPrefab != null)
                            {
                                Instantiate(stairsUpPrefab, position, Quaternion.identity, transform);
                            }
                            break;

                        case TileType.StairsDown:
                            if (stairsDownPrefab != null)
                            {
                                Instantiate(stairsDownPrefab, position, Quaternion.identity, transform);
                            }
                            break;
                    }
                }
            }
        }

        /// <summary>
        /// ダンジョンをクリア
        /// </summary>
        private void ClearDungeon()
        {
            // 既存のタイルを削除
            foreach (Transform child in transform)
            {
                Destroy(child.gameObject);
            }

            rooms.Clear();
        }

        /// <summary>
        /// プレイヤーの開始位置を取得
        /// </summary>
        public Vector3 GetPlayerStartPosition()
        {
            if (startRoom != null)
            {
                Vector2Int center = startRoom.GetCenter();
                return new Vector3(center.x, 0.5f, center.y);
            }
            return Vector3.zero;
        }

        /// <summary>
        /// 指定位置のタイル情報を取得
        /// </summary>
        public Tile GetTile(int x, int y)
        {
            if (x >= 0 && x < width && y >= 0 && y < height)
            {
                return dungeonGrid[x, y];
            }
            return null;
        }
    }

    /// <summary>
    /// BSPノードクラス
    /// </summary>
    public class BSPNode
    {
        public int x, y, width, height;
        public BSPNode left, right;
        public Room room;

        public BSPNode(int x, int y, int width, int height)
        {
            this.x = x;
            this.y = y;
            this.width = width;
            this.height = height;
        }
    }
}
