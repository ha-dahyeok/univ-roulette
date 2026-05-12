// This is a basic Flutter widget test.

import 'package:flutter_test/flutter_test.dart';
import 'package:campus_roulette/main.dart';

void main() {
  testWidgets('App loads successfully smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const CampusRouletteApp());

    // Verify that our app title exists.
    expect(find.text('🎡 캠퍼스 룰렛'), findsOneWidget);
  });
}
