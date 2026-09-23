class LearningInteraction {
  final String id;

  final String learnerId;

  final String? questionId;

  final String question;

  final String answer;

  final bool? correct;

  final List<String> conceptIds;

  final DateTime timestamp;

  final Map<String, dynamic> metadata;

  const LearningInteraction({
    required this.id,
    required this.learnerId,
    this.questionId,
    this.question = '',
    this.answer = '',
    this.correct,
    this.conceptIds = const [],
    required this.timestamp,
    this.metadata = const {},
  });
}
