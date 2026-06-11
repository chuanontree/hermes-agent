// ClaudeBridge — 批次模式場景建造橋接
// 用法: Unity.exe -batchmode -quit -projectPath <proj> -executeMethod ClaudeBridge.BuildScene
// 讀取專案根目錄的 claude_scene.json，重建 Assets/Scenes/<sceneName>.unity
using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ClaudeBridge
{
    public static void BuildScene()
    {
        try
        {
            string jsonPath = Path.Combine(Directory.GetCurrentDirectory(), "claude_scene.json");
            if (!File.Exists(jsonPath))
                throw new Exception("claude_scene.json not found at project root");

            var root = MiniJson.Parse(File.ReadAllText(jsonPath)) as Dictionary<string, object>;
            string sceneName = root.TryGetValue("sceneName", out var sn) ? (string)sn : "Main";

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var objects = root["objects"] as List<object>;
            var byName = new Dictionary<string, GameObject>();

            foreach (var entry in objects)
            {
                var o = entry as Dictionary<string, object>;
                GameObject go = CreateObject(o);
                byName[go.name] = go;
            }
            // 第二輪處理 parent，確保父物件都已存在
            foreach (var entry in objects)
            {
                var o = entry as Dictionary<string, object>;
                if (o.TryGetValue("parent", out var p) && byName.TryGetValue((string)p, out var parentGo))
                    byName[(string)o["name"]].transform.SetParent(parentGo.transform, true);
            }

            Directory.CreateDirectory("Assets/Scenes");
            string scenePath = $"Assets/Scenes/{sceneName}.unity";
            EditorSceneManager.SaveScene(scene, scenePath);
            AssetDatabase.SaveAssets();
            Debug.Log($"[ClaudeBridge] DONE scene={scenePath} objects={objects.Count}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[ClaudeBridge] FAILED: {e}");
            EditorApplication.Exit(1);
        }
    }

    static GameObject CreateObject(Dictionary<string, object> o)
    {
        string name = (string)o["name"];
        GameObject go;

        if (o.TryGetValue("light", out var lightType))
        {
            go = new GameObject(name);
            var light = go.AddComponent<Light>();
            light.type = (LightType)Enum.Parse(typeof(LightType), (string)lightType);
            if (o.TryGetValue("intensity", out var inten)) light.intensity = ToF(inten);
        }
        else if (o.ContainsKey("camera"))
        {
            go = new GameObject(name);
            go.AddComponent<Camera>();
            go.AddComponent<AudioListener>();
            go.tag = "MainCamera";
        }
        else if (o.TryGetValue("primitive", out var prim))
        {
            go = GameObject.CreatePrimitive((PrimitiveType)Enum.Parse(typeof(PrimitiveType), (string)prim));
            go.name = name;
        }
        else
        {
            go = new GameObject(name); // empty
        }

        if (o.TryGetValue("position", out var pos)) go.transform.position = ToV3(pos);
        if (o.TryGetValue("rotation", out var rot)) go.transform.eulerAngles = ToV3(rot);
        if (o.TryGetValue("scale", out var scl)) go.transform.localScale = ToV3(scl);

        if (o.TryGetValue("lookAt", out var look))
            go.transform.LookAt(ToV3(look));

        if (o.TryGetValue("color", out var col))
        {
            var renderer = go.GetComponent<Renderer>();
            if (renderer != null)
            {
                var shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
                var mat = new Material(shader);
                var c = ToV3(col);
                mat.color = new Color(c.x, c.y, c.z);
                Directory.CreateDirectory("Assets/Materials");
                AssetDatabase.CreateAsset(mat, $"Assets/Materials/{name}Mat.mat");
                renderer.sharedMaterial = mat;
            }
        }

        if (o.TryGetValue("rigidbody", out var rb))
        {
            var body = go.AddComponent<Rigidbody>();
            if (rb is Dictionary<string, object> rbo)
            {
                if (rbo.TryGetValue("mass", out var m)) body.mass = ToF(m);
                if (rbo.TryGetValue("kinematic", out var k)) body.isKinematic = (bool)k;
            }
        }

        if (o.TryGetValue("components", out var comps))
        {
            foreach (var compName in (List<object>)comps)
            {
                var type = FindType((string)compName);
                if (type == null)
                    throw new Exception($"Component type not found: {compName} (確認 Assets/Scripts 下有同名類別且無編譯錯誤)");
                go.AddComponent(type);
            }
        }
        return go;
    }

    static Type FindType(string name)
    {
        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
        {
            var t = asm.GetType(name);
            if (t != null) return t;
        }
        return null;
    }

    static Vector3 ToV3(object v)
    {
        var list = (List<object>)v;
        return new Vector3(ToF(list[0]), ToF(list[1]), ToF(list[2]));
    }

    static float ToF(object v) => Convert.ToSingle(v);
}

// 極簡 JSON parser（僅支援本橋接需要的物件/陣列/字串/數字/布林）
public static class MiniJson
{
    public static object Parse(string json)
    {
        int i = 0;
        return ParseValue(json, ref i);
    }

    static object ParseValue(string s, ref int i)
    {
        SkipWs(s, ref i);
        char c = s[i];
        if (c == '{') return ParseObject(s, ref i);
        if (c == '[') return ParseArray(s, ref i);
        if (c == '"') return ParseString(s, ref i);
        if (c == 't') { i += 4; return true; }
        if (c == 'f') { i += 5; return false; }
        if (c == 'n') { i += 4; return null; }
        return ParseNumber(s, ref i);
    }

    static Dictionary<string, object> ParseObject(string s, ref int i)
    {
        var d = new Dictionary<string, object>();
        i++; // {
        SkipWs(s, ref i);
        if (s[i] == '}') { i++; return d; }
        while (true)
        {
            SkipWs(s, ref i);
            string key = ParseString(s, ref i);
            SkipWs(s, ref i);
            i++; // :
            d[key] = ParseValue(s, ref i);
            SkipWs(s, ref i);
            if (s[i] == ',') { i++; continue; }
            i++; // }
            return d;
        }
    }

    static List<object> ParseArray(string s, ref int i)
    {
        var list = new List<object>();
        i++; // [
        SkipWs(s, ref i);
        if (s[i] == ']') { i++; return list; }
        while (true)
        {
            list.Add(ParseValue(s, ref i));
            SkipWs(s, ref i);
            if (s[i] == ',') { i++; continue; }
            i++; // ]
            return list;
        }
    }

    static string ParseString(string s, ref int i)
    {
        var sb = new System.Text.StringBuilder();
        i++; // "
        while (s[i] != '"')
        {
            if (s[i] == '\\') { i++; sb.Append(s[i] == 'n' ? '\n' : s[i]); }
            else sb.Append(s[i]);
            i++;
        }
        i++; // "
        return sb.ToString();
    }

    static object ParseNumber(string s, ref int i)
    {
        int start = i;
        while (i < s.Length && ("-+.eE0123456789".IndexOf(s[i]) >= 0)) i++;
        return double.Parse(s.Substring(start, i - start),
            System.Globalization.CultureInfo.InvariantCulture);
    }

    static void SkipWs(string s, ref int i)
    {
        while (i < s.Length && char.IsWhiteSpace(s[i])) i++;
    }
}
