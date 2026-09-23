enum KnowledgeLevel {
  beginner('beginner'),
  intermediate('intermediate'),
  advanced('advanced');

  final String value;

  const KnowledgeLevel(this.value);

  static KnowledgeLevel fromValue(String value) {
    return KnowledgeLevel.values.firstWhere(
      (level) => level.value == value,
      orElse: () => KnowledgeLevel.beginner,
    );
  }
}
