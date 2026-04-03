# 관상학 데이터 수집 출처 및 요약

## 개요

- **데이터 파일**: `ml/data/physiognomy_knowledge.json`
- **수집일**: 2026-04-02
- **총 항목 수**: 62개 (10개 카테고리)
- **언어**: 한국어
- **용도**: Supabase pgvector RAG 시스템을 위한 관상학 지식 데이터

## 카테고리별 항목 수

| 카테고리            | 항목 수 | 주요 내용                                                       |
| ------------------- | ------- | --------------------------------------------------------------- |
| 눈 (Eyes)           | 14      | 봉안, 용안, 삼백안, 사백안, 도화안, 원앙안, 음양안 등 13종 눈상 |
| 코 (Nose)           | 8       | 복코, 매부리코, 들창코, 단코, 높은코, 휜코, 뭉툭코              |
| 입 (Mouth)          | 8       | 큰입, 작은입, 입꼬리 방향, 입술 두께별 해석                     |
| 이마 (Forehead)     | 5       | 넓은/좁은/둥근/각진/주름진 이마                                 |
| 턱 (Chin/Jaw)       | 6       | 둥근턱, 사각턱, 뾰족턱, 주걱턱, 무턱, 이중턱                    |
| 귀 (Ears)           | 8       | 큰귀, 작은귀, 부처귀, 돌출귀, 부착귀, 뾰족귀, 두꺼운/얇은 귀    |
| 눈썹 (Eyebrows)     | 11      | 일자, 초승달, 버드나뭇잎, 팔자, 산모양, 삼각형, 칼날 등         |
| 얼굴형 (Face Shape) | 6       | 계란형, 둥근형, 각진형, 역삼각형, 긴 얼굴형, 마름모형           |
| 인중 (Philtrum)     | 5       | 길고 깊은/짧고 얕은/넓이별/굽은 인중                            |
| 광대뼈 (Cheekbones) | 4       | 높은/낮은/앞으로 나온/옆으로 나온 광대뼈                        |

## 데이터 구조

각 항목은 다음 필드를 포함:

- `category`: 부위 카테고리 (한국어)
- `name`: 관상 유형 이름 (한국어, 한자 포함)
- `description`: 해당 관상의 설명
- `visual_characteristics`: 시각적 특징 상세 설명
- `personality`: 성격 해석
- `fortune.wealth`: 재물운 해석
- `fortune.love`: 연애/결혼운 해석
- `fortune.career`: 직업/사업운 해석
- `famous_examples`: 유명 인물 예시 (해당시)

## 수집 출처

### 전문 관상학 사이트

1. [동양 관상학 눈상(眼相) 총정리](https://xn--yq5bk9r.com/blog/eye-reading) - 13종 눈 관상 상세 해석
2. [포춘에이드 운세 - 이마 관상](https://www.fortunade.com/unse/bbs/view.php?b_id=6&c_id=21&seq=4264) - 이마 형태별 관상 해석
3. [홍카페 관상 - 귀 관상](https://www.hongcafe.com/board/column/detail/BC-20190419142801-4541) - 귀 모양별 관상 해석
4. [홍카페 관상 - 삼백안](https://www.hongcafe.com/board/column/detail/BC-20190814135357-5516) - 삼백안 상세 해석

### 관상학 블로그 (The Universe)

5. [눈썹 모양별 11가지 관상](https://star.828free.com/entry/%EB%88%88%EC%8D%B9-%EB%AA%A8%EC%96%91%EB%B3%84-11%EA%B0%80%EC%A7%80-%EA%B4%80%EC%83%81) - 눈썹 관상 11종
6. [관상 보는법 - 입 입술 모양별 성격 운세](https://star.828free.com/entry/%EA%B4%80%EC%83%81-%EB%B3%B4%EB%8A%94%EB%B2%95-%EC%9E%85-%EC%9E%85%EC%88%A0) - 입/입술 관상
7. [턱관상 주걱턱 사각턱 이중턱 무턱](https://star.828free.com/entry/%ED%84%B1%EA%B4%80%EC%83%81-%EC%A3%BC%EA%B1%B1%ED%84%B1-%EC%82%AC%EA%B0%81%ED%84%B1-%EC%9D%B4%EC%A4%91%ED%84%B1-%EB%AC%B4%ED%84%B1-%EA%B4%80%EC%83%81) - 턱 유형별 관상

### 백과사전/위키

8. [나무위키 - 관상](https://namu.wiki/w/%EA%B4%80%EC%83%81) - 관상학 개요 및 각 부위별 해석
9. [나무위키 - 삼백안](https://namu.wiki/w/%EC%82%BC%EB%B0%B1%EC%95%88) - 삼백안 상세
10. [나무위키 - 사백안](https://namu.wiki/w/%EC%82%AC%EB%B0%B1%EC%95%88) - 사백안 상세
11. [나무위키 - 매부리코](https://namu.wiki/w/%EB%A7%A4%EB%B6%80%EB%A6%AC%EC%BD%94) - 매부리코 상세
12. [한국민족문화대백과사전 - 관상](https://encykorea.aks.ac.kr/Article/E0004873) - 관상학 학술적 개요

### 언론 기사

13. [에스콰이어 - 셀럽으로 보는 눈 관상 7가지](https://www.esquirekorea.co.kr/article/63686)
14. [경인일보 - 삼백안의 또 다른 가치](https://www.kyeongin.com/view.php?key=20200918010004214)
15. [대경일보 - 재밌는 관상 이야기 시리즈](https://www.dkilbo.com/news/articleView.html?idxno=352159)
16. [김포신문 - 인중의 모든 것](https://www.igimpo.com/news/articleView.html?idxno=66626)
17. [김포신문 - 귀로 본 사람의 성향](https://www.igimpo.com/news/articleView.html?idxno=65936)
18. [인사이트 - 턱 모양에 따른 성격 유형](https://www.insight.co.kr/amp/news/300114)
19. [헤럴드경제 - 돌출 광대뼈, 관상에도 영향](https://mbiz.heraldcorp.com/view.php?ud=201410071034030719540_1)
20. [한경닷컴 - 관상학적 코성형이란](http://news.hankyung.com/article/201011086631k)
21. [아시아경제 - 매부리코 들창코 재물운](https://www.asiae.co.kr/article/2016012914204556603)
22. [보그코리아 - 관상으로 보는 귀족 얼굴](https://www.vogue.co.kr/2016/11/14/%EB%B3%B5%EC%9D%B4-%EB%84%9D%EA%B5%B4%EC%A7%B8-%EA%B5%B4%EB%9F%AC-%EB%93%A4%EC%96%B4%EC%98%A4%EB%8A%94-%EC%96%BC%EA%B5%B4/)
23. [경향신문 - 귀의 귀함에 대하여](https://www.khan.co.kr/article/202505240600005)

### 분석 블로그

24. [광대뼈 관상 발달한 남자 vs 없는 남자 총정리](https://analyzersaju.com/entry/%EA%B4%91%EB%8C%80%EB%BC%88-%EA%B4%80%EC%83%81) - 광대뼈 관상 상세
25. [Milion - 입술 관상보는법](https://themilion.com/%EC%9E%85%EC%88%A0-%EA%B4%80%EC%83%81) - 입술 관상 해석
26. [충남일보 - 인중, 내 주머니 그 안에 돈이 있다](https://www.chungnamilbo.co.kr/news/articleView.html?idxno=556481) - 인중 재물운
27. [보험매일 - 인중으로 알아보는 나의 수명](http://www.fins.co.kr/news/articleView.html?idxno=7505) - 인중과 수명

## 면책 조항

본 데이터는 전통 동양 관상학(觀相學)에 기반한 문화적 해석을 수집한 것입니다.
과학적으로 검증된 내용이 아니며, 재미와 문화적 참고 용도로만 활용해야 합니다.
개인의 성격이나 운명은 얼굴 생김새로 결정되지 않으며,
본 데이터를 근거로 타인을 판단하거나 차별하는 것은 부적절합니다.
