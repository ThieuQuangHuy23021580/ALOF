import 'dart:ui';

import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class ProfileData {
  String fullName;
  String email;
  String language;

  ProfileData({
    required this.fullName,
    required this.email,
    required this.language,
  });
}

/// Show the floating learner profile modal.
///
/// Usage:
/// showProfileModal(context);
Future<void> showProfileModal(BuildContext context) async {
  final profile = ProfileData(
    fullName: 'Huy Nguyen',
    email: 'huy.nguyen@alof.internal',
    language: 'English (US)',
  );

  await showGeneralDialog(
    context: context,
    barrierDismissible: true,
    barrierLabel: 'Learner Account',
    barrierColor: ALOFColors.primary.withOpacity(0.25),
    transitionDuration: const Duration(milliseconds: 220),
    pageBuilder: (context, animation, secondaryAnimation) {
      return _ProfileModalOverlay(profile: profile);
    },
    transitionBuilder: (context, animation, secondaryAnimation, child) {
      final curved = CurvedAnimation(
        parent: animation,
        curve: Curves.easeOutCubic,
      );

      return FadeTransition(opacity: curved, child: child);
    },
  );
}

class _ProfileModalOverlay extends StatelessWidget {
  final ProfileData profile;

  const _ProfileModalOverlay({required this.profile});

  @override
  Widget build(BuildContext context) {
    return Material(
      type: MaterialType.transparency,
      child: Stack(
        children: [
          // Backdrop blur.
          Positioned.fill(
            child: GestureDetector(
              onTap: () => Navigator.of(context).pop(),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 2, sigmaY: 2),
                child: Container(color: Colors.transparent),
              ),
            ),
          ),

          // Floating profile card.
          Positioned.fill(
            child: SafeArea(
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final isMobile = constraints.maxWidth < 600;

                  if (isMobile) {
                    return Align(
                      alignment: Alignment.bottomCenter,
                      child: _ProfileCard(profile: profile, isMobile: true),
                    );
                  }

                  return Align(
                    alignment: Alignment.topRight,
                    child: Padding(
                      padding: const EdgeInsets.only(top: 12, right: 24),
                      child: _ProfileCard(profile: profile, isMobile: false),
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfileCard extends StatefulWidget {
  final ProfileData profile;
  final bool isMobile;

  const _ProfileCard({required this.profile, required this.isMobile});

  @override
  State<_ProfileCard> createState() => _ProfileCardState();
}

class _ProfileCardState extends State<_ProfileCard> {
  bool _isEditing = false;

  late final TextEditingController _nameController;
  late final TextEditingController _emailController;

  late String _selectedLanguage;

  @override
  void initState() {
    super.initState();

    _nameController = TextEditingController(text: widget.profile.fullName);

    _emailController = TextEditingController(text: widget.profile.email);

    _selectedLanguage = widget.profile.language;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  void _close() {
    Navigator.of(context).pop();
  }

  void _startEditing() {
    setState(() {
      _nameController.text = widget.profile.fullName;
      _emailController.text = widget.profile.email;
      _selectedLanguage = widget.profile.language;
      _isEditing = true;
    });
  }

  void _cancelEditing() {
    setState(() {
      _isEditing = false;
      _nameController.text = widget.profile.fullName;
      _emailController.text = widget.profile.email;
      _selectedLanguage = widget.profile.language;
    });
  }

  void _saveChanges() {
    final name = _nameController.text.trim();
    final email = _emailController.text.trim();

    if (name.isEmpty || email.isEmpty) {
      return;
    }

    setState(() {
      widget.profile.fullName = name;
      widget.profile.email = email;
      widget.profile.language = _selectedLanguage;
      _isEditing = false;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Profile updated successfully'),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _signOut() {
    Navigator.of(context).pop();

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Signed out of session'),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: widget.isMobile ? double.infinity : 420,
      constraints: BoxConstraints(
        maxHeight: widget.isMobile
            ? MediaQuery.of(context).size.height * 0.9
            : MediaQuery.of(context).size.height - 100,
      ),
      decoration: BoxDecoration(
        color: ALOFColors.surface,
        border: Border.all(color: ALOFColors.borderSubtle),
        borderRadius: BorderRadius.only(
          topLeft: const Radius.circular(18),
          topRight: const Radius.circular(18),
          bottomLeft: Radius.circular(widget.isMobile ? 0 : 18),
          bottomRight: Radius.circular(widget.isMobile ? 0 : 18),
        ),
        boxShadow: const [
          BoxShadow(
            offset: Offset(0, 16),
            blurRadius: 36,
            spreadRadius: -8,
            color: Color(0x29383B35),
          ),
          BoxShadow(
            offset: Offset(0, 4),
            blurRadius: 12,
            color: Color(0x0D000000),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.only(
          topLeft: const Radius.circular(18),
          topRight: const Radius.circular(18),
          bottomLeft: Radius.circular(widget.isMobile ? 0 : 18),
          bottomRight: Radius.circular(widget.isMobile ? 0 : 18),
        ),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [_buildTopBar(), _buildUserHeader(), _buildProfileBody()],
          ),
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TOP BAR
  // ---------------------------------------------------------------------------

  Widget _buildTopBar() {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 20, 20, 12),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Color(0xFFF1EDE5))),
      ),
      child: Row(
        children: [
          const Expanded(
            child: Text(
              'LEARNER ACCOUNT',
              style: TextStyle(
                fontFamily: 'JetBrains Mono',
                fontSize: 11,
                fontWeight: FontWeight.w500,
                letterSpacing: 1.1,
                color: ALOFColors.taupe,
              ),
            ),
          ),
          InkWell(
            onTap: _close,
            borderRadius: BorderRadius.circular(20),
            child: const SizedBox(
              width: 30,
              height: 30,
              child: Icon(Icons.close, size: 18, color: ALOFColors.taupe),
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // USER HEADER
  // ---------------------------------------------------------------------------

  Widget _buildUserHeader() {
    final initials = _getInitials(widget.profile.fullName);

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: const BoxDecoration(
        color: Color(0xFFFAF7F0),
        border: Border(bottom: BorderSide(color: Color(0xFFF1EDE5))),
      ),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: ALOFColors.primary,
              shape: BoxShape.circle,
              border: Border.all(color: ALOFColors.surface, width: 4),
            ),
            alignment: Alignment.center,
            child: Text(
              initials,
              style: const TextStyle(
                fontFamily: 'Newsreader',
                fontSize: 20,
                fontWeight: FontWeight.w500,
                color: ALOFColors.surface,
              ),
            ),
          ),

          const SizedBox(width: 16),

          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.profile.fullName,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontFamily: 'Newsreader',
                    fontSize: 21,
                    fontWeight: FontWeight.w500,
                    color: ALOFColors.primary,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  widget.profile.email,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontFamily: 'JetBrains Mono',
                    fontSize: 11,
                    color: Color(0xFF524434),
                  ),
                ),
                const SizedBox(height: 9),
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: [
                    _badge(
                      'STUDENT ID • #9821',
                      background: const Color(0xFFE8E3D8),
                      foreground: ALOFColors.primary,
                    ),
                    _badge(
                      'ACTIVE',
                      background: const Color(0xFFF1DCC6),
                      foreground: const Color(0xFF733513),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // PROFILE BODY
  // ---------------------------------------------------------------------------

  Widget _buildProfileBody() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionHeader(),
          const SizedBox(height: 4),
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 180),
            child: _isEditing ? _buildEditForm() : _buildStaticProfile(),
          ),
          const SizedBox(height: 12),
          _buildAccountFooter(),
        ],
      ),
    );
  }

  Widget _buildSectionHeader() {
    return Container(
      padding: const EdgeInsets.only(bottom: 6),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Color(0xFFF1EDE5))),
      ),
      child: Row(
        children: [
          const Expanded(
            child: Text(
              'ACCOUNT PROFILE',
              style: TextStyle(
                fontFamily: 'JetBrains Mono',
                fontSize: 10,
                fontWeight: FontWeight.w600,
                letterSpacing: 1.5,
                color: ALOFColors.taupe,
              ),
            ),
          ),
          if (!_isEditing)
            TextButton.icon(
              onPressed: _startEditing,
              style: TextButton.styleFrom(
                foregroundColor: ALOFColors.primary,
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                minimumSize: Size.zero,
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
              icon: const Icon(Icons.edit_outlined, size: 15),
              label: const Text(
                'Edit',
                style: TextStyle(fontFamily: 'JetBrains Mono', fontSize: 12),
              ),
            ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // STATIC VIEW
  // ---------------------------------------------------------------------------

  Widget _buildStaticProfile() {
    return Column(
      key: const ValueKey('static-profile'),
      children: [
        _profileRow(
          label: 'Full Name',
          value: widget.profile.fullName,
          trailing: _smallTag(
            'PRIMARY',
            background: const Color(0xFFFAF7F0),
            border: ALOFColors.borderSubtle,
            foreground: ALOFColors.taupe,
          ),
        ),
        _profileRow(
          label: 'Email Address',
          value: widget.profile.email,
          trailing: const Icon(
            Icons.verified_outlined,
            size: 17,
            color: Color(0xFF4D635C),
          ),
        ),
        _profileRow(
          label: 'Preferred Language',
          value: widget.profile.language,
          trailing: _smallTag(
            'en-US',
            background: const Color(0xFFE5EFEA),
            border: const Color(0xFFB4CCC3),
            foreground: ALOFColors.primary,
          ),
        ),
      ],
    );
  }

  Widget _profileRow({
    required String label,
    required String value,
    required Widget trailing,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Color(0xFFF1EDE5))),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: ALOFColors.taupe,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  value,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontFamily: label == 'Email Address'
                        ? 'JetBrains Mono'
                        : 'Inter',
                    fontSize: label == 'Email Address' ? 12.5 : 13.5,
                    fontWeight: FontWeight.w500,
                    color: ALOFColors.primary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          trailing,
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // EDIT FORM
  // ---------------------------------------------------------------------------

  Widget _buildEditForm() {
    return Form(
      key: const ValueKey('edit-profile'),
      child: Padding(
        padding: const EdgeInsets.only(top: 4),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _fieldLabel('Full Name'),
            const SizedBox(height: 5),
            TextField(
              controller: _nameController,
              style: const TextStyle(
                fontFamily: 'Inter',
                fontSize: 14,
                color: ALOFColors.primary,
              ),
              decoration: _inputDecoration(),
            ),
            const SizedBox(height: 14),
            _fieldLabel('Email Address'),
            const SizedBox(height: 5),
            TextField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              style: const TextStyle(
                fontFamily: 'JetBrains Mono',
                fontSize: 12.5,
                color: ALOFColors.primary,
              ),
              decoration: _inputDecoration(),
            ),
            const SizedBox(height: 14),
            _fieldLabel('Preferred Language'),
            const SizedBox(height: 5),
            DropdownButtonFormField<String>(
              value: _selectedLanguage,
              decoration: _inputDecoration(),
              style: const TextStyle(
                fontFamily: 'Inter',
                fontSize: 14,
                color: ALOFColors.primary,
              ),
              dropdownColor: ALOFColors.surface,
              items: const [
                DropdownMenuItem(
                  value: 'English (US)',
                  child: Text('English (US)'),
                ),
                DropdownMenuItem(
                  value: 'English (UK)',
                  child: Text('English (UK)'),
                ),
                DropdownMenuItem(
                  value: 'Tiếng Việt',
                  child: Text('Tiếng Việt'),
                ),
                DropdownMenuItem(value: 'Français', child: Text('Français')),
                DropdownMenuItem(value: 'Deutsch', child: Text('Deutsch')),
              ],
              onChanged: (value) {
                if (value == null) return;

                setState(() {
                  _selectedLanguage = value;
                });
              },
            ),
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.only(top: 10),
              decoration: const BoxDecoration(
                border: Border(top: BorderSide(color: Color(0xFFF1EDE5))),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: _cancelEditing,
                    style: TextButton.styleFrom(
                      foregroundColor: ALOFColors.taupe,
                    ),
                    child: const Text(
                      'CANCEL',
                      style: TextStyle(
                        fontFamily: 'JetBrains Mono',
                        fontSize: 11,
                        letterSpacing: 0.7,
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                  FilledButton(
                    onPressed: _saveChanges,
                    style: FilledButton.styleFrom(
                      backgroundColor: ALOFColors.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 9,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                    child: const Text(
                      'SAVE CHANGES',
                      style: TextStyle(
                        fontFamily: 'JetBrains Mono',
                        fontSize: 11,
                        letterSpacing: 0.7,
                      ),
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

  Widget _fieldLabel(String text) {
    return Text(
      text,
      style: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: ALOFColors.taupe,
      ),
    );
  }

  InputDecoration _inputDecoration() {
    return InputDecoration(
      filled: true,
      fillColor: ALOFColors.surface,
      isDense: true,
      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(4),
        borderSide: const BorderSide(color: Color(0xFFC2C8C4)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(4),
        borderSide: const BorderSide(color: Color(0xFFC2C8C4)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(4),
        borderSide: const BorderSide(color: ALOFColors.primary, width: 1.2),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // ACCOUNT FOOTER
  // ---------------------------------------------------------------------------

  Widget _buildAccountFooter() {
    return Container(
      padding: const EdgeInsets.only(top: 16),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Color(0xFFF1EDE5))),
      ),
      child: Row(
        children: [
          const Expanded(
            child: Text(
              'Session: Authenticated',
              style: TextStyle(
                fontFamily: 'JetBrains Mono',
                fontSize: 10,
                color: ALOFColors.taupe,
              ),
            ),
          ),
          TextButton.icon(
            onPressed: _signOut,
            style: TextButton.styleFrom(
              foregroundColor: const Color(0xFF8C4A32),
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
              minimumSize: Size.zero,
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
            icon: const Icon(Icons.logout_outlined, size: 15),
            label: const Text(
              'SIGN OUT',
              style: TextStyle(
                fontFamily: 'JetBrains Mono',
                fontSize: 11,
                letterSpacing: 0.8,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // SMALL UI HELPERS
  // ---------------------------------------------------------------------------

  Widget _badge(
    String text, {
    required Color background,
    required Color foreground,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontFamily: 'JetBrains Mono',
          fontSize: 9,
          fontWeight: FontWeight.w500,
          letterSpacing: 0.7,
          color: foreground,
        ),
      ),
    );
  }

  Widget _smallTag(
    String text, {
    required Color background,
    required Color border,
    required Color foreground,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: border),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontFamily: 'JetBrains Mono',
          fontSize: 10,
          letterSpacing: 0.5,
          color: foreground,
        ),
      ),
    );
  }

  String _getInitials(String name) {
    final parts = name
        .trim()
        .split(RegExp(r'\s+'))
        .where((e) => e.isNotEmpty)
        .toList();

    if (parts.isEmpty) return '';

    if (parts.length == 1) {
      return parts.first
          .substring(0, parts.first.length >= 2 ? 2 : 1)
          .toUpperCase();
    }

    return '${parts.first[0]}${parts.last[0]}'.toUpperCase();
  }
}
