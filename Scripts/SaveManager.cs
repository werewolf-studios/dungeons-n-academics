using Godot;
//using Godot.Collections;
using System.Collections.Generic;

public partial class SaveManager : Node
{
    // A static instance of the save manager that can be used anywhere
    public static SaveManager Instance => (SaveManager)((SceneTree)Engine.GetMainLoop()).Root.GetNode("SaveManager");

    // The player data that will be saved/loaded and used for displaying information
    private static PlayerSaveData playerData = new PlayerSaveData();
    
    public PlayerSaveData PlayerData { get => playerData; set => playerData = value; }

    // Topic Dictionaries
    private Dictionary<string, List<List<QuestionFormat>>> mathQuestionsThirdGrade = new Dictionary<string, List<List<QuestionFormat>>>();

    public Dictionary<string, List<List<QuestionFormat>>> MathQuestionsThirdGrade { get => mathQuestionsThirdGrade; set => mathQuestionsThirdGrade = value; }

    private Dictionary<string, List<List<QuestionFormat>>> mathQuestionsEighthGrade = new Dictionary<string, List<List<QuestionFormat>>>();

    public Dictionary<string, List<List<QuestionFormat>>> MathQuestionsEighthGrade { get => mathQuestionsEighthGrade; set => mathQuestionsEighthGrade = value; }

    // Save file locations
    string SavePathJson = "user://savegame.json";
    string SavePathBinary = "user://savegame.save"; // can be any extension for binary

    // Question file locations
    string mathQuestionsThirdGradePathJson = "res://QuestionsFolder/ThirdGrade/math_questions.json";
    string mathQuestionsEighthGradePathJson = "res://QuestionsFolder/EighthGrade/math_questions.json";
    string historyQuestionsPathJson = "res://QuestionsFolder/history_questions.json"; // to be implemented

    // Saving

    /// <summary>
    /// Saves the Player Data into a json format with the help of the FileHandler
    /// </summary>
    public void SavePlayerDataJson()
    {

        Error Error = FileHandler.StoreJsonFile(playerData.Model, SavePathJson, true);
        if (Error != Error.Ok)
            GD.PushError("Failed to save player data to JSON file: " + Error);

    }

    /// <summary>
    /// Saves the Player Data into a binary format with the help of the FileHandler
    /// </summary>
    public void SavePlayerDataBinary()
    {
        
        Error Error = FileHandler.StoreBinaryFile(playerData.Model, SavePathBinary, true);
        if (Error != Error.Ok)
            GD.PushError("Failed to save player data to BINARY file: " + Error);
    }

    // Loading

    /// <summary>
    /// Loads the player data
    /// Not used because we are only loading using Binary
    /// </summary>
    public void LoadPlayerDataJson()
    {
        (Error, PlayerSaveDataModel) result = FileHandler.OpenBinaryFile(SavePathJson);
        Error error = result.Item1;
        PlayerSaveDataModel data = result.Item2;

        if (error != Error.Ok)
        {
            GD.PushError("Failed to load player data from JSON file: " + error);
            return;
        }

        playerData.SetModel(data);
    }

    /// <summary>
    /// Loads the player data from a binary file
    /// </summary>
    public void LoadPlayerDataBinary()
    {
        (Error, PlayerSaveDataModel) result = FileHandler.OpenBinaryFile(SavePathBinary);
        Error error = result.Item1;
        PlayerSaveDataModel data = result.Item2;

        if (error != Error.Ok)
        {
            GD.PushError("Failed to load player data from Binary file: " + error);
            return;
        }
        
        playerData.SetModel(data);
    }

    /// <summary>
    /// A helper method that loads the questions from the specified filepath.
    /// </summary>
    /// <param name="filePath">The path of the question file</param>
    /// <returns>A complex dictionary of questions</returns>
    private Dictionary<string, List<List<QuestionFormat>>> LoadQuestionDataFromFile(string filePath)
    {
        Dictionary<string, List<List<QuestionFormat>>> questionData = new() { };
        Error error = FileHandler.OpenJsonQuestionFile(filePath, questionData);
        if (error != Error.Ok)
        {
            GD.PushError("Failed to load player data from JSON file: " + error);
            return null;
        }

        return questionData;
    }

    // Loading the question data

    /// <summary>
    /// Loads all of the questions from the specified files
    /// </summary>
    public void LoadQuestionDataJson()
    {
        mathQuestionsThirdGrade = LoadQuestionDataFromFile(mathQuestionsThirdGradePathJson);
        MathQuestionsEighthGrade = LoadQuestionDataFromFile(mathQuestionsEighthGradePathJson);
        // historyQuestions = LoadQuestionDataFromFile(historyQuestionsPathJson); // to be implemented
    }
}