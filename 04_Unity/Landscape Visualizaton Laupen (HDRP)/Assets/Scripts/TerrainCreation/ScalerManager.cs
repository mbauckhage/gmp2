using UnityEngine;

[ExecuteInEditMode] // Allows the script to run in the Editor
public class ScalerManager : MonoBehaviour
{
    [ContextMenu("Update All Scalers")]
    public void UpdateAllScalers()
    {
        // Iterate over all child objects of the parent
        foreach (Transform child in transform)
        {
            // Find all components that implement IScaler
            IScaler[] scalers = child.GetComponents<IScaler>();

            // Call UpdateParameters on each scaler script
            foreach (IScaler scaler in scalers)
            {
                scaler.UpdateParameters();
                Debug.Log($"Updated scaler: {scaler.GetType().Name} on object {child.name}");
            }
        }

        Debug.Log("All scaler scripts have been updated.");
    }
}
