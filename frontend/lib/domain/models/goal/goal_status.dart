enum GoalStatus {
  notStarted('not_started'),
  inProgress('in_progress'),
  completed('completed'),
  paused('paused'),
  cancelled('cancelled');

  final String value;

  const GoalStatus(this.value);

  static GoalStatus fromValue(String value) {
    return GoalStatus.values.firstWhere(
      (status) => status.value == value,
      orElse: () => GoalStatus.notStarted,
    );
  }
}
