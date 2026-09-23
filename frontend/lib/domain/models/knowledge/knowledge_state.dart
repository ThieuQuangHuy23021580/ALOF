import 'knowledge_level.dart';

class KnowledgeState {
  final String conceptId;

  final double mastery;

  final KnowledgeLevel level;

  final int attempts;

  final int correctAttempts;

  final double errorRate;

  final double recentAccuracy;

  final DateTime? lastInteractionAt;

  final Map<String, dynamic> metadata;

  const KnowledgeState({
    required this.conceptId,
    this.mastery = 0.0,
    this.level = KnowledgeLevel.beginner,
    this.attempts = 0,
    this.correctAttempts = 0,
    this.errorRate = 0.0,
    this.recentAccuracy = 0.0,
    this.lastInteractionAt,
    this.metadata = const {},
  });
}
