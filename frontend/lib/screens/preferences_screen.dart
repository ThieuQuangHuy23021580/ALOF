import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class PreferencesScreen extends StatefulWidget {
  const PreferencesScreen({super.key});

  @override
  State<PreferencesScreen> createState() => _PreferencesScreenState();
}

class _PreferencesScreenState extends State<PreferencesScreen> {
  String _difficulty = 'adaptive';
  bool _saving = false;
  String? _statusMessage;

  void _savePreferences() {
    setState(() {
      _saving = true;
      _statusMessage = null;
    });

    Future.delayed(const Duration(milliseconds: 500), () {
      if (!mounted) return;

      setState(() {
        _saving = false;
        _statusMessage = 'Preferences saved';
      });

      Future.delayed(const Duration(seconds: 3), () {
        if (!mounted) return;
        setState(() => _statusMessage = null);
      });
    });
  }

  void _resetDefaults() {
    setState(() {
      _difficulty = 'adaptive';
      _statusMessage = 'Defaults restored';
    });

    Future.delayed(const Duration(seconds: 2), () {
      if (!mounted) return;
      setState(() => _statusMessage = null);
    });
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(child: Center(child: _buildMain()));
  }

  Widget _buildMain() {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 1200),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildPageHeader(),
            const SizedBox(height: 32),
            _buildDifficultySection(),
            const SizedBox(height: 32),
            _buildPipelineSection(),
            const SizedBox(height: 32),
            _buildActions(),
          ],
        ),
      ),
    );
  }

  Widget _buildPageHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.only(bottom: 24),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(width: 8, height: 8, color: ALOFColors.terracotta),
              const SizedBox(width: 8),
              const Text(
                'LEARNER CONFIGURATION • ADAPTIVE PLANNING INPUTS',
                style: TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 1.4,
                  color: ALOFColors.taupe,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            'Learning Preferences',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 48,
              height: 1.1,
              color: ALOFColors.primary,
              fontWeight: FontWeight.w400,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'Configure how ALOF should organize and support your learning sessions.',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 18,
              height: 1.6,
              color: ALOFColors.taupe,
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // DIFFICULTY
  // ===========================================================================

  Widget _buildDifficultySection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: const BoxDecoration(color: ALOFColors.surface),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.only(bottom: 18),
            decoration: const BoxDecoration(
              border: Border(
                bottom: BorderSide(color: ALOFColors.borderSubtle),
              ),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    const Expanded(
                      child: Text(
                        'Preferred Difficulty',
                        style: TextStyle(
                          fontFamily: 'Newsreader',
                          fontSize: 26,
                          fontWeight: FontWeight.w500,
                          color: ALOFColors.primary,
                        ),
                      ),
                    ),
                    const Text(
                      'PRIMARY SETTING',
                      style: TextStyle(
                        fontFamily: 'JetBrains Mono',
                        fontSize: 9,
                        letterSpacing: 1,
                        color: ALOFColors.taupe,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                const Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'Specify your target challenge tier. Setting to Adaptive enables the system to calibrate dynamically based on continuous diagnostic assessment.',
                    style: TextStyle(
                      fontFamily: 'Newsreader',
                      fontSize: 14,
                      height: 1.5,
                      color: ALOFColors.taupe,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          LayoutBuilder(
            builder: (context, constraints) {
              final twoColumns = constraints.maxWidth >= 700;
              final width = twoColumns
                  ? (constraints.maxWidth - 16) / 2
                  : constraints.maxWidth;

              return Wrap(
                spacing: 16,
                runSpacing: 16,
                children: [
                  _difficultyCard(
                    width: width,
                    value: 'adaptive',
                    title: 'Adaptive',
                    description:
                        'Dynamically tuned to your learning state and ongoing mastery feedback.',
                    leftLabel: 'RECOMMENDED',
                    rightLabel: 'DEFAULT TIER',
                  ),
                  _difficultyCard(
                    width: width,
                    value: 'beginner',
                    title: 'Beginner',
                    description:
                        'Gentle scaffolding with foundational focus and guided exposition.',
                    leftLabel: 'LEVEL 01',
                    rightLabel: 'FIXED CONSTRAINT',
                  ),
                  _difficultyCard(
                    width: width,
                    value: 'medium',
                    title: 'Medium',
                    description:
                        'Balanced depth with structured conceptual challenges and practice.',
                    leftLabel: 'LEVEL 02',
                    rightLabel: 'FIXED CONSTRAINT',
                  ),
                  _difficultyCard(
                    width: width,
                    value: 'advanced',
                    title: 'Advanced',
                    description:
                        'Rigorous depth, edge cases, and high-complexity boundary questions.',
                    leftLabel: 'LEVEL 03',
                    rightLabel: 'FIXED CONSTRAINT',
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _difficultyCard({
    required double width,
    required String value,
    required String title,
    required String description,
    required String leftLabel,
    required String rightLabel,
  }) {
    final selected = _difficulty == value;

    return GestureDetector(
      onTap: () => setState(() => _difficulty = value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        width: width,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: ALOFColors.surfaceLow,
          border: Border(
            left: BorderSide(
              color: selected ? ALOFColors.terracotta : Colors.transparent,
              width: 4,
            ),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    title,
                    style: const TextStyle(
                      fontFamily: 'Newsreader',
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: ALOFColors.primary,
                    ),
                  ),
                ),
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: selected
                        ? ALOFColors.terracotta
                        : Colors.transparent,
                    border: Border.all(
                      color: selected
                          ? ALOFColors.terracotta
                          : ALOFColors.taupeLight,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              description,
              style: const TextStyle(
                fontFamily: 'Newsreader',
                fontSize: 14,
                height: 1.45,
                color: ALOFColors.onSurfaceMuted,
              ),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.only(top: 12),
              decoration: const BoxDecoration(
                border: Border(top: BorderSide(color: ALOFColors.borderSubtle)),
              ),
              child: Row(
                children: [
                  Text(
                    leftLabel,
                    style: TextStyle(
                      fontFamily: 'JetBrains Mono',
                      fontSize: 9,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 1,
                      color: selected
                          ? ALOFColors.terracotta
                          : ALOFColors.taupe,
                    ),
                  ),
                  const Spacer(),
                  Text(
                    rightLabel,
                    style: const TextStyle(
                      fontFamily: 'JetBrains Mono',
                      fontSize: 9,
                      color: ALOFColors.taupe,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ===========================================================================
  // PIPELINE
  // ===========================================================================

  Widget _buildPipelineSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: const BoxDecoration(color: ALOFColors.surface),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'RUNTIME SYNTHESIS',
            style: TextStyle(
              fontFamily: 'JetBrains Mono',
              fontSize: 10,
              letterSpacing: 1.5,
              color: ALOFColors.terracotta,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            '§ Adaptive Behavior & Planning Pipeline',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 30,
              height: 1.2,
              fontWeight: FontWeight.w500,
              color: ALOFColors.primary,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Your preferences serve as initial constraints for ALOF\'s Planning engine. When set to Adaptive, the system synthesizes your preferences with real-time diagnostic evidence.',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 18,
              height: 1.6,
              color: ALOFColors.taupe,
            ),
          ),
          const SizedBox(height: 28),
          const Text(
            'ARCHITECTURE TRACE',
            style: TextStyle(
              fontFamily: 'JetBrains Mono',
              fontSize: 10,
              letterSpacing: 1.3,
              color: ALOFColors.taupe,
            ),
          ),
          const SizedBox(height: 12),
          _buildPipelineCards(),
          const SizedBox(height: 24),
          _buildPipelineNote(),
        ],
      ),
    );
  }

  Widget _buildPipelineCards() {
    final cards = [
      (
        '01 / INPUT',
        'LearningPreference',
        'Target difficulty level or adaptive calibration.',
        false,
      ),
      (
        '02 / PLANNING',
        'Planner',
        'Formulates adaptive instructional strategy informed by LearningState & KnowledgeDiagnosis.',
        true,
      ),
      (
        '03 / ORCHESTRATION',
        'Workflow',
        'Orchestrates WorkflowNodes & transitions.',
        false,
      ),
      (
        '04 / EXECUTION',
        'Runtime',
        'Executes instructional steps within execution context.',
        false,
      ),
      (
        '05 / OUTPUT',
        'Component',
        'Produces ComponentResult and learning Artifacts.',
        true,
      ),
    ];

    return LayoutBuilder(
      builder: (context, constraints) {
        final columns = constraints.maxWidth >= 1050
            ? 5
            : constraints.maxWidth >= 700
            ? 2
            : 1;

        final width = columns == 5
            ? (constraints.maxWidth - 48) / 5
            : columns == 2
            ? (constraints.maxWidth - 12) / 2
            : constraints.maxWidth;

        return Wrap(
          spacing: 12,
          runSpacing: 12,
          children: cards.map((card) {
            return _pipelineCard(
              width: width,
              index: card.$1,
              title: card.$2,
              description: card.$3,
              accent: card.$4,
            );
          }).toList(),
        );
      },
    );
  }

  Widget _pipelineCard({
    required double width,
    required String index,
    required String title,
    required String description,
    required bool accent,
  }) {
    return Container(
      width: width,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: ALOFColors.surfaceLow,
        border: Border(
          top: BorderSide(
            color: accent ? ALOFColors.terracotta : ALOFColors.primary,
            width: 2,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            index,
            style: TextStyle(
              fontFamily: 'JetBrains Mono',
              fontSize: 9,
              color: accent ? ALOFColors.terracotta : ALOFColors.taupe,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            title,
            style: const TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 17,
              fontWeight: FontWeight.w700,
              color: ALOFColors.primary,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            description,
            style: const TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 13,
              height: 1.45,
              color: ALOFColors.taupe,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPipelineNote() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: const BoxDecoration(
        color: ALOFColors.surfaceLow,
        border: Border(
          left: BorderSide(color: ALOFColors.terracotta, width: 4),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(
            Icons.auto_awesome,
            color: ALOFColors.terracotta,
            size: 24,
          ),
          const SizedBox(width: 16),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '“Your learning preferences provide initial constraints for the Planner, while your active LearningState and KnowledgeDiagnosis inform continuous adaptive decisions.”',
                  style: TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 17,
                    height: 1.5,
                    fontStyle: FontStyle.italic,
                    fontWeight: FontWeight.w500,
                    color: ALOFColors.primary,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'AdaptiveTeachingAction (Introduce, Explain, Scaffold, Practice, Review, Challenge) is dynamically determined by the adaptive engine rather than manually configured.',
                  style: TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 14,
                    height: 1.5,
                    color: ALOFColors.taupe,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // ACTIONS
  // ===========================================================================

  Widget _buildActions() {
    return Container(
      padding: const EdgeInsets.only(top: 24, bottom: 16),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_statusMessage != null)
            Container(
              margin: const EdgeInsets.only(bottom: 14),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: ALOFColors.surface,
                border: Border.all(color: ALOFColors.borderSubtle),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(
                    Icons.check_circle_outline,
                    size: 16,
                    color: ALOFColors.primary,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _statusMessage!,
                    style: const TextStyle(
                      fontFamily: 'JetBrains Mono',
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: ALOFColors.primary,
                    ),
                  ),
                ],
              ),
            ),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              OutlinedButton(
                onPressed: _resetDefaults,
                style: OutlinedButton.styleFrom(
                  foregroundColor: ALOFColors.taupe,
                  backgroundColor: ALOFColors.surface,
                  side: const BorderSide(color: ALOFColors.borderSubtle),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 14,
                  ),
                  shape: const RoundedRectangleBorder(
                    borderRadius: BorderRadius.zero,
                  ),
                ),
                child: const Text(
                  'RESET TO DEFAULTS',
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 10,
                    letterSpacing: 1,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              FilledButton.icon(
                onPressed: _saving ? null : _savePreferences,
                icon: _saving
                    ? const SizedBox(
                        width: 15,
                        height: 15,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.save_outlined, size: 17),
                label: Text(_saving ? 'SAVING...' : 'SAVE PREFERENCES'),
                style: FilledButton.styleFrom(
                  backgroundColor: ALOFColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 14,
                  ),
                  shape: const RoundedRectangleBorder(
                    borderRadius: BorderRadius.zero,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
