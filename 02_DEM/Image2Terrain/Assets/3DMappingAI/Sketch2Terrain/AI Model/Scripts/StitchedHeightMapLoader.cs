using System.IO;
using UnityEngine;
using OpenCvSharp;
using System.Runtime.InteropServices;

namespace MappingAI
{
    public class StitchedHeightMapLoader : MonoBehaviour
    {
        [SerializeField] private string stitchedHeightMapPath = "Assets\\3DMappingAI\\Sketch2Terrain\\AI Model\\Test\\height_map_from_tiles.png"; // Path to the stitched PNG file
        [SerializeField] private GameObject StitchedMeshContainer; // GameObject to hold the mesh
        [SerializeField] private float heightMultiplier = 10f; // Multiplier for the height map
        [SerializeField] private Material meshMaterial; // Material for the mesh

        private MeshRenderer StitchedMeshRenderer;
        private int stitchedWidth;
        private int stitchedHeight;

        private void Start()
        {
            // Load the stitched PNG and generate the mesh
            LoadAndGenerateMesh();
        }

        private void LoadAndGenerateMesh()
        {
            // Ensure MeshFilter is present
            MeshFilter meshFilter = StitchedMeshContainer.GetComponent<MeshFilter>();
            if (meshFilter == null)
            {
                meshFilter = StitchedMeshContainer.AddComponent<MeshFilter>(); // Add MeshFilter if missing
            }

            // Ensure MeshRenderer is present
            StitchedMeshRenderer = StitchedMeshContainer.GetComponent<MeshRenderer>();
            if (StitchedMeshRenderer == null)
            {
                StitchedMeshRenderer = StitchedMeshContainer.AddComponent<MeshRenderer>(); // Add MeshRenderer if missing
            }

            // Load the stitched PNG as a float array (grayscale)
            float[,] heightMap = LoadPNGTo2DArray(stitchedHeightMapPath, out stitchedWidth, out stitchedHeight);

            if (heightMap == null)
            {
                Debug.LogError("Failed to load the stitched height map.");
                return;
            }

            // Generate the mesh
            Mesh mesh = MeshGenerator.GenerateMeshFlip(heightMap, out int width, out int height);
            if (mesh == null)
            {
                Debug.LogError("Failed to generate the mesh.");
                return;
            }

            // Apply mesh to the MeshFilter component
            meshFilter.sharedMesh = mesh;
            StitchedMeshContainer.transform.localScale = Vector3.one;

            // Set material and textures
            Material material = new Material(meshMaterial);
            StitchedMeshRenderer.material = material;
            StitchedMeshRenderer.material.SetFloat("_HeightMultiplier", heightMultiplier);

            // Place the mesh in the center
            float offset = Mathf.Max(stitchedWidth, stitchedHeight) * 0.5f;
            StitchedMeshContainer.transform.localPosition = new Vector3(-offset, 0, -offset);
        }

        public static float[,] LoadPNGTo2DArray(string path, out int width, out int height)
        {
            if (!File.Exists(path))
            {
                Debug.LogError($"File not found: {path}");
                width = height = 0;
                return null;
            }

            // Load the PNG using OpenCV
            Mat image = Cv2.ImRead(path, ImreadModes.Grayscale);
            if (image == null || image.Empty())
            {
                Debug.LogError($"Failed to load image at path: {path}");
                width = height = 0;
                return null;
            }

            width = image.Width;
            height = image.Height;

            // Convert the image to a 2D float array
            return MatTo2DArray(image);
        }

        public static float[,] MatTo2DArray(Mat mat)
        {
            int rows = mat.Rows;
            int cols = mat.Cols;

            // Ensure the input Mat is single channel (grayscale)
            if (mat.Type() != MatType.CV_8UC1)
            {
                Debug.LogError("Input Mat must be a grayscale (CV_8UC1) image.");
                return null;
            }

            // Create a byte array to hold the pixel values
            byte[] byteArray = new byte[rows * cols];

            // Use Marshal.Copy to copy data from the Mat to the byte array
            Marshal.Copy(mat.Data, byteArray, 0, rows * cols);

            // Convert byte array to float array
            float[,] floatArray = new float[rows, cols];
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    // Normalize byte to float
                    floatArray[i, j] = byteArray[i * cols + j] / 255.0f;
                }
            }

            return floatArray;
        }
    }
}
