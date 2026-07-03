using Godot;
//using Godot.Collections;
using System.Collections.Generic;

public partial class SaveManager : Node
{
    public static SaveManager Instance => (SaveManager)((SceneTree)Engine.GetMainLoop()).Root.GetNode("SaveManager");

    const string KEY_BUTTON_CLICKS = "Total_Button_Clicks";

    private int totalButtonClicks = 0;
    public int TotalButtonClicks { get => totalButtonClicks; set => totalButtonClicks = value; }

    // Subject Dictionaries
    private Dictionary<string, List<List<Question>>> mathQuestions = new Dictionary<string, List<List<Question>>>();

    public Dictionary<string, List<List<Question>>> MathQuestions { get => mathQuestions; set => mathQuestions = value; }

    // Save file locations
    string SavePathJson = "user://save_files/savegame.json";
    string SavePathBinary = "user://save_files/savegame.save"; // can be any extension for binary

    // Question file locations
    string mathQuestionsPathJson = "user://save_files/math_questions.json";
    string historyQuestionsPathJson = "user://save_files/history_questions.json"; // to be implemented

    // Saving

    public void SavePlayerDataJson()
    {
        Godot.Collections.Dictionary saveData = new()
        {
            { KEY_BUTTON_CLICKS, totalButtonClicks }
        };

        Error Error = FileHandler.StoreJsonFile(saveData, SavePathJson, true);
        if (Error != Error.Ok)
            GD.PushError("Failed to save player data to JSON file: " + Error);

    }

    public void SavePlayerDataBinary()
    {
        Godot.Collections.Dictionary saveData = new()
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
        Godot.Collections.Dictionary saveData = new() { };
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
        Godot.Collections.Dictionary saveData = new() { };
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

    private Dictionary<string, List<List<Question>>> LoadQuestionDataFromFile(string filePath)
    {
        Dictionary<string, List<List<Question>>> questionData = new() { };
        Error error = FileHandler.OpenJsonQuestionFile(filePath, questionData);
        if (error != Error.Ok)
        {
            GD.PushError("Failed to load player data from JSON file: " + error);
            return null;
        }

        //error = VerifySaveDataJson(questionData);
        if (error != Error.Ok)
        {
            GD.PushError("Invalid save file structure");
            return null;
        }

        return questionData;
    }

    // Loading the question data
    public void LoadQuestionDataJson()
    {
        mathQuestions = LoadQuestionDataFromFile(mathQuestionsPathJson);
        // historyQuestions = LoadQuestionDataFromFile(historyQuestionsPathJson); // to be implemented
    }

    // Verification
    private Error VerifySaveDataJson(Godot.Collections.Dictionary saveData)
    {
        if (!saveData.ContainsKey(KEY_BUTTON_CLICKS))
            return Error.DoesNotExist;
        return Error.Ok;
    }

    private Error VerifySaveDataBinary(Godot.Collections.Dictionary saveData)
    {
        if (!saveData.ContainsKey(KEY_BUTTON_CLICKS))
            return Error.DoesNotExist;
        return Error.Ok;
    }
}