using UnityEngine;
using UnityEditor;
using System.IO;

public class TileMeshPlacer : MonoBehaviour
{
    public string meshFolderPath = "Assets/Meshes"; // Folder where mesh assets are stored
    public int gridWidth = 5; // Number of tiles in the X direction
    public int gridHeight = 5; // Number of tiles in the Y direction
    public float tileSize = 300f; // Size of each tile (matches texture dimensions)
    public float overlap = 1.0f; // Overlap between tiles
    public Material defaultMaterial; // Material to apply to the meshes

    [ContextMenu("Place Tiles in Scene")]
    public void PlaceTilesInEditor()
    {
        // Parent object to organize tiles in the hierarchy
        GameObject parentObject = new GameObject("TileGrid");


        for (int x = 0; x < gridWidth; x++)
        {
            for (int y = 0; y < gridHeight; y++)
            {
                string tileName = $"tile_{x}_{y}"; // Match mesh naming
                string meshPath = $"{meshFolderPath}/{tileName}.asset";

                // Load the mesh from the asset
                Mesh tileMesh = AssetDatabase.LoadAssetAtPath<Mesh>(meshPath);
                if (tileMesh == null)
                {
                    Debug.LogWarning($"Mesh not found: {meshPath}");
                    continue;
                }

                // Create a GameObject for the tile
                GameObject tileObject = new GameObject(tileName);

                // Calculate position based on the starting position
                Vector3 position = new Vector3(x * tileSize - x * overlap, 0, -(y * tileSize) + y * overlap);
                tileObject.transform.position = position;

                // Set parent object for hierarchy organization
                tileObject.transform.SetParent(parentObject.transform);

                // Add MeshFilter and MeshRenderer components
                MeshFilter meshFilter = tileObject.AddComponent<MeshFilter>();
                meshFilter.mesh = tileMesh;

                // Add MeshRenderer and apply the material
                MeshRenderer meshRenderer = tileObject.AddComponent<MeshRenderer>();
                meshRenderer.material = defaultMaterial; // Apply material to the tile

                Debug.Log($"Placed tile: {tileName} at position {tileObject.transform.position}");
            }
        }

        Debug.Log("All tiles placed in the scene!");
    }
}
