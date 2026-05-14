import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:share_plus/share_plus.dart';
import 'dart:math';
import 'dart:async';
import 'dart:ui';
import 'package:flutter/foundation.dart' show kIsWeb, defaultTargetPlatform;
import 'package:screenshot/screenshot.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import '../constants.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  final ScreenshotController _screenshotController = ScreenshotController();
  String _selectedUniv = ''; // 기본값: 선택 안 됨
  final Set<int> _selectedBudgets = {};
  final Set<String> _selectedGates = {};

  List<Map<String, dynamic>> _restaurants = [];
  bool _isLoading = false;


  int _resultIndex = -1;
  bool _isSpinning = false;
  bool _isSnackBarShowing = false;
  bool _showResultPopup = false;
  DateTime? currentBackPressTime;

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
      if (_resultIndex != -1) {
        _showResultPopup = true;
      }
    });
  }

  Widget _buildResultPopupOverlay() {
    if (_resultIndex == -1) return const SizedBox.shrink();
    final winner = _restaurants[_resultIndex];
    final category = winner['category'] ?? '음식점';

    return Container(
      color: Colors.black54,
      alignment: Alignment.center,
      padding: const EdgeInsets.all(24.0),
      child: Material(
        color: Colors.transparent,
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(28),
          ),
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                      color: Colors.white,
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
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () async {
                            try {
                              // 화면 렌더링 후 캡처
                              await Future.delayed(const Duration(milliseconds: 100));
                              final imageBytes = await _screenshotController.capture(delay: const Duration(milliseconds: 50));
                              if (imageBytes != null) {
                                if (kIsWeb) {
                                  final xFile = XFile.fromData(imageBytes, mimeType: 'image/png', name: 'result_card.png');
                                  await Share.shareXFiles([xFile]);
                                } else {
                                  final directory = await getApplicationDocumentsDirectory();
                                  final imagePath = await File('${directory.path}/result_card.png').create();
                                  await imagePath.writeAsBytes(imageBytes);
                                  await Share.shareXFiles([XFile(imagePath.path)]);
                                }
                              }
                            } catch (e) {
                              debugPrint('공유 실패: $e');
                            }
                          },
                          icon: const Icon(Icons.image, color: Colors.black87, size: 20),
                          label: const Text('결과 이미지 공유', style: TextStyle(color: Colors.black87, fontWeight: FontWeight.bold, fontSize: 13)),
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            side: BorderSide(color: Colors.grey.shade300, width: 2),
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () async {
                            try {
                              final textMessage = '오늘 한 끼는 여기로 결정됨! 🎯\n${winner['name']} ($category)\n📍위치: ${winner['url']}\n\n나도 대학맛집 룰렛 돌려보기 👇\nhttps://ha-dahyeok.github.io/univ-roulette/';
                              await Share.share(textMessage);
                            } catch (e) {
                              debugPrint('공유 실패: $e');
                            }
                          },
                          icon: const Icon(Icons.text_snippet, color: Colors.black87, size: 20),
                          label: const Text('식당 정보 공유', style: TextStyle(color: Colors.black87, fontWeight: FontWeight.bold, fontSize: 13)),
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            side: BorderSide(color: Colors.grey.shade300, width: 2),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      TextButton(
                        onPressed: () {
                          setState(() { _showResultPopup = false; });
                          _spinBlindRoulette(); // 다시 돌리기
                        },
                        child: const Text('🔄 다시 돌리기', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      ),
                      TextButton(
                        onPressed: () {
                          setState(() { _showResultPopup = false; });
                        },
                        child: const Text('닫기', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold, fontSize: 16)),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }


  Color get _primaryColor {
    if (_selectedUniv.contains('연세')) return const Color(0xFF1428A0); // 연세 블루
    if (_selectedUniv.contains('고려')) return const Color(0xFF8A1538); // 크림슨
    if (_selectedUniv.contains('건국')) return const Color(0xFF006633); // 건국 그린
    if (_selectedUniv.contains('홍익')) return const Color(0xFF00205B); // 홍익 블루 (Navy)
    if (_selectedUniv.contains('한양')) return const Color(0xFF003B71); // 한양 블루
    if (_selectedUniv.contains('서강')) return const Color(0xFFB60005); // 서강 레드 (Crimson)
    if (_selectedUniv.contains('인하')) return const Color(0xFF005BAC); // 인하 블루 (Azure)
    if (_selectedUniv.contains('중앙')) return const Color(0xFF003087); // 중앙 블루
    if (_selectedUniv.contains('경희')) return const Color(0xFF9D2235); // 경희 레드 (Burgundy)
    return const Color(0xFF2D3436); // 기본
  }

  Color get _lightColor {
    if (_selectedUniv.contains('연세')) return const Color(0xFFE8EAF6);
    if (_selectedUniv.contains('고려')) return const Color(0xFFFCE4EC);
    if (_selectedUniv.contains('건국')) return const Color(0xFFE8F5E9); // 건국 연초록
    if (_selectedUniv.contains('홍익')) return const Color(0xFFE3F2FD); // 홍익 연파랑
    if (_selectedUniv.contains('한양')) return const Color(0xFFE1F5FE); // 한양 연파랑 (Light Blue)
    if (_selectedUniv.contains('서강')) return const Color(0xFFFFEBEE); // 서강 연핑크 (Light Red)
    if (_selectedUniv.contains('인하')) return const Color(0xFFE3F2FD); // 인하 연파랑
    if (_selectedUniv.contains('중앙')) return const Color(0xFFE8EAF6); // 중앙 연파랑
    if (_selectedUniv.contains('경희')) return const Color(0xFFFCE4EC); // 경희 연핑크
    return const Color(0xFFF1F2F6);
  }

  Widget _buildCustomChip({
    required String label,
    required bool isSelected,
    required VoidCallback onTap,
    Color? selectedColor,
  }) {
    final activeColor = selectedColor ?? _primaryColor;
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? activeColor : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: isSelected ? Colors.transparent : Colors.grey.shade300, width: 1.5),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: activeColor.withValues(alpha: 0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  )
                ]
              : [],
        ),
        child: Text(
          label,
          style: TextStyle(
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            color: isSelected ? Colors.white : Colors.black87,
            height: 1.2,
          ),
        ),
      ),
    );
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
        canPop: false,
        onPopInvoked: (didPop) {
          if (didPop) return;
          if (_isSpinning) return;

          DateTime now = DateTime.now();
          if (currentBackPressTime == null || 
              now.difference(currentBackPressTime!) > const Duration(seconds: 2)) {
            currentBackPressTime = now;
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('한 번 더 누르시면 앱이 종료됩니다.'),
                duration: Duration(seconds: 2),
              ),
            );
            return;
          }
          SystemNavigator.pop();
        },
        child: Screenshot(
          controller: _screenshotController,
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
            body: SafeArea(
              bottom: true,
              child: Column(
                children: [
                if (kIsWeb && defaultTargetPlatform == TargetPlatform.android)
                  Container(
                    color: Colors.transparent,
                    padding: const EdgeInsets.fromLTRB(20, 10, 20, 0),
                    child: SafeArea(
                      bottom: false,
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              '앱에서 더 빠르고 쾌적하게 즐겨보세요!',
                              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: _primaryColor),
                            ),
                          ),
                          ElevatedButton.icon(
                            onPressed: () async {
                              final url = Uri.parse('https://ha-dahyeok.github.io/univ-roulette/app-release.apk');
                              try {
                                await launchUrl(url, mode: LaunchMode.externalApplication);
                              } catch (e) {
                                debugPrint('Could not launch $url');
                              }
                            },
                            icon: const Icon(Icons.android_rounded, size: 16),
                            label: const Text('앱 다운로드', style: TextStyle(fontWeight: FontWeight.w800)),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: _primaryColor,
                              foregroundColor: Colors.white,
                              elevation: 0,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(20),
                              ),
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 0),
                              minimumSize: const Size(0, 36),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                  AnimatedSize(
                    duration: const Duration(milliseconds: 600),
                    curve: Curves.easeInOutCubic,
                    child: _selectedUniv.isEmpty
                        ? Padding(
                            padding: const EdgeInsets.only(top: 10, bottom: 40),
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
                      ConstrainedBox(
                        constraints: BoxConstraints(
                          maxHeight: MediaQuery.of(context).size.height * 0.35,
                        ),
                        child: RawScrollbar(
                          thumbVisibility: true,
                          thumbColor: _primaryColor.withValues(alpha: 0.3),
                          radius: const Radius.circular(20),
                          thickness: 4,
                          child: SingleChildScrollView(
                            child: Padding(
                              padding: const EdgeInsets.only(right: 12.0), // Scrollbar padding
                              child: Wrap(
                                spacing: 10,
                                runSpacing: 10,
                                children: targetUniversities.map((univ) {
                                  final isSelected = _selectedUniv == univ;
                                  return _buildCustomChip(
                                    label: univ,
                                    isSelected: isSelected,
                                    onTap: () {
                                      setState(() {
                                        if (isSelected) {
                                          _selectedUniv = '';
                                        } else {
                                          _selectedUniv = univ;
                                        }
                                        _selectedGates.clear(); // 대학이 바뀌면 선택된 게이트 초기화
                                      });
                                    },
                                  );
                                }).toList(),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),


                AnimatedSize(
                  alignment: Alignment.topCenter,
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
                            _buildCustomChip(
                              label: '전체 입구',
                              isSelected: _isAllGatesSelected,
                              selectedColor: _primaryColor.withValues(alpha: 0.8),
                              onTap: () {
                                _toggleAllGates(!_isAllGatesSelected);
                              },
                            ),
                            ...(universityGates[_selectedUniv] ?? []).map((gate) {
                              final isSelected = _selectedGates.contains(gate);
                              return _buildCustomChip(
                                label: gate,
                                isSelected: isSelected,
                                selectedColor: _primaryColor.withValues(alpha: 0.8),
                                onTap: () {
                                  setState(() {
                                    if (isSelected) {
                                      _selectedGates.remove(gate);
                                    } else {
                                      _selectedGates.add(gate);
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
                          _buildCustomChip(
                            label: '전체 가격대',
                            isSelected: _isAllBudgetsSelected,
                            selectedColor: _primaryColor.withValues(alpha: 0.8),
                            onTap: () {
                              _toggleAllBudgets(!_isAllBudgetsSelected);
                            },
                          ),
                          _buildCustomChip(
                            label: '가성비 🪙',
                            isSelected: _selectedBudgets.contains(1),
                            selectedColor: _primaryColor.withValues(alpha: 0.8),
                            onTap: () => setState(
                              () => _selectedBudgets.contains(1)
                                  ? _selectedBudgets.remove(1)
                                  : _selectedBudgets.add(1),
                            ),
                          ),
                          _buildCustomChip(
                            label: '보통 🍽️',
                            isSelected: _selectedBudgets.contains(2),
                            selectedColor: _primaryColor.withValues(alpha: 0.8),
                            onTap: () => setState(
                              () => _selectedBudgets.contains(2)
                                  ? _selectedBudgets.remove(2)
                                  : _selectedBudgets.add(2),
                            ),
                          ),
                          _buildCustomChip(
                            label: '플렉스 🥩',
                            isSelected: _selectedBudgets.contains(3),
                            selectedColor: _primaryColor.withValues(alpha: 0.8),
                            onTap: () => setState(
                              () => _selectedBudgets.contains(3)
                                  ? _selectedBudgets.remove(3)
                                  : _selectedBudgets.add(3),
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
              ],
            ),
          ),
          ),
          // 오버레이 결과 팝업
          if (_showResultPopup) _buildResultPopupOverlay(),
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
