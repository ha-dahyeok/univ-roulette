import re

with open('campus_roulette/lib/screens/home_screen.dart', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add color helpers
color_helpers = """
  Color get _primaryColor {
    if (_selectedUniv.contains('연세')) return const Color(0xFF1428A0); // 연세 블루
    if (_selectedUniv.contains('고려')) return const Color(0xFF8A1538); // 크림슨
    return const Color(0xFF2D3436); // 기본
  }

  Color get _lightColor {
    if (_selectedUniv.contains('연세')) return const Color(0xFFE8EAF6);
    if (_selectedUniv.contains('고려')) return const Color(0xFFFCE4EC);
    return const Color(0xFFF1F2F6);
  }

  Widget _buildSectionCard({required Widget child}) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 500),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: _primaryColor.withOpacity(0.08),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: child,
    );
  }
"""

# Insert helpers before build method
content = content.replace("  @override\n  Widget build(BuildContext context) {", color_helpers + "\n  @override\n  Widget build(BuildContext context) {")

# 2. Replace Scaffold
old_scaffold = """    return Scaffold(
      appBar: AppBar(
        title: const Text(
          '🎡 캠퍼스 룰렛',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: ["""

new_scaffold = """    return AnimatedTheme(
      data: Theme.of(context).copyWith(
        colorScheme: ColorScheme.fromSeed(
          seedColor: _primaryColor,
          primary: _primaryColor,
        ),
        primaryColor: _primaryColor,
      ),
      duration: const Duration(milliseconds: 500),
      child: Scaffold(
        backgroundColor: _lightColor,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          title: Text(
            '🎡 캠퍼스 룰렛',
            style: TextStyle(
              fontWeight: FontWeight.w900,
              color: _primaryColor,
              fontSize: 24,
            ),
          ),
          centerTitle: true,
        ),
        body: Stack(
          children: [
            SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: ["""

content = content.replace(old_scaffold, new_scaffold)

# 3. Replace University Choice
old_univ = """                // 1. 대학교 검색 (객관식 선택)
                const Text(
                  '🎓 대학교 선택',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: targetUniversities.map((univ) {
                    return ChoiceChip(
                      label: Text(univ),
                      showCheckmark: false,
                      selected: _selectedUniv == univ,
                      onSelected: (selected) {
                        setState(() {
                          if (selected) {
                            _selectedUniv = univ;
                          } else {
                            _selectedUniv = '';
                          }
                          _selectedGates.clear(); // 대학이 바뀌면 선택된 게이트 초기화
                        });
                      },
                    );
                  }).toList(),
                ),"""

new_univ = """                // 1. 대학교 검색 (객관식 선택)
                _buildSectionCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '🎓 대학교 선택',
                        style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18, color: _primaryColor),
                      ),
                      const SizedBox(height: 15),
                      Wrap(
                        spacing: 10,
                        runSpacing: 10,
                        children: targetUniversities.map((univ) {
                          final isSelected = _selectedUniv == univ;
                          return ChoiceChip(
                            label: Text(univ, style: TextStyle(fontWeight: isSelected ? FontWeight.bold : FontWeight.normal, color: isSelected ? Colors.white : Colors.black87)),
                            showCheckmark: false,
                            selected: isSelected,
                            selectedColor: _primaryColor,
                            backgroundColor: Colors.grey.shade100,
                            elevation: isSelected ? 4 : 0,
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                            onSelected: (selected) {
                              setState(() {
                                if (selected) {
                                  _selectedUniv = univ;
                                } else {
                                  _selectedUniv = '';
                                }
                                _selectedGates.clear(); // 대학이 바뀌면 선택된 게이트 초기화
                              });
                            },
                          );
                        }).toList(),
                      ),
                    ],
                  ),
                ),"""
content = content.replace(old_univ, new_univ)

# 4. Replace Gates
old_gates = """                // 2. 캠퍼스 게이트 동적 필터
                if (_selectedUniv.isNotEmpty) ...[
                  const Row(
                    children: [
                      Text(
                        '📍 어디로 나갈 예정인가요?',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      SizedBox(width: 8),
                      Text(
                        '(복수 선택 가능)',
                        style: TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 8,
                    children: [
                      FilterChip(
                        label: const Text(
                          '전체 입구',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        showCheckmark: false,
                        selected: _isAllGatesSelected,
                        onSelected: _toggleAllGates,
                        selectedColor: const Color(0xFFFFD166),
                      ),
                      ...(universityGates[_selectedUniv] ?? []).map((gate) {
                        final isSelected = _selectedGates.contains(gate);
                        return FilterChip(
                          label: Text(gate),
                          showCheckmark: false,
                          selected: isSelected,
                          onSelected: (bool selected) {
                            setState(() {
                              if (selected) {
                                _selectedGates.add(gate);
                              } else {
                                _selectedGates.remove(gate);
                              }
                            });
                          },
                        );
                      }),
                    ],
                  ),
                  const SizedBox(height: 20),
                ],"""

new_gates = """                // 2. 캠퍼스 게이트 동적 필터
                if (_selectedUniv.isNotEmpty) ...[
                  const SizedBox(height: 20),
                  _buildSectionCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              '📍 어디로 나갈 예정인가요?',
                              style: TextStyle(
                                fontWeight: FontWeight.w800,
                                fontSize: 18,
                                color: _primaryColor,
                              ),
                            ),
                            const SizedBox(width: 8),
                            const Text(
                              '(복수 선택 가능)',
                              style: TextStyle(fontSize: 12, color: Colors.grey),
                            ),
                          ],
                        ),
                        const SizedBox(height: 15),
                        Wrap(
                          spacing: 10,
                          runSpacing: 10,
                          children: [
                            FilterChip(
                              label: Text(
                                '전체 입구',
                                style: TextStyle(fontWeight: _isAllGatesSelected ? FontWeight.bold : FontWeight.normal, color: _isAllGatesSelected ? Colors.white : Colors.black87),
                              ),
                              showCheckmark: false,
                              selected: _isAllGatesSelected,
                              onSelected: _toggleAllGates,
                              selectedColor: _primaryColor.withOpacity(0.8),
                              backgroundColor: Colors.grey.shade100,
                              elevation: _isAllGatesSelected ? 4 : 0,
                            ),
                            ...(universityGates[_selectedUniv] ?? []).map((gate) {
                              final isSelected = _selectedGates.contains(gate);
                              return FilterChip(
                                label: Text(gate, style: TextStyle(fontWeight: isSelected ? FontWeight.bold : FontWeight.normal, color: isSelected ? Colors.white : Colors.black87)),
                                showCheckmark: false,
                                selected: isSelected,
                                selectedColor: _primaryColor.withOpacity(0.8),
                                backgroundColor: Colors.grey.shade100,
                                elevation: isSelected ? 4 : 0,
                                onSelected: (bool selected) {
                                  setState(() {
                                    if (selected) {
                                      _selectedGates.add(gate);
                                    } else {
                                      _selectedGates.remove(gate);
                                    }
                                  });
                                },
                              );
                            }),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],"""
content = content.replace(old_gates, new_gates)

# 5. Replace Budgets
old_budgets = """                // 3. 예산 필터
                const Row(
                  children: [
                    Text(
                      '💰 현재 지갑 사정은?',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    SizedBox(width: 8),
                    Text(
                      '(복수 선택 가능)',
                      style: TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 8,
                  children: [
                    FilterChip(
                      label: const Text(
                        '전체 가격대',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      showCheckmark: false,
                      selected: _isAllBudgetsSelected,
                      onSelected: _toggleAllBudgets,
                      selectedColor: const Color(0xFFFFD166),
                    ),
                    FilterChip(
                      label: const Text('가성비 🪙'),
                      showCheckmark: false,
                      selected: _selectedBudgets.contains(1),
                      onSelected: (s) => setState(
                        () => s
                            ? _selectedBudgets.add(1)
                            : _selectedBudgets.remove(1),
                      ),
                    ),
                    FilterChip(
                      label: const Text('보통 🍽️'),
                      showCheckmark: false,
                      selected: _selectedBudgets.contains(2),
                      onSelected: (s) => setState(
                        () => s
                            ? _selectedBudgets.add(2)
                            : _selectedBudgets.remove(2),
                      ),
                    ),
                    FilterChip(
                      label: const Text('플렉스 🥩'),
                      showCheckmark: false,
                      selected: _selectedBudgets.contains(3),
                      onSelected: (s) => setState(
                        () => s
                            ? _selectedBudgets.add(3)
                            : _selectedBudgets.remove(3),
                      ),
                    ),
                  ],
                ),"""

new_budgets = """                // 3. 예산 필터
                const SizedBox(height: 20),
                _buildSectionCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            '💰 현재 지갑 사정은?',
                            style: TextStyle(
                              fontWeight: FontWeight.w800,
                              fontSize: 18,
                              color: _primaryColor,
                            ),
                          ),
                          const SizedBox(width: 8),
                          const Text(
                            '(복수 선택 가능)',
                            style: TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                        ],
                      ),
                      const SizedBox(height: 15),
                      Wrap(
                        spacing: 10,
                        runSpacing: 10,
                        children: [
                          FilterChip(
                            label: Text(
                              '전체 가격대',
                              style: TextStyle(fontWeight: _isAllBudgetsSelected ? FontWeight.bold : FontWeight.normal, color: _isAllBudgetsSelected ? Colors.white : Colors.black87),
                            ),
                            showCheckmark: false,
                            selected: _isAllBudgetsSelected,
                            onSelected: _toggleAllBudgets,
                            selectedColor: _primaryColor.withOpacity(0.8),
                            backgroundColor: Colors.grey.shade100,
                            elevation: _isAllBudgetsSelected ? 4 : 0,
                          ),
                          FilterChip(
                            label: Text('가성비 🪙', style: TextStyle(fontWeight: _selectedBudgets.contains(1) ? FontWeight.bold : FontWeight.normal, color: _selectedBudgets.contains(1) ? Colors.white : Colors.black87)),
                            showCheckmark: false,
                            selected: _selectedBudgets.contains(1),
                            selectedColor: _primaryColor.withOpacity(0.8),
                            backgroundColor: Colors.grey.shade100,
                            elevation: _selectedBudgets.contains(1) ? 4 : 0,
                            onSelected: (s) => setState(
                              () => s
                                  ? _selectedBudgets.add(1)
                                  : _selectedBudgets.remove(1),
                            ),
                          ),
                          FilterChip(
                            label: Text('보통 🍽️', style: TextStyle(fontWeight: _selectedBudgets.contains(2) ? FontWeight.bold : FontWeight.normal, color: _selectedBudgets.contains(2) ? Colors.white : Colors.black87)),
                            showCheckmark: false,
                            selected: _selectedBudgets.contains(2),
                            selectedColor: _primaryColor.withOpacity(0.8),
                            backgroundColor: Colors.grey.shade100,
                            elevation: _selectedBudgets.contains(2) ? 4 : 0,
                            onSelected: (s) => setState(
                              () => s
                                  ? _selectedBudgets.add(2)
                                  : _selectedBudgets.remove(2),
                            ),
                          ),
                          FilterChip(
                            label: Text('플렉스 🥩', style: TextStyle(fontWeight: _selectedBudgets.contains(3) ? FontWeight.bold : FontWeight.normal, color: _selectedBudgets.contains(3) ? Colors.white : Colors.black87)),
                            showCheckmark: false,
                            selected: _selectedBudgets.contains(3),
                            selectedColor: _primaryColor.withOpacity(0.8),
                            backgroundColor: Colors.grey.shade100,
                            elevation: _selectedBudgets.contains(3) ? 4 : 0,
                            onSelected: (s) => setState(
                              () => s
                                  ? _selectedBudgets.add(3)
                                  : _selectedBudgets.remove(3),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),"""
content = content.replace(old_budgets, new_budgets)

# 6. Replace Roulette Button
old_button = """                // 4. 룰렛 돌리기 버튼
                ElevatedButton(
                  onPressed: _isLoading || _isSpinning
                      ? null
                      : _spinBlindRoulette,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFFF5C5C),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 20),
                    textStyle: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          height: 24,
                          width: 24,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 3,
                          ),
                        )
                      : const Text('대학맛집 룰렛 돌리기!!'),
                ),"""

new_button = """                // 4. 룰렛 돌리기 버튼 (Pulse Animation 적용)
                const SizedBox(height: 30),
                AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  height: 65,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(32.5),
                    boxShadow: _isLoading || _isSpinning ? [] : [
                      BoxShadow(
                        color: _primaryColor.withOpacity(0.4),
                        blurRadius: 15,
                        spreadRadius: 2,
                        offset: const Offset(0, 5),
                      )
                    ],
                  ),
                  child: ElevatedButton(
                    onPressed: _isLoading || _isSpinning
                        ? null
                        : _spinBlindRoulette,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _primaryColor,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(32.5)),
                      padding: const EdgeInsets.symmetric(vertical: 15),
                      elevation: 0,
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            height: 24,
                            width: 24,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 3,
                            ),
                          )
                        : const Text(
                            '대학맛집 룰렛 돌리기!! 🎯',
                            style: TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 1.5,
                            ),
                          ),
                  ),
                ),"""
content = content.replace(old_button, new_button)

# 7. Add closing for AnimatedTheme
old_closing = """          // 오버레이 팝업 룰렛 (Spin 중일 때만 표시)"""
new_closing = """          // 오버레이 팝업 룰렛 (Spin 중일 때만 표시)"""
content = content.replace("        ],\n      ),\n    );\n  }\n\n  Color _getColor(int index)", "        ],\n      ),\n      ),\n    );\n  }\n\n  Color _getColor(int index)")

# 8. Modernize Dialog
old_dialog = """    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: const Text('오늘의 추천 맛집! 🎉', textAlign: TextAlign.center),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
              Text(
                winner['name'] ?? '이름 없음',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                category,
                style: const TextStyle(color: Colors.grey),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                onPressed: () async {
                  final url = Uri.parse(winner['url'] ?? '');
                  try {
                    await launchUrl(url, mode: LaunchMode.externalApplication);
                  } catch (e) {
                    debugPrint('Could not launch $url');
                  }
                },
                icon: const Icon(Icons.map, color: Colors.black87),
                label: const Text(
                  '카카오맵 열기',
                  style: TextStyle(
                    color: Colors.black87,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFFEE500), // 카카오 시그니처 노란색
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),
              const SizedBox(height: 10),
              OutlinedButton.icon(
                onPressed: () {
                  // ignore: deprecated_member_use
                  Share.share(
                    '오늘 점심은 여기로 결정됨! 🎯\\n${winner['name']} ($category)\\n위치: ${winner['url']}',
                  );
                },
                icon: const Icon(Icons.share),
                label: const Text('결과 공유하기'),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),
            ],
          ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _spinBlindRoulette(); // 다시 돌리기
              },
              child: const Text('다시 돌리기'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('닫기', style: TextStyle(color: Colors.grey)),
            ),
          ],
        );
      },
    );"""

new_dialog = """    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(28),
          ),
          elevation: 10,
          backgroundColor: Colors.white,
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    '🎉 오늘의 추천 맛집! 🎉',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w900,
                      color: Colors.black87,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 20),
                  Container(
                    padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF8F9FA),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    width: double.infinity,
                    child: Column(
                      children: [
                        Text(
                          winner['name'] ?? '이름 없음',
                          style: const TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.w900,
                            color: Colors.black,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.grey.shade200,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            category,
                            style: const TextStyle(color: Colors.black54, fontWeight: FontWeight.bold),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () async {
                      final url = Uri.parse(winner['url'] ?? '');
                      try {
                        await launchUrl(url, mode: LaunchMode.externalApplication);
                      } catch (e) {
                        debugPrint('Could not launch $url');
                      }
                    },
                    icon: const Icon(Icons.map, color: Colors.black87),
                    label: const Text(
                      '카카오맵 열기',
                      style: TextStyle(
                        color: Colors.black87,
                        fontWeight: FontWeight.w900,
                        fontSize: 16,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFFEE500),
                      minimumSize: const Size(double.infinity, 55),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      elevation: 2,
                    ),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: () {
                      // ignore: deprecated_member_use
                      Share.share(
                        '오늘 점심은 여기로 결정됨! 🎯\\n${winner['name']} ($category)\\n위치: ${winner['url']}',
                      );
                    },
                    icon: const Icon(Icons.share, color: Colors.black87),
                    label: const Text('결과 공유하기', style: TextStyle(color: Colors.black87, fontWeight: FontWeight.bold)),
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 55),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      side: BorderSide(color: Colors.grey.shade300, width: 2),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      TextButton(
                        onPressed: () {
                          Navigator.of(context).pop();
                          _spinBlindRoulette(); // 다시 돌리기
                        },
                        child: const Text('🔄 다시 돌리기', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      ),
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: const Text('닫기', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold, fontSize: 16)),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );"""

content = content.replace(old_dialog, new_dialog)

with open('campus_roulette/lib/screens/home_screen.dart', 'w', encoding='utf-8') as f:
    f.write(content)
