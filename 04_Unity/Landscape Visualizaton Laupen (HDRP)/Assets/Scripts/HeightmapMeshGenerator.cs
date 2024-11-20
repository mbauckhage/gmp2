using UnityEngine;
using System.IO;
using UnityEditor;

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class HeightmapMeshGenerator : MonoBehaviour
{
    public Texture2D heightmapTexture; // Assign your heightmap PNG here
    public float heightMultiplier = 1f; // Adjust this to control the vertical scale of the mesh
    public Material meshMaterial;
    public string meshSavePath = "Assets/Meshes";
    public string meshName;

    private Mesh generatedMesh;

    void Start()
    {
        GenerateMeshFromHeightmap();
    }

    public void GenerateMeshFromHeightmap()
    {
        if (heightmapTexture == null)
        {
            Debug.LogError("No heightmap texture assigned!");
            return;
        }

        // Ensure the texture is readable in import settings
        if (!heightmapTexture.isReadable)
        {
            Debug.LogError("Heightmap texture must be set to 'Readable' in import settings.");
            return;
        }

        // Convert the heightmap texture to a 2D array of height values
        float[,] heightMap = GetHeightMapFromTexture(heightmapTexture);

        // Generate the mesh data from the heightmap
        MeshData meshData = Heightmap2Mesh.GenerateTerrainMesh(heightMap, heightMultiplier);

        // Create a mesh from the mesh data and assign it to the MeshFilter
        generatedMesh = meshData.CreateMesh(); // Store the generated mesh
        MeshFilter meshFilter = GetComponent<MeshFilter>();
        meshFilter.mesh = generatedMesh; // Assign the stored mesh

        // Ensure the object has a MeshRenderer and assign a material
        MeshRenderer meshRenderer = GetComponent<MeshRenderer>();
        if (meshMaterial != null)
        {
            meshRenderer.material = meshMaterial;
        }
        else
        {
            Debug.LogWarning("No material assigned. Assigning default material.");
            meshRenderer.material = new Material(Shader.Find("Standard"));
        }

        // Save the mesh asset
        SaveMeshAsset();
    }

    public float[,] GetHeightMapFromTexture(Texture2D texture)
    {
        int width = texture.width;
        int height = texture.height;
        float[,] heightMap = new float[width, height];

        // Loop through each pixel in the texture and get grayscale value as height
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                float heightValue = texture.GetPixel(x, y).grayscale;
                heightMap[x, y] = heightValue * heightMultiplier; // Apply heightMultiplier here if needed
            }
        }

        return heightMap;
    }

    // Method to save the mesh as an asset
    public void SaveMeshAsset()
    {
        if (generatedMesh == null)
        {
            Debug.LogError("No mesh generated to save.");
            return;
        }

        if (!Directory.Exists(meshSavePath))
        {
            Directory.CreateDirectory(meshSavePath);
        }

        string meshPath = $"{meshSavePath}/{meshName}.asset";

        AssetDatabase.CreateAsset(generatedMesh, meshPath);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        Debug.Log($"Mesh saved at {meshPath}");
    }
}
