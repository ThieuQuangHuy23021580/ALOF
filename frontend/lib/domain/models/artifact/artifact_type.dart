enum ArtifactType {
  response('response'),
  lesson('lesson'),
  research('research'),
  summary('summary'),
  roadmap('roadmap'),
  quiz('quiz'),
  flashcard('flashcard');

  final String value;

  const ArtifactType(this.value);

  static ArtifactType fromValue(String value) {
    return ArtifactType.values.firstWhere(
      (type) => type.value == value,
      orElse: () => ArtifactType.response,
    );
  }

  static Set<String> get valuesSet {
    return ArtifactType.values.map((type) => type.value).toSet();
  }

  static bool exists(String value) {
    return valuesSet.contains(value);
  }
}
