import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:share_plus/share_plus.dart';
import 'dart:math';
import 'dart:async';
import 'dart:ui';
import '../constants.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  String _selectedUniv = ''; // 기본값: 선택 안 됨
  final Set<int> _selectedBudgets = {};
  final Set<String> _selectedGates = {};

  List<Map<String, dynamic>> _restaurants = [];
  bool _isLoading = false;


  int _resultIndex = -1;
  bool _isSpinning = false;
  bool _isSnackBarShowing = false;

  bool get _isAllGatesSelected {
    final allGates = universityGates[_selectedUniv] ?? [];
    return _selectedGates.length == allGates.length && allGates.isNotEmpty;
  }

  void _toggleAllGates(bool selected) {
    setState(() {
      if (selected) {
        _selectedGates.addAll(universityGates[_selectedUniv] ?? []);
      } else {
        _selectedGates.clear();
      }
    });
  }

  bool get _isAllBudgetsSelected => _selectedBudgets.length == 3;

  void _toggleAllBudgets(bool selected) {
    setState(() {
      if (selected) {
        _selectedBudgets.addAll([1, 2, 3]);
      } else {
        _selectedBudgets.clear();
      }
    });
  }

  final supabase = Supabase.instance.client;

  @override
  void initState() {
    super.initState();
  }



  void _showErrorSnackBar(String message) async {
    if (_isSnackBarShowing) return;

    setState(() {
      _isSnackBarShowing = true;
    });

    final controller = ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(
      content: Text(message),
      duration: const Duration(seconds: 2), // 표시 시간 단축 (기본 4초 -> 2초)
    ));

    await controller.closed;

    if (mounted) {
      setState(() {
        _isSnackBarShowing = false;
      });
    }
  }

  void _spinBlindRoulette() async {
    String? errorMessage;
    if (_selectedUniv.isEmpty) {
      errorMessage = '😅 앗! 대학교를 먼저 선택해주셔야 맛집을 찾아드릴 수 있어요.';
    } else if (_selectedGates.isEmpty) {
      errorMessage = '🚶‍♂️ 나갈 입구를 최소 하나 이상 선택해주세요!';
    } else if (_selectedBudgets.isEmpty) {
      errorMessage = '💸 원하시는 가격대(지갑 사정)를 하나 이상 선택해주세요!';
    }

    // 1. 에러가 있을 때 (선택 누락)
    if (errorMessage != null) {
      if (_isSnackBarShowing) return; // 에러 상태에서는 안내 문구 중복 클릭 완전 무시
      _showErrorSnackBar(errorMessage);
      return;
    }

    // 2. 정상적으로 모두 선택되었을 때 (예외 처리)
    // 만약 예전 에러 안내 문구가 아직 떠있더라도 즉시 강제 종료하고 넘어감
    if (_isSnackBarShowing) {
      ScaffoldMessenger.of(context).clearSnackBars();
      _isSnackBarShowing = false;
    }

    if (_isSpinning) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final response = await supabase
          .from('restaurants')
          .select()
          .eq('univ', _selectedUniv);

      List<Map<String, dynamic>> data = List<Map<String, dynamic>>.from(
        response,
      );

      // 예산 필터 적용
      data = data
          .where((r) => _selectedBudgets.contains(r['price_level']))
          .toList();

      // 출입구 필터 적용
      data = data.where((restaurant) {
        final gatesStr = restaurant['gates']?.toString() ?? '';
        return _selectedGates.any((gate) => gatesStr.contains(gate));
      }).toList();

      if (data.isEmpty) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('조건에 맞는 식당이 없습니다. 다른 필터를 시도해보세요!')),
          );
        }
        setState(() {
          _isLoading = false;
        });
        return;
      }

      data.shuffle();
      _restaurants = [data.first]; // 하나만 몰래 뽑기
      _resultIndex = 0;

      setState(() {
        _isLoading = false;
        _isSpinning = true;
      });

      // 4초 후 결과 팝업 표시
      Future.delayed(const Duration(seconds: 4), () {
        if (mounted && _isSpinning) {
          _onSpinEnd();
        }
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('데이터를 불러오는데 실패했습니다: $e')));
      }
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _onSpinEnd() {
    HapticFeedback.heavyImpact(); // 룰렛 멈출 때 강력한 진동 추가!
    setState(() {
      _isSpinning = false;
    });
    _showResultDialog();
  }

  void _showResultDialog() {
    if (_resultIndex == -1) return;
    final winner = _restaurants[_resultIndex];
    final category = winner['category'] ?? '음식점';

    showDialog(
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
                        '오늘 점심은 여기로 결정됨! 🎯\n${winner['name']} ($category)\n위치: ${winner['url']}',
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
    );
  }


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
        color: Colors.white.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: _primaryColor.withValues(alpha: 0.08),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: child,
    );
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedTheme(
      data: Theme.of(context).copyWith(
        colorScheme: ColorScheme.fromSeed(
          seedColor: _primaryColor,
          primary: _primaryColor,
        ),
        primaryColor: _primaryColor,
      ),
      duration: const Duration(milliseconds: 500),
      child: PopScope(
        canPop: !_isSpinning,
        child: Stack(
        children: [
          Scaffold(
            backgroundColor: _lightColor,
            appBar: AppBar(
              backgroundColor: Colors.transparent,
              elevation: 0,
              title: Text(
                '대학맛집 룰렛 🎯',
                style: TextStyle(
                  fontWeight: FontWeight.w900,
                  color: _primaryColor,
                  fontSize: 24,
                ),
              ),
              centerTitle: true,
            ),
            body: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  AnimatedSize(
                    duration: const Duration(milliseconds: 600),
                    curve: Curves.easeInOutCubic,
                    child: _selectedUniv.isEmpty
                        ? Padding(
                            padding: const EdgeInsets.only(top: 40, bottom: 40),
                            child: Column(
                              children: [
                                const Icon(
                                  Icons.school_rounded,
                                  size: 80,
                                  color: Colors.black26,
                                ),
                                const SizedBox(height: 20),
                                const Text(
                                  '환영합니다!',
                                  style: TextStyle(
                                    fontSize: 32,
                                    fontWeight: FontWeight.w900,
                                    color: Colors.black87,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                const Text(
                                  '어느 대학교의 맛집을 찾으시나요?',
                                  style: TextStyle(
                                    fontSize: 16,
                                    color: Colors.black54,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          )
                        : const SizedBox.shrink(),
                  ),

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
                ),
                const SizedBox(height: 20),


                AnimatedSize(
                  duration: const Duration(milliseconds: 600),
                  curve: Curves.easeInOutCubic,
                  child: (_selectedUniv.isNotEmpty ? Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                  _buildSectionCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Wrap(
                          crossAxisAlignment: WrapCrossAlignment.center,
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
                              selectedColor: _primaryColor.withValues(alpha: 0.8),
                              backgroundColor: Colors.grey.shade100,
                              elevation: _isAllGatesSelected ? 4 : 0,
                            ),
                            ...(universityGates[_selectedUniv] ?? []).map((gate) {
                              final isSelected = _selectedGates.contains(gate);
                              return FilterChip(
                                label: Text(gate, style: TextStyle(fontWeight: isSelected ? FontWeight.bold : FontWeight.normal, color: isSelected ? Colors.white : Colors.black87)),
                                showCheckmark: false,
                                selected: isSelected,
                                selectedColor: _primaryColor.withValues(alpha: 0.8),
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
                  ),                const SizedBox(height: 20),
                _buildSectionCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Wrap(
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          Text(
                            '💰 가격대를 선택해 주세요!',
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
                            selectedColor: _primaryColor.withValues(alpha: 0.8),
                            backgroundColor: Colors.grey.shade100,
                            elevation: _isAllBudgetsSelected ? 4 : 0,
                          ),
                          FilterChip(
                            label: Text('가성비 🪙', style: TextStyle(fontWeight: _selectedBudgets.contains(1) ? FontWeight.bold : FontWeight.normal, color: _selectedBudgets.contains(1) ? Colors.white : Colors.black87)),
                            showCheckmark: false,
                            selected: _selectedBudgets.contains(1),
                            selectedColor: _primaryColor.withValues(alpha: 0.8),
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
                            selectedColor: _primaryColor.withValues(alpha: 0.8),
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
                            selectedColor: _primaryColor.withValues(alpha: 0.8),
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
                ),
                const SizedBox(height: 30),


                const SizedBox(height: 30),
                AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  height: 65,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(32.5),
                    boxShadow: _isLoading || _isSpinning ? [] : [
                      BoxShadow(
                        color: _primaryColor.withValues(alpha: 0.4),
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
                ),
              ],
            ) : const SizedBox.shrink()),
          ),
        ],
      ),
          ),
          ),
          // 오버레이 팝업 룰렛 (Spin 중일 때만 표시)
          if (_isSpinning)
            BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
              child: Container(
                color: Colors.white.withValues(alpha: 0.6), // 깔끔한 화이트 반투명 배경
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      _FloatingSpinner(
                        child: TweenAnimationBuilder<double>(
                          tween: Tween(begin: 0.0, end: 1.0),
                          duration: const Duration(milliseconds: 1000),
                          curve: Curves.elasticOut, // 통통 튀며 등장
                          builder: (context, scale, child) {
                            return Transform.scale(
                              scale: scale,
                              child: child,
                            );
                          },
                          child: Container(
                            width: 120, // 로딩 스피너 크기로 대폭 축소
                            height: 120,
                            decoration: BoxDecoration(
                              color: Colors.white,
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: _primaryColor.withValues(alpha: 0.3), // 은은한 후광
                                  blurRadius: 30,
                                  spreadRadius: 5,
                                ),
                              ],
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(4.0),
                              child: _StepRotationSpinner(primaryColor: _primaryColor),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 40),
                      // 로딩 텍스트 추가
                      DefaultTextStyle(
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w800,
                          color: _primaryColor,
                          letterSpacing: 1.2,
                        ),
                        child: const Text("대학 맛집 탐색 중..."),
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
      ),
    );
  }
}

class _FloatingSpinner extends StatefulWidget {
  final Widget child;
  const _FloatingSpinner({required this.child});

  @override
  State<_FloatingSpinner> createState() => _FloatingSpinnerState();
}

class _FloatingSpinnerState extends State<_FloatingSpinner> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 1500))..repeat(reverse: true);
    _animation = Tween<double>(begin: -15, end: 15).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOutSine));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Transform.translate(
          offset: Offset(0, _animation.value),
          child: child,
        );
      },
      child: widget.child,
    );
  }
}

class _StepRotationSpinner extends StatefulWidget {
  final Color primaryColor;
  const _StepRotationSpinner({required this.primaryColor});

  @override
  State<_StepRotationSpinner> createState() => _StepRotationSpinnerState();
}

class _StepRotationSpinnerState extends State<_StepRotationSpinner> {
  int _currentIndex = 0;
  late Timer _timer;

  @override
  void initState() {
    super.initState();
    // 0.6초마다 한 칸씩(60도) 부드럽게 튕기듯 이동
    _timer = Timer.periodic(const Duration(milliseconds: 800), (timer) {
      if (mounted) {
        setState(() {
          _currentIndex++;
        });
      }
    });
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedRotation(
      turns: _currentIndex / 6.0,
      duration: const Duration(milliseconds: 600),
      curve: Curves.easeInOutCubic, // 부드럽고 우아하게 미끄러지듯 이동
      child: Stack(
        alignment: Alignment.center,
        children: [
          for (int i = 0; i < 6; i++)
            Transform.translate(
              offset: Offset(
                35 * cos(i * 2 * pi / 6 - pi / 2),
                35 * sin(i * 2 * pi / 6 - pi / 2),
              ),
              child: AnimatedRotation(
                // 부모가 회전할 때 자식을 역회전시켜 아이콘이 항상 정면을 보게 유지 (관람차 효과)
                turns: -_currentIndex / 6.0,
                duration: const Duration(milliseconds: 600),
                curve: Curves.easeInOutCubic,
                child: Icon(
                  [
                    Icons.restaurant,
                    Icons.local_cafe,
                    Icons.fastfood,
                    Icons.local_pizza,
                    Icons.ramen_dining,
                    Icons.icecream,
                  ][i],
                  size: 24,
                  color: widget.primaryColor,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
