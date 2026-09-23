import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../theme/app_theme.dart';

class LedgerScreen extends StatefulWidget {
  const LedgerScreen({super.key});

  @override
  State<LedgerScreen> createState() => _LedgerScreenState();
}

class _LedgerScreenState extends State<LedgerScreen> {
  String selectedFilter = 'all';
  int selectedConcept = 1;

  final concepts = const [
    LedgerConcept(
      name: 'Recursion',
      level: 'Intermediate',
      description:
          'Call stack frame resolution, self-referential mathematical formulations.',
      category: 'intermediate',
    ),
    LedgerConcept(
      name: 'Base Case',
      level: 'Beginner',
      description: 'Terminal criteria, stack-overflow prevention, edge guards.',
      category: 'beginner',
      weak: true,
    ),
    LedgerConcept(
      name: 'Recursive Tree',
      level: 'Beginner',
      description: 'Branching factor visualization, subproblem depth mapping.',
      category: 'beginner',
    ),
    LedgerConcept(
      name: 'Sorting Algorithms',
      level: 'Intermediate',
      description:
          'Merge sort divide-and-conquer, QuickSort partition mechanics.',
      category: 'intermediate',
    ),
    LedgerConcept(
      name: 'Dynamic Programming',
      level: 'Advanced',
      description: 'Overlapping subproblems, memoization tables vs tabulation.',
      category: 'advanced',
      weak: true,
    ),
    LedgerConcept(
      name: 'Big-O Complexity',
      level: 'Advanced',
      description:
          'Asymptotic space-time bounds, Master Theorem recurrence classification.',
      category: 'advanced',
    ),
  ];

  List<LedgerConcept> get filteredConcepts {
    if (selectedFilter == 'all') return concepts;

    if (selectedFilter == 'weak') {
      return concepts.where((c) => c.weak).toList();
    }

    return concepts.where((c) => c.category == selectedFilter).toList();
  }

  LedgerConcept get currentConcept => concepts[selectedConcept];

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(24, 32, 24, 48),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildPageHeader(),
                const SizedBox(height: 28),
                _buildFilters(),
                const SizedBox(height: 28),
                _buildWorkspace(),
                const SizedBox(height: 64),
                _buildEvidenceSection(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // PAGE HEADER
  // ---------------------------------------------------------------------------

  Widget _buildPageHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Row(
          children: [
            Text(
              'KNOWLEDGE LEDGER',
              style: TextStyle(
                fontFamily: 'JetBrains Mono',
                fontSize: 11,
                letterSpacing: 1.4,
                color: ALOFColors.taupe,
              ),
            ),
            SizedBox(width: 10),
            Icon(Icons.circle, size: 6, color: ALOFColors.terracotta),
            SizedBox(width: 10),
            Text(
              'ALGORITHMIC FOUNDATIONS',
              style: TextStyle(
                fontFamily: 'JetBrains Mono',
                fontSize: 11,
                color: ALOFColors.onSurfaceMuted,
              ),
            ),
          ],
        ),
        SizedBox(height: 10),
        Text(
          'Learning Ledger',
          style: TextStyle(
            fontFamily: 'Newsreader',
            fontSize: 52,
            height: 1.05,
            fontWeight: FontWeight.w400,
            color: ALOFColors.primary,
          ),
        ),
        SizedBox(height: 8),
        Text(
          'Your current knowledge state and the evidence behind it.',
          style: TextStyle(
            fontFamily: 'Newsreader',
            fontSize: 18,
            height: 1.55,
            color: ALOFColors.taupe,
          ),
        ),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // FILTERS
  // ---------------------------------------------------------------------------

  Widget _buildFilters() {
    final filters = [
      ('all', 'All Concepts', 6),
      ('beginner', 'Beginner', 2),
      ('intermediate', 'Intermediate', 2),
      ('advanced', 'Advanced', 2),
      ('weak', 'Weak', 2),
    ];

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: filters.map((filter) {
            final active = selectedFilter == filter.$1;

            return InkWell(
              onTap: () {
                setState(() {
                  selectedFilter = filter.$1;
                });
              },
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                decoration: active
                    ? const BoxDecoration(
                        border: Border(
                          bottom: BorderSide(
                            color: ALOFColors.terracotta,
                            width: 2,
                          ),
                        ),
                      )
                    : null,
                child: RichText(
                  text: TextSpan(
                    children: [
                      TextSpan(
                        text: filter.$2.toUpperCase(),
                        style: TextStyle(
                          fontFamily: 'JetBrains Mono',
                          fontSize: 11,
                          letterSpacing: 1,
                          fontWeight: active
                              ? FontWeight.w600
                              : FontWeight.w400,
                          color: active
                              ? ALOFColors.primary
                              : ALOFColors.onSurfaceMuted,
                        ),
                      ),
                      TextSpan(
                        text: '  (${filter.$3})',
                        style: const TextStyle(
                          fontFamily: 'JetBrains Mono',
                          fontSize: 10,
                          color: ALOFColors.taupe,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // WORKSPACE
  // ---------------------------------------------------------------------------

  Widget _buildWorkspace() {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < 850) {
          return Column(
            children: [
              _buildConceptList(),
              const SizedBox(height: 24),
              _buildSelectedConcept(),
            ],
          );
        }

        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(flex: 8, child: _buildConceptList()),
            const SizedBox(width: 32),
            Expanded(flex: 4, child: _buildSelectedConcept()),
          ],
        );
      },
    );
  }

  Widget _buildConceptList() {
    final items = filteredConcepts;

    return Column(
      children: items.map((concept) {
        final index = concepts.indexOf(concept);
        final selected = index == selectedConcept;

        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: _conceptCard(concept, index, selected),
        );
      }).toList(),
    );
  }

  Widget _conceptCard(LedgerConcept concept, int index, bool selected) {
    return InkWell(
      onTap: () {
        setState(() {
          selectedConcept = index;
        });
      },
      borderRadius: BorderRadius.circular(4),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: selected ? ALOFColors.surfaceLow : ALOFColors.surface,
          borderRadius: BorderRadius.circular(4),
          border: Border.all(
            color: selected ? ALOFColors.terracotta : ALOFColors.borderSubtle,
          ),
        ),
        child: Row(
          children: [
            SizedBox(
              width: 32,
              child: Text(
                '${index + 1}'.padLeft(2, '0') + '.',
                style: TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 11,
                  color: selected
                      ? ALOFColors.terracottaDark
                      : ALOFColors.taupe,
                  fontWeight: selected ? FontWeight.w700 : FontWeight.w400,
                ),
              ),
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    children: [
                      Text(
                        concept.name,
                        style: TextStyle(
                          fontFamily: 'Newsreader',
                          fontSize: 19,
                          fontWeight: selected
                              ? FontWeight.w600
                              : FontWeight.w500,
                          color: ALOFColors.primary,
                        ),
                      ),
                      _levelTag(concept.level),
                      if (concept.weak) _weakTag(),
                      if (selected)
                        const Text(
                          'SELECTED',
                          style: TextStyle(
                            fontFamily: 'JetBrains Mono',
                            fontSize: 10,
                            letterSpacing: .8,
                            fontWeight: FontWeight.w600,
                            color: ALOFColors.terracotta,
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    concept.description,
                    style: const TextStyle(
                      fontFamily: 'Newsreader',
                      fontSize: 13,
                      height: 1.4,
                      color: ALOFColors.taupe,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Icon(
              selected ? Icons.arrow_forward : Icons.chevron_right,
              size: 20,
              color: selected ? ALOFColors.terracotta : ALOFColors.taupe,
            ),
          ],
        ),
      ),
    );
  }

  Widget _levelTag(String level) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: ALOFColors.surfaceLow,
        borderRadius: BorderRadius.circular(3),
      ),
      child: Text(
        level.toUpperCase(),
        style: const TextStyle(
          fontFamily: 'JetBrains Mono',
          fontSize: 10,
          letterSpacing: .5,
          color: ALOFColors.primary,
        ),
      ),
    );
  }

  Widget _weakTag() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: ALOFColors.terracottaLight,
        borderRadius: BorderRadius.circular(3),
      ),
      child: const Text(
        'WEAK',
        style: TextStyle(
          fontFamily: 'JetBrains Mono',
          fontSize: 10,
          letterSpacing: .5,
          fontWeight: FontWeight.w600,
          color: ALOFColors.terracottaDark,
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // SELECTED CONCEPT
  // ---------------------------------------------------------------------------

  Widget _buildSelectedConcept() {
    final concept = currentConcept;

    return Column(
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: ALOFColors.surface,
            border: Border.all(color: ALOFColors.borderSubtle),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _selectedHeader(concept),
              const SizedBox(height: 16),
              Text(
                concept.name,
                style: const TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 28,
                  fontWeight: FontWeight.w500,
                  color: ALOFColors.primary,
                ),
              ),
              const SizedBox(height: 14),
              Divider(color: ALOFColors.borderSubtle),
              const SizedBox(height: 14),
              const Row(
                children: [
                  Icon(
                    Icons.verified_outlined,
                    size: 18,
                    color: ALOFColors.terracotta,
                  ),
                  SizedBox(width: 8),
                  Text(
                    'KNOWLEDGE DIAGNOSIS',
                    style: TextStyle(
                      fontFamily: 'JetBrains Mono',
                      fontSize: 10,
                      letterSpacing: 1,
                      color: ALOFColors.taupe,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                'Diagnostic assessment indicates recurring omission of leaf return guarantees and improper edge guard ordering in recursive termination branches.',
                style: TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 14,
                  height: 1.55,
                  color: ALOFColors.onSurfaceMuted,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        _buildEvidenceCard(),
        const SizedBox(height: 20),
        _buildRecommendedAction(),
      ],
    );
  }

  Widget _selectedHeader(LedgerConcept concept) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Expanded(
          child: Text(
            'SELECTED CONCEPT',
            style: TextStyle(
              fontFamily: 'JetBrains Mono',
              fontSize: 10,
              letterSpacing: 1.2,
              color: ALOFColors.taupe,
            ),
          ),
        ),
        _levelTag(concept.level),
        if (concept.weak) ...[const SizedBox(width: 6), _weakTag()],
      ],
    );
  }

  Widget _buildEvidenceCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: ALOFColors.surface,
        border: Border.all(color: ALOFColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.description_outlined,
                size: 20,
                color: ALOFColors.taupe,
              ),
              SizedBox(width: 8),
              Text(
                'Learning Evidence',
                style: TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 20,
                  fontWeight: FontWeight.w500,
                  color: ALOFColors.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _evidenceItem(
            label: 'ASSESSMENT EVIDENCE',
            text:
                'Omission of explicit terminal return in recursive binary tree traversal condition.',
            accent: ALOFColors.terracotta,
          ),
          const SizedBox(height: 12),
          _evidenceItem(
            label: 'INTERACTION NOTE',
            text:
                'Demonstrated accurate explanation of call stack unwinding during guided explanation session.',
            accent: ALOFColors.taupe,
          ),
        ],
      ),
    );
  }

  Widget _evidenceItem({
    required String label,
    required String text,
    required Color accent,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: ALOFColors.surfaceLow,
        border: Border(left: BorderSide(color: accent, width: 2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: TextStyle(
              fontFamily: 'JetBrains Mono',
              fontSize: 10,
              letterSpacing: 1,
              fontWeight: FontWeight.w600,
              color: accent,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            text,
            style: const TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 14,
              height: 1.5,
              color: ALOFColors.onSurfaceMuted,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendedAction() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: ALOFColors.surface,
        border: Border.all(color: ALOFColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.play_circle_outline,
                size: 20,
                color: ALOFColors.terracotta,
              ),
              SizedBox(width: 8),
              Text(
                'ACTION TYPE: PRACTICE',
                style: TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 10,
                  letterSpacing: 1,
                  fontWeight: FontWeight.w600,
                  color: ALOFColors.terracotta,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          const Text(
            'Targeted Practice: Base-case invariants and terminal boundary conditions.',
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 14,
              height: 1.5,
              color: ALOFColors.onSurfaceMuted,
            ),
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: () {
                // Router → Planner → Runtime
                context.go('/learning-session');
              },
              icon: const Icon(Icons.arrow_forward, size: 16),
              label: const Text('START PRACTICE SESSION'),
              style: FilledButton.styleFrom(
                backgroundColor: ALOFColors.terracotta,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // RECENT EVIDENCE
  // ---------------------------------------------------------------------------

  Widget _buildEvidenceSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.only(top: 32),
          decoration: BoxDecoration(
            border: Border(top: BorderSide(color: ALOFColors.borderSubtle)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Row(
                children: [
                  Text(
                    'EVIDENCE RECORD',
                    style: TextStyle(
                      fontFamily: 'JetBrains Mono',
                      fontSize: 10,
                      letterSpacing: 1.1,
                      color: ALOFColors.taupe,
                    ),
                  ),
                  SizedBox(width: 10),
                  Icon(Icons.circle, size: 4, color: ALOFColors.taupe),
                  SizedBox(width: 10),
                  Text(
                    'CHRONOLOGY',
                    style: TextStyle(
                      fontFamily: 'JetBrains Mono',
                      fontSize: 10,
                      color: ALOFColors.taupe,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 5),
              Text(
                'Recent Learning Evidence',
                style: TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 28,
                  fontWeight: FontWeight.w500,
                  color: ALOFColors.primary,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        LayoutBuilder(
          builder: (context, constraints) {
            final count = constraints.maxWidth < 700 ? 1 : 3;

            return GridView.count(
              crossAxisCount: count,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisSpacing: 20,
              mainAxisSpacing: 20,
              childAspectRatio: count == 1 ? 2.1 : 1.35,
              children: const [
                EvidenceRecord(
                  type: 'DIAGNOSTIC ASSESSMENT',
                  status: 'WEAK RESPONSE',
                  concept: 'Base Case',
                  description: 'Incomplete base-case guard',
                  accent: ALOFColors.terracotta,
                ),
                EvidenceRecord(
                  type: 'PRACTICE EXERCISE',
                  status: 'VERIFIED',
                  concept: 'Recursive Tree',
                  description: 'Branching depth correctly calculated',
                  accent: ALOFColors.primary,
                ),
                EvidenceRecord(
                  type: 'ASSESSMENT CHECK',
                  status: 'VERIFIED',
                  concept: 'Big-O Complexity',
                  description: 'Correct logarithmic bound classification',
                  accent: ALOFColors.primary,
                ),
              ],
            );
          },
        ),
      ],
    );
  }

}

// -----------------------------------------------------------------------------
// MODELS
// -----------------------------------------------------------------------------

class LedgerConcept {
  final String name;
  final String level;
  final String description;
  final String category;
  final bool weak;

  const LedgerConcept({
    required this.name,
    required this.level,
    required this.description,
    required this.category,
    this.weak = false,
  });
}

class EvidenceRecord extends StatelessWidget {
  final String type;
  final String status;
  final String concept;
  final String description;
  final Color accent;

  const EvidenceRecord({
    super.key,
    required this.type,
    required this.status,
    required this.concept,
    required this.description,
    required this.accent,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: ALOFColors.surface,
        border: Border.all(color: ALOFColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  type,
                  style: const TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 10,
                    letterSpacing: .9,
                    color: ALOFColors.taupe,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                decoration: BoxDecoration(
                  color: accent == ALOFColors.terracotta
                      ? ALOFColors.terracottaLight
                      : ALOFColors.surfaceLow,
                  borderRadius: BorderRadius.circular(3),
                ),
                child: Text(
                  status,
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 9,
                    fontWeight: FontWeight.w600,
                    color: accent,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            concept,
            style: const TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: ALOFColors.primary,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            description,
            style: const TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 13,
              height: 1.4,
              color: ALOFColors.taupe,
            ),
          ),
          const Spacer(),
          Divider(color: ALOFColors.borderSubtle),
          const SizedBox(height: 8),
          Row(
            children: [
              Text(
                'CONCEPT RECORD',
                style: TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 9,
                  color: accent,
                ),
              ),
              const Spacer(),
              const Text(
                'View Details  →',
                style: TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 13,
                  color: ALOFColors.taupe,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
