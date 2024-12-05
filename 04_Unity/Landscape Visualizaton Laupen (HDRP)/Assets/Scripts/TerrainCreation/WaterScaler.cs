using UnityEngine;

namespace UnityEngine.Rendering.HighDefinition
{
    [ExecuteInEditMode]
    public class WaterScaler : MonoBehaviour, IScaler
    {
        public GameObject parentObject;

        [ContextMenu("Update Water Parameters")]
        public void UpdateWaterParametersContextMenu()
        {
            UpdateParameters();
        }

        private void OnValidate()
        {
            if (!Application.isPlaying)
            {
                UpdateParameters();
            }
        }

        private void OnEnable()
        {
            UpdateParameters();
        }

        public void UpdateParameters()
        {
            if (parentObject == null)
            {
                Debug.LogError("Parent object is not assigned.");
                return;
            }

            Transform waterTransform = parentObject.transform.Find("Water");
            if (waterTransform == null)
            {
                Debug.LogError("Water object not found under the parent.");
                return;
            }

            WaterSurface waterSurface = waterTransform.GetComponent<WaterSurface>();
            if (waterSurface == null)
            {
                Debug.LogError("WaterSurface component not found on the Water object.");
                return;
            }

            ModifySimulationParameters(waterSurface);
        }

        private void ModifySimulationParameters(WaterSurface waterSurface)
        {
            waterSurface.largeWindSpeed = 0;
            waterSurface.absorptionDistance = 0.001f;
            waterSurface.ripplesWindSpeed = 1.8f;
            waterSurface.absorptionDistance = 0.01f;

            Debug.Log("Water simulation parameters updated: DistantWindSpeed = 0, Absorption distance = 0.001");
        }
    }
}
