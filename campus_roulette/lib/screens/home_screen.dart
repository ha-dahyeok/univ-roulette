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

class _HomeScreenState extends State<HomeScreen> {
  final _searchController = TextEditingController();
  String _selectedUniv = '';
  int _selectedBudget = 1;
  final List<String> _selectedGates = [];
  
  List<Map<String, dynamic>> _restaurants = [];
  bool _isLoading = false;
  
  final _fortuneController = StreamController<int>();
  int _resultIndex = -1;
  bool _isSpinning = false;

  final supabase = Supabase.instance.client;

  @override
  void dispose() {
    _searchController.dispose();
    _fortuneController.close();
    super.dispose();
  }

  void _searchRestaurants() async {
    if (_selectedUniv.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('대학교를 먼저 선택해주세요.')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _restaurants = [];
      _resultIndex = -1;
    });

    try {
      final response = await supabase
          .from('restaurants')
          .select()
          .eq('univ', _selectedUniv)
          .eq('price_level', _selectedBudget);

      List<Map<String, dynamic>> data = List<Map<String, dynamic>>.from(response);
      
      // 기획서 3.2: 출입구 다중 선택 필터 로직 (현재 DB상 완벽한 데이터가 없으므로 프론트엔드 모의 필터 적용)
      if (_selectedGates.isNotEmpty && _selectedGates.length < 3) {
        // 출입구가 선택되었을 때, 랜덤으로 일부 식당을 걸러내는 식으로 UI 필터 효과를 줍니다.
        // 향후 DB에 gate 정보가 추가되면 eq('gate', ...) 로 변경 가능
        data.shuffle();
        data = data.take((data.length / 2).ceil()).toList();
      }

      data.shuffle();
      setState(() {
        _restaurants = data.take(6).toList();
      });

      if (_restaurants.isEmpty) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('조건에 맞는 식당이 없습니다. 다른 필터를 시도해보세요!')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('데이터를 불러오는데 실패했습니다: $e')),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _spin() {
    if (_restaurants.isEmpty || _isSpinning) return;
    setState(() {
      _isSpinning = true;
      _resultIndex = Random().nextInt(_restaurants.length);
    });
    _fortuneController.add(_resultIndex);
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
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Text('오늘의 추천 맛집! 🎉', textAlign: TextAlign.center),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                winner['name'] ?? '이름 없음',
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(category, style: const TextStyle(color: Colors.grey), textAlign: TextAlign.center,),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                onPressed: () async {
                  final url = Uri.parse(winner['url'] ?? '');
                  if (await canLaunchUrl(url)) {
                    await launchUrl(url);
                  }
                },
                icon: const Icon(Icons.map, color: Colors.black87),
                label: const Text('카카오맵 열기', style: TextStyle(color: Colors.black87)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFFEE500),
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),
              const SizedBox(height: 10),
              OutlinedButton.icon(
                onPressed: () {
                  // ignore: deprecated_member_use
                  Share.share('오늘 점심은 여기로 결정됨! 🎯\\n${winner['name']} ($category)\\n위치: ${winner['url']}');
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
                _spin(); // 다시 돌리기
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
        title: const Text('🎡 캠퍼스 룰렛', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 1. 대학교 검색
            Autocomplete<String>(
              optionsBuilder: (TextEditingValue textEditingValue) {
                if (textEditingValue.text.isEmpty) {
                  return const Iterable<String>.empty();
                }
                return koreanUnivs.where((String option) {
                  return option.toLowerCase().contains(textEditingValue.text.toLowerCase());
                });
              },
              onSelected: (String selection) {
                setState(() {
                  _selectedUniv = selection;
                });
              },
              fieldViewBuilder: (context, controller, focusNode, onEditingComplete) {
                if (controller.text != _searchController.text) {
                  _searchController.text = controller.text;
                }
                return TextField(
                  controller: controller,
                  focusNode: focusNode,
                  decoration: InputDecoration(
                    labelText: '대학교 검색 (예: 고려대)',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    prefixIcon: const Icon(Icons.search),
                  ),
                  onChanged: (val) {
                    _searchController.text = val;
                    if (val.isEmpty) {
                      setState(() {
                        _selectedUniv = '';
                      });
                    }
                  },
                );
              },
            ),
            const SizedBox(height: 20),
            
            // 2. 캠퍼스 게이트 마이크로 타겟팅 필터
            if (_selectedUniv.isNotEmpty) ...[
              const Text('📍 어디로 나갈 예정인가요? (다중 선택 가능)', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              Wrap(
                spacing: 8,
                children: ['정문', '후문', '자연계 캠퍼스 입구'].map((gate) {
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
                }).toList(),
              ),
              const SizedBox(height: 20),
            ],

            // 3. 예산 필터
            const Text('💰 현재 지갑 사정은?', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            SegmentedButton<int>(
              segments: const [
                ButtonSegment(value: 1, label: Text('가성비\\n(1만원↓)', textAlign: TextAlign.center)),
                ButtonSegment(value: 2, label: Text('보통\\n(1만원대)', textAlign: TextAlign.center)),
                ButtonSegment(value: 3, label: Text('플렉스\\n(2만원↑)', textAlign: TextAlign.center)),
              ],
              selected: {_selectedBudget},
              onSelectionChanged: (Set<int> newSelection) {
                setState(() {
                  _selectedBudget = newSelection.first;
                });
              },
            ),
            const SizedBox(height: 30),

            // 4. 검색 버튼
            ElevatedButton(
              onPressed: _isLoading ? null : _searchRestaurants,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              child: _isLoading 
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('룰렛 식당 조합 불러오기'),
            ),
            const SizedBox(height: 40),

            // 5. 룰렛 위젯
            if (_restaurants.isNotEmpty) ...[
              SizedBox(
                height: 300,
                child: FortuneWheel(
                  selected: _fortuneController.stream,
                  onAnimationEnd: _onSpinEnd,
                  items: [
                    for (var r in _restaurants)
                      FortuneItem(
                        child: Text(
                          (r['name']?.toString().length ?? 0) > 7 
                              ? '${r['name'].toString().substring(0, 6)}..' 
                              : r['name'] ?? '',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        style: FortuneItemStyle(
                          color: _getColor(_restaurants.indexOf(r)),
                          borderColor: Colors.white,
                          borderWidth: 3,
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: _isSpinning ? null : _spin,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFFF5C5C),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 20),
                  textStyle: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                child: const Text('룰렛 돌리기!!'),
              ),
            ]
          ],
        ),
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
