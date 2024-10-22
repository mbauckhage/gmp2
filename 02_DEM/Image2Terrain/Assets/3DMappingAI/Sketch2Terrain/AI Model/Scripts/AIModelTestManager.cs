using System;
using System.IO;
using UnityEngine;
using System.Threading.Tasks;
using System.Diagnostics;
using Unity.Barracuda;
using OpenCvSharp;
using Unity.Mathematics;
using System.Runtime.InteropServices;
using UnityEditor;

namespace MappingAI
{
    public struct Prediction
    {
        public float[] predicted;
        public void SetPrediction(Tensor t)
        {
            predicted = t.AsFloats();
        }
    }
    public enum FilterType
    {
        Laplacian, HC
    };
    public enum GradientTheme
    {
        SnowyMountains,
        EarthyMountains,
        ForestedMountains,
        SelfDefined
    }
    public class AIModelTestManager : MonoBehaviour
    {
        [SerializeField]
        private float LowerBound = 0;

        [SerializeField]
        private float UpperBound = 1f;
        public Material ReliefShadingMaterial;
        [SerializeField]
        protected NNModel modelAsset;
        [SerializeField]
        protected Gradient heightmapGradient;
        // Smooth the terrain mesh after generated
        [SerializeField] FilterType smoothType = FilterType.Laplacian;
        [SerializeField] int smoothTimes = 5;

        protected IWorker _engine;
        protected Prediction prediction;
        //[SerializeField]
        protected string inputFilePath = "Assets\\3DMappingAI\\Sketch2Terrain\\AI Model\\Test\\tiles\\tile_8_11.png"; // Path to the TXT file
        string directoryPath = "Assets\\3DMappingAI\\Sketch2Terrain\\AI Model\\Test\\tiles"; // Change this to your directory path
        protected string outputDirectoryPath = "Assets/3DMappingAI/HeightMaps/";

        protected float[] predicted_result;
        protected float[] input_public;
        protected Texture2D inputDataTexture;
        protected static float[,] rescaled_predicted_heightmap;
        protected Model _runtimeModel;
        [SerializeField]
        protected GradientTheme gradientTheme = GradientTheme.SelfDefined;
        [SerializeField]
        protected GameObject AIGeneratedModelContainer;
        [SerializeField]
        protected GameObject StrokeModelContainer;
        protected MeshRenderer AIGeneratedModelContainerMeshRenderer;
        [SerializeField]
        protected float scaleRatio = 1f; //scale down the ratio for the height map, e.g., from 512 * 512 * 1 to 256 * 256 * 1
        protected int inputChunkSize = 512;

        protected bool CanExecuteInference = true;
        protected int previousStrokeNum = 0;
        protected bool materialChangedByDraw = false;
        protected Texture2D heightMapTexture;
        protected Texture2D heightmapGradientTexture;

        void Start()
        {
            _runtimeModel = ModelLoader.Load(modelAsset);
            _engine = SystemInfo.supportsComputeShaders
                ? WorkerFactory.CreateWorker(WorkerFactory.Type.Compute, _runtimeModel)
                : WorkerFactory.CreateWorker(WorkerFactory.Type.Auto, _runtimeModel);
            prediction = new Prediction();

            AIGeneratedModelContainerMeshRenderer = AIGeneratedModelContainer.GetComponent<MeshRenderer>();
            heightmapGradient = ColorManager.InitializeGradient(gradientTheme);

            // Run inference for all PNG files in the directory
            
            ExecuteInferenceForAllFilesInDirectory(directoryPath);
        }


        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.Space))
            {
                ExecuteInferenceAsyncTest();
            }
        }

        public async void WarmupExecuteInferenceAsync()
        {
            await AsyncWarmupExecuteInferenceTask();
        }
        private async Task AsyncWarmupExecuteInferenceTask()
        {
            float[] inputData = new float[inputChunkSize * inputChunkSize];
            await RunInference(inputData);
            await Task.Yield();
        }
        public async Task RunInference(float[] inputData)
        {
            // Create the input tensor
            int[] inputShape = new int[8] { 1, 1, 1, 1, 1, 512, 512, 1 };
            using (var inputTensor = new Tensor(inputShape, inputData))
            {
                // Execute the model
                _engine.Execute(inputTensor);
                await Task.Yield();
                // Get the output tensor
                Tensor outputTensor = _engine.PeekOutput();
                await Task.Yield();
                // Set and return the prediction
                prediction.SetPrediction(outputTensor);

                // Dispose the output tensor
                outputTensor.Dispose();
                inputTensor.Dispose();
            }
        }

        public async void ExecuteInferenceAsyncTest()
        {
            await Task.WhenAll(AsyncExecuteInferenceTaskFromPNG());
            //await Task.WhenAll(AsyncVisualizeMeshFromPNG(AIGeneratedModelContainer, StrokeModelContainer, "Assets/3DMappingAI/AI Model/output_height_raster", "Assets/3DMappingAI/AI Model/output_height_raster.tiff"));
        }


        
        protected (Texture2D, Texture2D, Texture2D, float[,], Mesh) PostProcess(
            float[] inputData, float[] predicted_result, string inputFilePath, string outputDirectoryPath, float inputMin, float inputMax)
        {
            // Normalize the predicted result based on the input min/max values
            float[] normalizedPredictedResult = NormalizePredictionToInputMinMax(predicted_result, inputMin, inputMax);

            (var heightMapTexture, var heightmapGradientTexture, var inputDataTexture) = 
                ColorManager.Create1DHeightMapTexture(normalizedPredictedResult, inputChunkSize, heightmapGradient, inputData);

            (var rescaled_predicted_heightmap, Mesh mesh) = 
                HeightMapProcessor.ScaleHeightMap_GenerateMesh(inputData, normalizedPredictedResult, inputChunkSize, scaleRatio);

            // Export the predicted heightmap as a TIFF using the input file's name
            ExportHeightMap(rescaled_predicted_heightmap, inputFilePath, outputDirectoryPath);

            return (heightMapTexture, heightmapGradientTexture, inputDataTexture, rescaled_predicted_heightmap, mesh);
        }

        // Add a new function to normalize predicted results to the input min/max range
        private float[] NormalizePredictionToInputMinMax(float[] predicted, float inputMin, float inputMax)
        {
            float predictedMin = float.MaxValue;
            float predictedMax = float.MinValue;

            // Find the min and max values in the predicted results
            for (int i = 0; i < predicted.Length; i++)
            {
                if (predicted[i] < predictedMin) predictedMin = predicted[i];
                if (predicted[i] > predictedMax) predictedMax = predicted[i];
            }

            // Normalize predicted results to the range of the input's min/max
            float[] normalized = new float[predicted.Length];
            for (int i = 0; i < predicted.Length; i++)
            {
                // Scale and shift the predicted values to match the input min/max range
                normalized[i] = (predicted[i] - predictedMin) / (predictedMax - predictedMin) * (inputMax - inputMin) + inputMin;
            }

            return normalized;
        }


        public async Task AsyncExecuteInferenceTaskFromPNG()
        {
            string path = inputFilePath;
            string outputPath = outputDirectoryPath;

            // Declare the tuple first
            (float[] heightMapData, float inputMin, float inputMax) result;

            // Assign the result by calling the function
            result = LoadInputDataFromPNG(path);

            // Access the values using result
            float[] heightMapData = result.heightMapData;
            float inputMin = result.inputMin;
            float inputMax = result.inputMax;


            Stopwatch stopwatch = new Stopwatch();
            stopwatch.Start();
            input_public = LoadPNGTo1DArray(path);
            await RunInference(input_public);

            stopwatch.Stop();
            TimeSpan elapsed = stopwatch.Elapsed;
            UnityEngine.Debug.Log($"Execution Time RunInference: {elapsed.TotalMilliseconds} ms");
            predicted_result = prediction.predicted;

            // Post-process: Normalize predicted results using input min/max
            Mesh mesh;
            (heightMapTexture, heightmapGradientTexture, inputDataTexture, rescaled_predicted_heightmap, mesh) =
                PostProcess(input_public, predicted_result, path, outputPath, inputMin, inputMax);

            await Task.Yield();

            // Set the material to the mesh
            Material m = ReliefShadingMaterial;
            m.SetTexture("_MainTex", heightmapGradientTexture);
            m.SetTexture("_HeightMap", heightMapTexture);
            m.SetFloat("_HeightMultiplier", 10f); // Set your height multiplier
            AIGeneratedModelContainerMeshRenderer.material = m;

            await Task.WhenAll(AsyncGenerateTerrainTask(rescaled_predicted_heightmap, AIGeneratedModelContainer));
        }


        // placing the mesh in the center of the terrain
        protected async Task AsyncGenerateTerrainTask(float[,] heightMap, GameObject gameObject)
        {
            Mesh mesh = MeshGenerator.GenerateMeshFlip(heightMap, out int width, out int height);
            await Task.Yield();
            if (smoothTimes > 0)
            {
                mesh = MeshGenerator.Smooth(mesh, smoothType, smoothTimes);
                await Task.Yield();
            }
            gameObject.GetComponent<MeshFilter>().sharedMesh = mesh;
            gameObject.transform.localScale = Vector3.one;
            //gameObject.transform.localScale = new Vector3((float)SketchingBoundary.localScale.x / width, SketchingBoundary.localScale.y, (float)SketchingBoundary.localScale.z / height);

            float offset = GetXZBounds().Item2 - GetXZBounds().Item1;
            // reset the position and localscale
            gameObject.transform.localPosition = Vector3.zero;
            gameObject.transform.localPosition = new Vector3(0 - 0.5f * offset, 0, 0 - 0.5f * offset); //offset the model into center

            // save the mesh as an asset
            //SaveMeshAsset(mesh, "DEM_Mesh.asset");
        }


        private void SaveMeshAsset(Mesh mesh, string assetName)
        {
#if UNITY_EDITOR // Ensure this only runs in the Unity Editor
            string path = "Assets/3DMappingAI/Meshes/" + assetName;

            // Check if the folder exists, if not, create it
            if (!AssetDatabase.IsValidFolder("Assets/3DMappingAI"))
            {
                AssetDatabase.CreateFolder("Assets", "3DMappingAI");
            }
            if (!AssetDatabase.IsValidFolder("Assets/3DMappingAI/Meshes"))
            {
                AssetDatabase.CreateFolder("Assets/3DMappingAI", "Meshes");
            }

            // Save the DEM mesh as an asset
            AssetDatabase.CreateAsset(mesh, path);
            AssetDatabase.SaveAssets();

            UnityEngine.Debug.Log($"DEM Mesh saved as {path}");
#endif
        }

        public Tuple<float, float> GetXZBounds()
        {

            return new Tuple<float, float>(LowerBound , UpperBound);

        }

        public async Task AsyncVisualizeMeshFromPNG(GameObject AIGeneratedModelContainer, GameObject StrokeModelContainer, string pathTerrain, string pathSketch)
        {
            await GenerateTestMesh(pathTerrain, AIGeneratedModelContainer);
            await GenerateTestMesh(pathSketch, StrokeModelContainer);
        }
        protected float[,] ReshapeArray(float[] data1D)
        {
            float[,] data2D = new float[inputChunkSize, inputChunkSize];
            for (int i = 0; i < inputChunkSize; i++)
            {
                for (int j = 0; j < inputChunkSize; j++)
                {
                    data2D[i, j] = data1D[i + j * inputChunkSize];
                }
            }
            return data2D;
        }

        private async Task GenerateTestMesh(string path, GameObject gameObject)
        {

            //input_public = ConvertPNGToGrayscaleArray1D(path);
            var input_public = LoadPNGTo1DArray(path);
            await Task.WhenAll(AsyncGenerateTerrainTask(ReshapeArray(input_public), gameObject));
        }
        public static float[] LoadPNGTo1DArray(string path)
        {
            if (!File.Exists(path))
            {
                return null;
            }

            // Load the image using Emgu CV
            
            Mat image = Cv2.ImRead(path, ImreadModes.Grayscale);

            if (image == null)
            {
                return null;
            }

            // Convert Mat to 1D float array
            return MatTo1DArray(image);
        }

        public static float[] MatTo1DArray(Mat mat)
        {
            // Ensure the input Mat is single channel (grayscale)
            if (mat.Type() != MatType.CV_8UC1)
                throw new ArgumentException("Input Mat must be a grayscale (CV_8UC1) image.");

            // Get the number of elements in the Mat
            int totalElements = mat.Rows * mat.Cols;

            // Create a byte array to hold the pixel values
            byte[] byteArray = new byte[totalElements];

            // Use Marshal.Copy to copy data from the Mat to the byte array
            Marshal.Copy(mat.Data, byteArray, 0, totalElements);

            // Now convert byte[] to float[]
            float[] floatArray = new float[totalElements];
            for (int i = 0; i < totalElements; i++)
            {
                // Cast byte values to float or normalize if needed
                floatArray[i] = (float)byteArray[i] / 255.0f; // You can normalize by dividing by 255.0f if required
            }

            return floatArray;
        }

        private (float[], float, float) LoadInputDataFromPNG(string pngFilePath)
        {
            // Load the input data (this remains the same as the previous version)
            byte[] pngData = File.ReadAllBytes(pngFilePath);
            Texture2D texture = new Texture2D(2, 2);
            texture.LoadImage(pngData);

            int width = texture.width;
            int height = texture.height;

            float[] heightMapData = new float[width * height];
            float inputMin = float.MaxValue;
            float inputMax = float.MinValue;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixelColor = texture.GetPixel(x, y);
                    float heightValue = pixelColor.grayscale;

                    heightMapData[y * width + x] = heightValue;

                    // Track the min and max values
                    if (heightValue < inputMin) inputMin = heightValue;
                    if (heightValue > inputMax) inputMax = heightValue;
                }
            }

            // Return the height map data along with the min and max values
            return (heightMapData, inputMin, inputMax);
        }

        public static float[] ConvertPNGToGrayscaleArray1D(string path)
        {
            // Load the PNG file as a Texture2D
            //byte[] fileData = File.ReadAllBytes(path);
            byte[] fileData = File.ReadAllBytes(path);
            Texture2D texture = new Texture2D(2, 2); // Create a temporary texture
            texture.LoadImage(fileData); // Load the image data into the texture

            int width = texture.width;
            int height = texture.height;

            if (width != 512 || height != 512)
            {
                UnityEngine.Debug.LogError("The PNG file must be 512x512 pixels.");
                return null;
            }

            // Create a 512*512 float array to store grayscale values
            float[] grayscaleArray = new float[512 * 512];

            // Loop through each pixel and convert to grayscale
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixelColor = texture.GetPixel(x, y);
                    float grayscaleValue = pixelColor.grayscale; // Unity provides a grayscale property
                    grayscaleArray[y * height + x] = grayscaleValue;
                }
            }

            return grayscaleArray;
        }
        public static float[] ReadTxtData(string filePath, int inputChunkSize)
        {
            float[] data1D = new float[inputChunkSize * inputChunkSize];
            string[] lines = File.ReadAllLines(filePath);

            if (lines.Length != inputChunkSize)
            {
                throw new System.Exception($"Expected {inputChunkSize} lines in the input file, but got {lines.Length}");
            }

            for (int i = 0; i < inputChunkSize; i++)
            {
                string[] values = lines[i].Split(' ');

                if (values.Length != inputChunkSize)
                {
                    throw new System.Exception($"Expected {inputChunkSize} values in line {i}, but got {values.Length}");
                }

                for (int j = 0; j < inputChunkSize; j++)
                {
                    data1D[i * inputChunkSize + j] = float.Parse(values[j]);
                }
            }
            return data1D;
        }
        public static float[] GetTxtData(float[,] heightMap, int inputChunkSize)
        {
            float[] data1D = new float[inputChunkSize * inputChunkSize];

            if (heightMap.Length != inputChunkSize)
            {
                throw new System.Exception($"Expected {inputChunkSize} lines in the input file, but got {heightMap.Length}");
            }

            for (int i = 0; i < inputChunkSize; i++)
            {
                for (int j = 0; j < inputChunkSize; j++)
                {
                    data1D[i * inputChunkSize + j] = heightMap[i, j];
                }
            }
            return data1D;
        }

        private void ExportHeightMap(float[,] heightMap, string inputFilePath, string outputDirectoryPath)
        {
            // Extract the filename without extension
            string fileName = Path.GetFileNameWithoutExtension(inputFilePath);

            // Define the output file name (prepended with 'height_map_')
            string outputFileName = $"height_map_{fileName}.tif";

            

            // Ensure the directory exists
            if (!Directory.Exists(outputDirectoryPath))
            {
                Directory.CreateDirectory(outputDirectoryPath);
            }

            // Combine directory and filename to get the full path
            string outputFilePath = Path.Combine(directoryPath, outputFileName);

            int width = heightMap.GetLength(0);
            int height = heightMap.GetLength(1);

            // Create an empty Mat to store the image data
            Mat image = new Mat(height, width, MatType.CV_32FC1); // 32-bit float single-channel matrix

            // Populate the image with the height map data
            for (int i = 0; i < height; i++)
            {
                for (int j = 0; j < width; j++)
                {
                    image.Set(i, j, heightMap[i, j]); // Set the pixel value (normalized height data)
                }
            }

            // Normalize the image between 0 and 1 if necessary (for grayscale)
            Cv2.Normalize(image, image, 0, 1, NormTypes.MinMax);

            // Convert the float image to 8-bit for saving as TIFF
            Mat image8Bit = new Mat();
            image.ConvertTo(image8Bit, MatType.CV_8UC1, 255.0);

            // Save the image as TIFF
            Cv2.ImWrite(outputFilePath, image8Bit);

            UnityEngine.Debug.Log($"Height map exported as TIFF to {outputFilePath}");
        }

        public async void ExecuteInferenceForAllFilesInDirectory(string directoryPath)
        {
            if (!Directory.Exists(directoryPath))
            {
                UnityEngine.Debug.LogError($"Directory does not exist: {directoryPath}");
                return;
            }

            // Get all PNG files in the directory
            var pngFiles = Directory.GetFiles(directoryPath, "*.png");

            if (pngFiles.Length == 0)
            {
                UnityEngine.Debug.LogError("No PNG files found in the directory.");
                return;
            }

            // Process each PNG file one by one
            foreach (var pngFile in pngFiles)
            {
                inputFilePath = pngFile; // Update the input file path to the current file
                await AsyncExecuteInferenceTaskFromPNG(); // Run the inference task for the current file
            }

            UnityEngine.Debug.Log("Finished processing all PNG files.");
        }

    }

}
