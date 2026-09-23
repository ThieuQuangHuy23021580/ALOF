import 'package:frontend/domain/models/student/learning_preference.dart';
import 'package:frontend/domain/models/student/learning_profile.dart';
import 'package:frontend/domain/models/student/learning_progress.dart';
import 'package:frontend/domain/models/student/student.dart';

import '../../data/api/api_client.dart';

class AlofRepository {
  final ApiClient api;

  const AlofRepository({required this.api});

  Future<Student> getStudent(String studentId) async {
    final json = await api.get('/api/v1/students/$studentId');

    return _studentFromJson(Map<String, dynamic>.from(json));
  }

  Future<Map<String, dynamic>> getJourney(String studentId) async {
    final json = await api.get('/api/v1/journey/$studentId');

    return Map<String, dynamic>.from(json);
  }

  Future<Map<String, dynamic>> getSessions(String studentId) async {
    final json = await api.get('/api/v1/sessions/$studentId');

    return Map<String, dynamic>.from(json);
  }

  Future<Map<String, dynamic>> getLedger(String studentId) async {
    final json = await api.get('/api/v1/ledger/$studentId');

    return Map<String, dynamic>.from(json);
  }

  Future<LearningPreference> getPreferences(String studentId) async {
    final json = await api.get('/api/v1/preferences/$studentId');

    return _preferenceFromJson(Map<String, dynamic>.from(json));
  }

  Future<LearningPreference> updatePreferences(
    String studentId,
    LearningPreference preference,
  ) async {
    final json = await api.put(
      '/api/v1/preferences/$studentId',
      body: {
        'preferred_outputs': preference.preferredOutputs,
        'preferred_difficulty': preference.preferredDifficulty,
        'preferred_pace': preference.preferredPace,
        'session_duration_minutes': preference.sessionDurationMinutes,
        'include_examples': preference.includeExamples,
        'include_quiz': preference.includeQuiz,
        'include_flashcards': preference.includeFlashcards,
        'include_summary': preference.includeSummary,
      },
    );

    return _preferenceFromJson(Map<String, dynamic>.from(json));
  }

  Future<Map<String, dynamic>> getLearningSession(String studentId) async {
    final json = await api.get('/api/v1/learning-sessions/$studentId');

    return Map<String, dynamic>.from(json);
  }

  Future<Map<String, dynamic>> createLearningSession({
    required String studentId,
    required String question,
    List<String> conceptIds = const [],
  }) async {
    final json = await api.post(
      '/api/v1/learning-sessions/$studentId',
      body: {
        'student_id': studentId,
        'question': question,
        'concept_ids': conceptIds,
      },
    );

    return Map<String, dynamic>.from(json);
  }

  Student _studentFromJson(Map<String, dynamic> json) {
    return Student(
      id: json['id'] as String,
      displayName: json['display_name'] as String,
      learningProfile: _profileFromJson(
        Map<String, dynamic>.from(json['learning_profile'] ?? {}),
      ),
      learningPreference: _preferenceFromJson(
        Map<String, dynamic>.from(json['learning_preference'] ?? {}),
      ),
      learningProgress: _progressFromJson(
        Map<String, dynamic>.from(json['learning_progress'] ?? {}),
      ),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  LearningProfile _profileFromJson(Map<String, dynamic> json) {
    return LearningProfile(
      currentLevel: json['current_level'] as String? ?? '',
      targetLevel: json['target_level'] as String? ?? '',
      interests: List<String>.from(json['interests'] ?? const []),
      strengths: List<String>.from(json['strengths'] ?? const []),
      weaknesses: List<String>.from(json['weaknesses'] ?? const []),
      preferredLanguage: json['preferred_language'] as String? ?? 'vi',
    );
  }

  LearningProgress _progressFromJson(Map<String, dynamic> json) {
    return LearningProgress(
      completedTopics: json['completed_topics'] as int? ?? 0,
      completedSessions: json['completed_sessions'] as int? ?? 0,
      masteredTopics: json['mastered_topics'] as int? ?? 0,
      currentStreak: json['current_streak'] as int? ?? 0,
      totalLearningMinutes: json['total_learning_minutes'] as int? ?? 0,
      overallMastery: (json['overall_mastery'] as num?)?.toDouble() ?? 0.0,
    );
  }

  LearningPreference _preferenceFromJson(Map<String, dynamic> json) {
    return LearningPreference(
      preferredOutputs: List<String>.from(
        json['preferred_outputs'] ?? const [],
      ),
      preferredDifficulty:
          json['preferred_difficulty'] as String? ?? 'adaptive',
      preferredPace: json['preferred_pace'] as String? ?? 'adaptive',
      sessionDurationMinutes: json['session_duration_minutes'] as int? ?? 30,
      includeExamples: json['include_examples'] as bool? ?? true,
      includeQuiz: json['include_quiz'] as bool? ?? true,
      includeFlashcards: json['include_flashcards'] as bool? ?? true,
      includeSummary: json['include_summary'] as bool? ?? true,
    );
  }
}
