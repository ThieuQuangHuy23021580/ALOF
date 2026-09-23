import '../learning/adaptive_teaching_action.dart';

class WorkflowNode {
  final String id;
  final String componentId;
  final String objective;
  final String expectedOutput;
  final List<String> dependsOn;

  final TeachingActionType? action;
  final TeachingStrategy? strategy;
  final String? difficulty;
  final List<String> focusConcepts;

  final Map<String, dynamic> metadata;

  const WorkflowNode({
    required this.id,
    required this.componentId,
    required this.objective,
    this.expectedOutput = '',
    this.dependsOn = const [],
    this.action,
    this.strategy,
    this.difficulty,
    this.focusConcepts = const [],
    this.metadata = const {},
  });

  bool get hasAdaptiveAction {
    return action != null && strategy != null;
  }
}
