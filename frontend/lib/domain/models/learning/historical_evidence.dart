import 'learning_interaction.dart';

class HistoricalEvidence {
  final String learnerId;

  final String currentQuestion;

  final List<LearningInteraction> relevantInteractions;

  final List<LearningInteraction> recentInteractions;

  final List<LearningInteraction> relatedInteractions;

  final List<String> relatedConceptIds;

  final Map<String, dynamic> metadata;

  final DateTime createdAt;

  const HistoricalEvidence({
    required this.learnerId,
    this.currentQuestion = '',
    this.relevantInteractions = const [],
    this.recentInteractions = const [],
    this.relatedInteractions = const [],
    this.relatedConceptIds = const [],
    this.metadata = const {},
    required this.createdAt,
  });

  bool get hasEvidence {
    return relevantInteractions.isNotEmpty ||
        recentInteractions.isNotEmpty ||
        relatedInteractions.isNotEmpty;
  }

  int get interactionCount {
    return relevantInteractions.length +
        recentInteractions.length +
        relatedInteractions.length;
  }
}
