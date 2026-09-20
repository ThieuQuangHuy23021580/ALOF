import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'theme/app_theme.dart';
import 'screens/journey_screen.dart';
import 'screens/sessions_screen.dart';
import 'screens/ledger_screen.dart';

void main() {
  runApp(const ALOFApp());
}

class ALOFApp extends StatelessWidget {
  const ALOFApp({super.key});

  static final _router = GoRouter(
    initialLocation: '/journey',
    routes: [
      GoRoute(
        path: '/journey',
        builder: (context, state) => const JourneyScreen(),
      ),
      GoRoute(
        path: '/sessions',
        builder: (context, state) => const SessionsScreen(),
      ),
      GoRoute(
        path: '/ledger',
        builder: (context, state) => const LedgerScreen(),
      ),
      GoRoute(
        path: '/preferences',
        builder: (context, state) =>
            const PlaceholderPage(title: 'Preferences'),
      ),
    ],
  );

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      debugShowCheckedModeBanner: false,
      title: 'ALOF Notebook',
      theme: ALOFTheme.light,
      routerConfig: _router,
    );
  }
}

class PlaceholderPage extends StatelessWidget {
  final String title;

  const PlaceholderPage({super.key, required this.title});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ALOFColors.background,
      body: Center(
        child: Text(
          title,
          style: const TextStyle(
            fontFamily: 'Newsreader',
            fontSize: 32,
            color: ALOFColors.primary,
          ),
        ),
      ),
    );
  }
}
