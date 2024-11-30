using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.XR.Interaction.Toolkit;

public class SceneLoader : MonoBehaviour
{
    [SerializeField] private string sceneName; // Name of the scene to load

    public void LoadScene()
    {
        // Load the specified scene
        SceneManager.LoadScene(sceneName);
    }

    public void TestScript()
    {
        Debug.Log("--> Testing the Button");
    }
}
