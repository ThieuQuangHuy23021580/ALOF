import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../domain/data/repositories/alof_repository.dart';
import '../theme/app_theme.dart';

class JourneyScreen extends StatefulWidget {
  const JourneyScreen({super.key});

  @override
  State<JourneyScreen> createState() => _JourneyScreenState();
}

class _JourneyScreenState extends State<JourneyScreen> {
  static const String studentId = 'student-demo';

  late Future<Map<String, dynamic>> _journeyFuture;

  @override
  void initState() {
    super.initState();

    final repository = context.read<AlofRepository>();
    _journeyFuture = repository.getJourney(studentId);
  }

  void _reload() {
    final repository = context.read<AlofRepository>();

    setState(() {
      _journeyFuture = repository.getJourney(studentId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: _journeyFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const _JourneyLoading();
        }

        if (snapshot.hasError) {
          return _JourneyError(error: snapshot.error, onRetry: _reload);
        }

        final journey = snapshot.data ?? const <String, dynamic>{};

        return _JourneyContent(journey: journey);
      },
    );
  }
}

/* -------------------------------------------------------------------------- */
/* JOURNEY CONTENT                                                            */
/* -------------------------------------------------------------------------- */

class _JourneyContent extends StatelessWidget {
  final Map<String, dynamic> journey;

  const _JourneyContent({required this.journey});

  Map<String, dynamic> _map(dynamic value) {
    if (value is Map) {
      return Map<String, dynamic>.from(value);
    }

    return const {};
  }

  List<dynamic> _list(dynamic value) {
    if (value is List) {
      return value;
    }

    return const [];
  }

  @override
  Widget build(BuildContext context) {
    final goal = _map(journey['goal']);
    final diagnosis = _map(journey['diagnosis']);
    final evidence = _map(journey['evidence']);
    final teachingAction = _map(journey['teaching_action']);
    final artifacts = _list(journey['artifacts']);

    return SingleChildScrollView(
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1152),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 36),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _JourneyHeader(goal: goal),
                const SizedBox(height: 48),
                _JourneyWorkspace(
                  goal: goal,
                  diagnosis: diagnosis,
                  evidence: evidence,
                  teachingAction: teachingAction,
                  artifacts: artifacts,
                ),
                const SizedBox(height: 56),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/* JOURNEY HEADER                                                             */
/* -------------------------------------------------------------------------- */

class _JourneyHeader extends StatelessWidget {
  final Map<String, dynamic> goal;

  const _JourneyHeader({required this.goal});

  @override
  Widget build(BuildContext context) {
    final knowledgeNodeId = goal['knowledge_node_id']?.toString().trim() ?? '';

    final targetLevel = goal['target_level']?.toString().trim() ?? '';

    final goalText = knowledgeNodeId.isNotEmpty
        ? knowledgeNodeId
        : 'Learning Goal';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.only(bottom: 32),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              _MonoLabel(text: 'FOLIO 04', color: ALOFColors.taupe),
              SizedBox(width: 8),
              Text('•', style: TextStyle(color: ALOFColors.borderStrong)),
              SizedBox(width: 8),
              _MonoLabel(
                text: 'STUDENT WORKSPACE',
                color: ALOFColors.terracotta,
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            'Good morning, Huy',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 48,
              fontWeight: FontWeight.w400,
              height: 1.1,
              letterSpacing: -1,
              color: ALOFColors.primary,
            ),
          ),
          const SizedBox(height: 8),
          RichText(
            text: TextSpan(
              style: const TextStyle(
                fontFamily: 'Newsreader',
                fontSize: 18,
                color: ALOFColors.onSurfaceMuted,
              ),
              children: [
                const TextSpan(text: 'Current Goal: '),
                TextSpan(
                  text: goalText,
                  style: const TextStyle(
                    fontStyle: FontStyle.italic,
                    fontWeight: FontWeight.w600,
                    color: ALOFColors.onSurface,
                  ),
                ),
                if (targetLevel.isNotEmpty) ...[
                  const TextSpan(text: ' · target '),
                  TextSpan(
                    text: targetLevel.toUpperCase(),
                    style: const TextStyle(
                      fontFamily: 'JetBrains Mono',
                      fontSize: 11,
                      color: ALOFColors.terracotta,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/* WORKSPACE                                                                  */
/* -------------------------------------------------------------------------- */

class _JourneyWorkspace extends StatelessWidget {
  final Map<String, dynamic> goal;
  final Map<String, dynamic> diagnosis;
  final Map<String, dynamic> evidence;
  final Map<String, dynamic> teachingAction;
  final List<dynamic> artifacts;

  const _JourneyWorkspace({
    required this.goal,
    required this.diagnosis,
    required this.evidence,
    required this.teachingAction,
    required this.artifacts,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth >= 900;

        if (!isWide) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _CurrentLearningStep(
                goal: goal,
                diagnosis: diagnosis,
                evidence: evidence,
                teachingAction: teachingAction,
                artifacts: artifacts,
              ),
              const SizedBox(height: 32),
              _ALOFSuggests(teachingAction: teachingAction),
            ],
          );
        }

        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              flex: 8,
              child: _CurrentLearningStep(
                goal: goal,
                diagnosis: diagnosis,
                evidence: evidence,
                teachingAction: teachingAction,
                artifacts: artifacts,
              ),
            ),
            const SizedBox(width: 32),
            Expanded(
              flex: 4,
              child: _ALOFSuggests(teachingAction: teachingAction),
            ),
          ],
        );
      },
    );
  }
}

/* -------------------------------------------------------------------------- */
/* CURRENT LEARNING STEP                                                      */
/* -------------------------------------------------------------------------- */

class _CurrentLearningStep extends StatelessWidget {
  final Map<String, dynamic> goal;
  final Map<String, dynamic> diagnosis;
  final Map<String, dynamic> evidence;
  final Map<String, dynamic> teachingAction;
  final List<dynamic> artifacts;

  const _CurrentLearningStep({
    required this.goal,
    required this.diagnosis,
    required this.evidence,
    required this.teachingAction,
    required this.artifacts,
  });

  @override
  Widget build(BuildContext context) {
    final primaryConcepts = _stringList(diagnosis['primary_concepts']);

    final weakConcepts = _stringList(diagnosis['weak_concepts']);

    final focusConcepts = _stringList(teachingAction['focus_concepts']);

    final concept = focusConcepts.isNotEmpty
        ? focusConcepts.first
        : primaryConcepts.isNotEmpty
        ? primaryConcepts.first
        : goal['knowledge_node_id']?.toString() ?? 'Current topic';

    final level =
        teachingAction['difficulty']?.toString() ??
        _firstDiagnosisLevel(diagnosis) ??
        'adaptive';

    final strategy = teachingAction['strategy']?.toString() ?? 'adaptive';

    final action = teachingAction['action']?.toString() ?? 'continue';

    final reason =
        teachingAction['reason']?.toString() ??
        'Recommended from the current learning state and evidence.';

    final artifact = artifacts.isNotEmpty
        ? _map(artifacts.first)
        : const <String, dynamic>{};

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionHeading(
          number: '§ 01.1',
          title: 'Current Learning Step',
          trailing: 'BACKEND STATE',
        ),
        const SizedBox(height: 12),
        Container(
          clipBehavior: Clip.antiAlias,
          decoration: BoxDecoration(
            color: ALOFColors.surface,
            border: Border.all(color: ALOFColors.borderSubtle),
            borderRadius: BorderRadius.circular(3),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(width: 4, color: ALOFColors.terracotta),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(28),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _TopicHeader(
                        concept: concept,
                        level: level,
                        strategy: strategy,
                      ),
                      const SizedBox(height: 20),
                      _StepDescription(
                        concept: concept,
                        action: action,
                        reason: reason,
                        weakConcepts: weakConcepts,
                      ),
                      const SizedBox(height: 20),
                      _ArtifactPreview(artifact: artifact),
                      const SizedBox(height: 16),
                      const _StepActions(),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Map<String, dynamic> _map(dynamic value) {
    if (value is Map) {
      return Map<String, dynamic>.from(value);
    }

    return const {};
  }

  List<String> _stringList(dynamic value) {
    if (value is List) {
      return value.map((item) => item.toString()).toList();
    }

    if (value is String && value.isNotEmpty) {
      return [value];
    }

    return const [];
  }

  String? _firstDiagnosisLevel(Map<String, dynamic> diagnosis) {
    final concepts = diagnosis['concepts'];

    if (concepts is Map && concepts.isNotEmpty) {
      final first = concepts.values.first;

      if (first is Map) {
        return first['level']?.toString();
      }
    }

    return null;
  }
}

/* -------------------------------------------------------------------------- */
/* TOPIC HEADER                                                               */
/* -------------------------------------------------------------------------- */

class _TopicHeader extends StatelessWidget {
  final String concept;
  final String level;
  final String strategy;

  const _TopicHeader({
    required this.concept,
    required this.level,
    required this.strategy,
  });

  @override
  Widget build(BuildContext context) {
    return Wrap(
      crossAxisAlignment: WrapCrossAlignment.center,
      spacing: 8,
      runSpacing: 8,
      children: [
        const _MonoLabel(text: 'TOPIC', color: ALOFColors.taupe),
        const Text('•', style: TextStyle(color: ALOFColors.borderStrong)),
        Text(
          concept,
          style: const TextStyle(
            fontFamily: 'Newsreader',
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: ALOFColors.primary,
          ),
        ),
        const SizedBox(width: 8),
        _Badge(
          text: level.toUpperCase(),
          background: ALOFColors.surfaceLow,
          foreground: ALOFColors.taupe,
        ),
        _Badge(
          text: _formatStrategy(strategy),
          background: ALOFColors.terracottaLight,
          foreground: ALOFColors.terracottaDark,
        ),
      ],
    );
  }

  String _formatStrategy(String value) {
    if (value.isEmpty) {
      return 'ADAPTIVE';
    }

    return value.replaceAll('_', ' ').toUpperCase();
  }
}

/* -------------------------------------------------------------------------- */
/* STEP DESCRIPTION                                                           */
/* -------------------------------------------------------------------------- */

class _StepDescription extends StatelessWidget {
  final String concept;
  final String action;
  final String reason;
  final List<String> weakConcepts;

  const _StepDescription({
    required this.concept,
    required this.action,
    required this.reason,
    required this.weakConcepts,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          _formatAction(action, concept),
          style: const TextStyle(
            fontFamily: 'Newsreader',
            fontSize: 30,
            fontWeight: FontWeight.w400,
            height: 1.25,
            color: ALOFColors.primary,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          reason,
          style: const TextStyle(
            fontFamily: 'Newsreader',
            fontSize: 16,
            height: 1.6,
            color: ALOFColors.onSurfaceMuted,
          ),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.only(top: 10),
          decoration: const BoxDecoration(
            border: Border(top: BorderSide(color: ALOFColors.borderSubtle)),
          ),
          child: Wrap(
            children: [
              const Text(
                'WHY THIS STEP: ',
                style: TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  letterSpacing: .8,
                  color: ALOFColors.terracotta,
                ),
              ),
              Text(
                weakConcepts.isNotEmpty
                    ? 'Weak concepts detected: ${weakConcepts.join(', ')}.'
                    : reason,
                style: const TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 14,
                  fontStyle: FontStyle.italic,
                  color: ALOFColors.taupe,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _formatAction(String action, String concept) {
    final formatted = action.replaceAll('_', ' ').trim();

    if (formatted.isEmpty || formatted == 'continue') {
      return concept;
    }

    return '${formatted[0].toUpperCase()}${formatted.substring(1)} · $concept';
  }
}

/* -------------------------------------------------------------------------- */
/* ARTIFACT                                                                   */
/* -------------------------------------------------------------------------- */

class _ArtifactPreview extends StatelessWidget {
  final Map<String, dynamic> artifact;

  const _ArtifactPreview({required this.artifact});

  @override
  Widget build(BuildContext context) {
    final title = artifact['title']?.toString() ?? 'Learning Artifact';

    final content =
        artifact['content']?.toString() ??
        artifact['summary']?.toString() ??
        'No artifact has been generated yet.';

    final producer = artifact['producer']?.toString() ?? 'ALOF';

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F5EE),
        border: Border.all(color: ALOFColors.borderSubtle),
        borderRadius: BorderRadius.circular(3),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.auto_stories_outlined,
                size: 17,
                color: ALOFColors.terracotta,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'LEARNING ARTIFACT · $title',
                  style: const TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    letterSpacing: .8,
                    color: ALOFColors.primary,
                  ),
                ),
              ),
              Text(
                producer.toUpperCase(),
                style: const TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 10,
                  color: ALOFColors.taupe,
                ),
              ),
            ],
          ),
          const Divider(color: ALOFColors.borderSubtle, height: 18),
          SelectableText(
            content,
            style: const TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 15,
              height: 1.6,
              color: ALOFColors.onSurfaceMuted,
            ),
          ),
        ],
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/* ACTIONS                                                                    */
/* -------------------------------------------------------------------------- */

class _StepActions extends StatelessWidget {
  const _StepActions();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.only(top: 12),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxWidth < 500;

          if (compact) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const _ChooseStepButton(),
                const SizedBox(height: 12),
                const _ContinueButton(),
              ],
            );
          }

          return const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [_ChooseStepButton(), _ContinueButton()],
          );
        },
      ),
    );
  }
}

class _ChooseStepButton extends StatelessWidget {
  const _ChooseStepButton();

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: () {
        context.go('/sessions');
      },
      style: TextButton.styleFrom(
        foregroundColor: ALOFColors.taupe,
        padding: EdgeInsets.zero,
      ),
      child: const Text(
        'View workflow or choose another step',
        style: TextStyle(
          fontFamily: 'Newsreader',
          fontSize: 14,
          fontStyle: FontStyle.italic,
          decoration: TextDecoration.underline,
          decorationColor: ALOFColors.taupe,
        ),
      ),
    );
  }
}

class _ContinueButton extends StatelessWidget {
  const _ContinueButton();

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: () {
        context.go('/sessions');
      },
      icon: const Icon(Icons.arrow_forward, size: 15),
      label: const Text(
        'CONTINUE LEARNING',
        style: TextStyle(
          fontFamily: 'JetBrains Mono',
          fontSize: 11,
          letterSpacing: .8,
        ),
      ),
      style: ElevatedButton.styleFrom(
        backgroundColor: ALOFColors.primary,
        foregroundColor: ALOFColors.surface,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/* ALOF SUGGESTS                                                              */
/* -------------------------------------------------------------------------- */

class _ALOFSuggests extends StatelessWidget {
  final Map<String, dynamic> teachingAction;

  const _ALOFSuggests({required this.teachingAction});

  @override
  Widget build(BuildContext context) {
    final action = teachingAction['action']?.toString() ?? 'continue';

    final strategy = teachingAction['strategy']?.toString() ?? 'adaptive';

    final reason =
        teachingAction['reason']?.toString() ??
        'Recommended from your current learning state.';

    final focusConcepts = teachingAction['focus_concepts'];

    final focusText = focusConcepts is List && focusConcepts.isNotEmpty
        ? focusConcepts.map((item) => item.toString()).join(', ')
        : 'Current learning state';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionHeading(
          number: '§ 01.2 ALOF Suggests',
          title: '',
          trailing: 'ADAPTIVE ACTION',
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: ALOFColors.surface,
            border: Border.all(color: ALOFColors.borderSubtle),
            borderRadius: BorderRadius.circular(3),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                height: 2,
                color: ALOFColors.terracotta.withOpacity(.4),
              ),
              const SizedBox(height: 16),
              const Row(
                children: [
                  Icon(
                    Icons.auto_awesome,
                    size: 16,
                    color: ALOFColors.terracotta,
                  ),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'RECOMMENDED NEXT ACTION',
                      style: TextStyle(
                        fontFamily: 'JetBrains Mono',
                        fontSize: 9,
                        fontWeight: FontWeight.w600,
                        letterSpacing: .7,
                        color: ALOFColors.taupe,
                      ),
                    ),
                  ),
                ],
              ),
              const Divider(color: ALOFColors.borderSubtle, height: 24),
              Text(
                _formatAction(action),
                style: const TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 19,
                  fontWeight: FontWeight.w500,
                  color: ALOFColors.primary,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                'Strategy: ${_formatStrategy(strategy)}',
                style: const TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 14,
                  fontStyle: FontStyle.italic,
                  height: 1.5,
                  color: ALOFColors.taupe,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Focus: $focusText',
                style: const TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 14,
                  height: 1.5,
                  color: ALOFColors.onSurfaceMuted,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                reason,
                style: const TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 14,
                  height: 1.5,
                  color: ALOFColors.onSurfaceMuted,
                ),
              ),
              const SizedBox(height: 20),
              const Divider(color: ALOFColors.borderSubtle),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () {
                  context.go('/sessions');
                },
                style: TextButton.styleFrom(
                  padding: EdgeInsets.zero,
                  foregroundColor: ALOFColors.terracotta,
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '[ Follow suggestion → ]',
                      style: TextStyle(
                        fontFamily: 'Newsreader',
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                    SizedBox(width: 5),
                    Icon(Icons.open_in_new, size: 13),
                  ],
                ),
              ),
              TextButton(
                onPressed: () {
                  context.go('/sessions');
                },
                style: TextButton.styleFrom(
                  padding: const EdgeInsets.only(top: 2),
                  foregroundColor: ALOFColors.taupe,
                ),
                child: const Text(
                  '[ Choose another step → ]',
                  style: TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 12,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _formatAction(String value) {
    if (value.isEmpty) {
      return 'Continue learning';
    }

    final formatted = value.replaceAll('_', ' ').trim();

    return formatted.isEmpty
        ? 'Continue learning'
        : '${formatted[0].toUpperCase()}${formatted.substring(1)}';
  }

  String _formatStrategy(String value) {
    if (value.isEmpty) {
      return 'adaptive';
    }

    return value.replaceAll('_', ' ');
  }
}

/* -------------------------------------------------------------------------- */
/* LOADING                                                                    */
/* -------------------------------------------------------------------------- */

class _JourneyLoading extends StatelessWidget {
  const _JourneyLoading();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Padding(
        padding: EdgeInsets.symmetric(vertical: 120),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(
              color: ALOFColors.terracotta,
              strokeWidth: 2,
            ),
            SizedBox(height: 16),
            Text(
              'Loading learner state...',
              style: TextStyle(
                fontFamily: 'Newsreader',
                fontSize: 16,
                color: ALOFColors.taupe,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/* ERROR                                                                      */
/* -------------------------------------------------------------------------- */

class _JourneyError extends StatelessWidget {
  final Object? error;
  final VoidCallback onRetry;

  const _JourneyError({required this.error, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 100),
        child: Container(
          constraints: const BoxConstraints(maxWidth: 600),
          padding: const EdgeInsets.all(28),
          decoration: BoxDecoration(
            color: ALOFColors.surface,
            border: Border.all(color: ALOFColors.borderSubtle),
            borderRadius: BorderRadius.circular(3),
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
                'Unable to load Journey',
                style: TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 24,
                  color: ALOFColors.primary,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                error?.toString() ?? 'Unknown API error.',
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 11,
                  height: 1.5,
                  color: ALOFColors.taupe,
                ),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: onRetry,
                style: ElevatedButton.styleFrom(
                  backgroundColor: ALOFColors.primary,
                  foregroundColor: ALOFColors.surface,
                  elevation: 0,
                ),
                child: const Text(
                  'RETRY',
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 11,
                    letterSpacing: .8,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/* COMMON COMPONENTS                                                          */
/* -------------------------------------------------------------------------- */

class _SectionHeading extends StatelessWidget {
  final String number;
  final String title;
  final String trailing;

  const _SectionHeading({
    required this.number,
    required this.title,
    required this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Row(
            children: [
              Text(
                number,
                style: const TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.3,
                  color: ALOFColors.terracotta,
                ),
              ),
              if (title.isNotEmpty) ...[
                const SizedBox(width: 8),
                Text(
                  title,
                  style: const TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 20,
                    fontWeight: FontWeight.w500,
                    color: ALOFColors.primary,
                  ),
                ),
              ],
            ],
          ),
        ),
        Text(
          trailing,
          style: const TextStyle(
            fontFamily: 'JetBrains Mono',
            fontSize: 10,
            letterSpacing: 1,
            color: ALOFColors.taupe,
          ),
        ),
      ],
    );
  }
}

class _MonoLabel extends StatelessWidget {
  final String text;
  final Color color;

  const _MonoLabel({required this.text, required this.color});

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: TextStyle(
        fontFamily: 'JetBrains Mono',
        fontSize: 10,
        fontWeight: FontWeight.w600,
        letterSpacing: 1.2,
        color: color,
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  final String text;
  final Color background;
  final Color foreground;

  const _Badge({
    required this.text,
    required this.background,
    required this.foreground,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: background,
        border: Border.all(color: foreground.withOpacity(.18)),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontFamily: 'JetBrains Mono',
          fontSize: 9,
          letterSpacing: 1,
          color: foreground,
        ),
      ),
    );
  }
}
