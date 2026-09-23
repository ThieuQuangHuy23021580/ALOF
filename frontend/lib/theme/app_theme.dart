import 'package:flutter/material.dart';

class ALOFColors {
  static const background = Color(0xFFF4F0E8);
  static const surface = Color(0xFFFFFDF8);
  static const surfaceLow = Color(0xFFEFEAE0);
  static const surfaceSubtle = Color(0xFFE8E2D5);

  static const borderSubtle = Color(0xFFDDD7CA);
  static const borderStrong = Color(0xFFC5BEAF);

  static const primary = Color(0xFF263B35);
  static const primaryDark = Color(0xFF162723);

  static const terracotta = Color(0xFFB86B45);
  static const terracottaDark = Color(0xFF99522F);
  static const terracottaLight = Color(0xFFF8EFEA);

  static const taupe = Color(0xFF7A6A58);
  static const taupeLight = Color(0xFFA39482);

  static const onSurface = Color(0xFF1C1C17);
  static const onSurfaceMuted = Color(0xFF575249);
}

class ALOFTheme {
  static ThemeData get light {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: ALOFColors.background,
      colorScheme: const ColorScheme.light(
        primary: ALOFColors.primary,
        surface: ALOFColors.surface,
        error: Color(0xFFBA1A1A),
      ),
      fontFamily: 'Newsreader',
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFFFBF8F2),
        elevation: 0,
        surfaceTintColor: Colors.transparent,
      ),
      dividerColor: ALOFColors.borderSubtle,
      textTheme: const TextTheme(
        displayLarge: TextStyle(
          fontFamily: 'Newsreader',
          fontSize: 48,
          fontWeight: FontWeight.w400,
          color: ALOFColors.primary,
          height: 1.1,
        ),
        headlineMedium: TextStyle(
          fontFamily: 'Newsreader',
          fontSize: 30,
          fontWeight: FontWeight.w400,
          color: ALOFColors.primary,
        ),
        titleLarge: TextStyle(
          fontFamily: 'Newsreader',
          fontSize: 20,
          fontWeight: FontWeight.w500,
          color: ALOFColors.primary,
        ),
        bodyLarge: TextStyle(
          fontFamily: 'Newsreader',
          fontSize: 18,
          height: 1.6,
          color: ALOFColors.onSurfaceMuted,
        ),
        bodyMedium: TextStyle(
          fontFamily: 'Newsreader',
          fontSize: 16,
          height: 1.6,
          color: ALOFColors.onSurfaceMuted,
        ),
      ),
    );
  }
}
