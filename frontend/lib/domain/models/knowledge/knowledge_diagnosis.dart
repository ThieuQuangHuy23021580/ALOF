import '../learning/concept_diagnosis.dart';

class KnowledgeDiagnosis {
  final String learnerId;

  final String currentQuestion;

  final Map<String, ConceptDiagnosis> concepts;

  final List<String> primaryConcepts;

  final List<String> weakConcepts;

  final List<String> transferDeficitConcepts;

  final Map<String, dynamic> metadata;

  const KnowledgeDiagnosis({
    required this.learnerId,
    this.currentQuestion = '',
    this.concepts = const {},
    this.primaryConcepts = const [],
    this.weakConcepts = const [],
    this.transferDeficitConcepts = const [],
    this.metadata = const {},
  });

  int get conceptCount => concepts.length;

  bool get hasWeakness => weakConcepts.isNotEmpty;

  bool get hasTransferDeficit => transferDeficitConcepts.isNotEmpty;

  ConceptDiagnosis? getConcept(String conceptId) {
    return concepts[conceptId];
  }
}
