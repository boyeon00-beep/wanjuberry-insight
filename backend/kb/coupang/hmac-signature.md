# HMAC Signature 생성 (Authorization 헤더) — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

HMAC(Hash-based Message Authentication Code, RFC2014)은 키 기반 메시지 인증 코드 표준 암호화 프로토콜입니다. 쿠팡 Open API는 HMAC 기반으로 제작되어 **모든 요청의 `Authorization` 헤더에 HMAC signature를 포함**해야 합니다. 본 문서는 단일 엔드포인트가 아닌 **인증 가이드**(`doc_type: guide`)입니다.

## Endpoint
- Method: N/A (가이드 문서. 모든 쿠팡 Open API 호출 시 동일하게 적용)
- URL: 모든 호출 기본 호스트 — https://api-gateway.coupang.com
- 인증: HMAC-SHA256 기반 Custom `Authorization` 헤더 (`CEA algorithm=HmacSHA256, access-key=..., signed-date=..., signature=...`)

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | `CEA algorithm=HmacSHA256, access-key={accessKey}, signed-date={yyMMddTHHmmssZ}, signature={hexHmac}` |
| Content-Type | N | `application/json;charset=UTF-8` (요청 본문이 JSON인 경우) |

### Query Parameters / Body
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| accessKey | string | Y | 쿠팡에서 발급한 액세스 키. Authorization 헤더 `access-key` 값으로 그대로 사용 | MASKED |
| secretKey | string | Y | 쿠팡에서 발급한 시크릿 키. HMAC-SHA256 키로만 로컬에서 사용, 외부 전송 금지 | MASKED |
| method | string | Y | 요청의 HTTP method | GET |
| path | string | Y | 요청 경로 (호스트 제외) | /v2/providers/openapi/apis/api/v4/vendors/MASKED/returnRequests |
| query | string | N | URL 쿼리 문자열 (앞의 `?` 제외, key=value&...) | createdAtFrom=2018-08-09&createdAtTo=2018-08-09&status=UC |
| datetime | string | Y | 서명용 timestamp. `yyMMddTHHmmssZ` (GMT+0) | 180809T010203Z |
| message (내부) | string | Y | 서명 대상 문자열. 형식: `{datetime}{method}{path}{query}` | 180809T010203ZGET/v2/...UC |
| signature (출력) | string | Y | HMAC-SHA256(message, secretKey) → hex 문자열 | MASKED |

### 조회 가능 기간
- 최대: N/A (가이드 문서)
- 기본값: N/A

### 페이지네이션
- 방식: 없음
- 파라미터: -
- 최대 size: -

## Response

### 주요 필드
이 가이드는 응답 스키마 대신 **Authorization 헤더 포맷**과 **언어별 구현 예시**를 제공합니다.

#### Authorization 헤더 포맷
```
Authorization: CEA algorithm=HmacSHA256, access-key={accessKey}, signed-date={datetime}, signature={signature}
```

#### message 생성 규칙
| 부분 | 값 | 예시 |
|---|---|---|
| `datetime` | GMT+0 기준 `yyMMddTHHmmssZ` | `180809T010203Z` |
| `method` | HTTP 메소드 (대문자) | `GET` |
| `path` | URL 경로 (앞에 `/`, 호스트 제외) | `/v2/providers/openapi/apis/api/v4/vendors/A00*****/returnRequests` |
| `query` | 쿼리 문자열 (앞 `?` 제외, 빈 쿼리면 빈 문자열) | `createdAtFrom=2018-08-09&createdAtTo=2018-08-09&status=UC` |
| `message` | 위 4개를 단순 연결 (구분자 없음) | `180809T010203ZGET/v2/.../returnRequestscreatedAtFrom=...` |

#### 언어별 핵심 구현
| 언어 | HMAC 함수 | 인코딩 | datetime 포맷 |
|---|---|---|---|
| Java | `Hmac.generate(method, uri, SECRET_KEY, ACCESS_KEY)` (쿠팡 SDK) | hex | 라이브러리 내장 |
| PHP | `hash_hmac('sha256', $message, $secretkey)` | hex | `date("ymd").'T'.date("His").'Z'` (GMT+0) |
| Python | `hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()` | hex | `time.strftime('%y%m%d')+'T'+time.strftime('%H%M%S')+'Z'` |
| C# | `HMACSHA256(secretKeyBytes).ComputeHash(messageBytes)` → `ToString("x2")` 반복 | hex | `DateTime.Now.ToUniversalTime().ToString("yyMMddTHHmmssZ")` |

### 상태 코드
| 코드 | 의미 |
|---|---|
| 200 | 인증된 정상 요청 |
| 401 | Unauthorized — Authorization 헤더 누락/잘못 |
| 403 | Forbidden — 권한 없음, 시간 차이 등 |

## 제약사항
- 호출 한도: 명시 없음 (각 API별 한도는 별도 문서)
- **시간 동기화 필수** — `datetime`은 **GMT+0** 기준. 클라이언트 시계가 어긋나면 인증 실패
- `datetime` 유효 범위는 명시 없으나 서버 시간과 큰 차이 시 거부됨 → 호출 직전 생성
- **`secretKey` 외부 전송 금지** — HMAC 계산에만 로컬에서 사용
- `message` 구성 시 path와 query에 **공백/특수문자 인코딩 일관성** 유지 필요 (서버와 동일한 인코딩 규칙)
- `query` 파라미터 순서는 클라이언트가 보내는 순서대로 — 서버는 받은 순서로 검증하므로 일치해야 함
- 매 요청마다 새 `datetime` + 새 `signature` 생성 (재사용 금지)
- SDK 미사용 시 hex 출력 형식(`02x` 패딩) 엄격히 준수

## 에이전트 사용 메모
- **모든 쿠팡 Open API 호출 에이전트의 공통 사전 단계** — 매 요청마다 본 절차로 Authorization 헤더 생성
- 표준 호출 패턴:
  1. 현재 GMT+0 시각으로 `datetime` 생성 (`yyMMddTHHmmssZ`)
  2. method + path + query를 정확히 일치시켜 message 구성
  3. HMAC-SHA256(message, secretKey) → hex
  4. `CEA algorithm=HmacSHA256, access-key=..., signed-date=..., signature=...` 헤더 조립
  5. HTTPS 요청 전송
- 디버깅: 401/403 발생 시 가장 흔한 원인은 (a) 시계 어긋남 (b) path/query가 실제 호출 URL과 불일치
- query 인코딩 차이로 인한 401 빈발 → 라이브러리 URL 빌더와 서명용 query 문자열을 **동일한 소스로** 생성
- `accessKey`/`secretKey`는 secret manager에 보관, 코드/로그에 노출 금지 → 로그 출력 시 `MASKED`
- season_flag: 시즌별 대량 호출 직전 키 로테이션 일정 점검
- 엣지 케이스: GMT+9(KST)로 datetime을 만들면 거의 항상 인증 실패 — GMT+0 강제
- 엣지 케이스: GET 요청에 body가 있는 경우는 본 가이드에서 다루지 않음. 표준 GET 호출은 body 미포함
- 엣지 케이스: signature를 Base64로 출력하면 실패 — **반드시 hex(lowercase, 2자리 패딩)**
- 다운로드 자원: `hmac_sdk.zip` (공식 문서 첨부) — SDK 사용 시 위 단계가 자동화됨
