import 'artifact_type.dart';

class Artifact {
  final String id;

  final ArtifactType type;

  final String title;

  final String content;

  final String producer;

  final String summary;

  final Map<String, dynamic> metadata;

  final DateTime createdAt;

  const Artifact({
    required this.id,
    required this.type,
    this.title = '',
    required this.content,
    required this.producer,
    this.summary = '',
    this.metadata = const {},
    required this.createdAt,
  });
}
