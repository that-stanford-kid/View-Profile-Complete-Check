using System.Collections.Generic;

public class Program {
    public string TournamentWinner(List<List<string>> competitions, List<int> results) {
        Dictionary<string, int> teamScores = new Dictionary<string, int>();
        string currentBestTeam = "";
        teamScores[currentBestTeam] = 0;
        for (int idx = 0; idx < competitions.Count; idx++) {
            List<string> competition = competitions[idx];
            int result = results[idx];
            string homeTeam = competition[0];
            string awayTeam = competition[1];
            string winningTeam = (result == 1) ? homeTeam : awayTeam;
            if (!teamScores.ContainsKey(winningTeam)) {
                teamScores[winningTeam] = 0;
            }
            teamScores[winningTeam] += 3;
            if (teamScores[winningTeam] > teamScores[currentBestTeam]) {
                currentBestTeam = winningTeam;
            }
        }
        return currentBestTeam;
    }
}
// iterative mem on completetions total
