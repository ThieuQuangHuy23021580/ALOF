enum TeachingActionType {
  introduce('introduce'),
  explain('explain'),
  scaffold('scaffold'),
  practice('practice'),
  review('review'),
  challenge('challenge');

  final String value;

  const TeachingActionType(this.value);

  static TeachingActionType fromValue(String value) {
    return TeachingActionType.values.firstWhere(
      (action) => action.value == value,
      orElse: () => TeachingActionType.review,
    );
  }
}

enum TeachingStrategy {
  directExplanation('direct_explanation'),
  guidedExplanation('guided_explanation'),
  stepByStep('step_by_step'),
  targetedPractice('targeted_practice'),
  spacedReview('spaced_review'),
  deepening('deepening');

  final String value;

  const TeachingStrategy(this.value);

  static TeachingStrategy fromValue(String value) {
    return TeachingStrategy.values.firstWhere(
      (strategy) => strategy.value == value,
      orElse: () => TeachingStrategy.directExplanation,
    );
  }
}

class AdaptiveTeachingAction {
  final TeachingActionType action;

  final TeachingStrategy strategy;

  final String difficulty;

  final List<String> focusConcepts;

  final String reason;

  final Map<String, dynamic> metadata;

  const AdaptiveTeachingAction({
    required this.action,
    required this.strategy,
    this.difficulty = 'medium',
    this.focusConcepts = const [],
    this.reason = '',
    this.metadata = const {},
  });

  bool get hasFocus => focusConcepts.isNotEmpty;
}
