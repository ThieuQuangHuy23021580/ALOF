import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../domain/data/repositories/alof_repository.dart';
import '../theme/app_theme.dart';

class SessionsScreen extends StatefulWidget {
  const SessionsScreen({super.key});

  @override
  State<SessionsScreen> createState() => _SessionsScreenState();
}

class _SessionsScreenState extends State<SessionsScreen> {
  static const String studentId = 'student-demo';

  late Future<Map<String, dynamic>> _sessionsFuture;
  int selectedSession = 0;

  @override
  void initState() {
    super.initState();

    _sessionsFuture = context.read<AlofRepository>().getSessions(studentId);
  }

  Future<void> _reload() async {
    setState(() {
      selectedSession = 0;
      _sessionsFuture = context.read<AlofRepository>().getSessions(studentId);
    });

    await _sessionsFuture;
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: _sessionsFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return _buildLoading();
        }

        if (snapshot.hasError) {
          return _buildError(snapshot.error);
        }

        final data = snapshot.data ?? {};
        final sessions = _parseSessions(data);

        if (sessions.isEmpty) {
          return _buildEmpty();
        }

        final safeIndex = selectedSession >= sessions.length
            ? 0
            : selectedSession;

        final current = sessions[safeIndex];

        return RefreshIndicator(
          color: ALOFColors.terracotta,
          onRefresh: _reload,
          child: _buildContent(sessions: sessions, current: current),
        );
      },
    );
  }

  List<SessionItem> _parseSessions(Map<String, dynamic> data) {
    final rawHistory = data['history'];

    if (rawHistory is! List) {
      return [];
    }

    return rawHistory
        .whereType<Map>()
        .map((item) => SessionItem.fromJson(Map<String, dynamic>.from(item)))
        .toList();
  }

  Widget _buildLoading() {
    return const Center(
      child: CircularProgressIndicator(color: ALOFColors.terracotta),
    );
  }

  Widget _buildError(Object? error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: ALOFColors.surface,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: ALOFColors.borderSubtle),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.cloud_off_outlined,
                  size: 32,
                  color: ALOFColors.terracotta,
                ),
                const SizedBox(height: 16),
                const Text(
                  'Unable to load sessions',
                  style: TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 24,
                    color: ALOFColors.primary,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  error?.toString() ?? 'Unknown error.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 14,
                    height: 1.5,
                    color: ALOFColors.onSurfaceMuted,
                  ),
                ),
                const SizedBox(height: 20),
                OutlinedButton(onPressed: _reload, child: const Text('RETRY')),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmpty() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Container(
          width: double.infinity,
          constraints: const BoxConstraints(maxWidth: 700),
          padding: const EdgeInsets.all(40),
          decoration: BoxDecoration(
            color: ALOFColors.surface,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: ALOFColors.borderSubtle),
          ),
          child: const Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.menu_book_outlined, size: 34, color: ALOFColors.taupe),
              SizedBox(height: 16),
              Text(
                'No learning sessions yet',
                style: TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 28,
                  color: ALOFColors.primary,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'Your learning sessions will appear here after you start learning with ALOF.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 15,
                  height: 1.5,
                  color: ALOFColors.onSurfaceMuted,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildContent({
    required List<SessionItem> sessions,
    required SessionItem current,
  }) {
    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(24, 32, 24, 48),
            child: Column(
              children: [
                _buildPageIntro(),
                const SizedBox(height: 32),
                LayoutBuilder(
                  builder: (context, constraints) {
                    if (constraints.maxWidth < 850) {
                      return Column(
                        children: [
                          _buildSessionHistory(sessions),
                          const SizedBox(height: 24),
                          _buildCurrentSession(current),
                        ],
                      );
                    }

                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          flex: 5,
                          child: _buildSessionHistory(sessions),
                        ),
                        const SizedBox(width: 32),
                        Expanded(flex: 7, child: _buildCurrentSession(current)),
                      ],
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPageIntro() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: ALOFColors.surfaceLow,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: ALOFColors.borderSubtle),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.circle, size: 6, color: ALOFColors.terracotta),
              SizedBox(width: 8),
              Text(
                'LEARNING SESSIONS',
                style: TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 11,
                  letterSpacing: 1.2,
                  fontWeight: FontWeight.w600,
                  color: ALOFColors.taupe,
                ),
              ),
            ],
          ),
          SizedBox(height: 8),
          Text(
            'Learning Sessions',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 36,
              fontWeight: FontWeight.w400,
              color: ALOFColors.primary,
            ),
          ),
          SizedBox(height: 6),
          Text(
            'Review past sessions and continue your active learning session.',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 16,
              height: 1.5,
              color: ALOFColors.onSurfaceMuted,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSessionHistory(List<SessionItem> sessions) {
    return Container(
      decoration: BoxDecoration(
        color: ALOFColors.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: ALOFColors.borderSubtle),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: [
          _sectionHeader(
            icon: Icons.history_edu,
            title: 'SESSION HISTORY',
            trailing: '${sessions.length} RECORDS',
          ),
          Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                ...List.generate(
                  sessions.length,
                  (index) => Padding(
                    padding: EdgeInsets.only(
                      bottom: index == sessions.length - 1 ? 0 : 16,
                    ),
                    child: _sessionCard(sessions[index], index),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _sectionHeader({
    required IconData icon,
    required String title,
    required String trailing,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: ALOFColors.surfaceLow,
        border: Border(bottom: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: Row(
        children: [
          Icon(icon, size: 20, color: ALOFColors.taupe),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                fontFamily: 'JetBrains Mono',
                fontSize: 11,
                letterSpacing: 1.1,
                fontWeight: FontWeight.w700,
                color: ALOFColors.onSurface,
              ),
            ),
          ),
          Text(
            trailing,
            style: const TextStyle(
              fontFamily: 'JetBrains Mono',
              fontSize: 10,
              letterSpacing: .8,
              color: ALOFColors.taupe,
            ),
          ),
        ],
      ),
    );
  }

  Widget _sessionCard(SessionItem session, int index) {
    final selected = selectedSession == index;

    return InkWell(
      onTap: () {
        setState(() {
          selectedSession = index;
        });
      },
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: selected ? ALOFColors.terracottaLight : ALOFColors.surface,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: selected
                ? ALOFColors.terracotta.withValues(alpha: .35)
                : ALOFColors.borderSubtle,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                if (selected) ...[
                  const Icon(
                    Icons.circle,
                    size: 8,
                    color: ALOFColors.terracotta,
                  ),
                  const SizedBox(width: 8),
                ],
                _tag(session.type, current: selected),
                const Spacer(),
                Text(
                  session.time,
                  style: const TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 10,
                    color: ALOFColors.taupe,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              session.title,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontFamily: 'Newsreader',
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: ALOFColors.onSurface,
              ),
            ),
            const SizedBox(height: 3),
            Text(
              session.subtitle,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontFamily: 'Newsreader',
                fontSize: 13,
                height: 1.4,
                color: ALOFColors.onSurfaceMuted,
              ),
            ),
            const SizedBox(height: 10),
            Divider(
              height: 1,
              color: ALOFColors.borderSubtle.withValues(alpha: .7),
            ),
            const SizedBox(height: 9),
            Row(
              children: [
                Expanded(
                  child: Text(
                    session.activity,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontFamily: 'JetBrains Mono',
                      fontSize: 10,
                      color: ALOFColors.taupe,
                    ),
                  ),
                ),
                Text(
                  session.status,
                  style: const TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 13,
                    color: ALOFColors.taupe,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _tag(String text, {bool current = false}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 4),
      decoration: BoxDecoration(
        color: current ? ALOFColors.terracottaLight : ALOFColors.surfaceLow,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text.toUpperCase(),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: TextStyle(
          fontFamily: 'JetBrains Mono',
          fontSize: 10,
          letterSpacing: .7,
          fontWeight: FontWeight.w600,
          color: current ? ALOFColors.terracottaDark : ALOFColors.taupe,
        ),
      ),
    );
  }

  Widget _buildCurrentSession(SessionItem session) {
    return Container(
      decoration: BoxDecoration(
        color: ALOFColors.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: ALOFColors.borderSubtle),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _currentHeader(session),
          Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _tag(session.type, current: true),
                const SizedBox(height: 12),
                Text(
                  session.title,
                  style: const TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 42,
                    height: 1.05,
                    fontWeight: FontWeight.w400,
                    color: ALOFColors.primary,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  session.subtitle,
                  style: const TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 18,
                    height: 1.65,
                    color: ALOFColors.onSurfaceMuted,
                  ),
                ),
                const SizedBox(height: 24),
                _objectiveCard(session),
              ],
            ),
          ),
          _currentActions(),
        ],
      ),
    );
  }

  Widget _currentHeader(SessionItem session) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: ALOFColors.surfaceLow,
        border: Border(bottom: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          const Icon(Icons.circle, size: 10, color: ALOFColors.terracotta),
          const Text(
            'SELECTED SESSION',
            style: TextStyle(
              fontFamily: 'JetBrains Mono',
              fontSize: 11,
              letterSpacing: 1.1,
              fontWeight: FontWeight.w700,
              color: ALOFColors.primary,
            ),
          ),
          _tag(session.type, current: true),
          _tag(session.status),
        ],
      ),
    );
  }

  Widget _objectiveCard(SessionItem session) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: ALOFColors.surfaceLow,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: ALOFColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.description_outlined,
                size: 18,
                color: ALOFColors.taupe,
              ),
              SizedBox(width: 8),
              Text(
                'SESSION REQUEST',
                style: TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 11,
                  letterSpacing: 1.1,
                  fontWeight: FontWeight.w700,
                  color: ALOFColors.taupe,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            session.request.isEmpty ? 'No request recorded.' : session.request,
            style: const TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 16,
              height: 1.6,
              color: ALOFColors.onSurfaceMuted,
            ),
          ),
        ],
      ),
    );
  }

  Widget _currentActions() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: ALOFColors.surfaceLow,
        border: Border(top: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: Wrap(
        spacing: 20,
        runSpacing: 16,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          FilledButton.icon(
            onPressed: () {
              context.go('/learning-session');
            },
            icon: const Icon(Icons.arrow_forward, size: 18),
            label: const Text('CONTINUE SESSION'),
            style: FilledButton.styleFrom(
              backgroundColor: ALOFColors.terracotta,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 15),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(5),
              ),
            ),
          ),
          TextButton(
            onPressed: () {
              context.go('/journey');
            },
            child: const Text(
              'Choose another activity/session',
              style: TextStyle(
                fontFamily: 'Newsreader',
                fontSize: 16,
                color: ALOFColors.taupe,
                decoration: TextDecoration.underline,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class SessionItem {
  final String id;
  final String request;
  final String type;
  final String title;
  final String subtitle;
  final String activity;
  final String status;
  final String time;
  final DateTime? createdAt;

  const SessionItem({
    required this.id,
    required this.request,
    required this.type,
    required this.title,
    required this.subtitle,
    required this.activity,
    required this.status,
    required this.time,
    this.createdAt,
  });

  factory SessionItem.fromJson(Map<String, dynamic> json) {
    final request = json['request']?.toString().trim() ?? '';

    final createdAtRaw = json['created_at']?.toString();

    DateTime? createdAt;

    if (createdAtRaw != null && createdAtRaw.isNotEmpty) {
      createdAt = DateTime.tryParse(createdAtRaw);
    }

    final title = request.isEmpty ? 'Learning Session' : request;

    return SessionItem(
      id: json['id']?.toString() ?? '',
      request: request,
      type: 'Learning Session',
      title: title,
      subtitle: request.isEmpty
          ? 'No session request recorded.'
          : 'Learning request recorded by ALOF.',
      activity: 'Learning Session',
      status: 'Recorded',
      time: _formatTime(createdAt),
      createdAt: createdAt,
    );
  }

  static String _formatTime(DateTime? value) {
    if (value == null) {
      return 'Unknown';
    }

    final local = value.toLocal();

    final day = local.day.toString().padLeft(2, '0');
    final month = local.month.toString().padLeft(2, '0');
    final year = local.year.toString();

    final hour = local.hour.toString().padLeft(2, '0');
    final minute = local.minute.toString().padLeft(2, '0');

    return '$day/$month/$year  $hour:$minute';
  }
}
