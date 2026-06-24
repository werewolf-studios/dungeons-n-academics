using Godot;
using Godot.Collections;
using System;

public partial class FileHandler : Node
{
    public static Error StoreJsonFile(Dictionary data, string filePath, bool createDir)
    {
        (Error, FileAccess) result = OpenFileForWrite(filePath, createDir);

        // result will return an array with an error code and a file access object
        Error error = result.Item1;
        FileAccess file = result.Item2;

        if (error != Error.Ok)
            return error;

        file.StoreString(Json.Stringify(data));
        file.Close();
        return Error.Ok;
    }

    public static Error StoreBinaryFile(Dictionary data, string filePath, bool createDir)
    {
        (Error, FileAccess) result = OpenFileForWrite(filePath, createDir);

        // result will return an array with an error code and a file access object
        Error error = result.Item1;
        FileAccess file = result.Item2;

        if (error != Error.Ok)
            return error;

        file.StoreVar(data, false);
        file.Close();
        return Error.Ok;
    }

    public static Error OpenJsonFile(string filePath, Dictionary outData)
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

        // Ovewrite the save data dictionary
        outData.Merge((Dictionary)jsonData, true);
        return Error.Ok;
    }

    public static Error OpenBinaryFile(string filePath, Dictionary outData)
    {
        outData.Clear();

        (Error, FileAccess) result = OpenFileForRead(filePath);
        Error error = result.Item1;
        FileAccess file = result.Item2;

        if (error != Error.Ok)
            return error;

        // Get the value and close the file
        Variant value = file.GetVar(false); // objects should never be allowed
        file.Close();

        // Verify the value is a dictionary
        if (value.VariantType != Variant.Type.Dictionary)
            return Error.InvalidData;

        // Ovewrite the save data dictionary
        outData.Merge((Dictionary)value, true);
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
