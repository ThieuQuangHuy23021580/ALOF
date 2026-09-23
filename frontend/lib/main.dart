import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'domain/data/api/api_client.dart';
import 'domain/data/repositories/alof_repository.dart';
import 'theme/app_theme.dart';
import 'widgets/app_shell.dart';
import 'screens/journey_screen.dart';
import 'screens/sessions_screen.dart';
import 'screens/ledger_screen.dart';
import 'screens/preferences_screen.dart';
import 'screens/learning_session_screen.dart';

String _apiBaseUrl() {
  if (kIsWeb) {
    return 'http://127.0.0.1:8000';
  }

  if (Platform.isAndroid) {
    return 'http://10.0.2.2:8000';
  }

  return 'http://127.0.0.1:8000';
}

void main() {
  final apiClient = ApiClient(baseUrl: _apiBaseUrl());

  final repository = AlofRepository(api: apiClient);

  runApp(
    Provider<AlofRepository>.value(value: repository, child: const ALOFApp()),
  );
}

class ALOFApp extends StatelessWidget {
  const ALOFApp({super.key});

  static final _router = GoRouter(
    initialLocation: '/journey',
    routes: [
      ShellRoute(
        builder: (context, state, child) => AppShell(child: child),
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
            builder: (context, state) => const PreferencesScreen(),
          ),
        ],
      ),
      GoRoute(
        path: '/learning-session',
        builder: (context, state) => const LearningSessionScreen(),
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
