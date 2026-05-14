import os

file_path = "lib/screens/home_screen.dart"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
content = content.replace(
    "import 'package:share_plus/share_plus.dart';",
    "import 'package:share_plus/share_plus.dart';\nimport 'package:flutter/foundation.dart' show kIsWeb, defaultTargetPlatform;\nimport 'package:screenshot/screenshot.dart';\nimport 'package:path_provider/path_provider.dart';\nimport 'dart:io';"
)

# 2. ScreenshotController
content = content.replace(
    "String _selectedUniv = ''; // 기본값: 선택 안 됨",
    "final ScreenshotController _screenshotController = ScreenshotController();\n  String _selectedUniv = ''; // 기본값: 선택 안 됨"
)

# 3. Screenshot wrapping
old_dialog_content = """                  const Text(
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
                  ),"""
new_dialog_content = """                  Screenshot(
                    controller: _screenshotController,
                    child: Container(
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
                  ),"""
content = content.replace(old_dialog_content, new_dialog_content)

# 4. Share Logic
old_share = """                  OutlinedButton.icon(
                    onPressed: () {
                      // ignore: deprecated_member_use
                      Share.share(
                        '오늘 점심은 여기로 결정됨! 🎯\\n${winner['name']} ($category)\\n위치: ${winner['url']}',
                      );
                    },"""
new_share = """                  OutlinedButton.icon(
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
content = content.replace(old_share, new_share)

# 5. Android Download Banner
old_body = """            body: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  AnimatedSize("""
new_body = """            body: Column(
              children: [
                if (kIsWeb && defaultTargetPlatform == TargetPlatform.android)
                  Container(
                    color: const Color(0xFFFEE500),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: SafeArea(
                      bottom: false,
                      child: Row(
                        children: [
                          const Expanded(
                            child: Text(
                              '안드로이드에서 더 빠르고 쾌적하게 즐겨보세요!',
                              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.black87),
                            ),
                          ),
                          ElevatedButton(
                            onPressed: () async {
                              final url = Uri.parse('https://github.com/ha-dahyeok/univ-roulette/releases/latest');
                              try {
                                await launchUrl(url, mode: LaunchMode.externalApplication);
                              } catch (e) {
                                debugPrint('Could not launch $url');
                              }
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.black87,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 0),
                              minimumSize: const Size(0, 36),
                            ),
                            child: const Text('앱 다운로드'),
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
                        AnimatedSize("""
content = content.replace(old_body, new_body)

old_body_end = """              ]
            ) : const SizedBox.shrink()),
          ),
        ],
      ),
          ),
          ),
          // 오버레이 팝업 룰렛 (Spin 중일 때만 표시)"""
new_body_end = """              ]
            ) : const SizedBox.shrink()),
          ),
        ],
      ),
      ),
    ],
  ),
          ),
          ),
          // 오버레이 팝업 룰렛 (Spin 중일 때만 표시)"""
content = content.replace(old_body_end, new_body_end)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
