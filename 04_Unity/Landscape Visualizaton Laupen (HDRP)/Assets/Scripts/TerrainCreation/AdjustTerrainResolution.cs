using UnityEngine;
using System.Collections.Generic;

[ExecuteInEditMode]
public class AdjustTerrainAndObjects : MonoBehaviour, IScaler
{
    // List of parent GameObject names (e.g., "1975", "1939", etc.)
    [SerializeField] private List<string> parentObjectNames;

    // Scaling factor for width, length, and height
    [SerializeField] private float scalingFactor = 1000f;

    [ContextMenu("Adjust Terrain and Objects")]

    public void UpdateParameters()
    {
        AdjustTerrainAndObjectsInParent();

    }

    private void AdjustTerrainAndObjectsInParent()
    {
        if (parentObjectNames == null || parentObjectNames.Count == 0)
        {
            Debug.LogWarning("No parent object names provided. Please add some names to the 'parentObjectNames' list.");
            return;
        }

        foreach (var parentName in parentObjectNames)
        {
            // Find the parent GameObject by name
            GameObject parentObject = GameObject.Find(parentName);
            if (parentObject == null)
            {
                Debug.LogWarning($"Parent object with name '{parentName}' not found in the scene.");
                continue;
            }

            // Adjust Terrain "Tile__0__0"
            AdjustTerrain(parentObject);

            // Adjust "Water" GameObject
            AdjustObjectScale(parentObject, "Water");

            // Adjust "Buildings" GameObject
            AdjustObjectScale(parentObject, "buildings");
        }
    }

    private void AdjustTerrain(GameObject parentObject)
    {
        // Find the terrain GameObject named "Tile__0__0" under the parent
        Transform terrainTransform = parentObject.transform.Find("Tile__0__0");
        if (terrainTransform == null)
        {
            Debug.LogWarning($"Terrain object 'Tile__0__0' not found under parent '{parentObject.name}'.");
            return;
        }

        GameObject terrainObject = terrainTransform.gameObject;
        Terrain terrain = terrainObject.GetComponent<Terrain>();
        if (terrain == null)
        {
            Debug.LogWarning($"The object 'Tile__0__0' under parent '{parentObject.name}' does not have a Terrain component.");
            return;
        }

        // Get the TerrainData and adjust its dimensions
        TerrainData terrainData = terrain.terrainData;
        if (terrainData == null)
        {
            Debug.LogWarning($"TerrainData is missing for 'Tile__0__0' under parent '{parentObject.name}'.");
            return;
        }

        // Adjust the terrain size
        Vector3 originalSize = terrainData.size;
        Vector3 newSize = new Vector3(
            originalSize.x * scalingFactor, // Adjust width
            originalSize.y * scalingFactor, // Adjust height
            originalSize.z * scalingFactor  // Adjust length
        );

        terrainData.size = newSize;
        Debug.Log($"<color=#20E7B0>Adjusted Terrain 'Tile__0__0' under parent '{parentObject.name}' to new size {newSize}.</color>");

        // Adjust Terrain Layers (textures)
        AdjustTerrainLayers(terrainData);
    }

    private void AdjustTerrainLayers(TerrainData terrainData)
    {
        // Adjust the tileSize for each TerrainLayer
        if (terrainData.terrainLayers == null || terrainData.terrainLayers.Length == 0)
        {
            Debug.LogWarning("No terrain layers found to adjust.");
            return;
        }

        foreach (var terrainLayer in terrainData.terrainLayers)
        {
            // Adjust the tiling of the texture based on the scaling factor
            Vector2 originalTileSize = terrainLayer.tileSize;
            Vector2 newTileSize = originalTileSize * scalingFactor;

            terrainLayer.tileSize = newTileSize;
            Debug.Log($"<color=#20E7B0>Adjusted texture tile size for terrain layer '{terrainLayer.name}' to {newTileSize}.</color>");
        }
    }

    private void AdjustObjectScale(GameObject parentObject, string objectName)
    {
        // Find the specified object under the parent (e.g., "Water" or "Buildings")
        Transform objectTransform = parentObject.transform.Find(objectName);
        if (objectTransform == null)
        {
            Debug.LogWarning($"'{objectName}' GameObject not found under parent '{parentObject.name}'.");
            return;
        }

        // Apply the scaling factor to the object's transform
        objectTransform.localScale *= scalingFactor;
        Debug.Log($"<color=#20E7B0>Scaled '{objectName}' under parent '{parentObject.name}' by a factor of {scalingFactor}.</color>");
    }
}
