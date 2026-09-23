import 'package:frontend/domain/models/knowledge/knowledge_level.dart';

class ConceptDiagnosis {
  final String conceptId;

  final double mastery;

  final KnowledgeLevel level;

  final int attempts;

  final int correctAttempts;

  final double accuracy;

  final double errorRate;

  final int evidenceCount;

  final bool hasRecentEvidence;

  final bool hasRelevantEvidence;

  final bool weaknessSignal;

  final bool transferDeficitSignal;

  const ConceptDiagnosis({
    required this.conceptId,
    this.mastery = 0.0,
    this.level = KnowledgeLevel.beginner,
    this.attempts = 0,
    this.correctAttempts = 0,
    this.accuracy = 0.0,
    this.errorRate = 0.0,
    this.evidenceCount = 0,
    this.hasRecentEvidence = false,
    this.hasRelevantEvidence = false,
    this.weaknessSignal = false,
    this.transferDeficitSignal = false,
  });
}
