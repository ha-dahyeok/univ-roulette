# 🎯 대학맛집 룰렛 (Campus Roulette)

**"오늘 뭐 먹지?"** 대학생들의 가장 큰 고민을 해결해주는 **대학교 맛집 랜덤 추천 서비스**입니다.
여러분의 캠퍼스, 원하는 출입구, 그리고 예산(가격대)에 맞춰 숨겨진 맛집을 룰렛으로 재미있게 추천받아보세요!

[![Web Demo](https://img.shields.io/badge/Web-Live_Demo-blue?style=for-the-badge&logo=googlechrome)](https://ha-dahyeok.github.io/univ-roulette/)
[![Download APK](https://img.shields.io/badge/Android-Download_APK-green?style=for-the-badge&logo=android)](https://ha-dahyeok.github.io/univ-roulette/app-release.apk)

---

## 🌟 주요 기능 (Key Features)

- **🏫 다양한 대학교 지원**: 건국대, 고려대, 서강대, 연세대, 인하대, 중앙대, 한양대, 홍익대, 경희대 등 여러 대학교 캠퍼스 주변 맛집 데이터를 제공합니다.
- **📍 맞춤형 필터링**: 내가 있는 곳과 가까운 '출입구' 단위 필터링 및 지갑 사정에 맞춘 '가격대(가성비, 보통, 플렉스)' 필터링이 가능합니다.
- **🎲 랜덤 룰렛 추천**: 결정 장애를 해결해 주는 짜릿한 룰렛 UI를 제공합니다.
- **🗺️ 카카오맵 연동**: 추천받은 맛집의 위치와 상세 정보를 카카오맵을 통해 즉시 확인할 수 있습니다.
- **📱 크로스 플랫폼 지원**: 웹 브라우저(PC/모바일) 및 안드로이드(APK) 앱 환경을 완벽하게 지원합니다.

## 🛠 기술 스택 (Tech Stack)

- **Frontend**: Flutter (Dart)
- **Backend / Database**: Supabase (PostgreSQL)
- **Data Ingestion**: Python (Kakao Local API)
- **Deployment**: GitHub Pages (Web), GitHub Actions

## 🔗 프로젝트 링크 모음 (Submission Links)

1. **Github Public Repository**: [https://github.com/ha-dahyeok/univ-roulette](https://github.com/ha-dahyeok/univ-roulette)
2. **라이브 데모 (웹)**: [https://ha-dahyeok.github.io/univ-roulette/](https://ha-dahyeok.github.io/univ-roulette/)
3. **안드로이드 앱 다운로드**: [앱 다운로드(APK)](https://ha-dahyeok.github.io/univ-roulette/app-release.apk)

## 🚀 로컬 실행 방법 (How to Run Locally)

```bash
# 1. 저장소 클론
git clone https://github.com/ha-dahyeok/univ-roulette.git
cd univ-roulette

# 2. 패키지 설치
flutter pub get

# 3. 프로젝트 실행 (웹 환경 권장)
flutter run -d chrome
```
