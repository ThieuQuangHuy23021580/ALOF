class LearningProfile {
  final String currentLevel;
  final String targetLevel;
  final List<String> interests;
  final List<String> strengths;
  final List<String> weaknesses;
  final String preferredLanguage;

  const LearningProfile({
    this.currentLevel = '',
    this.targetLevel = '',
    this.interests = const [],
    this.strengths = const [],
    this.weaknesses = const [],
    this.preferredLanguage = 'vi',
  });
}
