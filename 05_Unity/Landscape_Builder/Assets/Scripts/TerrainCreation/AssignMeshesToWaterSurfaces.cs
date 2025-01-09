using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering.HighDefinition;


[ExecuteInEditMode]
public class AssignMeshesToWaterSurfaces : MonoBehaviour
{
    // List of parent GameObject names (e.g., "1975", "1939", etc.)
    [SerializeField] private List<string> parentObjectNames;

    // Context Menu action to assign meshes and add WaterSurface components
    [ContextMenu("Assign Water Surfaces to All")]
    private void AssignWaterSurfacesToAll()
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

            // Find the "Water" child GameObject under the parent
            Transform waterTransform = parentObject.transform.Find("Water");
            if (waterTransform == null)
            {
                Debug.LogWarning($"'Water' GameObject not found under parent '{parentName}'.");
                continue;
            }

            GameObject waterObject = waterTransform.gameObject;

            // Ensure the WaterSurface component is attached
            WaterSurface waterSurface = waterObject.GetComponent<WaterSurface>();
            if (waterSurface == null)
            {
                waterSurface = waterObject.AddComponent<WaterSurface>();
                Debug.Log($"<color=#20E7B0>Added WaterSurface component to '{waterObject.name}' under parent '{parentName}'.</color>");
            }

            /// Configure WaterSurface properties
            waterSurface.surfaceType = WaterSurfaceType.River; // Set Surface Type to "River"
            waterSurface.geometryType = WaterGeometryType.Custom; // Set Geometry Type to "Custom"


            // Find all MeshRenderers under the "Water" GameObject
            var meshRenderers = waterObject.GetComponentsInChildren<MeshRenderer>();
            if (meshRenderers.Length == 0)
            {
                Debug.LogWarning($"No MeshRenderers found under 'Water' GameObject for parent '{parentName}'.");
                continue;
            }

            // Assign the MeshRenderers to the WaterSurface component
            waterSurface.meshRenderers.Clear();
            //waterSurface.meshRenderers.AddRange(meshRenderers);
            foreach (var meshRenderer in meshRenderers)
            {
                waterSurface.meshRenderers.Add(meshRenderer);
                meshRenderer.enabled = false; // Deactivate the MeshRenderer
            }

            Debug.Log($"<color=#20E7B0>Successfully assigned {meshRenderers.Length} MeshRenderers to WaterSurface for '{parentName}'.</color>");
        }
    }
}
