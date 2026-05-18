# KB Index — 완주베리 AI 운영 인사이트 시스템

> API Knowledge Base 전체 목록. 파일 추가/수정 시 반드시 현행화.

---

## 폴더 구조

```
kb/
├── _index.md                  ← 이 파일 (전체 목록)
├── conversion-template.md     ← 3종 세트 작성 기준
│
├── naver-searchad/            ← 네이버 검색광고 API
│   ├── campaign-list/
│   │   ├── campaign-list.md
│   │   ├── campaign-list.sample.json
│   │   └── campaign-list.fields.csv
│   └── ...
│
├── naver-commerce/            ← 네이버 커머스 API
│   └── ...
│
└── coupang/                   ← 쿠팡 API
    └── ...
```

---

## P0 API 현황

| 플랫폼 | API | 폴더 | 상태 |
|---|---|---|---|
| 네이버 검색광고 | Campaign list | naver-searchad/campaign-list/ | ✅ 완료 |
| 네이버 검색광고 | 광고 성과 리포트 | naver-searchad/ad-performance/ | ⬜ 미완료 |
| 네이버 커머스 | 상품 목록 조회 | naver-commerce/product-list/ | ✅ 연동 완료 (POST /v1/products/search) |
| 네이버 커머스 | 채널 상품 판매 성과 조회 | naver-commerce/channel-sales/ | ⬜ 미완료 |
| 네이버 커머스 | 리뷰 목록 조회 | naver-commerce/review-list/ | ⬜ 미완료 |
| 쿠팡 | 매출내역 조회 | coupang/sales-history/ | ⬜ 미완료 |

---

## 업데이트 이력

| 날짜 | 내용 |
|---|---|
| 2026-05-17 | 초기 구조 생성, campaign-list 파일럿 반영 |
