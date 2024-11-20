using UnityEngine;

public static class Heightmap2Mesh
{
    public static MeshData GenerateTerrainMesh(float[,] heightMap, float heightMultiplier)
    {
        int width = heightMap.GetLength(0);
        int height = heightMap.GetLength(1);

        // Scale to center the map
        float topLeftX = (width - 1) / -2f;
        float topLeftZ = (height - 1) / -2f;

        MeshData meshData = new MeshData(width, height);
        int vertexIndex = 0;

        // 2D array to keep track of valid vertices
        int[,] vertexIndices = new int[width, height]; // Stores indices for valid vertices

        // First pass: Create vertices for valid (non-zero) heightmap pixels
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                // Only create vertices for non-zero pixels
                if (heightMap[x, y] > 0)
                {
                    meshData.vertices[vertexIndex] = new Vector3(topLeftX + x, heightMap[x, y] * heightMultiplier, topLeftZ + y);
                    meshData.uvs[vertexIndex] = new Vector2(x / (float)width, y / (float)height);
                    vertexIndices[x, y] = vertexIndex;  // Store index for valid vertex
                    vertexIndex++;
                }
                else
                {
                    vertexIndices[x, y] = -1;  // Mark invalid pixels with -1
                }
            }
        }

        // Second pass: Create triangles using only valid vertices
        for (int y = 0; y < height - 1; y++)
        {
            for (int x = 0; x < width - 1; x++)
            {
                // Get the indices of the four neighboring vertices (top-left, top-right, bottom-left, bottom-right)
                int topLeft = vertexIndices[x, y];
                int topRight = vertexIndices[x + 1, y];
                int bottomLeft = vertexIndices[x, y + 1];
                int bottomRight = vertexIndices[x + 1, y + 1];

                // Ensure that all four vertices are valid (i.e., they exist and are non-zero)
                if (topLeft >= 0 && topRight >= 0 && bottomLeft >= 0 && bottomRight >= 0)
                {
                    // Add triangles for this square
                    meshData.AddTriangle(topLeft, bottomLeft, bottomRight);
                    meshData.AddTriangle(topLeft, bottomRight, topRight);
                }
            }
        }

        return meshData;
    }
}

public class MeshData
{
    public Vector3[] vertices;
    public int[] triangles;
    public Vector2[] uvs;

    int triangleIndex;

    public MeshData(int meshWidth, int meshHeight)
    {
        vertices = new Vector3[meshWidth * meshHeight];
        uvs = new Vector2[meshWidth * meshHeight];
        triangles = new int[(meshWidth - 1) * (meshHeight - 1) * 6]; // 2 triangles per square
    }

    public void AddTriangle(int a, int b, int c)
    {
        triangles[triangleIndex] = a;
        triangles[triangleIndex + 1] = b;
        triangles[triangleIndex + 2] = c;

        triangleIndex += 3;
    }

    public Mesh CreateMesh()
    {
        Mesh mesh = new Mesh();
        mesh.vertices = vertices;
        mesh.triangles = triangles;
        mesh.uv = uvs;
        mesh.RecalculateNormals();
        return mesh;
    }
}
