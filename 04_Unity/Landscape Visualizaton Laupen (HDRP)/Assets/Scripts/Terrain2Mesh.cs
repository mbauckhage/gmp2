using UnityEngine;

public class Terrain2Mesh : MonoBehaviour
{
    public Terrain terrain; // Assign your terrain in the inspector
    public float heightMultiplier = 10f; // Adjust this for the desired mesh height

    void Start()
    {
        CreateMeshFromTerrain();
    }

    void CreateMeshFromTerrain()
    {
        if (terrain == null)
        {
            Debug.LogError("Terrain not assigned!");
            return;
        }

        // Get heightmap dimensions
        int width = terrain.terrainData.heightmapResolution;
        int height = terrain.terrainData.heightmapResolution;

        // Create mesh
        Mesh mesh = new Mesh();
        Vector3[] vertices = new Vector3[width * height];
        int[] triangles = new int[(width - 1) * (height - 1) * 6]; // 6 indices for each quad

        for (int x = 0; x < width; x++)
        {
            for (int y = 0; y < height; y++)
            {
                float heightValue = terrain.terrainData.GetHeight(x, y) * heightMultiplier;
                vertices[x + y * width] = new Vector3(x, heightValue, y);

                if (x < width - 1 && y < height - 1)
                {
                    int start = x + y * width;
                    int triangleIndex = (x + y * (width - 1)) * 6;
                    triangles[triangleIndex + 0] = start;
                    triangles[triangleIndex + 1] = start + width;
                    triangles[triangleIndex + 2] = start + 1;
                    triangles[triangleIndex + 3] = start + width;
                    triangles[triangleIndex + 4] = start + width + 1;
                    triangles[triangleIndex + 5] = start + 1;
                }
            }
        }

        mesh.vertices = vertices;
        mesh.triangles = triangles;
        mesh.RecalculateNormals();

        // Create a GameObject to hold the mesh
        GameObject meshObject = new GameObject("TerrainMesh");
        MeshFilter filter = meshObject.AddComponent<MeshFilter>();
        MeshRenderer renderer = meshObject.AddComponent<MeshRenderer>();
        filter.mesh = mesh;

        // Assign a material to the mesh
        renderer.material = new Material(Shader.Find("Standard"));

        // Optionally add a MeshCollider
        meshObject.AddComponent<MeshCollider>().sharedMesh = mesh;

        // Position the mesh correctly in the scene
        meshObject.transform.position = new Vector3(terrain.transform.position.x, 0, terrain.transform.position.z);
    }
}
