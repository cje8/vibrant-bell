# 재현 절차

공개 보관본의 `/path/to/co2-quantum-path`와 `/path/to/co2-pes-scratch`는 사용자별 경로를 제거한 placeholder다. 실행 전에 실제 checkout 및 새 scratch 절대경로로 바꾼다. 아래의 “현재”는 최초 로컬 감사 시점이며 임시 환경을 저장소가 배포하거나 보존하지는 않는다.

## 현재 임시 작업 폴더에서 재실행

이 실행에서 만든 환경은 `/path/to/co2-pes-scratch`에 남아 있다. OS가 임시 폴더를 정리하면 아래의 fresh setup이 필요하다. repo에는 upstream 소스·데이터나 compiler를 포함하지 않았다.

```sh
cd /path/to/co2-quantum-path
sh research/native-pes-audit-2026-09-04/build_native.sh /path/to/co2-pes-scratch

./.venv/bin/python research/native-pes-audit-2026-09-04/run_native_cases.py \
  /path/to/co2-pes-scratch/builds/o2/native_probe \
  /path/to/co2-pes-scratch/runs/original-kernel \
  --finite-difference --require-finite
```

현재 원본에 대한 기대 결과는 **24개 중 19개 유한, 종료 코드 1**이다. 성공하는 테스트처럼 exit 0을 기대하면 안 된다. `--require-finite`를 빼면 동일한 실패를 JSON에 수집하고 진단 프로그램 자체는 exit 0으로 끝난다.

`o2`를 `o0`로 바꾸면 유한한 점이 21개다. `original-kernel`을 `rebuilt-csv`로 바꾸면 O0로 재생성해 놓은 커널을 사용한다. 재생성 디렉터리에 현재 `.kernel`이 있으므로, 이 재실행은 CSV에서 다시 계수를 생성하는 작업이 아니다.

원시 결과의 요약을 다시 계산하려면:

```sh
./.venv/bin/python research/native-pes-audit-2026-09-04/summarize_results.py
./.venv/bin/python -m unittest discover -s tests -v
```

`trace_probe`는 표준입력 한 줄로 거리 3개를 받는다. 동일한 data directory에서 실행해 `4.412 2.206 2.206`을 입력하면 각 chart, 최초 gradient, wrapper gradient, 차분점의 물리 영역 여부와 에너지를 출력한다. trace의 `STENCIL` 출력은 wrapper와 같은 점을 독립적으로 호출한 진단이다. 모든 경우에 wrapper가 실제로 fallback을 실행했다는 뜻은 아니다. `DIRECT`에 NaN이 있는 경우 source의 조건과 함께 해석한다.

## 새 scratch에서 시작할 때

1. `mktemp -d /private/tmp/co2-pes-native.XXXXXX`로 새 디렉터리를 만든다. 기존 원본이나 캐시를 삭제하지 않는다.
2. [environment.json](environment.json)의 고정 PES/RKHS codeload URL에서 아카이브를 내려받는다. SHA-256을 검증하고 archive 경로를 확인한 뒤 scratch 안에 푼다. `main`/`master` 최신판으로 대체하지 않는다.
3. macOS arm64용 micromamba를 공식 배포처에서 받아 scratch의 `bin/micromamba`에 둔다. 이번에는 2.9.0을 사용했다. `/latest` URL의 미래 응답이 기록된 SHA-256과 다르면 동일한 설치 artifact로 간주하지 않는다. SHA-256 및 실제 버전은 manifest를 기준으로 확인한다.
4. 아래 방식으로 scratch에 compiler를 설치했다. 환경 변수와 prefix 모두 새 scratch 경로로 바꾼다. shell init이나 전역 package manager 변경은 필요하지 않다.

```sh
XDG_CACHE_HOME=/path/to/co2-pes-scratch/cache \
CONDA_PKGS_DIRS=/path/to/co2-pes-scratch/mamba-root/pkgs \
/path/to/co2-pes-scratch/bin/micromamba --no-rc \
  --root-prefix /path/to/co2-pes-scratch/mamba-root \
  create --prefix /path/to/co2-pes-scratch/compiler \
  --channel conda-forge gfortran_osx-arm64=16.2.0 --yes
```

이 설치 명령은 최상위 compiler 버전을 고정하지만 모든 전이 의존성의 미래 resolution까지 고정하지는 않는다. 정확한 package build/URL은 [compiler-packages.txt](compiler-packages.txt)와 대조한다. 이 파일은 실제 `micromamba list --explicit` 출력 기록이며, 그대로 유효한 lockfile이라고 보증하지 않는다. 새 환경이 다르면 별도 재현 환경으로 기록해야 한다.

5. 새 `runs/original-kernel` 디렉터리에 upstream `1AP/asymp.dat`, `pes11.kernel`, `pes12.kernel`, `pes13.kernel`만 복사한다. CSV를 넣지 않는다.
6. 별도의 새 `runs/rebuilt-csv` 디렉터리에는 `asymp.dat`, `pes11.csv`, `pes12.csv`, `pes13.csv`만 복사한다. `.kernel`이 없음을 확인한다. 원 파일은 수정하지 않는다.
7. 별도의 `runs/rkhs-control`에는 RKHS의 `multidimensional-grid.csv`를 복사한다. 이 디렉터리는 예제의 `test.kernel`·복원 CSV 생성용이다.
8. `build_native.sh <새 scratch 절대경로>`를 실행한다. 현재 스크립트는 이번 macOS arm64 도구 이름과 SDK 경로를 명시한다. 다른 플랫폼에 이식할 때는 별도 빌드 설정과 결과를 기록한다.
9. 먼저 O0 `upstream_test`를 원본 커널 디렉터리에서, `rkhs_example`을 RKHS 대조 디렉터리에서 실행한다. RKHS의 README golden 값 불일치를 숨기지 않는다.
10. O0 native matrix를 **커널 없는 재생성 디렉터리**에서 먼저 실행한다. 최초 호출만 CSV를 읽어 커널을 생성하고, 이후 새 프로세스들은 생성된 커널을 읽는다. 생성 전·후 파일 목록 및 checksum을 기록한다. 최초 계수 생성 시간이 길면 `--timeout 120` 등으로 점별 제한을 명시한다.
11. O0/O2 각각 원본·재생성 커널로 24점과 내부 미분을 검사한다. 예외 trap 빌드는 `ulimit -c 0`인 shell에서 별도로 실행해 core dump를 만들지 않고 raw stderr를 보존한다.

원본에 대한 gate는 현재 실패하는 것이 올바른 결과다. 다른 환경에서 모든 값이 유한하더라도 그 자체로 물리 정확도나 좌표 특이점 문제가 해결됐다고 해석하지 않는다. 이 감사에는 전역 gradient 보정, eigenstate, propagation, scattering probability 계산이 없다.
