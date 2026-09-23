class LearningPreference {
  final List<String> preferredOutputs;
  final String preferredDifficulty;
  final String preferredPace;
  final int sessionDurationMinutes;
  final bool includeExamples;
  final bool includeQuiz;
  final bool includeFlashcards;
  final bool includeSummary;

  const LearningPreference({
    this.preferredOutputs = const [],
    this.preferredDifficulty = 'adaptive',
    this.preferredPace = 'adaptive',
    this.sessionDurationMinutes = 30,
    this.includeExamples = true,
    this.includeQuiz = true,
    this.includeFlashcards = true,
    this.includeSummary = true,
  });
}
