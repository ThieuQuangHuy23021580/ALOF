class LearningProgress {
  final int completedTopics;
  final int completedSessions;
  final int masteredTopics;
  final int currentStreak;
  final int totalLearningMinutes;
  final double overallMastery;

  const LearningProgress({
    this.completedTopics = 0,
    this.completedSessions = 0,
    this.masteredTopics = 0,
    this.currentStreak = 0,
    this.totalLearningMinutes = 0,
    this.overallMastery = 0.0,
  });
}
