using Godot;
using Godot.Collections;
using System.Collections.Generic;

public partial class SaveManager : Node
{
    public static SaveManager Instance => (SaveManager)((SceneTree)Engine.GetMainLoop()).Root.GetNode("SaveManager");

    const string KEY_BUTTON_CLICKS = "Total_Button_Clicks";

    private int totalButtonClicks = 0;
    public int TotalButtonClicks { get => totalButtonClicks; set => totalButtonClicks = value; }

    private System.Collections.Generic.Dictionary<string, List<Question>> questions = new System.Collections.Generic.Dictionary<string, List<Question>>();

    public System.Collections.Generic.Dictionary<string, List<Question>> Questions { get => questions; set => questions = value; }

    string SavePathJson = "user://save_files/savegame.json";
    string SavePathBinary = "user://save_files/savegame.save"; // can be any extension for binary
    string LoadQuestionPathJson = "user://save_files/questions.json";

    // Saving

    public void SavePlayerDataJson()
    {
        Dictionary saveData = new()
        {
            { KEY_BUTTON_CLICKS, totalButtonClicks }
        };

        Error Error = FileHandler.StoreJsonFile(saveData, SavePathJson, true);
        if (Error != Error.Ok)
            GD.PushError("Failed to save player data to JSON file: " + Error);

    }

    public void SavePlayerDataBinary()
    {
        Dictionary saveData = new()
        {
            { KEY_BUTTON_CLICKS, totalButtonClicks }
        };

        Error Error = FileHandler.StoreBinaryFile(saveData, SavePathBinary, true);
        if (Error != Error.Ok)
            GD.PushError("Failed to save player data to BINARY file: " + Error);
    }

    // Loading

    public void LoadPlayerDataJson()
    {
        Dictionary saveData = new() { };
        Error error = FileHandler.OpenJsonFile(SavePathJson, saveData);
        if (error != Error.Ok)
        {
            GD.PushError("Failed to load player data from JSON file: " + error);
            return;
        }

        error = VerifySaveDataJson(saveData);
        if (error != Error.Ok)
        {
            GD.PushError("Invalid save file structure");
            return;
        }

        totalButtonClicks = (int)saveData[KEY_BUTTON_CLICKS];
    }

    public void LoadPlayerDataBinary()
    {
        Dictionary saveData = new() { };
        Error error = FileHandler.OpenBinaryFile(SavePathBinary, saveData);
        if (error != Error.Ok)
        {
            GD.PushError("Failed to load player data from Binary file: " + error);
            return;
        }

        error = VerifySaveDataBinary(saveData);
        if (error != Error.Ok)
        {
            GD.PushError("Invalid save file structure");
            return;
        }

        totalButtonClicks = (int)saveData[KEY_BUTTON_CLICKS];
    }

    public void LoadQuestionDataJson()
    {
        System.Collections.Generic.Dictionary<string, List<Question>> questionData = new() { };
        Error error = FileHandler.OpenJsonQuestionFile(LoadQuestionPathJson, questionData);
        if (error != Error.Ok)
        {
            GD.PushError("Failed to load player data from JSON file: " + error);
            return;
        }

        //error = VerifySaveDataJson(questionData);
        if (error != Error.Ok)
        {
            GD.PushError("Invalid save file structure");
            return;
        }

        Questions = questionData;
    }

    // Verification
    private Error VerifySaveDataJson(Dictionary saveData)
    {
        if (!saveData.ContainsKey(KEY_BUTTON_CLICKS))
            return Error.DoesNotExist;
        return Error.Ok;
    }

    private Error VerifySaveDataBinary(Dictionary saveData)
    {
        if (!saveData.ContainsKey(KEY_BUTTON_CLICKS))
            return Error.DoesNotExist;
        return Error.Ok;
    }
}