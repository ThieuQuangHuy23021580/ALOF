import 'learning_preference.dart';
import 'learning_profile.dart';
import 'learning_progress.dart';

class Student {
  final String id;
  final String displayName;
  final LearningProfile learningProfile;
  final LearningPreference learningPreference;
  final LearningProgress learningProgress;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Student({
    required this.id,
    required this.displayName,
    required this.learningProfile,
    required this.learningPreference,
    required this.learningProgress,
    required this.createdAt,
    required this.updatedAt,
  });
}
