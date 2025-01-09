using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering.HighDefinition;

[ExecuteInEditMode]
public class AssignMeshesToWaterSurface : MonoBehaviour
{
    // The parent object containing all the tile meshes
    [SerializeField] private GameObject parentObject;

    // The Water Surface component
    [SerializeField] private WaterSurface waterSurface;

    [ContextMenu("Assign Custom Mesh Renderers")]
    private void AssignCustomMeshRenderers()
    {
        if (parentObject == null)
        {
            Debug.LogWarning("Parent object is not assigned. Please assign a GameObject containing tile meshes.");
            return;
        }

        if (waterSurface == null)
        {
            Debug.LogWarning("Water Surface component is not assigned. Please assign a Water Surface component.");
            return;
        }

        // Find all MeshRenderer components in the children of the parentObject
        var meshRenderers = parentObject.GetComponentsInChildren<MeshRenderer>();
        if (meshRenderers.Length == 0)
        {
            Debug.LogWarning("No MeshRenderers found in the parent object or its children. Ensure there are valid meshes to assign.");
            return;
        }

        // Clear the current list and assign the new MeshRenderers
        waterSurface.meshRenderers.Clear();
        waterSurface.meshRenderers.AddRange(meshRenderers);

        Debug.Log($"<color=#20E7B0>Successfully assigned {meshRenderers.Length} MeshRenderers to the Water Surface.</color>");
    }
}
