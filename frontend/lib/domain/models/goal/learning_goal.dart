import 'goal_status.dart';

class LearningGoal {
  final String id;
  final String studentId;
  final String knowledgeNodeId;
  final String targetLevel;
  final GoalStatus status;
  final DateTime createdAt;
  final DateTime? completedAt;

  const LearningGoal({
    required this.id,
    required this.studentId,
    required this.knowledgeNodeId,
    required this.targetLevel,
    this.status = GoalStatus.notStarted,
    required this.createdAt,
    this.completedAt,
  });
}
