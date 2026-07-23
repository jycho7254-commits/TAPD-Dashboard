# 🎲 트릭컬 HUN TAPD 품질 대시보드

> 트릭컬 Revive 결함 추적 · 품질 관리 대시보드 (TAPD API 실시간 연동)

🔗 **URL**: https://jycho7254-commits.github.io/TAPD-Dashboard/tapd/

---

## 📊 주요 기능

### 핵심 지표
| 항목 | 내용 |
|------|------|
| HUN 전체 결함 수 | 총 결함 건수 (신규/진행중/종료) |
| 미해결 / 검증중 | 현재 처리 대기 건수 |
| 종료율 | 전체 대비 종료 비율 |
| 치명/심각 | 우선순위별 결함 수 |

### 필터 시스템
| 필터 | 옵션 |
|------|------|
| 수정 버전 | v1.1 ~ v1.5, 주차별 (W33~W42) |
| 발견 버전 | 각 버전별 |
| 상태 | 신규 / 진행중 / 해결·검증 / 반려 / 보류 / 종료 |
| 심각도 | 치명 / 심각 / 일반 |

### 차트 (Chart.js 4.4)
- **일일 버그 추세** — 최근 30일 결함 발생 추이
- **버전별 상태 분포** — 누적 막대 차트
- **버전별 심각도 분포** — 치명/심각/일반 분류
- **버전별 총량 추이** — 시계열 라인
- **결함 유형 추이** — 카테고리별 분포

### 특수 기능
- 🔔 **변경 알림** — 새 결함/상태 변화 실시간 감지
- 🔄 **수동 업데이트** — 캐시 무시하고 TAPD API 재호출

---

## 🏗 아키텍처

### 구조
```
TAPD-Dashboard/
└── tapd/
    ├── index.html          # 대시보드 (단일 HTML)
    ├── tapd_data.json      # TAPD 결함 데이터 캐시
    ├── fetch_tapd.py        # TAPD API 수집 스크립트
    ├── cron_tapd.py         # 크론 자동 수집
    ├── auto_update_tapd.sh  # 자동 업데이트 셸
    ├── tapd_proxy.py        # 로컬 프록시 (CORS 우회)
    └── scripts/             # 보조 스크립트
```

### 기술 스택
| 영역 | 기술 |
|------|------|
| 프론트엔드 | 순수 HTML/CSS/JS |
| 차트 | Chart.js 4.4.7 (CDN) |
| 데이터 | TAPD REST API → JSON 캐시 |
| 자동화 | GitHub Actions (매시 정각) |
| 배포 | GitHub Pages |

### 데이터 파이프라인
```
TAPD API (192.168.4.139:8080)
    ↓ fetch_tapd.py
tapd_data.json (GitHub Actions 매시 갱신)
    ↓ index.html에서 fetch
대시보드 렌더링 (필터/차트/테이블)
```

### HUN 필터 로직
- TAPD 결함 중 `de` 필드에 "HUN" 포함된 건만 필터링
- 기존 `iteration` + `label` 조합에서 `de` 단일 필드로 정확도 향상 (916→576건)

---

## 🔧 TAPD API 설정

| 항목 | 값 |
|------|-----|
| API 키 | 환경변수 `TAPD_API_KEY` |
| 엔드포인트 | `https://api.tapd.cn/` |
| 워크스페이스 | Trickcal_Revive |
| 필터 | `de` 필드 contains "HUN" |
| 갱신 주기 | 매시 정각 (GitHub Actions) |

---

## 👥 기여자

- **명훈 조** — 기획, QA, TAPD 관리
- **Hermes Agent (2호)** — 개발, 자동화, 배포
