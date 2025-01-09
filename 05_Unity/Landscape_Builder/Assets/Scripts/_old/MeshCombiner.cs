using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

public class InstanceCombiner : MonoBehaviour
{
    // GameObject containing all the meshes to combine
    [SerializeField] private GameObject sourceGameObject;

    // Make a new mesh to be the target of the combine operation
    [SerializeField] private MeshFilter TargetMesh;

    [ContextMenu("Combine Meshes")]
    private void CombineMesh()
    {
        if (sourceGameObject == null)
        {
            Debug.LogWarning("No source GameObject assigned. Please assign a GameObject with MeshFilters.");
            return;
        }

        // Retrieve all MeshFilters from the source GameObject and its children
        var meshFilters = new List<MeshFilter>(sourceGameObject.GetComponentsInChildren<MeshFilter>());

        if (meshFilters.Count == 0)
        {
            Debug.LogWarning("No MeshFilters found in the provided GameObject. Please make sure it has MeshFilters attached.");
            return;
        }

        // Make an array of CombineInstance.
        var combine = new CombineInstance[meshFilters.Count];

        // Set Mesh And their Transform to the CombineInstance
        for (int i = 0; i < meshFilters.Count; i++)
        {
            if (meshFilters[i] == null || meshFilters[i].sharedMesh == null)
            {
                Debug.LogWarning($"MeshFilter at index {i} is missing or has no mesh assigned.");
                continue;
            }

            combine[i].mesh = meshFilters[i].sharedMesh;
            combine[i].transform = meshFilters[i].transform.localToWorldMatrix;
        }

        // Create an empty Mesh
        var mesh = new Mesh();

        // Use UInt32 index format to support more than 65,535 vertices
        mesh.indexFormat = UnityEngine.Rendering.IndexFormat.UInt32;

        // Combine meshes
        mesh.CombineMeshes(combine, true, true);

        // Assign the target mesh to the mesh filter of the combination GameObject
        TargetMesh.mesh = mesh;

#if UNITY_EDITOR
        // Save the Mesh to the asset folder
        SaveMesh(TargetMesh.sharedMesh, gameObject.name, false, true);
#endif

        // Print Results
        Debug.Log($"<color=#20E7B0>Combine Meshes was Successful!</color>");
    }

#if UNITY_EDITOR
    public static void SaveMesh(Mesh mesh, string name, bool makeNewInstance, bool optimizeMesh)
    {
        string path = EditorUtility.SaveFilePanel("Save Combined Mesh Asset", "Assets/", name, "asset");
        if (string.IsNullOrEmpty(path)) return;

        path = FileUtil.GetProjectRelativePath(path);

        Mesh meshToSave = makeNewInstance ? Object.Instantiate(mesh) : mesh;

        if (optimizeMesh)
            MeshUtility.Optimize(meshToSave);

        AssetDatabase.CreateAsset(meshToSave, path);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
    }
#endif
}
