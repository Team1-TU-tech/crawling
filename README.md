# yes24 crawling

yes24의 경우, 옛날 데이터부터 수집하는 과정에 예외처리할 것이 많았습니다.
이슈는 마지막페이지 구분과 중간중간 데이터가 없는 페이지 모두 같은 값입니다.
타협한 점은, 최근 데이터 num이 5만이 넘기때문에 5만 미만일 시 건너뛰고 실행하게 하였습니다.
다음은 예외처리 결과입니다.

```bash
이전 페이지 523는 정상적이었고, 현재 페이지 524는 404 오류입니다. 종료합니다.
저장 경로: /Users/seon-u/TU-tech/crawling/src/crawling/config/offset.ini
offset 값을 524으로 저장했습니다.
다음 페이지 525는 정상적입니다. 계속 진행합니다.
크롤링 중: 페이지 http://ticket.yes24.com/Perf/525
크롤링 중: 페이지 http://ticket.yes24.com/Perf/526
크롤링 중: 페이지 http://ticket.yes24.com/Perf/527
크롤링 중: 페이지 http://ticket.yes24.com/Perf/528
크롤링 중: 페이지 http://ticket.yes24.com/Perf/529
크롤링 중: 페이지 http://ticket.yes24.com/Perf/530
크롤링 중: 페이지 http://ticket.yes24.com/Perf/531
크롤링 중: 페이지 http://ticket.yes24.com/Perf/532
크롤링 중: 페이지 http://ticket.yes24.com/Perf/533
크롤링 중: 페이지 http://ticket.yes24.com/Perf/534
크롤링 중: 페이지 http://ticket.yes24.com/Perf/535
```
