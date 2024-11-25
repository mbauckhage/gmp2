#if UNITY_EDITOR
using UnityEditor; // Required for saving assets
#endif
using UnityEngine;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;
using System.Linq;  // <-- Add this line to enable LINQ methods like Sum

public class GeoJsonParser2 : MonoBehaviour
{
    public TextAsset geoJsonFile; // Assign your GeoJSON file in the Inspector
    public string savePath = "Assets/GeneratedMeshes/"; // Default save location

    [ContextMenu("Parse GeoJSON and Save Mesh")]
    void ParseGeoJsonAndSaveMesh()
    {
        if (geoJsonFile == null)
        {
            Debug.LogError("GeoJSON file not assigned.");
            return;
        }

        string geoJson = geoJsonFile.text;
        var json = JObject.Parse(geoJson);

        // Check if the GeoJSON is a FeatureCollection
        if ((string)json["type"] == "FeatureCollection")
        {
            var features = json["features"];
            if (features == null || !features.HasValues)
            {
                Debug.LogError("FeatureCollection contains no features.");
                return;
            }

            // Iterate through features to find MultiPolygon geometries
            foreach (var feature in features)
            {
                var geometry = feature["geometry"];
                if (geometry == null)
                {
                    Debug.LogWarning("Feature contains no geometry.");
                    continue;
                }

                string geometryType = (string)geometry["type"];
                if (geometryType == "MultiPolygon")
                {
                    var coordinates = geometry["coordinates"];
                    List<List<List<Vector3>>> multiPolygon = ParseCoordinates(coordinates);

                    Debug.Log($"Parsed MultiPolygon with {multiPolygon.Count} polygons.");
                    Mesh mesh = CreateMeshFromMultiPolygon(multiPolygon);

                    // Save the mesh
                    SaveMesh(mesh, geoJsonFile.name);
                    return; // Stop after first MultiPolygon is processed
                }
            }

            Debug.LogError("No MultiPolygon geometry found in FeatureCollection.");
        }
        else
        {
            Debug.LogError("GeoJSON does not contain a FeatureCollection.");
        }
    }

    List<List<List<Vector3>>> ParseCoordinates(JToken coordinates)
    {
        List<List<List<Vector3>>> multiPolygon = new List<List<List<Vector3>>>();

        foreach (var polygon in coordinates)
        {
            List<List<Vector3>> parsedPolygon = new List<List<Vector3>>();

            foreach (var ring in polygon)
            {
                List<Vector3> vertices = new List<Vector3>();
                foreach (var point in ring)
                {
                    float x = (float)point[0];
                    float z = (float)point[1];
                    vertices.Add(new Vector3(x, 0, z)); // Z = 0 for 2D geometry
                }

                // Log the number of vertices in this ring
                Debug.Log($"Ring has {vertices.Count} vertices.");

                parsedPolygon.Add(vertices);
            }

            // Log the number of vertices in this polygon
            int totalVertices = parsedPolygon.Sum(ring => ring.Count); // Using LINQ Sum to count vertices in the polygon
            Debug.Log($"Polygon has {parsedPolygon.Count} rings and {totalVertices} vertices.");

            multiPolygon.Add(parsedPolygon);
        }

        return multiPolygon;
    }

    Mesh CreateMeshFromMultiPolygon(List<List<List<Vector3>>> multiPolygon)
    {
        Mesh mesh = new Mesh();
        List<Vector3> vertices = new List<Vector3>();
        List<int> triangles = new List<int>();

        foreach (var polygon in multiPolygon)
        {
            foreach (var ring in polygon) // Only process outer rings for simplicity
            {
                int startIndex = vertices.Count;
                vertices.AddRange(ring);

                // Generate triangles for the polygon ring
                for (int i = 1; i < ring.Count - 1; i++)
                {
                    triangles.Add(startIndex);
                    triangles.Add(startIndex + i);
                    triangles.Add(startIndex + i + 1);
                }
            }
        }

        // Calculate the centroid of the mesh (average position of all vertices)
        Vector3 centroid = Vector3.zero;
        foreach (var vertex in vertices)
        {
            centroid += vertex;
        }
        centroid /= vertices.Count;

        // Offset vertices to center the mesh at (0, 0)
        List<Vector3> centeredVertices = new List<Vector3>();
        foreach (var vertex in vertices)
        {
            centeredVertices.Add(vertex - centroid); // Shift vertices by the centroid
        }

        // Assign the centered vertices and triangles to the mesh
        mesh.vertices = centeredVertices.ToArray();
        mesh.triangles = triangles.ToArray();
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();

        return mesh;
    }

    void SaveMesh(Mesh mesh, string baseName)
    {
#if UNITY_EDITOR
        // Ensure the save directory exists
        if (!AssetDatabase.IsValidFolder(savePath))
        {
            string[] folders = savePath.Split('/');
            string currentPath = "";
            foreach (string folder in folders)
            {
                if (!string.IsNullOrEmpty(currentPath))
                    currentPath += "/";
                currentPath += folder;
                if (!AssetDatabase.IsValidFolder(currentPath))
                {
                    AssetDatabase.CreateFolder(currentPath.Substring(0, currentPath.LastIndexOf('/')), folder);
                }
            }
        }

        // Create a unique name for the mesh asset
        string meshName = baseName.Replace(" ", "_") + "_Mesh.asset";
        string assetPath = AssetDatabase.GenerateUniqueAssetPath(savePath + meshName);

        // Save the mesh as an asset
        AssetDatabase.CreateAsset(mesh, assetPath);
        AssetDatabase.SaveAssets();

        Debug.Log($"Mesh saved to: {assetPath}");
#else
        Debug.LogError("Mesh saving is only supported in the Unity Editor.");
#endif
    }
}
