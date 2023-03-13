using System.Collections;
using System.Collections.Generic;
using System.IO;
using System;
using UnityEditor;
using UnityEngine;
using System.Linq;
//using Unity.Mathematics;

public class CalibrateTool : MonoBehaviour
{
    static CalibrateTool instance;
    public static CalibrateTool Instance
    {
        get
        {
            if (instance == null)
            {
                instance = FindObjectOfType(typeof(CalibrateTool)) as CalibrateTool;
            }

            return instance;
        }
    }

    [Header("Main Properties")]
    /// <summary>
    /// Add the cameras you want to calibrate into this list
    /// </summary>
    public List<Camera> camerasToCalibrate;

    /// <summary>
    /// Define the targetParentFolder to save the data;
    /// </summary>
    public string targetParentFolder = @"../CalibrateTool/";

    /// <summary>
    /// Fake chessboard will be generated from this transform
    /// </summary>
    public Transform chessboardGenerateCenter;
    
    /// <summary>
    /// Scaling of OpenCV coordinate
    /// </summary>
    [Range(0, 10f)]
    public float Scaling = 1;


    [SerializeField] bool enableLog = false;

    [Header("Chessboard Properties")]
    /// <summary>
    /// The inteval bettween the chessboard to change its transform
    /// </summary>
    [SerializeField] float updateChessboardInterval = 0.5f;

    /// <summary>
    /// Count how many times(views) is the chessboard going to be updated
    /// </summary>
    [SerializeField] int chessboardCount = 50;

    /// <summary>
    /// The length of the sides of the fake checkerboard
    /// </summary>
    [SerializeField] float SQUARE_SIZE = 0.14f;

    /// <summary>
    /// How many squares in width of the chessboard, better be odd
    /// </summary>
    [SerializeField] int widthOfChessboard = 9;

    /// <summary>
    /// How many squares in height of the chessboard, better be odd
    /// </summary>
    [SerializeField] int heightOfChessboard = 7;

    [Header("Staic Mark Points Properties")]
    /// <summary>
    /// The square length of mark points square
    /// </summary>
    [SerializeField] int lengthOfMarkPointsSquare = 7;

    /// <summary>
    /// The distance bettween two points
    /// </summary>
    [SerializeField] float gapBetweenMarkPoints = 1;

    [SerializeField] GameObject humanModel;
    [SerializeField] bool showModel = false;
    GameObject go;

    [Header("Dataset Parameters")]
    /// <summary>
    /// This transform indicate the Origin of grid of Wildtrack system.
    /// </summary>
    public Transform gridOrigin;
    public int MAP_HEIGHT = 16;
    public int MAP_WIDTH = 25;
    public int MAP_EXPAND = 40;
    public float MAN_RADIUS = 0.16f;
    public float MAN_HEIGHT = 1.8f;
    public int IMAGE_WIDTH = 1920;
    public int IMAGE_HEIGHT = 1080;

    //format the file name of frames, 0001.png for RW = 4 , 00001.png for RW = 5
    public int RJUST_WIDTH = 4;

    [Header("Others")]
    /// <summary>
    /// Random offsets for updating the chessboard 
    /// </summary>
    [SerializeField] float tRandomOffset = 5f;
    [SerializeField] float rRandomOffset = 120;


    /// <summary>
    /// A dictionary to store the cornerpoints(GameObject) on chessboard and their coordinates(follow OpenCV,(x,y,0)) of the chessboard
    /// </summary>
    Dictionary<GameObject, Vector3> cornerPointsDic = new Dictionary<GameObject, Vector3>();

    /// <summary>
    /// An array to store the static mark points 
    /// </summary>
    Vector3[] markPoints;

    Vector3[] validatePoints;

    /// <summary>
    /// Index of chessboard
    /// </summary>
    int boardIndex = 0;

    private void Awake()
    {
        chessboardGenerateCenter.rotation = Quaternion.identity;
        GenerateMarkPoints();
        GenerateValidatePoints();
        GenerateVisualChessboard();
    }


    void Start()
    {
        WriteDatasetParametersPy(); 
        //WriteGridOrigin();
        targetParentFolder = targetParentFolder + "\\calib";
        Debug.Log("[IO][Calib]Calibrate saved in " + targetParentFolder);
        ResetFolder(targetParentFolder);
        BeginToCalibrate();
    }

    void BeginToCalibrate()
    {
        if (camerasToCalibrate.Count < 1)
        {
            Debug.LogWarning("[Calib] No camera to calibrate, please check " + nameof(CalibrateTool) + "." + nameof(camerasToCalibrate));
            return;
        }

        int cameraIndex = 0;
        foreach (var cam in camerasToCalibrate)
        {
            WriteWorldPointsScreenPos(cam, cameraIndex, markPoints, nameof(markPoints));
            WriteWorldPointsScreenPos(cam, cameraIndex,validatePoints,nameof(validatePoints));
            //GetNativeCalibrationByMath(cam);
            cameraIndex++;
        }
        StartCoroutine(Func());
    }



    IEnumerator Func()
    {

        while (true)// or for(i;i;i)
        {
            yield return new WaitForSeconds(updateChessboardInterval); // first
            //Specific functions put here 

            int cameraIndex = 0;
            foreach (var cam in camerasToCalibrate)
            {
                WriteChessboardScreenPos(cam, cameraIndex);
                cameraIndex++;
            }
            UpdateChessboard();
            // Note the order of codes above.  Different order shows different outcome.
            if (boardIndex >= chessboardCount)
            {
                Debug.Log("[Calib] Chessboard Finished");
                break;
            }
        }
    }

    void GetNativeCalibrationByMath(Camera cam)
    {
        float w = cam.pixelWidth;
        float h = cam.pixelHeight;
        float fov = cam.fieldOfView;

        float u_0 = w / 2;
        float v_0 = h / 2;

        float fx = (h / 2) / (float)System.Math.Tan((fov / 180 * System.Math.PI) / 2);

        //float fx = w / (2 * (math.tan((fov / 2) * (math.PI / 180))));
        float fy = h / (2 * (float)(Math.Tan((fov / 2) * (Math.PI / 180))));


        //float3x3 camIntriMatrix = new float3x3(new float3(fx, 0f, u_0),
        //                               new float3(0f, fy, v_0),
        //                               new float3(0f, 0f, 1f));

        //Debug.Log(camIntriMatrix);
        //Matrix4x4 cameraToWorldMatrix = cam.cameraToWorldMatrix;
        //Matrix4x4 projectionMatrix = cam.projectionMatrix;

        ////Debug.Log(cam.worldToCameraMatrix);
        //Debug.Log("[Calib][OpenCV-RightHandedness] " + cam.transform.name + " Rotation Matrix:");
        //Debug.Log(ConvertUnityWorldToCameraRotationToOpenCV(cam.worldToCameraMatrix));
        //Debug.Log(cam.projectionMatrix);
    }

    /// <summary>
    /// This method indicate the coordinates of the project
    /// </summary>
    void GenerateMarkPoints()
    {
        markPoints = new Vector3[(2 * lengthOfMarkPointsSquare) * (2 * lengthOfMarkPointsSquare)];
        int index = 0;

        for (int i = -lengthOfMarkPointsSquare; i < lengthOfMarkPointsSquare; i++)
        {
            for (int j = -lengthOfMarkPointsSquare; j < lengthOfMarkPointsSquare; j++)
            {
                //Debug.Log(index);
                markPoints[index] = chessboardGenerateCenter.transform.position + new Vector3(i * gapBetweenMarkPoints, 0, j * gapBetweenMarkPoints);
                index++;
            }
        }
    }


    void GenerateValidatePoints() 
    {
        System.Random ran = new System.Random();
        validatePoints = new Vector3[markPoints.Length];
        for (int i = 0; i < validatePoints.Length; i++)
        {
            validatePoints[i] = new Vector3(markPoints[i].x + NextFloat(ran, -tRandomOffset*0.1f, tRandomOffset*0.1f), 0, markPoints[i].z + NextFloat(ran, -tRandomOffset * 0.1f, tRandomOffset * 0.1f));
        }
    }

    /// <summary>
    /// Generate the visual chessboard
    /// </summary>
    void GenerateVisualChessboard()
    {
        for (int w = 0; w < widthOfChessboard; w++)
        {
            for (int h = 0; h < heightOfChessboard; h++)
            {
                GameObject cornerPoint = new GameObject(w.ToString() + "_" + h.ToString());
                cornerPoint.transform.position = new Vector3(w * SQUARE_SIZE, 0, h * SQUARE_SIZE);
                cornerPoint.transform.parent = transform;
                cornerPointsDic.Add(cornerPoint, new Vector3(w * SQUARE_SIZE/Scaling, h * SQUARE_SIZE/Scaling, 0));
            }
        }
        gameObject.transform.position = chessboardGenerateCenter.transform.position;
        gameObject.transform.rotation = chessboardGenerateCenter.transform.rotation;
        //gameObject.transform.rotation = Quaternion.identity;
        //foreach (var go in markPointsDic)
        //{
        //Debug.Log(go.Key.transform.position);
        //}
    }

    void UpdateChessboard()
    {
        boardIndex++;
        System.Random ran = new System.Random();
        transform.position = new Vector3(NextFloat(ran, tRandomOffset, -tRandomOffset), NextFloat(ran, tRandomOffset, -tRandomOffset), NextFloat(ran, tRandomOffset, -tRandomOffset));
        transform.rotation = Quaternion.Euler(NextFloat(ran, rRandomOffset, -rRandomOffset), NextFloat(ran, rRandomOffset, -rRandomOffset), NextFloat(ran, rRandomOffset, -rRandomOffset));
    }

    void WriteDatasetParametersPy() 
    {
        string pyPath = targetParentFolder + "\\datasetParameters.py";
        if (File.Exists(pyPath))
        {
           File.Delete(pyPath);
        }

        FileInfo fileinfo = new FileInfo(pyPath);
        StreamWriter pysw = new StreamWriter(pyPath);

        pysw.WriteLine("GRID_ORIGIN = [" + gridOrigin.position.x.ToString() + "," + gridOrigin.position.y.ToString() + "," + gridOrigin.position.z.ToString() + "]");
        pysw.WriteLine("NUM_CAM = " + camerasToCalibrate.Count().ToString());
        pysw.WriteLine("CHESSBOARD_COUNT = " + chessboardCount.ToString());
        pysw.WriteLine(nameof(MAP_HEIGHT) + " = " +  MAP_HEIGHT.ToString());
        pysw.WriteLine(nameof(MAP_WIDTH) + " = " + MAP_WIDTH.ToString());
        pysw.WriteLine(nameof(MAP_EXPAND) + " = " + MAP_EXPAND.ToString());
        pysw.WriteLine(nameof(IMAGE_WIDTH) + " = " + IMAGE_WIDTH.ToString());
        pysw.WriteLine(nameof(IMAGE_HEIGHT) + " = " + IMAGE_HEIGHT.ToString());
        pysw.WriteLine(nameof(MAN_HEIGHT) + " = " + MAN_HEIGHT.ToString());
        pysw.WriteLine(nameof(MAN_RADIUS) + " = " + MAN_RADIUS.ToString());
        pysw.WriteLine(nameof(RJUST_WIDTH) + " = " + RJUST_WIDTH.ToString());
        pysw.WriteLine(nameof(Scaling) + "=" + Scaling.ToString()); 
        pysw.WriteLine(@"NUM_FRAMES = 0");
        pysw.WriteLine(@"DATASET_NAME = ''");
        pysw.Close();
    }

    void WriteWorldPointsScreenPos(Camera cam, int cameraIndex, Vector3[] arr, string name)
    {
        Vector2[] screenPoints = ConvertWorldPointsToScreenPointsOpenCV(arr, cam);
        List<Vector3> worldPointsList = arr.ToList(); // Convert arr1 to a List<Vector3>
        List<Vector2> screenPointsList = screenPoints.ToList(); // Convert arr2 to a List<Vector3>

        Rect screenBounds = new Rect(0, 0, Screen.width, Screen.height);

        for (int i = screenPointsList.Count - 1; i >= 0; i--)
        {
            if (!screenBounds.Contains(screenPoints[i]))
            {
                //Debug.Log("[Calib] Delete this : " + screenPoints[i]);
                worldPointsList.RemoveAt(i);
                screenPointsList.RemoveAt(i);
            }
        }

        Vector3[] worldPoints = worldPointsList.ToArray(); // Convert the List<Vector3> back to an array
        screenPoints = screenPointsList.ToArray();

        //for (int i = 0; i < worldPoints.Length; i++)
        //{
        //    float temp = worldPoints[i].y;
        //    worldPoints[i].y = worldPoints[i].z;
        //    worldPoints[i].z = temp + 5;
        //    worldPoints[i].x = worldPoints[i].x + 5;
        //}

        string file_name_3d = name + "_3d.txt";
        string file_name = name + ".txt";

        StreamWriter sw_3d = CreateSW(cameraIndex, file_name_3d);
        StreamWriter sw = CreateSW(cameraIndex, file_name);

        WriteArrayToFile(worldPoints, ref sw_3d);
        WriteArrayToFile(screenPoints, ref sw);

        sw_3d.Close();
        sw.Close();
    }

    void WriteChessboardScreenPos(Camera cam, int cameraIndex)
    {
        List<Vector2> screenPointsList = new List<Vector2>();
        List<Vector3> outPutObjList = new List<Vector3>();

        Rect screenBounds = new Rect(0, 0, Screen.width, Screen.height);

        foreach (var go in cornerPointsDic)
        {
            Vector2 viewPos = cam.WorldToScreenPoint(go.Key.transform.position);
            if (screenBounds.Contains(viewPos))
            {
                screenPointsList.Add(new Vector2(viewPos.x, Screen.height - viewPos.y));
                outPutObjList.Add(go.Value);
            }
        }

        Vector2[] imagePoints = screenPointsList.ToArray();

        string file_name = boardIndex + ".txt";
        string file_name_3d = boardIndex + "_3d.txt";

        StreamWriter sw = CreateSW(cameraIndex, file_name);
        StreamWriter sw_3d = CreateSW(cameraIndex, file_name_3d);
        WriteArrayToFile(imagePoints, ref sw);
        WriteArrayToFile(outPutObjList.ToArray(), ref sw_3d);

        sw.Close();
        sw_3d.Close();
    }

    public void ResetFolder(string foldername)
    {
        DirectoryInfo dir = new DirectoryInfo(foldername);

        if (dir.Exists)
        {
            dir.Delete(true);
            Debug.Log("[IO]" + foldername + " have been reset");
        }

    }

    StreamWriter CreateSW(int cameraIdx, string filename)
    {
        StreamWriter sw;
        cameraIdx++;

        Directory.CreateDirectory(targetParentFolder + "/C" + cameraIdx.ToString() + "/");
        FileInfo fileInfo = new FileInfo(targetParentFolder + "/C" + cameraIdx.ToString() + "/" + filename);
        if (!fileInfo.Exists)
        {
            sw = fileInfo.CreateText();
            if (enableLog)
            {
                Debug.Log("[IO]File " + filename + " has been inited");
            }

            return sw;
        }
        else
        {
            sw = fileInfo.AppendText();
            return sw;
        }
    }


    public void WriteArrayToFile(Vector2[] array, ref StreamWriter sw)
    {
        // Create a new StreamWriter to write the array to a text file

        // Loop through each element in the array and write it to the file
        foreach (Vector3 element in array)
        {
            sw.WriteLine(element.x + " " + element.y);
        }
        //Debug.Log("[IO]Vector3 array written to file: " + filename + ".txt");
    }

    public void WriteArrayToFile(Vector3[] array, ref StreamWriter sw)
    {
        // Create a new StreamWriter to write the array to a text file

        // Loop through each element in the array and write it to the file
        foreach (Vector3 element in array)
        {

            sw.WriteLine(element.x + " " + element.y + " " + element.z);
        }
        //Debug.Log("[IO]Vector3 array written to file: " + filename + ".txt");
    }

    public float NextFloat(System.Random ran, float minValue, float maxValue)
    {
        return (float)(ran.NextDouble() * (maxValue - minValue) + minValue);
    }

    public Vector2[] ConvertWorldPointsToScreenPointsOpenCV(Vector3[] worldPoints, Camera cam)
    {
        var points2D = new Vector2[worldPoints.Length];
        for (int i = 0; i < worldPoints.Length; i++)
        {

            points2D[i] = cam.WorldToScreenPoint(worldPoints[i]);
            points2D[i].y = cam.pixelHeight - points2D[i].y;
            //Debug.Log(points2D[i]);
            //Debug.Log(points2D[i]);
        }
        return points2D;

    }

    public Matrix4x4 ConvertUnityWorldToCameraRotationToOpenCV(Matrix4x4 worldToCameraMatrix)
    {
        // Convert the right-handed coordinate system to left-handed
        // by negating the z-axis
        worldToCameraMatrix.SetColumn(2, -worldToCameraMatrix.GetColumn(2));

        // Convert the left-handed rotation matrix to a right-handed
        // rotation matrix by reversing the order of the columns
        worldToCameraMatrix = new Matrix4x4(
            worldToCameraMatrix.GetColumn(0),
            worldToCameraMatrix.GetColumn(2),
            worldToCameraMatrix.GetColumn(1),
            new Vector4(0, 0, 0, 1)
        );

        return worldToCameraMatrix;
    }

    #region Gizmos
    private void OnDrawGizmos()
    {
        DrawChessboard();
        DrawGrid();
        DrawScaling();
        DrawMarkPoints();
    }

    void DrawChessboard() 
    {
        foreach (var go in cornerPointsDic)
        {
            Gizmos.color = new Color(1, 0, 0, 0.5f);
            Gizmos.DrawCube(go.Key.transform.position, new Vector3(0.01f, 0.01f, 0.01f));
            Handles.Label(go.Key.transform.position, go.Value.ToString());
        }
    }

    void DrawGrid()
    {
        if (gridOrigin == null) return;
        Gizmos.color = new Color(0, 0, 1, 1f);
        //Gizmos.DrawLine(gridOrigin.transform.position * Scaling, gridOrigin.transform.position * Scaling + MAP_HEIGHT * Scaling * Vector3.forward);
        Handles.Label(gridOrigin.transform.position + 3 * Vector3.forward, "Grid Height+");
        for (int i = 0; i < MAP_WIDTH + 1; i++)
        {
            Gizmos.DrawLine(gridOrigin.transform.position + new Vector3(i, 0, 0) * Scaling, gridOrigin.transform.position + MAP_HEIGHT * Scaling * Vector3.forward + new Vector3(i, 0, 0) * Scaling);
            Handles.Label(gridOrigin.transform.position + new Vector3(i, 0, 0) * Scaling, i.ToString());
            //for (int j = 1; j < MAP_EXPAND; j++)
            //{
            //    Gizmos.DrawLine(gridOrigin.transform.position + new Vector3(i + j * (1f / MAP_EXPAND), 0, 0), gridOrigin.transform.position + MAP_HEIGHT * Vector3.forward + new Vector3(i + j * (1f / MAP_EXPAND), 0, 0));
            //}
        }

        Gizmos.color = new Color(1, 0, 1, 1f);
        //Gizmos.DrawLine(gridOrigin.transform.position, gridOrigin.transform.position + MAP_WIDTH * Vector3.right);
        Handles.Label(gridOrigin.transform.position + 3 * Vector3.right, "Grid Width+");
        for (int i = 0; i < MAP_HEIGHT + 1; i++)
        {
            Gizmos.DrawLine(gridOrigin.transform.position + new Vector3(0,0,i) * Scaling, gridOrigin.transform.position + MAP_WIDTH * Scaling * Vector3.right + new Vector3(0, 0, i) * Scaling);
            Handles.Label(gridOrigin.transform.position + new Vector3(0, 0, i) * Scaling, i.ToString());
            //for (int j = 1; j < MAP_EXPAND; j++)
            //{
            //    Gizmos.DrawLine(gridOrigin.transform.position + new Vector3(0, 0, i + j * (1f / MAP_EXPAND)), gridOrigin.transform.position + MAP_WIDTH * Vector3.right + new Vector3(0, 0, i + j * (1f / MAP_EXPAND)));
            //}
        }
    }

    void DrawScaling() 
    {
        Gizmos.color = new Color(0, 1, 0, 1f);

        Vector3 footPos = gridOrigin.transform.position + new Vector3(MAP_WIDTH*0.5f, 0, MAP_HEIGHT * 0.5f) * Scaling;

        Handles.Label(footPos + Vector3.left * Scaling +  new Vector3(0, MAN_HEIGHT, 0) * Scaling, MAN_HEIGHT.ToString());
        Gizmos.DrawLine(footPos + Vector3.left * Scaling, footPos + Vector3.left * Scaling + new Vector3(0, MAN_HEIGHT, 0) * Scaling);
        Gizmos.DrawLine(footPos + Vector3.left * Scaling + Vector3.back * Scaling, footPos + Vector3.left * Scaling + Vector3.back * Scaling + new Vector3(0, MAN_HEIGHT, 0) * Scaling);
        Gizmos.DrawLine(footPos + Vector3.back * Scaling, footPos + Vector3.back * Scaling + new Vector3(0, MAN_HEIGHT, 0) * Scaling);
        Gizmos.DrawLine(footPos, footPos + new Vector3(0, MAN_HEIGHT, 0) * Scaling);
        Gizmos.DrawLine(footPos, footPos + Vector3.left * Scaling);
        Gizmos.DrawLine(footPos, footPos + Vector3.back * Scaling);
        Gizmos.DrawLine(footPos + Vector3.left * Scaling + Vector3.back * Scaling, footPos + Vector3.left * Scaling);
        Gizmos.DrawLine(footPos + Vector3.left * Scaling + Vector3.back * Scaling, footPos + Vector3.back * Scaling);
        Gizmos.DrawLine(footPos + new Vector3(0, MAN_HEIGHT, 0) * Scaling, footPos + Vector3.left * Scaling + new Vector3(0, MAN_HEIGHT, 0) * Scaling);



        for (int j = 0; j < MAP_EXPAND+ 1; j++)
        {
            Gizmos.DrawLine(footPos + new Vector3( -j * (1f / MAP_EXPAND), 0, 0) * Scaling, footPos +  Vector3.back*Scaling + new Vector3( - j * (1f / MAP_EXPAND), 0, 0) * Scaling);
            Gizmos.DrawLine(footPos + new Vector3(-j * (1f / MAP_EXPAND), 0, 0)* Scaling + new Vector3(0, MAN_HEIGHT, 0) * Scaling, footPos + Vector3.back * Scaling + new Vector3(0, MAN_HEIGHT, 0) * Scaling + new Vector3(-j * (1f / MAP_EXPAND), 0, 0) * Scaling);
        }

        if (Application.isPlaying)
        {
            if (go != null)
            {
                Destroy(go);
            }

            return;

        }

        if (!showModel)
        {
            if (go != null) 
            {
                go.SetActive(false);
            }

            GameObject[] modelgo = GameObject.FindGameObjectsWithTag("EditorOnly");
            foreach (var mgo in modelgo)
            { 
                mgo.SetActive(false);
                Destroy(mgo);
            }
            return;
        }
        else
        {
            if (go != null)
            {
                go.SetActive(true);
            }

        }

        if (humanModel != null && go == null)
        {
            go = Instantiate(humanModel, footPos + Vector3.left * 0.5f * Scaling + Vector3.back * 0.5f * Scaling, Quaternion.identity);
            go.transform.localScale = Vector3.one * Scaling;
            go.name = "Scaling Model";
            go.tag = "EditorOnly";
        }
        

    }

    void DrawMarkPoints() 
    {
        if (markPoints is null) return;

        foreach (var go in markPoints)
        {
            //Debug.Log(go);
            Gizmos.color = new Color(0, 1, 0, 0.4f);
            Gizmos.DrawCube(go*Scaling, new Vector3(0.01f, 0.01f, 0.01f));
            Handles.Label(go*Scaling, go.ToString());
        }
    }
    #endregion
}
