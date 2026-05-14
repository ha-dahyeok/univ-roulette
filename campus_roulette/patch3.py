import os

file_path = "lib/screens/home_screen.dart"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. State variable
content = content.replace(
    "  bool _isSnackBarShowing = false;",
    "  bool _isSnackBarShowing = false;\n  bool _showResultPopup = false;"
)

# 2. _onSpinEnd
old_on_spin_end = """  void _onSpinEnd() {
    HapticFeedback.heavyImpact(); // 룰렛 멈출 때 강력한 진동 추가!
    setState(() {
      _isSpinning = false;
    });
    _showResultDialog();
  }"""
new_on_spin_end = """  void _onSpinEnd() {
    HapticFeedback.heavyImpact(); // 룰렛 멈출 때 강력한 진동 추가!
    setState(() {
      _isSpinning = false;
      if (_resultIndex != -1) {
        _showResultPopup = true;
      }
    });
  }"""
content = content.replace(old_on_spin_end, new_on_spin_end)

# 3. Replace _showResultDialog with _buildResultPopupOverlay
old_dialog_start = """  void _showResultDialog() {
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
                  Screenshot(
                    controller: _screenshotController,
                    child: Container("""
new_dialog_start = """  Widget _buildResultPopupOverlay() {
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
                  Container("""
content = content.replace(old_dialog_start, new_dialog_start)

# Remove Screenshot closing tag
old_screenshot_close = """                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),"""
new_screenshot_close = """                        ],
                      ),
                    ),
                  const SizedBox(height: 24),"""
content = content.replace(old_screenshot_close, new_screenshot_close)

# 4. Modify Share Logic & add Clipboard
old_share_logic = """                  OutlinedButton.icon(
                    onPressed: () async {
                      try {
                        final imageBytes = await _screenshotController.capture(delay: const Duration(milliseconds: 10));
                        if (imageBytes != null) {
                          if (kIsWeb) {
                            final xFile = XFile.fromData(imageBytes, mimeType: 'image/png', name: 'result_card.png');
                            await Share.shareXFiles(
                              [xFile],
                              text: '오늘 점심은 여기로 결정됨! 🎯\\n${winner['name']} ($category)\\n📍위치: ${winner['url']}\\n\\n나도 대학맛집 룰렛 돌려보기 👇\\nhttps://ha-dahyeok.github.io/univ-roulette/',
                            );
                          } else {
                            final directory = await getApplicationDocumentsDirectory();
                            final imagePath = await File('${directory.path}/result_card.png').create();
                            await imagePath.writeAsBytes(imageBytes);
                            await Share.shareXFiles(
                              [XFile(imagePath.path)],
                              text: '오늘 점심은 여기로 결정됨! 🎯\\n${winner['name']} ($category)\\n📍위치: ${winner['url']}\\n\\n나도 대학맛집 룰렛 돌려보기 👇\\nhttps://ha-dahyeok.github.io/univ-roulette/',
                            );
                          }
                        }
                      } catch (e) {
                        debugPrint('공유 실패: $e');
                      }
                    },"""
new_share_logic = """                  OutlinedButton.icon(
                    onPressed: () async {
                      try {
                        final textMessage = '오늘 점심은 여기로 결정됨! 🎯\\n${winner['name']} ($category)\\n📍위치: ${winner['url']}\\n\\n나도 대학맛집 룰렛 돌려보기 👇\\nhttps://ha-dahyeok.github.io/univ-roulette/';
                        Clipboard.setData(ClipboardData(text: textMessage));
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('안내 텍스트가 복사되었습니다!\\n카카오톡 등에 공유 시 붙여넣기 해주세요.')),
                        );
                        
                        // 화면 렌더링 후 캡처
                        await Future.delayed(const Duration(milliseconds: 100));
                        final imageBytes = await _screenshotController.capture(delay: const Duration(milliseconds: 50));
                        if (imageBytes != null) {
                          if (kIsWeb) {
                            final xFile = XFile.fromData(imageBytes, mimeType: 'image/png', name: 'result_card.png');
                            await Share.shareXFiles([xFile], text: textMessage);
                          } else {
                            final directory = await getApplicationDocumentsDirectory();
                            final imagePath = await File('${directory.path}/result_card.png').create();
                            await imagePath.writeAsBytes(imageBytes);
                            await Share.shareXFiles([XFile(imagePath.path)], text: textMessage);
                          }
                        }
                      } catch (e) {
                        debugPrint('공유 실패: $e');
                      }
                    },"""
content = content.replace(old_share_logic, new_share_logic)

# 5. Modify Navigator.pop in Dialog
old_dialog_end = """                      TextButton(
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
  }"""
new_dialog_end = """                      TextButton(
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
  }"""
content = content.replace(old_dialog_end, new_dialog_end)

# 6. Wrap Stack with Screenshot and add overlay
old_stack = """        child: Stack(
        children: [
          Scaffold("""
new_stack = """        child: Screenshot(
          controller: _screenshotController,
          child: Stack(
            children: [
              Scaffold("""
content = content.replace(old_stack, new_stack)

old_stack_end = """          // 오버레이 팝업 룰렛 (Spin 중일 때만 표시)
          if (_isSpinning)"""
new_stack_end = """          // 오버레이 결과 팝업
          if (_showResultPopup) _buildResultPopupOverlay(),
          // 오버레이 팝업 룰렛 (Spin 중일 때만 표시)
          if (_isSpinning)"""
content = content.replace(old_stack_end, new_stack_end)

# Fix Screenshot closing bracket
old_scaffold_close = """      ),
    ],
  ),
          ),
          ),
          // 오버레이 팝업 룰렛 (Spin 중일 때만 표시)"""
# We don't need to touch this because we replaced old_stack_end directly
# But wait, we opened Screenshot at `child: Screenshot( controller: ... child: Stack(`.
# This means we need one more `)` to close Screenshot where Stack ends.
old_final_close = """                  ),
                ),
              ],
            ),
          ),
        ],
      ),
          ),
          ),"""
# wait, my previous patch did this:
# ```dart
#           // 오버레이 팝업 룰렛 (Spin 중일 때만 표시)
#           if (_isSpinning)
#             BackdropFilter( ... )
#         ],
#       ),
#       ),
#     );
# ```
# Stack ends at line 830 `      ),`. Then PopScope ends at `      ),`. Then build ends at `    );`.
# Let's check lines 825-835.

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
old_final_close = """        ],
      ),
      ),
    );
  }"""
new_final_close = """        ],
      ),
        ),
      ),
    );
  }"""
content = content.replace(old_final_close, new_final_close)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
