import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../theme/app_theme.dart';
import 'profile_modal.dart';

class AppShell extends StatelessWidget {
  final Widget child;

  const AppShell({super.key, required this.child});

  static const _tabs = [
    ('Journey', '/journey'),
    ('Sessions', '/sessions'),
    ('Ledger', '/ledger'),
    ('Preferences', '/preferences'),
  ];

  @override
  Widget build(BuildContext context) {
    final path = GoRouterState.of(context).uri.path;

    return Scaffold(
      backgroundColor: ALOFColors.background,
      body: SafeArea(
        child: Column(
          children: [
            _TopNavigation(currentPath: path),
            Expanded(child: child),
            const _AppFooter(),
          ],
        ),
      ),
    );
  }
}

class _TopNavigation extends StatelessWidget {
  final String currentPath;

  const _TopNavigation({required this.currentPath});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 64,
      decoration: const BoxDecoration(
        color: Color(0xFFFBF8F2),
        border: Border(
          bottom: BorderSide(color: ALOFColors.borderSubtle, width: .8),
        ),
      ),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(
              children: [
                const _Brand(),
                const SizedBox(width: 24),
                Container(width: 1, height: 16, color: ALOFColors.borderSubtle),
                const SizedBox(width: 16),
                Expanded(
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        for (final tab in AppShell._tabs)
                          _NavItem(
                            label: tab.$1,
                            path: tab.$2,
                            active: currentPath == tab.$2,
                          ),
                      ],
                    ),
                  ),
                ),
                const _UserPill(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Brand extends StatelessWidget {
  const _Brand();

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        if (GoRouterState.of(context).uri.path != '/journey') {
          context.go('/journey');
        }
      },
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: ALOFColors.primary,
              borderRadius: BorderRadius.circular(3),
            ),
            child: const Text(
              'A',
              style: TextStyle(
                fontFamily: 'Newsreader',
                fontSize: 19,
                fontWeight: FontWeight.bold,
                color: ALOFColors.surface,
              ),
            ),
          ),
          const SizedBox(width: 12),
          const Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'ALOF',
                style: TextStyle(
                  fontFamily: 'Newsreader',
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: ALOFColors.primary,
                  height: 1,
                ),
              ),
              SizedBox(height: 3),
              Text(
                'NOTEBOOK',
                style: TextStyle(
                  fontFamily: 'JetBrains Mono',
                  fontSize: 9,
                  letterSpacing: 1.4,
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

class _NavItem extends StatelessWidget {
  final String label;
  final String path;
  final bool active;

  const _NavItem({
    required this.label,
    required this.path,
    required this.active,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        if (GoRouterState.of(context).uri.path != path) {
          context.go(path);
        }
      },
      child: Container(
        height: 64,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              color: active ? ALOFColors.terracotta : Colors.transparent,
              width: 2,
            ),
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              fontFamily: 'Newsreader',
              fontSize: 14,
              fontWeight: active ? FontWeight.w600 : FontWeight.w400,
              color: active ? ALOFColors.terracotta : ALOFColors.onSurfaceMuted,
            ),
          ),
        ),
      ),
    );
  }
}

class _UserPill extends StatelessWidget {
  const _UserPill();

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () => showProfileModal(context),
      borderRadius: BorderRadius.circular(30),
      child: Padding(
        padding: const EdgeInsets.only(left: 8),
        child: Row(
          children: [
            Container(width: 1, height: 24, color: ALOFColors.borderSubtle),
            const SizedBox(width: 12),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'Huy',
                  style: TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: ALOFColors.onSurface,
                  ),
                ),
                SizedBox(height: 2),
                Text(
                  'Intermediate',
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 9,
                    color: ALOFColors.taupe,
                  ),
                ),
              ],
            ),
            const SizedBox(width: 10),
            Container(
              width: 32,
              height: 32,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: ALOFColors.primary,
              ),
              child: const Icon(
                Icons.person_outline,
                size: 17,
                color: ALOFColors.surface,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AppFooter extends StatelessWidget {
  const _AppFooter();

  @override
  Widget build(BuildContext context) {
    final wide = MediaQuery.sizeOf(context).width > 650;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
      decoration: const BoxDecoration(
        color: Color(0xFFFBF8F2),
        border: Border(top: BorderSide(color: ALOFColors.borderSubtle)),
      ),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Row(
            children: [
              const Expanded(
                child: Text(
                  '§ ALOF Digital Learning Notebook — Academic Archival System',
                  style: TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 12,
                    color: ALOFColors.taupe,
                  ),
                ),
              ),
              if (wide)
                const Text(
                  'EPISTEMIC RECORD • CONTINUOUS INQUIRY',
                  style: TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 9,
                    letterSpacing: 1,
                    color: ALOFColors.taupe,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
