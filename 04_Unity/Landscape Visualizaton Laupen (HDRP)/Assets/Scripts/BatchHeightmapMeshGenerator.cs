using UnityEngine;
using System.IO;
using UnityEditor;

public class BatchHeightmapMeshGenerator : MonoBehaviour
{
    public string heightmapFolder = "Assets/Heightmaps/river_tiles"; // Path to the folder with heightmap PNGs
    public Material defaultMaterial; // Material to apply to the generated meshes
    public float heightMultiplier = 1f; // Adjust this to control the vertical scale of the mesh
    public string meshSavePath = "Assets/Meshes/river_tiles"; // Path to save generated meshes

    private void Start()
    {
        GenerateAllMeshes();
    }

    [ContextMenu("Generate All Meshes")]
    public void GenerateAllMeshes()
    {
        if (!Directory.Exists(heightmapFolder))
        {
            Debug.LogError($"The specified folder does not exist: {heightmapFolder}");
            return;
        }

        string[] pngFiles = Directory.GetFiles(heightmapFolder, "*.png");
        if (pngFiles.Length == 0)
        {
            Debug.LogWarning("No PNG files found in the specified folder.");
            return;
        }

        foreach (string filePath in pngFiles)
        {
            Debug.Log("Start processing "+ filePath);
            CreateMeshFromHeightmap(filePath);
        }

        Debug.Log("All meshes generated successfully!");
    }

    private void CreateMeshFromHeightmap(string filePath)
    {
        // Load the heightmap texture
        Texture2D heightmapTexture = LoadHeightmapTexture(filePath);
        if (heightmapTexture == null)
        {
            Debug.LogError($"Failed to load texture from {filePath}");
            return;
        }

        // Determine the tile's position based on its file name or index
        string fileName = Path.GetFileNameWithoutExtension(filePath);
        string[] parts = fileName.Split('_'); // Assuming file naming convention includes position, e.g., "tile_0_0"
        if (parts.Length >= 3 && int.TryParse(parts[1], out int tileX) && int.TryParse(parts[2], out int tileY))
        {
            float tileSize = heightmapTexture.width; // Assuming square tiles
            Vector3 tilePosition = new Vector3(tileX * tileSize, 0, tileY * tileSize);

            // Log the tile position
            Debug.Log($"Tile '{fileName}' position: {tilePosition}");


            // Create a new GameObject to hold the mesh
            GameObject tileObject = new GameObject(Path.GetFileNameWithoutExtension(filePath));
            tileObject.transform.position = Vector3.zero;



            // Add HeightmapMeshGenerator component
            HeightmapMeshGenerator meshGenerator = tileObject.AddComponent<HeightmapMeshGenerator>();
            meshGenerator.heightmapTexture = heightmapTexture;
            meshGenerator.heightMultiplier = heightMultiplier;
            meshGenerator.meshMaterial = defaultMaterial;
            meshGenerator.meshSavePath = meshSavePath;
            meshGenerator.meshName = Path.GetFileNameWithoutExtension(filePath);

            // Generate the mesh
            meshGenerator.GenerateMeshFromHeightmap();
        }
        else
        {
            Debug.LogWarning($"Filename does not follow expected pattern: {fileName}");
        }




    }

    private Texture2D LoadHeightmapTexture(string filePath)
    {
        byte[] fileData = File.ReadAllBytes(filePath);
        Texture2D texture = new Texture2D(2, 2);
        if (texture.LoadImage(fileData))
        {
            texture.Apply();
            return texture;
        }
        return null;
    }
}
