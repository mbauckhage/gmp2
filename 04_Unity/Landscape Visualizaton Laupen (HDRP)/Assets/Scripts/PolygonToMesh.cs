using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

public class PolygonToMesh : MonoBehaviour
{
    public TextAsset geoJsonFile;

    [ContextMenu("Generate Mesh from GeoJSON")]
    public void GenerateMesh()
    {
        if (geoJsonFile == null)
        {
            Debug.LogError("GeoJSON file is not assigned!");
            return;
        }

        // Parse GeoJSON
        var geoData = GeoJsonParser.Parse(geoJsonFile.text);


        if (geoData.Polygons == null)
        {
            Debug.LogError("geoData.Polygons is null!");
            return;
        }

        Debug.Log($"Number of polygons: {geoData.Polygons.Count}");



        Debug.Log("Going through polyongs...");
        foreach (var polygon in geoData.Polygons)
        {
            Debug.Log(polygon.Coordinates);
            // Convert coordinates to Unity space
            Vector3[] vertices = ConvertToUnitySpace(polygon.Coordinates);

            // Triangulate
            int[] triangles = TriangulatePolygon(vertices);

            // Create mesh
            Mesh mesh = new Mesh();
            mesh.name = "GeneratedMesh";
            mesh.vertices = vertices;
            mesh.triangles = triangles;

            Debug.Log("Save mesh...");

            // Save the mesh asset
            SaveMesh(mesh, "Assets/GeneratedMeshes/GeneratedMesh.asset");

            Debug.Log("Create Mesh Game Object");

            // Add it to the scene for visualization
            CreateMeshGameObject(mesh);
        }

    }

    private Vector3[] ConvertToUnitySpace(List<Vector2> coordinates)
    {
        List<Vector3> unityPoints = new List<Vector3>();

        // Find the centroid to center the mesh
        float centerX = 0;
        float centerZ = 0;
        foreach (Vector2 coord in coordinates)
        {
            centerX += coord.x;
            centerZ += coord.y;
        }
        centerX /= coordinates.Count;
        centerZ /= coordinates.Count;

        // Adjust all vertices relative to the centroid
        foreach (Vector2 coord in coordinates)
        {
            float x = (coord.x - centerX) * 0.001f; // Scale down for Unity space
            float z = (coord.y - centerZ) * 0.001f;
            unityPoints.Add(new Vector3(x, 0, z));
        }

        return unityPoints.ToArray();
    }


    private int[] TriangulatePolygon(Vector3[] vertices)
    {
        List<int> triangles = new List<int>();

        // Simple triangulation assuming convex polygon
        for (int i = 1; i < vertices.Length - 1; i++)
        {
            triangles.Add(0);
            triangles.Add(i + 1);
            triangles.Add(i); // Reverse the order
        }

        return triangles.ToArray();
    }


    private void SaveMesh(Mesh mesh, string path)
    {
        // Ensure the directory exists
        string directory = System.IO.Path.GetDirectoryName(path);
        if (!System.IO.Directory.Exists(directory))
        {
            System.IO.Directory.CreateDirectory(directory);
        }

        // Save the mesh as an asset
        AssetDatabase.CreateAsset(mesh, path);
        AssetDatabase.SaveAssets();

        Debug.Log($"Mesh saved to {path}");
    }

    private void CreateMeshGameObject(Mesh mesh)
    {
        GameObject polygonObject = new GameObject("PolygonMesh");
        MeshFilter meshFilter = polygonObject.AddComponent<MeshFilter>();
        meshFilter.mesh = mesh;

        MeshRenderer renderer = polygonObject.AddComponent<MeshRenderer>();
        renderer.material = new Material(Shader.Find("Standard"));
    }
}
