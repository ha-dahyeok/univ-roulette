import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter_fortune_wheel/flutter_fortune_wheel.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:share_plus/share_plus.dart';
import 'dart:math';
import 'dart:async';
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

  StreamController<int> _fortuneController = StreamController<int>();
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

  late final AnimationController _floatController;
  late final Animation<Offset> _floatAnimation;

  @override
  void initState() {
    super.initState();
    _floatController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    )..repeat(reverse: true);

    _floatAnimation =
        Tween<Offset>(
          begin: const Offset(0, -0.05),
          end: const Offset(0, 0.05),
        ).animate(
          CurvedAnimation(parent: _floatController, curve: Curves.easeInOut),
        );
  }

  @override
  void dispose() {
    _floatController.dispose();
    _fortuneController.close();
    super.dispose();
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
        _fortuneController = StreamController<int>(); // 매번 새로운 스트림 생성하여 구독 에러 방지
      });

      Future.delayed(const Duration(milliseconds: 100), () {
        if (!_fortuneController.isClosed) {
          _fortuneController.add(Random().nextInt(8)); // 8칸 룰렛 중 아무데나 멈추기
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
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: const Text('오늘의 추천 맛집! 🎉', textAlign: TextAlign.center),
          content: Column(
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
                    '오늘 점심은 여기로 결정됨! 🎯\n${winner['name']} ($category)\n위치: ${winner['url']}',
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
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
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
              children: [
                // 1. 대학교 검색 (객관식 선택)
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
                ),
                const SizedBox(height: 20),

                // 2. 캠퍼스 게이트 동적 필터
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
                        selected: _isAllGatesSelected,
                        onSelected: _toggleAllGates,
                        selectedColor: const Color(0xFFFFD166),
                      ),
                      ...(universityGates[_selectedUniv] ?? []).map((gate) {
                        final isSelected = _selectedGates.contains(gate);
                        return FilterChip(
                          label: Text(gate),
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
                ],

                // 3. 예산 필터
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
                      selected: _isAllBudgetsSelected,
                      onSelected: _toggleAllBudgets,
                      selectedColor: const Color(0xFFFFD166),
                    ),
                    FilterChip(
                      label: const Text('가성비 🪙'),
                      selected: _selectedBudgets.contains(1),
                      onSelected: (s) => setState(
                        () => s
                            ? _selectedBudgets.add(1)
                            : _selectedBudgets.remove(1),
                      ),
                    ),
                    FilterChip(
                      label: const Text('보통 🍽️'),
                      selected: _selectedBudgets.contains(2),
                      onSelected: (s) => setState(
                        () => s
                            ? _selectedBudgets.add(2)
                            : _selectedBudgets.remove(2),
                      ),
                    ),
                    FilterChip(
                      label: const Text('플렉스 🥩'),
                      selected: _selectedBudgets.contains(3),
                      onSelected: (s) => setState(
                        () => s
                            ? _selectedBudgets.add(3)
                            : _selectedBudgets.remove(3),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 30),

                // 4. 룰렛 돌리기 버튼
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
                ),
              ],
            ),
          ),

          // 오버레이 팝업 룰렛 (Spin 중일 때만 표시)
          if (_isSpinning)
            Container(
              color: Colors.black54, // 반투명 검정 배경
              child: Center(
                child: SlideTransition(
                  position: _floatAnimation,
                  child: Container(
                    width: 220,
                    height: 220,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.3),
                          blurRadius: 15,
                          spreadRadius: 5,
                        ),
                      ],
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: FortuneWheel(
                        animateFirst: false,
                        selected: _fortuneController.stream,
                        onAnimationEnd: _onSpinEnd,
                        indicators: const <FortuneIndicator>[
                          FortuneIndicator(
                            alignment: Alignment.topCenter,
                            child: TriangleIndicator(color: Color(0xFFFF5C5C)),
                          ),
                        ],
                        items: [
                          for (int i = 0; i < 8; i++)
                            FortuneItem(
                              child: const Text(
                                '❓',
                                style: TextStyle(
                                  fontSize: 28,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              style: FortuneItemStyle(
                                color: _getColor(i),
                                borderColor: Colors.white,
                                borderWidth: 2,
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Color _getColor(int index) {
    const colors = [
      Color(0xFFFF6B6B),
      Color(0xFFFFD166),
      Color(0xFF06D6A0),
      Color(0xFF118AB2),
      Color(0xFFEF476F),
      Color(0xFFF78C6B),
    ];
    return colors[index % colors.length];
  }
}
