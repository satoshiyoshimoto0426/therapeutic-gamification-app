using UnityEngine;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Dungeon
{
    /// <summary>
    /// ダンジョンの3D視覚化を担当するクラス
    /// DungeonGeneratorが生成した論理的なダンジョンデータを3Dモデルとして配置
    /// </summary>
    public class DungeonVisualizer : MonoBehaviour
    {
        [Header("Tile Prefabs")]
        [Tooltip("床タイルのプレハブ")]
        public GameObject floorPrefab;
        
        [Tooltip("壁タイルのプレハブ")]
        public GameObject wallPrefab;
        
        [Tooltip("階段（下り）のプレハブ")]
        public GameObject stairsDownPrefab;
        
        [Tooltip("階段（上り）のプレハブ")]
        public GameObject stairsUpPrefab;

        [Header("Room Variations")]
        [Tooltip("通常部屋の床プレハブリスト（ランダム選択）")]
        public List<GameObject> normalFloorVariations = new List<GameObject>();
        
        [Tooltip("特殊部屋の床プレハブリスト（ランダム選択）")]
        public List<GameObject> specialFloorVariations = new List<GameObject>();

        [Header("Wall Variations")]
        [Tooltip("外壁プレハブリスト")]
        public List<GameObject> outerWallVariations = new List<GameObject>();
        
        [Tooltip("内壁プレハブリスト")]
        public List<GameObject> innerWallVariations = new List<GameObject>();

        [Header("Decoration Objects")]
        [Tooltip("装飾オブジェクト（柱、松明など）")]
        public List<GameObject> decorationPrefabs = new List<GameObject>();
        
        [Tooltip("装飾オブジェクトの配置確率 (0.0 - 1.0)")]
        [Range(0f, 1f)]
        public float decorationSpawnChance = 0.1f;

        [Header("Lighting")]
        [Tooltip("部屋ごとのポイントライト")]
        public GameObject roomLightPrefab;
        
        [Tooltip("通路のポイントライト")]
        public GameObject corridorLightPrefab;
        
        [Tooltip("ライト配置間隔")]
        public int lightSpacing = 5;

        [Header("Materials")]
        [Tooltip("床のマテリアル")]
        public Material floorMaterial;
        
        [Tooltip("壁のマテリアル")]
        public Material wallMaterial;
        
        [Tooltip("特殊部屋のマテリアル")]
        public Material specialRoomMaterial;

        [Header("Visual Settings")]
        [Tooltip("タイルサイズ")]
        public float tileSize = 1.0f;
        
        [Tooltip("壁の高さ")]
        public float wallHeight = 3.0f;
        
        [Tooltip("視覚化の親オブジェクト")]
        public Transform visualContainer;

        // 生成されたオブジェクトを保持
        private Dictionary<Vector2Int, GameObject> tileObjects = new Dictionary<Vector2Int, GameObject>();
        private List<GameObject> decorationObjects = new List<GameObject>();
        private List<GameObject> lightObjects = new List<GameObject>();

        private void Awake()
        {
            if (visualContainer == null)
            {
                GameObject container = new GameObject("DungeonVisuals");
                visualContainer = container.transform;
                visualContainer.SetParent(transform);
            }
        }

        /// <summary>
        /// ダンジョンデータから3D環境を生成
        /// </summary>
        public void VisualizeDungeon(Tile[,] tiles, List<Room> rooms)
        {
            ClearVisualization();

            int width = tiles.GetLength(0);
            int height = tiles.GetLength(1);

            // 床と壁の配置
            for (int x = 0; x < width; x++)
            {
                for (int y = 0; y < height; y++)
                {
                    Tile tile = tiles[x, y];
                    Vector3 position = new Vector3(x * tileSize, 0, y * tileSize);

                    switch (tile.type)
                    {
                        case TileType.Floor:
                            CreateFloor(position, tile, rooms);
                            break;

                        case TileType.Wall:
                            CreateWall(position, tile, x, y, tiles);
                            break;

                        case TileType.StairsDown:
                            CreateStairs(position, stairsDownPrefab);
                            break;

                        case TileType.StairsUp:
                            CreateStairs(position, stairsUpPrefab);
                            break;
                    }
                }
            }

            // 装飾オブジェクトの配置
            PlaceDecorations(tiles, rooms);

            // ライティングの配置
            PlaceLights(tiles, rooms);
        }

        /// <summary>
        /// 床タイルを生成
        /// </summary>
        private void CreateFloor(Vector3 position, Tile tile, List<Room> rooms)
        {
            GameObject prefab = floorPrefab;
            
            // 部屋の種類に応じたプレハブを選択
            if (tile.roomId >= 0 && tile.roomId < rooms.Count)
            {
                Room room = rooms[tile.roomId];
                if (room.isSpecial && specialFloorVariations.Count > 0)
                {
                    prefab = specialFloorVariations[Random.Range(0, specialFloorVariations.Count)];
                }
                else if (normalFloorVariations.Count > 0)
                {
                    prefab = normalFloorVariations[Random.Range(0, normalFloorVariations.Count)];
                }
            }

            if (prefab != null)
            {
                GameObject floor = Instantiate(prefab, position, Quaternion.identity, visualContainer);
                floor.name = $"Floor_{position.x}_{position.z}";
                
                // マテリアル適用
                if (tile.roomId >= 0 && rooms[tile.roomId].isSpecial && specialRoomMaterial != null)
                {
                    ApplyMaterial(floor, specialRoomMaterial);
                }
                else if (floorMaterial != null)
                {
                    ApplyMaterial(floor, floorMaterial);
                }

                tileObjects[new Vector2Int((int)position.x, (int)position.z)] = floor;
            }
        }

        /// <summary>
        /// 壁タイルを生成
        /// </summary>
        private void CreateWall(Vector3 position, Tile tile, int x, int y, Tile[,] tiles)
        {
            GameObject prefab = wallPrefab;

            // 外壁か内壁かを判定
            bool isOuterWall = IsOuterWall(x, y, tiles);
            
            if (isOuterWall && outerWallVariations.Count > 0)
            {
                prefab = outerWallVariations[Random.Range(0, outerWallVariations.Count)];
            }
            else if (!isOuterWall && innerWallVariations.Count > 0)
            {
                prefab = innerWallVariations[Random.Range(0, innerWallVariations.Count)];
            }

            if (prefab != null)
            {
                // 壁の高さを調整
                position.y = wallHeight / 2f;
                
                GameObject wall = Instantiate(prefab, position, Quaternion.identity, visualContainer);
                wall.name = $"Wall_{position.x}_{position.z}";
                
                // 壁の向きを調整（隣接タイルに基づく）
                AdjustWallRotation(wall, x, y, tiles);

                // マテリアル適用
                if (wallMaterial != null)
                {
                    ApplyMaterial(wall, wallMaterial);
                }

                tileObjects[new Vector2Int(x, y)] = wall;
            }
        }

        /// <summary>
        /// 階段を生成
        /// </summary>
        private void CreateStairs(Vector3 position, GameObject prefab)
        {
            if (prefab != null)
            {
                GameObject stairs = Instantiate(prefab, position, Quaternion.identity, visualContainer);
                stairs.name = $"Stairs_{position.x}_{position.z}";
                tileObjects[new Vector2Int((int)position.x, (int)position.z)] = stairs;
            }
        }

        /// <summary>
        /// 外壁かどうかを判定
        /// </summary>
        private bool IsOuterWall(int x, int y, Tile[,] tiles)
        {
            int width = tiles.GetLength(0);
            int height = tiles.GetLength(1);

            // 境界チェック
            if (x == 0 || x == width - 1 || y == 0 || y == height - 1)
                return true;

            // 隣接する全方向が壁なら外壁
            int wallCount = 0;
            for (int dx = -1; dx <= 1; dx++)
            {
                for (int dy = -1; dy <= 1; dy++)
                {
                    if (dx == 0 && dy == 0) continue;

                    int nx = x + dx;
                    int ny = y + dy;

                    if (nx >= 0 && nx < width && ny >= 0 && ny < height)
                    {
                        if (tiles[nx, ny].type == TileType.Wall)
                        {
                            wallCount++;
                        }
                    }
                }
            }

            return wallCount >= 7; // 8方向中7つ以上が壁なら外壁
        }

        /// <summary>
        /// 壁の回転を調整
        /// </summary>
        private void AdjustWallRotation(GameObject wall, int x, int y, Tile[,] tiles)
        {
            int width = tiles.GetLength(0);
            int height = tiles.GetLength(1);

            bool north = y + 1 < height && tiles[x, y + 1].type != TileType.Wall;
            bool south = y - 1 >= 0 && tiles[x, y - 1].type != TileType.Wall;
            bool east = x + 1 < width && tiles[x + 1, y].type != TileType.Wall;
            bool west = x - 1 >= 0 && tiles[x - 1, y].type != TileType.Wall;

            // 開口部の方向に基づいて回転
            if (north && !south)
            {
                wall.transform.rotation = Quaternion.Euler(0, 0, 0);
            }
            else if (south && !north)
            {
                wall.transform.rotation = Quaternion.Euler(0, 180, 0);
            }
            else if (east && !west)
            {
                wall.transform.rotation = Quaternion.Euler(0, 90, 0);
            }
            else if (west && !east)
            {
                wall.transform.rotation = Quaternion.Euler(0, 270, 0);
            }
        }

        /// <summary>
        /// 装飾オブジェクトを配置
        /// </summary>
        private void PlaceDecorations(Tile[,] tiles, List<Room> rooms)
        {
            if (decorationPrefabs.Count == 0) return;

            foreach (Room room in rooms)
            {
                // 部屋の壁際に装飾を配置
                for (int x = room.x; x < room.x + room.width; x++)
                {
                    for (int y = room.y; y < room.y + room.height; y++)
                    {
                        if (Random.value < decorationSpawnChance)
                        {
                            if (IsWallAdjacent(x, y, tiles))
                            {
                                Vector3 position = new Vector3(x * tileSize, 0, y * tileSize);
                                GameObject prefab = decorationPrefabs[Random.Range(0, decorationPrefabs.Count)];
                                GameObject decoration = Instantiate(prefab, position, Quaternion.Euler(0, Random.Range(0, 360), 0), visualContainer);
                                decoration.name = $"Decoration_{x}_{y}";
                                decorationObjects.Add(decoration);
                            }
                        }
                    }
                }
            }
        }

        /// <summary>
        /// ライティングを配置
        /// </summary>
        private void PlaceLights(Tile[,] tiles, List<Room> rooms)
        {
            // 部屋の中央にライトを配置
            if (roomLightPrefab != null)
            {
                foreach (Room room in rooms)
                {
                    Vector3 center = new Vector3(
                        (room.x + room.width / 2) * tileSize,
                        wallHeight,
                        (room.y + room.height / 2) * tileSize
                    );

                    GameObject light = Instantiate(roomLightPrefab, center, Quaternion.identity, visualContainer);
                    light.name = $"RoomLight_{room.x}_{room.y}";
                    lightObjects.Add(light);
                }
            }

            // 通路に定期的にライトを配置
            if (corridorLightPrefab != null)
            {
                int width = tiles.GetLength(0);
                int height = tiles.GetLength(1);

                for (int x = 0; x < width; x += lightSpacing)
                {
                    for (int y = 0; y < height; y += lightSpacing)
                    {
                        if (tiles[x, y].type == TileType.Floor && tiles[x, y].roomId == -1)
                        {
                            Vector3 position = new Vector3(x * tileSize, wallHeight * 0.7f, y * tileSize);
                            GameObject light = Instantiate(corridorLightPrefab, position, Quaternion.identity, visualContainer);
                            light.name = $"CorridorLight_{x}_{y}";
                            lightObjects.Add(light);
                        }
                    }
                }
            }
        }

        /// <summary>
        /// 壁に隣接しているかチェック
        /// </summary>
        private bool IsWallAdjacent(int x, int y, Tile[,] tiles)
        {
            int width = tiles.GetLength(0);
            int height = tiles.GetLength(1);

            for (int dx = -1; dx <= 1; dx++)
            {
                for (int dy = -1; dy <= 1; dy++)
                {
                    if (dx == 0 && dy == 0) continue;

                    int nx = x + dx;
                    int ny = y + dy;

                    if (nx >= 0 && nx < width && ny >= 0 && ny < height)
                    {
                        if (tiles[nx, ny].type == TileType.Wall)
                        {
                            return true;
                        }
                    }
                }
            }

            return false;
        }

        /// <summary>
        /// マテリアルを適用
        /// </summary>
        private void ApplyMaterial(GameObject obj, Material material)
        {
            Renderer renderer = obj.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material = material;
            }

            // 子オブジェクトにも適用
            foreach (Transform child in obj.transform)
            {
                Renderer childRenderer = child.GetComponent<Renderer>();
                if (childRenderer != null)
                {
                    childRenderer.material = material;
                }
            }
        }

        /// <summary>
        /// 視覚化をクリア
        /// </summary>
        public void ClearVisualization()
        {
            foreach (var kvp in tileObjects)
            {
                if (kvp.Value != null)
                {
                    Destroy(kvp.Value);
                }
            }
            tileObjects.Clear();

            foreach (GameObject decoration in decorationObjects)
            {
                if (decoration != null)
                {
                    Destroy(decoration);
                }
            }
            decorationObjects.Clear();

            foreach (GameObject light in lightObjects)
            {
                if (light != null)
                {
                    Destroy(light);
                }
            }
            lightObjects.Clear();
        }

        /// <summary>
        /// 特定位置のタイルオブジェクトを取得
        /// </summary>
        public GameObject GetTileObject(Vector2Int position)
        {
            return tileObjects.ContainsKey(position) ? tileObjects[position] : null;
        }

        private void OnDestroy()
        {
            ClearVisualization();
        }
    }
}
