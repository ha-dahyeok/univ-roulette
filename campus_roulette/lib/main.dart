import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'screens/home_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await Supabase.initialize(
    url: 'https://yyvhukmxifjtabcmwolj.supabase.co',
    anonKey: 'sb_publishable_vD0jOojh1AwquZvEKUD1gw_T9v8Y1Hy',
  );

  runApp(const CampusRouletteApp());
}

class CampusRouletteApp extends StatelessWidget {
  const CampusRouletteApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '캠퍼스 룰렛',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.grey, // 기본 색상은 중립적인 회색
          primary: Colors.black87,
        ),
        scaffoldBackgroundColor: const Color(0xFFF8F9FA), // 연한 회색 배경
        useMaterial3: true,
        fontFamily: 'Pretendard',
      ),
      home: const HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
