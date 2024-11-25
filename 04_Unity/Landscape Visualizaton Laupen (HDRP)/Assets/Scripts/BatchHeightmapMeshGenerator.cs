using UnityEngine;
using System.IO;
using UnityEditor;

public class BatchHeightmapMeshGenerator : MonoBehaviour
{
    public string heightmapRootFolder = "Assets/Heightmaps/river_tiles"; // Path to the root folder with heightmap subfolders
    public Material defaultMaterial; // Material to apply to the generated meshes
    public float heightMultiplier = 1f; // Adjust this to control the vertical scale of the mesh

    private void Start()
    {
        GenerateAllMeshes();
    }

    [ContextMenu("Generate All Meshes")]
    public void GenerateAllMeshes()
    {
        if (!Directory.Exists(heightmapRootFolder))
        {
            Debug.LogError($"The specified folder does not exist: {heightmapRootFolder}");
            return;
        }

        // Get all subdirectories (subfolders) inside the root folder
        string[] subfolders = Directory.GetDirectories(heightmapRootFolder);
        if (subfolders.Length == 0)
        {
            Debug.LogWarning("No subfolders found in the specified root folder.");
            return;
        }

        foreach (string subfolder in subfolders)
        {
            Debug.Log("Start processing folder: " + subfolder);
            // Process all PNG files in the current subfolder
            string[] pngFiles = Directory.GetFiles(subfolder, "*.png");
            if (pngFiles.Length == 0)
            {
                Debug.LogWarning($"No PNG files found in the folder: {subfolder}");
                continue;
            }

            // Save path will be based on the subfolder name
            string folderName = Path.GetFileName(subfolder); // Get folder name
            string meshSavePath = $"Assets/Meshes/River_Tiles/{folderName}";
            
            // Create a subfolder inside the "Assets/Meshes/River_Tiles" if it doesn't exist
            if (!Directory.Exists(meshSavePath))
            {
                Directory.CreateDirectory(meshSavePath);
            }

            // Process each PNG file in the subfolder
            foreach (string filePath in pngFiles)
            {
                CreateMeshFromHeightmap(filePath, meshSavePath);
            }
        }

        Debug.Log("All meshes generated successfully!");
    }

    private void CreateMeshFromHeightmap(string filePath, string meshSavePath)
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
            GameObject tileObject = new GameObject(fileName);
            tileObject.transform.position = Vector3.zero;

            // Add HeightmapMeshGenerator component
            HeightmapMeshGenerator meshGenerator = tileObject.AddComponent<HeightmapMeshGenerator>();
            meshGenerator.heightmapTexture = heightmapTexture;
            meshGenerator.heightMultiplier = heightMultiplier;
            meshGenerator.meshMaterial = defaultMaterial;
            meshGenerator.meshSavePath = meshSavePath;
            meshGenerator.meshName = fileName;

            // Generate the mesh and save it to the appropriate folder
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
