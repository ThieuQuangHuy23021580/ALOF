import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../theme/app_theme.dart';

class LearningSessionScreen extends StatefulWidget {
  const LearningSessionScreen({super.key});

  @override
  State<LearningSessionScreen> createState() => _LearningSessionScreenState();
}

class _LearningSessionScreenState extends State<LearningSessionScreen> {
  String? selectedAnswer;
  final TextEditingController questionController = TextEditingController();

  @override
  void dispose() {
    questionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ALOFColors.background,
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(16, 32, 16, 48),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 1180),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _buildHeader(context),
                      const SizedBox(height: 32),

                      if (constraints.maxWidth >= 900)
                        _buildDesktopWorkspace()
                      else
                        _buildMobileWorkspace(),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // HEADER
  // ---------------------------------------------------------------------------

  Widget _buildHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.only(bottom: 16),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: Row(
        children: [
          Expanded(
            child: InkWell(
              onTap: () => context.go('/sessions'),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(
                    Icons.arrow_back,
                    size: 16,
                    color: ALOFColors.taupe,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Back to Sessions',
                    style: _mono(
                      fontSize: 12,
                      color: ALOFColors.taupe,
                      fontWeight: FontWeight.w500,
                      letterSpacing: 1.1,
                    ),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(width: 16),

          Flexible(
            child: Wrap(
              alignment: WrapAlignment.end,
              crossAxisAlignment: WrapCrossAlignment.center,
              spacing: 10,
              runSpacing: 6,
              children: [
                Text(
                  'Recursion · Current Node',
                  style: const TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 14,
                    fontStyle: FontStyle.italic,
                    color: ALOFColors.taupe,
                  ),
                ),
                Text(
                  '/',
                  style: TextStyle(
                    color: ALOFColors.borderSubtle,
                    fontSize: 14,
                  ),
                ),
                _statusBadge(
                  icon: Icons.circle,
                  label: 'Active',
                  color: ALOFColors.primary,
                  background: ALOFColors.surfaceLow,
                ),
                _statusBadge(
                  label: 'Learning · Guided Explanation',
                  color: ALOFColors.onSurfaceMuted,
                  background: ALOFColors.surfaceLow,
                  border: true,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _statusBadge({
    String? label,
    IconData? icon,
    required Color color,
    required Color background,
    bool border = false,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(4),
        border: border ? Border.all(color: ALOFColors.borderSubtle) : null,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 7, color: color),
            const SizedBox(width: 6),
          ],
          Text(
            label ?? '',
            style: _mono(
              fontSize: 11,
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // WORKSPACE
  // ---------------------------------------------------------------------------

  Widget _buildDesktopWorkspace() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(width: 360, child: _buildSourceDocument()),
        const SizedBox(width: 32),
        Expanded(child: _buildResponseColumn()),
      ],
    );
  }

  Widget _buildMobileWorkspace() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _buildSourceDocument(),
        const SizedBox(height: 32),
        _buildResponseColumn(),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // SOURCE DOCUMENT
  // ---------------------------------------------------------------------------

  Widget _buildSourceDocument() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: ALOFColors.surfaceLow,
        border: Border.all(color: ALOFColors.borderSubtle),
        borderRadius: BorderRadius.circular(8),
        boxShadow: const [
          BoxShadow(
            color: Color(0x12000000),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildSourceHeader(),
          const SizedBox(height: 16),
          _buildSourceExcerpt(),
          const SizedBox(height: 16),
          _buildSelectedPassage(),
        ],
      ),
    );
  }

  Widget _buildSourceHeader() {
    return Container(
      padding: const EdgeInsets.only(bottom: 12),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.description_outlined,
            size: 20,
            color: ALOFColors.taupe,
          ),
          const SizedBox(width: 8),

          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'SOURCE DOCUMENT',
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 11,
                    letterSpacing: 1.4,
                    fontWeight: FontWeight.w600,
                    color: ALOFColors.taupe,
                  ),
                ),
                SizedBox(height: 3),
                Text(
                  'recursion_notes.pdf',
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: ALOFColors.onSurface,
                  ),
                ),
              ],
            ),
          ),

          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              const Text(
                'PDF · 12 pages',
                style: TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 10,
                  color: ALOFColors.onSurfaceMuted,
                ),
              ),
              const SizedBox(height: 4),
              IconButton(
                visualDensity: VisualDensity.compact,
                padding: EdgeInsets.zero,
                onPressed: () {},
                icon: const Icon(
                  Icons.open_in_new,
                  size: 16,
                  color: ALOFColors.taupe,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSourceExcerpt() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          '§ 2.1 Base Case Invariant',
          style: _mono(
            fontSize: 11,
            color: ALOFColors.taupe,
            fontWeight: FontWeight.w600,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          'A recursive function must have an explicit condition that terminates '
          'further recursive self-invocation. Without this boundary invariant, '
          'the routine continues to dispatch stack frames until the host '
          'process exhausts available memory.',
          textAlign: TextAlign.justify,
          style: TextStyle(
            fontFamily: 'Newsreader',
            fontSize: 15,
            height: 1.6,
            color: ALOFColors.onSurface,
          ),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.only(left: 12),
          decoration: const BoxDecoration(
            border: Border(
              left: BorderSide(color: ALOFColors.borderSubtle, width: 2),
            ),
          ),
          child: const Text(
            'In mathematical terms, recursive progression relies on inductive '
            'reduction toward a proven minimal state.',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 13,
              fontStyle: FontStyle.italic,
              height: 1.5,
              color: ALOFColors.onSurfaceMuted,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSelectedPassage() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: ALOFColors.surface,
        borderRadius: BorderRadius.circular(6),
        border: const Border(
          left: BorderSide(color: ALOFColors.terracotta, width: 2),
        ),
        boxShadow: const [
          BoxShadow(
            color: Color(0x10000000),
            blurRadius: 5,
            offset: Offset(0, 1),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              const Icon(
                Icons.format_quote,
                size: 13,
                color: ALOFColors.terracotta,
              ),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  'SELECTED PASSAGE',
                  style: _mono(
                    fontSize: 10,
                    color: ALOFColors.terracotta,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.3,
                  ),
                ),
              ),
              _smallTag('Lines 14–16'),
            ],
          ),
          const SizedBox(height: 10),
          const Text(
            '“A recursive function must have an explicit condition that '
            'terminates further recursive self-invocation.”',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 14,
              fontStyle: FontStyle.italic,
              height: 1.4,
              color: ALOFColors.onSurface,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              TextButton(
                onPressed: () {},
                style: TextButton.styleFrom(
                  padding: EdgeInsets.zero,
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: Row(
                  children: [
                    Text(
                      'Ask about selection',
                      style: _mono(
                        fontSize: 11,
                        color: ALOFColors.terracotta,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(width: 4),
                    const Icon(
                      Icons.north_east,
                      size: 13,
                      color: ALOFColors.terracotta,
                    ),
                  ],
                ),
              ),
              const Spacer(),
              _smallTag('Selected from Source'),
            ],
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // RESPONSE COLUMN
  // ---------------------------------------------------------------------------

  Widget _buildResponseColumn() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _buildResponseCard(),
        const SizedBox(height: 24),
        _buildNextActionBar(),
        const SizedBox(height: 24),
        _buildNextLearningActivity(),
        const SizedBox(height: 24),
        _buildKnowledgeFeedback(),
        const SizedBox(height: 24),
        _buildAskBar(),
        const SizedBox(height: 24),
        _buildFooter(),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // ALOF RESPONSE
  // ---------------------------------------------------------------------------

  Widget _buildResponseCard() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: ALOFColors.surface,
        border: Border.all(color: ALOFColors.borderSubtle),
        borderRadius: BorderRadius.circular(8),
        boxShadow: const [
          BoxShadow(
            color: Color(0x12000000),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildResponseContext(),
          const SizedBox(height: 24),

          const Text(
            'Why a Base Case Is Necessary',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 30,
              fontWeight: FontWeight.w500,
              height: 1.15,
              color: ALOFColors.onSurface,
            ),
          ),

          const SizedBox(height: 24),
          _buildExplanation(),

          const SizedBox(height: 24),
          _buildKeyIdea(),

          const SizedBox(height: 24),
          _buildCodeExample(),

          const SizedBox(height: 20),
          _buildGroundedReference(),
        ],
      ),
    );
  }

  Widget _buildResponseContext() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Expanded(
              child: Align(
                alignment: Alignment.centerLeft,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: ALOFColors.surfaceLow,
                    borderRadius: BorderRadius.circular(5),
                    border: Border.all(color: ALOFColors.borderSubtle),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.auto_awesome,
                        size: 14,
                        color: ALOFColors.primary,
                      ),
                      const SizedBox(width: 6),
                      Text(
                        'ALOF RESPONSE · GUIDED EXPLANATION',
                        style: _mono(
                          fontSize: 11,
                          color: ALOFColors.primary,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 1,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const Text(
              'Active Companion',
              style: TextStyle(
                fontFamily: 'JetBrains Mono',
                fontSize: 11,
                color: ALOFColors.onSurfaceMuted,
              ),
            ),
          ],
        ),

        const SizedBox(height: 12),

        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: ALOFColors.surfaceLow,
            borderRadius: BorderRadius.circular(6),
            border: const Border(
              left: BorderSide(color: ALOFColors.primary, width: 2),
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(
                Icons.psychology_outlined,
                size: 18,
                color: ALOFColors.primary,
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'WHY THIS RESPONSE?',
                      style: TextStyle(
                        fontFamily: 'JetBrains Mono',
                        fontSize: 11,
                        letterSpacing: 1.1,
                        fontWeight: FontWeight.w600,
                        color: ALOFColors.primary,
                      ),
                    ),
                    SizedBox(height: 3),
                    Text(
                      'Based on your current knowledge state and recent learning '
                      'evidence, ALOF selected a guided explanation to solidify '
                      'base-case invariants.',
                      style: TextStyle(
                        fontFamily: 'Inter',
                        fontSize: 12,
                        height: 1.5,
                        color: ALOFColors.onSurfaceMuted,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildExplanation() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _sectionLabel('EXPLANATION'),
        const SizedBox(height: 8),
        const Text(
          'At its core, recursion is the deliberate reduction of a problem '
          'state into simpler, self-similar instances. However, because each '
          'invocation requests an independent slice of runtime memory, the '
          'algorithm must possess an unambiguous terminal boundary to arrest '
          'descent and begin propagating return values back up the call chain.',
          style: TextStyle(
            fontFamily: 'Newsreader',
            fontSize: 18,
            height: 1.65,
            color: ALOFColors.onSurface,
          ),
        ),
      ],
    );
  }

  Widget _buildKeyIdea() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: ALOFColors.terracottaLight,
        borderRadius: const BorderRadius.only(
          topRight: Radius.circular(6),
          bottomRight: Radius.circular(6),
        ),
        border: const Border(
          left: BorderSide(color: ALOFColors.terracotta, width: 4),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(
            Icons.lightbulb_outline,
            size: 20,
            color: ALOFColors.terracotta,
          ),
          const SizedBox(width: 14),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'KEY IDEA',
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 11,
                    letterSpacing: 1.2,
                    fontWeight: FontWeight.w700,
                    color: ALOFColors.terracotta,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'The base case determines the exact invariant when recursive '
                  'frame dispatch arrests and returns control.',
                  style: TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 16,
                    fontStyle: FontStyle.italic,
                    height: 1.4,
                    color: ALOFColors.onSurface,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // CODE EXAMPLE
  // ---------------------------------------------------------------------------

  Widget _buildCodeExample() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Expanded(child: _sectionLabel('EXAMPLE · FROM YOUR SOURCE')),
            const Text(
              'Python 3',
              style: TextStyle(
                fontFamily: 'JetBrains Mono',
                fontSize: 11,
                color: ALOFColors.onSurfaceMuted,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),

        Container(
          decoration: BoxDecoration(
            color: ALOFColors.surface,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: ALOFColors.borderSubtle),
          ),
          clipBehavior: Clip.antiAlias,
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 10,
                ),
                color: ALOFColors.surfaceLow,
                child: Row(
                  children: [
                    _codeDot(),
                    _codeDot(),
                    _codeDot(),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        'countdown(n)',
                        style: TextStyle(
                          fontFamily: 'JetBrains Mono',
                          fontSize: 11,
                          color: ALOFColors.taupe,
                        ),
                      ),
                    ),
                    const Text(
                      'ALOF ANNOTATED',
                      style: TextStyle(
                        fontFamily: 'JetBrains Mono',
                        fontSize: 10,
                        color: ALOFColors.onSurfaceMuted,
                      ),
                    ),
                  ],
                ),
              ),

              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.all(16),
                child: const Text(
                  '''def countdown(n):
    if n <= 0:          # Base case: arrests recursion & returns
        print("Done!")
        return
    print(n)
    countdown(n - 1)    # Recursive step: descent towards base invariant''',
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 12,
                    height: 1.65,
                    color: ALOFColors.onSurface,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _codeDot() {
    return Container(
      width: 10,
      height: 10,
      margin: const EdgeInsets.only(right: 6),
      decoration: const BoxDecoration(
        color: ALOFColors.borderSubtle,
        shape: BoxShape.circle,
      ),
    );
  }

  Widget _buildGroundedReference() {
    return Container(
      padding: const EdgeInsets.only(top: 12),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: Wrap(
        alignment: WrapAlignment.spaceBetween,
        runSpacing: 8,
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.link, size: 15, color: ALOFColors.taupe),
              const SizedBox(width: 6),
              const Text(
                'Based on passage in ',
                style: TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 10,
                  color: ALOFColors.taupe,
                ),
              ),
              const Text(
                'recursion_notes.pdf (§ 2.1)',
                style: TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: ALOFColors.onSurface,
                ),
              ),
            ],
          ),

          TextButton(
            onPressed: () {},
            style: TextButton.styleFrom(
              padding: EdgeInsets.zero,
              minimumSize: Size.zero,
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'View source',
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                    color: ALOFColors.terracotta,
                  ),
                ),
                const SizedBox(width: 4),
                const Icon(
                  Icons.north_east,
                  size: 13,
                  color: ALOFColors.terracotta,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // NEXT ACTION
  // ---------------------------------------------------------------------------

  Widget _buildNextActionBar() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: ALOFColors.surfaceLow,
        border: Border.all(color: ALOFColors.borderSubtle),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Wrap(
        alignment: WrapAlignment.spaceBetween,
        crossAxisAlignment: WrapCrossAlignment.center,
        runSpacing: 14,
        spacing: 16,
        children: [
          const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'What would you like to do next?',
                style: TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  color: ALOFColors.onSurface,
                ),
              ),
              SizedBox(height: 3),
              Text(
                'Guide your learning flow with ALOF',
                style: TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 11,
                  color: ALOFColors.onSurfaceMuted,
                ),
              ),
            ],
          ),

          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _actionButton(
                icon: Icons.tune,
                label: 'Explain simpler',
                onPressed: () {},
              ),
              _actionButton(
                icon: Icons.lightbulb_outline,
                label: 'Give an example',
                onPressed: () {},
              ),
              _actionButton(
                icon: Icons.play_circle_outline,
                label: 'Practice this',
                primary: true,
                onPressed: () {},
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _actionButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
    bool primary = false,
  }) {
    return Material(
      color: primary ? ALOFColors.primary : ALOFColors.surface,
      borderRadius: BorderRadius.circular(5),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(5),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(5),
            border: primary ? null : Border.all(color: ALOFColors.borderSubtle),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                size: 15,
                color: primary ? Colors.white : ALOFColors.terracotta,
              ),
              const SizedBox(width: 6),
              Text(
                label,
                style: _mono(
                  fontSize: 11,
                  color: primary ? Colors.white : ALOFColors.onSurface,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // NEXT LEARNING ACTIVITY
  // ---------------------------------------------------------------------------

  Widget _buildNextLearningActivity() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: ALOFColors.surface,
        border: Border.all(color: ALOFColors.borderSubtle),
        borderRadius: BorderRadius.circular(8),
        boxShadow: const [
          BoxShadow(
            color: Color(0x12000000),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.only(bottom: 12),
            decoration: const BoxDecoration(
              border: Border(
                bottom: BorderSide(color: ALOFColors.borderSubtle),
              ),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.verified_outlined,
                  size: 18,
                  color: ALOFColors.terracotta,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'NEXT LEARNING ACTIVITY · TARGETED PRACTICE',
                    style: _mono(
                      fontSize: 11,
                      color: ALOFColors.taupe,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 1.1,
                    ),
                  ),
                ),
                _smallTag('Adaptive Check'),
              ],
            ),
          ),

          const SizedBox(height: 20),

          const Text(
            'Which architectural condition stops the recursion and triggers '
            'call stack unwinding?',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 21,
              fontWeight: FontWeight.w500,
              height: 1.3,
              color: ALOFColors.onSurface,
            ),
          ),

          const SizedBox(height: 6),

          const Text(
            'Select the option that correctly describes the termination lifecycle.',
            style: TextStyle(
              fontFamily: 'Inter',
              fontSize: 11,
              color: ALOFColors.onSurfaceMuted,
            ),
          ),

          const SizedBox(height: 18),

          _buildAnswerOption(
            value: 'A',
            title: 'The invocation of a child subprocess',
            description: 'Delegates execution to an auxiliary process thread.',
          ),
          const SizedBox(height: 10),
          _buildAnswerOption(
            value: 'B',
            title:
                'An explicit conditional check satisfying the base case invariant',
            description:
                'Arrests recursive frame allocation and initiates memory release.',
          ),
          const SizedBox(height: 10),
          _buildAnswerOption(
            value: 'C',
            title: 'Memory quota automatic reallocation',
            description:
                'Continuous allocation until runtime pool replenishment.',
          ),

          const SizedBox(height: 18),

          Row(
            children: [
              const Expanded(
                child: Text(
                  'Single choice selection',
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 11,
                    color: ALOFColors.onSurfaceMuted,
                  ),
                ),
              ),
              ElevatedButton.icon(
                onPressed: selectedAnswer == null ? null : _checkAnswer,
                icon: const Icon(Icons.done, size: 16),
                label: const Text('Check Answer'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: ALOFColors.primary,
                  foregroundColor: Colors.white,
                  disabledBackgroundColor: ALOFColors.surfaceSubtle,
                  disabledForegroundColor: ALOFColors.taupe,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 12,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(5),
                  ),
                  textStyle: const TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 11,
                    letterSpacing: 1,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAnswerOption({
    required String value,
    required String title,
    required String description,
  }) {
    final selected = selectedAnswer == value;

    return InkWell(
      onTap: () {
        setState(() {
          selectedAnswer = value;
        });
      },
      borderRadius: BorderRadius.circular(6),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: selected ? ALOFColors.surface : ALOFColors.surfaceLow,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(
            color: selected ? ALOFColors.primary : ALOFColors.borderSubtle,
            width: selected ? 1.5 : 1,
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Radio<String>(
              value: value,
              groupValue: selectedAnswer,
              onChanged: (value) {
                setState(() {
                  selectedAnswer = value;
                });
              },
              activeColor: ALOFColors.primary,
              visualDensity: VisualDensity.compact,
            ),
            const SizedBox(width: 4),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '($value) $title',
                    style: const TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: ALOFColors.onSurface,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: const TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 11,
                      height: 1.4,
                      color: ALOFColors.onSurfaceMuted,
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

  void _checkAnswer() {
    final correct = selectedAnswer == 'B';

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          correct
              ? 'Correct. The base case terminates recursive descent.'
              : 'Review the base case invariant and try again.',
        ),
        backgroundColor: correct
            ? ALOFColors.primary
            : ALOFColors.terracottaDark,
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // KNOWLEDGE FEEDBACK
  // ---------------------------------------------------------------------------

  Widget _buildKnowledgeFeedback() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: ALOFColors.surface,
        border: Border.all(color: ALOFColors.borderSubtle),
        borderRadius: BorderRadius.circular(8),
        boxShadow: const [
          BoxShadow(
            color: Color(0x12000000),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.only(bottom: 12),
            decoration: const BoxDecoration(
              border: Border(
                bottom: BorderSide(color: ALOFColors.borderSubtle),
              ),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.insights_outlined,
                  size: 18,
                  color: ALOFColors.taupe,
                ),
                const SizedBox(width: 8),
                Text(
                  'KNOWLEDGE FEEDBACK',
                  style: _mono(
                    fontSize: 11,
                    color: ALOFColors.taupe,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 1.1,
                  ),
                ),
                const Spacer(),
                const Text(
                  'Real-time State',
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 10,
                    color: ALOFColors.onSurfaceMuted,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          _feedbackItem(
            icon: Icons.check_circle_outline,
            iconColor: ALOFColors.primary,
            title: 'Understood: Base case termination invariant',
            description:
                'Accurately differentiated recursive descent from termination criteria.',
          ),

          const SizedBox(height: 8),

          _feedbackItem(
            icon: Icons.error_outline,
            iconColor: ALOFColors.terracotta,
            title: 'Needs reinforcement: Multi-branch call stack unwinding',
            description:
                'Scheduled next in sequence: handling multiple descent branches (e.g. tree recursion).',
          ),

          const SizedBox(height: 8),

          Container(
            padding: const EdgeInsets.only(top: 12),
            decoration: const BoxDecoration(
              border: Border(top: BorderSide(color: ALOFColors.borderSubtle)),
            ),
            child: Wrap(
              alignment: WrapAlignment.spaceBetween,
              crossAxisAlignment: WrapCrossAlignment.center,
              runSpacing: 10,
              children: [
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text(
                      'Next adaptive action:',
                      style: TextStyle(
                        fontFamily: 'JetBrains Mono',
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                        color: ALOFColors.taupe,
                      ),
                    ),
                    const SizedBox(width: 8),
                    _smallTag('Targeted Practice'),
                  ],
                ),
                TextButton(
                  onPressed: () {},
                  style: TextButton.styleFrom(
                    padding: EdgeInsets.zero,
                    minimumSize: Size.zero,
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'CONTINUE TO NEXT STEP',
                        style: _mono(
                          fontSize: 11,
                          color: ALOFColors.terracotta,
                          fontWeight: FontWeight.w500,
                          letterSpacing: 1,
                        ),
                      ),
                      const SizedBox(width: 6),
                      const Icon(
                        Icons.arrow_forward,
                        size: 16,
                        color: ALOFColors.terracotta,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _feedbackItem({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String description,
  }) {
    return Container(
      padding: const EdgeInsets.all(8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 18, color: iconColor),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                    color: ALOFColors.onSurface,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  description,
                  style: const TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 11,
                    height: 1.4,
                    color: ALOFColors.onSurfaceMuted,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // ASK ALOF
  // ---------------------------------------------------------------------------

  Widget _buildAskBar() {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: ALOFColors.surface,
        border: Border.all(color: ALOFColors.borderSubtle),
        borderRadius: BorderRadius.circular(8),
        boxShadow: const [
          BoxShadow(
            color: Color(0x10000000),
            blurRadius: 6,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          const Padding(
            padding: EdgeInsets.only(left: 8),
            child: Icon(
              Icons.chat_bubble_outline,
              size: 20,
              color: ALOFColors.taupe,
            ),
          ),
          const SizedBox(width: 10),

          Expanded(
            child: TextField(
              controller: questionController,
              decoration: const InputDecoration(
                hintText:
                    'Ask ALOF about this material or your source document...',
                border: InputBorder.none,
                isDense: true,
              ),
              style: const TextStyle(
                fontFamily: 'Inter',
                fontSize: 13,
                color: ALOFColors.onSurface,
              ),
              onSubmitted: (_) => _sendQuestion(),
            ),
          ),

          const SizedBox(width: 8),

          IconButton(
            onPressed: _sendQuestion,
            style: IconButton.styleFrom(
              backgroundColor: ALOFColors.primary,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(5),
              ),
            ),
            icon: const Icon(Icons.arrow_forward, size: 18),
          ),
        ],
      ),
    );
  }

  void _sendQuestion() {
    final question = questionController.text.trim();

    if (question.isEmpty) return;

    // TODO:
    // Router -> Planner -> Runtime -> Mentor
    //
    // Hiện tại chỉ clear input để giữ UI.
    questionController.clear();

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Question submitted to ALOF.')),
    );
  }

  // ---------------------------------------------------------------------------
  // FOOTER
  // ---------------------------------------------------------------------------

  Widget _buildFooter() {
    return Container(
      padding: const EdgeInsets.only(top: 16, bottom: 32),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Text(
              'Current Learning Node: Recursion · Base Case Invariant',
              style: TextStyle(
                fontFamily: 'JetBrains Mono',
                fontSize: 10,
                color: ALOFColors.onSurfaceMuted,
              ),
            ),
          ),
          SizedBox(width: 16),
          Text(
            'ALOF Living Notebook',
            style: TextStyle(
              fontFamily: 'JetBrains Mono',
              fontSize: 10,
              color: ALOFColors.onSurfaceMuted,
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // HELPERS
  // ---------------------------------------------------------------------------

  Widget _sectionLabel(String text) {
    return Text(
      text,
      style: _mono(
        fontSize: 11,
        color: ALOFColors.taupe,
        fontWeight: FontWeight.w600,
        letterSpacing: 1.2,
      ),
    );
  }

  Widget _smallTag(String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
      decoration: BoxDecoration(
        color: ALOFColors.surfaceLow,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: const TextStyle(
          fontFamily: 'JetBrains Mono',
          fontSize: 9,
          color: ALOFColors.onSurfaceMuted,
        ),
      ),
    );
  }

  TextStyle _mono({
    required double fontSize,
    required Color color,
    FontWeight fontWeight = FontWeight.w400,
    double letterSpacing = 0,
  }) {
    return TextStyle(
      fontFamily: 'JetBrains Mono',
      fontSize: fontSize,
      color: color,
      fontWeight: fontWeight,
      letterSpacing: letterSpacing,
    );
  }
}
