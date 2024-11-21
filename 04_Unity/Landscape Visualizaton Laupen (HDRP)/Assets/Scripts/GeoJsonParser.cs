using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json.Linq;

public class GeoJsonParser
{
    public class GeoData
    {
        public List<Polygon> Polygons = new List<Polygon>();
    }

    public class Polygon
    {
        public List<Vector2> Coordinates = new List<Vector2>();
    }

    public static GeoData Parse(string geoJsonText)
    {
        GeoData geoData = new GeoData();

        // Parse the GeoJSON
        JObject geoJson = JObject.Parse(geoJsonText);
        JArray features = (JArray)geoJson["features"];

        foreach (JObject feature in features)
        {
            string geometryType = feature["geometry"]["type"].ToString();

            if (geometryType == "Polygon")
            {
                JArray coordinates = (JArray)feature["geometry"]["coordinates"][0];
                Polygon polygon = new Polygon();

                foreach (JArray coord in coordinates)
                {
                    float x = (float)coord[0]; // Longitude
                    float y = (float)coord[1]; // Latitude
                    polygon.Coordinates.Add(new Vector2(x, y));
                }

                geoData.Polygons.Add(polygon);
            }
        }

        return geoData;
    }
}
