using Godot;
using Godot.Collections;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;

public partial class FileHandler : Node
{
    /// <summary>
    /// Stores the PlayerSaveData object as a JSON file at the specified file path.
    /// </summary>
    /// <param name="data">The PlayerSaveData object to store</param>
    /// <param name="filePath">The path where the JSON file will be saved</param>
    /// <param name="createDir">Whether to create the directory if it doesn't exist</param>
    /// <returns>An Error describing the outcome</returns>
    public static Error StoreJsonFile(PlayerSaveDataModel data, string filePath, bool createDir)
    {
        (Error, FileAccess) result = OpenFileForWrite(filePath, createDir);

        // result will return an array with an error code and a file access object
        Error error = result.Item1;
        FileAccess file = result.Item2;

        if (error != Error.Ok)
            return error;
        
        // Storing the data as a JSON
        file.StoreString(JsonSerializer.Serialize(data));
        file.Close();

        return Error.Ok;
    }

    /// <summary>
    /// Stores the Dictionary object as a binary file at the specified file path.
    /// </summary>
    /// <param name="data">The Dictionary object to store</param>
    /// <param name="filePath">The path where the binary file will be saved</param>
    /// <param name="createDir">Whether to create the directory if it doesn't exist</param>
    /// <returns>An Error describing the outcome</returns>
    public static Error StoreBinaryFile(PlayerSaveDataModel data, string filePath, bool createDir)
    {
        (Error, FileAccess) result = OpenFileForWrite(filePath, createDir);

        // result will return an array with an error code and a file access object
        Error error = result.Item1;
        FileAccess file = result.Item2;

        if (error != Error.Ok)
            return error;

        // Converting the data into a JSON
        string json = JsonSerializer.Serialize(data);

        // Converting the JSON into bytes
        byte[] bytes = System.Text.Encoding.UTF8.GetBytes(json);

        // Storing the bytes
        bool success = file.StoreBuffer(bytes);

        if (!success)
        {
            file.Close();
            return Error.Failed;
        }

        file.Close();
        
        return Error.Ok;
    }

    /// <summary>
    /// Opens a JSON file and deserializes its contents into a PlayerSaveData object.
    /// </summary>
    /// <param name="filePath">The path of the JSON file</param>
    /// <param name="outData">The PlayerSaveData object to populate</param>
    /// <returns>An Error describing the outcome</returns>
    public static (Error, PlayerSaveDataModel) OpenJsonFile(string filePath)
    {
        
        //outData.Clear();

        (Error, FileAccess) result = OpenFileForRead(filePath);
        Error error = result.Item1;
        FileAccess file = result.Item2;

        if (error != Error.Ok)
            return (error, null);

        string json = file.GetAsText();

        PlayerSaveDataModel outData = JsonSerializer.Deserialize<PlayerSaveDataModel>(json);

        file.Close();

        return (Error.Ok, outData);
    }

    /// <summary>
    /// Opens a binary file and deserializes its contents into a PlayerSaveData object.
    /// </summary>
    /// <param name="filePath">The path of the binary file</param>
    /// <param name="outData">The PlayerSaveData object to populate</param>
    /// <returns>An Error describing the outcome</returns>
    public static (Error, PlayerSaveDataModel) OpenBinaryFile(string filePath)
    {
        (Error, FileAccess) result = OpenFileForRead(filePath);
        Error error = result.Item1;
        FileAccess file = result.Item2;

        if (error != Error.Ok)
            return (error, null);

        byte[] bytes = file.GetBuffer((long)file.GetLength());

        string json = System.Text.Encoding.UTF8.GetString(bytes);

        PlayerSaveDataModel outData = JsonSerializer.Deserialize<PlayerSaveDataModel>(json);

        file.Close();

        return (Error.Ok, outData);
    }

    /// <summary>
    /// Opens a JSON file containing questions and deserializes its contents into a dictionary of questions.
    /// </summary>
    /// <param name="filePath">The path of the JSON file</param>
    /// <param name="outData">The dictionary to populate with questions</param>
    /// <returns>An Error describing the outcome</returns>
    public static Error OpenJsonQuestionFile(string filePath, System.Collections.Generic.Dictionary<string, List<List<Question>>> outData)
    {
        outData.Clear();
        (Error, FileAccess) result = OpenFileForRead(filePath);
        Error error = result.Item1;
        FileAccess file = result.Item2;

        if (error != Error.Ok)
            return error;

        // Get the json as a string and close the file
        String jsonString = file.GetAsText();
        file.Close();

        // Parse the string into a json object and check for errors
        Json json = new Json();
        error = json.Parse(jsonString);
        if (error != Error.Ok)
            return error;

        // Get the dictionary data from the json object
        Variant jsonData = json.GetData();
        if (jsonData.VariantType != Variant.Type.Dictionary)
            return Error.InvalidData;

        var jsonDict = jsonData.AsGodotDictionary();

        // Loop through categories
        foreach(KeyValuePair<Variant, Variant> entry in jsonDict)
        {
            string category = entry.Key.AsString();
            var tierArray = entry.Value.AsGodotArray();

            List<List<Question>> questions = new List<List<Question>>();

            // Loop through tiers
            for (int i = 0; i < tierArray.Count; i++)
            {
                List<Question> tierQuestions = new List<Question>();
                 var questionArray = tierArray[i].AsGodotArray();

                // Loop through questions
                foreach (Variant item in questionArray)
                {
                    var qDict = item.AsGodotDictionary();

                    Question q = new Question
                    {
                        Problem = qDict["problem"].ToString(),
                        Answer = qDict["answer"].ToString(),
                        Wrong = qDict["wrong_answers"].AsStringArray(),
                    };

                    tierQuestions.Add(q);
                }
                questions.Add(tierQuestions);
            }
            outData.Add(category, questions);
        }

        return Error.Ok;
    }

    static (Error err, FileAccess file) OpenFileForWrite(string filePath, bool createDir)
    {
        Error error = CheckAndCreateDirectory(filePath, createDir);

        if (error != Error.Ok)
            return (error, null);

        FileAccess file = FileAccess.Open(filePath, FileAccess.ModeFlags.Write);

        if (file == null)
            return new(FileAccess.GetOpenError(), null);

        return new(Error.Ok, file);
    }

    static (Error err, FileAccess file) OpenFileForRead(string filePath)
    {
        if (!FileAccess.FileExists(filePath))
            return new(Error.FileNotFound, null);

        FileAccess file = FileAccess.Open(filePath, FileAccess.ModeFlags.Read);
        if (file == null)
            return new(FileAccess.GetOpenError(), null);

        return new(Error.Ok, file);
    }

    static Error CheckAndCreateDirectory(string filePath, bool create)
    {
        string dirPath = filePath.GetBaseDir();

        // Check if the file already exists
        if (DirAccess.DirExistsAbsolute(dirPath))
            return Error.Ok;

        if (!create)
            return Error.CantCreate;

        // Make the directory if it doesnt yet exist
        return DirAccess.MakeDirRecursiveAbsolute(dirPath);
    }
}
