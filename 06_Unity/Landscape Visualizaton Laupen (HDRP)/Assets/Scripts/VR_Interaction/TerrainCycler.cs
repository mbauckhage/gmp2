using UnityEngine;
using UnityEngine.InputSystem; // For the new Input System

public class TerrainCycler : MonoBehaviour
{
    [SerializeField] private GameObject[] terrains; // Array of terrain GameObjects
    private int currentTerrainIndex = 0;

    [SerializeField] private InputActionProperty thumbstickInput; // Input Action for thumbstick

    private float thumbstickThreshold = 0.8f; // Threshold for registering thumbstick input
    private bool canCycle = true; // Prevent rapid cycling

    private void Update()
    {
        OVRInput.Get(OVRInput.Button.One);


        Vector2 input = thumbstickInput.action.ReadValue<Vector2>();

        Debug.Log("Input 1: " + OVRInput.GetDown(OVRInput.RawButton.A)); // OVRInput.Controller.RTouch)
        Debug.Log("Input 2: " + OVRInput.GetDown(OVRInput.RawButton.B));
        Debug.Log("Input 3: " + OVRInput.Get(OVRInput.Axis1D.SecondaryHandTrigger, OVRInput.Controller.RTouch));



        if (input.x > thumbstickThreshold && canCycle) // Right
        {
            Debug.Log("Thumbstick detected -> Right");
            CycleTerrain(1);
        }
        else if (input.x < -thumbstickThreshold && canCycle) // Left
        {
            Debug.Log("Thumbstick detected -> Left");
            CycleTerrain(-1);
        }
        else if (Mathf.Abs(input.x) < 0.2f) // Reset canCycle when thumbstick is neutral
        {
            canCycle = true;
        }
    }

    private void CycleTerrain(int direction)
    {
        canCycle = false; // Prevent immediate repeated input

        // Deactivate current terrain
        terrains[currentTerrainIndex].SetActive(false);

        // Calculate next terrain index
        currentTerrainIndex += direction;

        // Wrap around if out of bounds
        if (currentTerrainIndex < 0)
            currentTerrainIndex = terrains.Length - 1;
        else if (currentTerrainIndex >= terrains.Length)
            currentTerrainIndex = 0;

        // Activate next terrain
        terrains[currentTerrainIndex].SetActive(true);
    }
}
