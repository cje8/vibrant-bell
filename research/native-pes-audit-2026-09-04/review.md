# 공개 CO₂ 1A′ PES: 실제 Fortran 경계 감사

검토일: 2026-09-04. 저장소 master: `ee8046bd7aa35c225cc11bc86ae9456a5e55ff6e`.

공개 보관본: 아래 내용은 최초 로컬 감사 시점의 기록이다. 게시 준비 중에는 측정값을 바꾸지 않고 사용자별 경로를 `/path/to/co2-quantum-path`, `/path/to/co2-pes-scratch`로 치환했다. 이 보관본 및 진단 parser의 CI 검사는 원본 Fortran의 물리 정확성 승인과 별개다.

## 결론

이전의 소스·기하학 감사에서 제기한 경계 문제가 **고정된 원본 evaluator를 실제로 실행해도 재현됐다.** 이 환경에서는 선형 구조에 대한 NaN·Infinity, 최적화 설정 의존성, 배포 커널과 CSV 재생성 결과의 차이가 나타났다. 따라서 이 evaluator를 현재 상태로 검증된 전역 energy/gradient 공급자로 승인하지 않는다.

이는 공개 소스의 특정 revision·컴파일 환경에서 얻은 결과다. 원 논문의 전체 계산이 틀렸다는 판정도, 다른 evaluator가 모두 실패한다는 판정도 아니다. 특히 **CO₂의 최소작용 양자 경로나 광해리 수율을 계산한 결과가 아니다.**

최초 감사에서는 저장소의 Python 구현·GitHub CI·머지된 PR을 변경하지 않고 로컬 연구 스크립트와 원시 결과만 추가했다. upstream 소스·데이터는 별도 임시 폴더에 내려받았고 수정하거나 이 저장소에 재배포하지 않았다.

## 1. 환경과 입력을 분리했다

- PES: [MMunibas/CO2-PESs, `020c61d…`](https://github.com/MMunibas/CO2-PESs/tree/020c61d365f2f1c3ac44644378901ba0ab3c9406), `1AP/CO2-1AP-PES.f90`.
- RKHS: [MMunibas/RKHS, `a392786…`](https://github.com/MMunibas/RKHS/tree/a392786bd3575dec6ae63b485112a40b20b5d1a8), `src/RKHS.f90`.
- macOS 27.0 / arm64, GNU Fortran 16.2.0 (conda-forge 16.2.0-4). 한 컴파일러·한 호스트에서만 검사했다.
- 빌드: `-O0`, `-O2`, 그리고 `-O0 -ffpe-trap=invalid,zero,overflow`. 모두 `-g -fbacktrace` 및 설치된 macOS SDK 사용. `-ffast-math`는 사용하지 않았다.
- 원본 커널 모드: `asymp.dat`와 배포된 세 `.kernel`만 복사. CSV 없음.
- 재생성 모드: 처음에는 `asymp.dat`와 세 CSV만 복사. 원 evaluator의 첫 O0 호출이 커널을 생성했다. 이후 O0/O2 비교는 **동일한 O0 재생성 커널을 로드**한 것이다. O2로 계수를 별도 재생성한 비교는 아니다.
- 각 시험점은 새 프로세스에서 평가했다. 에너지는 Hartree, gradient는 `(OO, OC, CO)` 순서의 거리 미분으로 Hartree/bohr다. Cartesian force가 아니다.

Exa로 [공식 micromamba 설치 안내](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)를 확인해 compiler·cache를 `/path/to/co2-pes-scratch`에 격리했다. 전역 Homebrew 설치나 shell 초기화는 하지 않았다. 환경·소스·데이터 SHA-256은 [environment.json](environment.json), 패키지 URL은 [compiler-packages.txt](compiler-packages.txt)에 있다.

## 2. 선형 경계: 정상 종료가 정상 숫자를 의미하지 않는다

24개 진단점을 구성했다. 원본 예제·산소 교환·bent 대조군·선형 OCO/OOC·근선형 각도 6개·두 arrangement의 원거리 점을 포함한다. 임의로 선택한 스트레스 테스트이며 통계적 성공률이나 물리 정확도 점수가 아니다.

| 빌드 / 데이터 | energy와 3개 gradient 모두 유한한 점 | 실패점의 프로세스 종료 |
| --- | --- | --- |
| O0 / 배포 커널 | 21 / 24 | 모두 0 |
| O2 / 배포 커널 | 19 / 24 | 모두 0 |
| O0 / 재생성 커널 | 21 / 24 | 모두 0 |
| O2 / 재생성 커널 | 19 / 24 | 모두 0 |
| O0 + 예외 trap / 배포 커널 | 21 / 24 | 3개 모두 SIGILL, subprocess −4 |

주요 반례:

| `(OO, OC, CO)` bohr | O0 / 배포 커널 | O2 / 배포 커널 |
| --- | --- | --- |
| `(4.412, 2.206, 2.206)` | E 유한, gradient 모두 NaN | E 유한, gradient 모두 NaN |
| `(4.4, 2.2, 2.2)` | 모두 유한 | E와 gradient 모두 NaN |
| `(4.5, 2.25, 2.25)` | 모두 유한 | E 유한, gradient 모두 NaN |
| `(4.5, 2.0, 2.5)` | E 유한, gradient `+Inf, −Inf, −Inf` | 동일한 비유한 패턴 |

마지막 두 거리 배치는 이진 부동소수점으로 정확히 표현되고 삼각부등식의 등호를 만족한다. 따라서 모든 반례를 “사용자가 입력한 소수 거리의 미세한 비물리성”으로 돌릴 수 없다. `paper_rounded`라는 시험점 이름은 반올림된 길이를 가리키며 문헌 최소점의 고정밀 재현을 주장하지 않는다.

원본 예제 `(2.4, 2.3, 4.5)`는 O0에서 E = −0.31217332377797824 Hartree와 유한 gradient를 반환했다. 이것은 호출·데이터 로드의 정상 대조군이지, 독립적인 ab initio 정답과의 비교는 아니다.

### NaN fallback을 통과해도 회복되지 않는다

[trace_probe.f90](trace_probe.f90)은 원본의 공개 routine을 직접 호출한다. 원본 수식이나 PES 계수는 변경하지 않는다. [trace-output.json](trace-output.json)에서 다음을 확인할 수 있다.

1. `(4.412, 2.206, 2.206)`에서 arrangement 2/3의 Jacobi 각도가 0이고 좌표 미분이 비유한이다.
2. `pes3d`의 최초 gradient가 NaN이고, `co21appes`의 fallback 이후에도 NaN이다.
3. 이 점에서 wrapper와 동일한 ±0.005/±0.010 bohr 거리 차분 12개를 따로 호출하면, 삼각부등식을 위반한 6개 점의 에너지가 실제로 NaN이다. bent 대조군에서는 12개 모두 물리적인 거리 배치이며 에너지도 유한하다.
4. `(4.4, 2.2, 2.2)`의 arrangement 1에서 O0는 작은 R 보정값을 반환하지만 O2는 R 자체가 NaN이다. 이는 [제곱근 후에만 작은 R을 보정하는 코드](https://github.com/MMunibas/CO2-PESs/blob/020c61d365f2f1c3ac44644378901ba0ab3c9406/1AP/CO2-1AP-PES.f90#L152)의 경계 민감성과 일치한다. 특정 기계 명령이나 compiler 버그까지 규명한 것은 아니다.

예외 trap 실행의 최초 경계 오류는 `crdtrf` 171행으로 보고됐다. 플랫폼에서 실제로 관측한 신호는 SIGILL이며 SIGFPE라고 바꾸어 기록하지 않았다. trap은 최초 예외에서 중단하므로 fallback 완료 경로의 증거는 일반 O0/O2 실행과 구분한다.

### Infinity는 fallback 조건에서 빠진다

정확히 표현 가능한 `(4.5, 2.0, 2.5)`에서 최초 gradient가 `+Inf, −Inf, −Inf`이고 wrapper 반환도 그대로다. [453행의 조건](https://github.com/MMunibas/CO2-PESs/blob/020c61d365f2f1c3ac44644378901ba0ab3c9406/1AP/CO2-1AP-PES.f90#L453)은 `any(isNaN(dvdr))`다. Infinity만 발생하면 이 조건이 참이 되지 않는다.

단순히 조건을 `not finite`로 바꾸는 것만으로 해결되지는 않는다. 같은 거리 fallback에는 물리 영역 이탈 문제가 남는다. 어떤 선형 배치에서는 비물리적 차분점도 유한 에너지를 반환한다. **유한성은 필요조건이지, 좌표·미분 정확성의 충분조건이 아니다.**

## 3. 배포 커널과 재생성 커널은 같은 결과가 아니다

두 경로 모두 이 환경에서 실행됐다. 따라서 바이너리가 아예 로드되지 않는다는 이전 가능성은 이 실행에서는 발생하지 않았다. 반면 커널 파일의 SHA-256과 평가값은 달랐다.

24개 진단점의 비교 가능한 유한 성분 중, O0 배포 커널과 O0 재생성 커널의 최대 에너지 차이는 **4.7582654 × 10⁻⁵ Hartree**, 최대 gradient 성분 차이는 **7.7402765 × 10⁻⁵ Hartree/bohr**였다. 둘 다 `(3.0, 2.1, 2.3)`에서 발생했다.

같은 배포 커널에서 O0/O2의 비교 가능한 유한 에너지 차이는 최대 2.8733 × 10⁻¹⁰ Hartree였다. 이 작은 값에서 **한쪽이 NaN인 경계점은 비교 대상에서 제외**되므로, 최적화 설정 전반의 동등성을 뜻하지 않는다.

재생성 차이가 원래 계수 생성 방식, 훈련값, compiler, 수치 조건 중 어디서 발생하는지는 미규명이다. 차이를 곧바로 논문의 허용 오차 초과나 데이터 손상이라고 부르지 않는다. 다만 source·CSV만 고정하고 “동일한 PES 실행”이라고 주장할 수 없다는 실측 근거다. 전체 지표는 [summary.json](summary.json)에 있다.

## 4. 정상 영역도 추가 검증이 필요하다

산소 교환의 수치 잔차도 0이 아니었다. 원본 예제와 산소를 교환한 점을 비교하면 O0 배포 커널의 |ΔE|는 2.19467 × 10⁻⁶ Hartree, gradient를 올바르게 교환한 뒤 최대 성분 차이는 1.57332 × 10⁻⁴ Hartree/bohr였다. 별도 bent 쌍에서는 더 작았다. 이 두 쌍만으로 전역 대칭 오차를 추정하지 않으며, 필요한 허용 오차도 아직 정하지 않았다.

내부점 `(3.0, 2.1, 2.3)`의 물리적으로 유효한 중심 차분도 시험했다. O0 배포 커널의 OC축 gradient 오차는 h = 10⁻³, 10⁻⁴, 10⁻⁵ bohr에서 각각 약 **3.63 × 10⁻⁶, 4.38 × 10⁻⁵, 4.34 × 10⁻⁴ Hartree/bohr**로 커졌다. 따라서 “차분 미분 검증 통과”라고 기록하지 않는다. 격자 경계, 평가 수치 오차, 계수 조건화 등을 분리하는 후속 검사가 필요하며 원인은 아직 확정하지 않았다.

근선형 6개 점과 C + O₂ / O + CO의 R = 10, 20, 40 bohr 점은 이 시험에서 모두 유한했다. 그러나 원거리 에너지 기준·전자상태 correlation·미분 극한을 독립 정답과 대조하지 않았으므로 물리적 asymptote 검증 완료는 아니다. O0에서 특정 선형점이 유한하다는 사실도 정확한 선형 극한임을 보증하지 않는다.

## 5. RKHS 자체 예제의 정답 대조는 미해결이다

[원본 README](https://github.com/MMunibas/RKHS/blob/a392786bd3575dec6ae63b485112a40b20b5d1a8/README.md)의 fast 예제 값은 약 1.6807426364인데, 고정된 source·grid의 실제 예제 출력은 −2.7367794365였다. 이 golden-value 대조는 **실패**다.

한편 slow/fast 에너지 차이는 약 4.10 × 10⁻⁹였고, 저장 후 재로드한 fast 값은 동일했다. `multidimensional-grid-RECOVERED.csv`와 입력 CSV는 `cmp` 및 SHA-256 모두 일치했다. 따라서 단순한 줄바꿈·CSV 복원 실패는 이 실행에서 관측되지 않았다. 이것만으로 README가 틀렸다거나 compiler가 옳다고 결론 내리지 않는다. slow 출력의 Hessian 상삼각 원소도 독립적으로 검증하지 않았다.

원시 출력은 [control-output.json](control-output.json)에 있다. 이 미해결 대조 때문에 RKHS 전체의 정확성을 승인하지 않는다. 선형점의 NaN·Inf 및 잘못된 차분 영역은 별도로 직접 관측한 실패다.

## 6. CI 판단과 다음 승인 조건

현재 저장소의 실제 테스트 명령 `python -m unittest discover -s tests -v`는 **73개 모두 통과**했다. 이는 Python 계약 계층의 결과이며, upstream Fortran 경계 검사가 기존 CI에 들어 있다는 뜻이 아니다. 이번에 GitHub Actions를 새로 실행하거나 수정하지 않았다.

[run_native_cases.py](run_native_cases.py)는 연구 모드에서 실패를 JSON에 수집하고, `--require-finite`를 주면 비유한 결과를 발견할 때 exit 1을 반환한다. 실제 O2/배포 커널에 이 옵션을 적용해 **24개 중 5개 실패와 exit 1**을 확인했다. NaN/Inf의 원시 문자열은 stdout에 보존하고 JSON 수치 필드에서는 null로 바꿔 비표준 JSON 숫자를 쓰지 않는다. 이 옵션도 단지 유한성 gate이며 물리 정확성 gate가 아니다.

다음 최소 구현 후보는 wavepacket 전파기가 아니라 **PES 검증 어댑터와 회귀시험**이다. 승인 조건은 다음과 같다.

1. 실제 사용 데이터 경로·커널/CSV 모드·checksums·compiler를 명시한다.
2. 호출 전 물리적 거리 영역, 호출 후 energy와 모든 gradient의 유한성을 검사하고 실패를 명시적으로 전달한다. NaN을 0으로 치환하지 않는다.
3. 선형 경계의 미분은 유효한 Cartesian/Jacobi 변위와 좌표 극한으로 검증한다. 무조건 clamp하거나 거리별 대칭 차분을 유지하는 수정은 승인하지 않는다.
4. 산소 교환, step-size 변화, kernel 재생성 차이, RKHS 예제 불일치의 의미를 판정한다. Linux/다른 compiler에서도 재현한다.
5. 데이터 재배포 권한과 크기를 확인한 다음 별도 native CI job에 연결한다. 이번에는 upstream 파일을 vendoring하거나 자동 다운로드 CI를 추가하지 않았다.

정적 1A′ PES 호출의 수치 신뢰성을 확보한 뒤에도 중성 광해리의 상태 준비·광결합·비단열 결합·관측량 정의가 남는다. 이 감사 결과가 전체 양자상태 공간의 유일한 최소에너지/최소작용 경로를 결정해 주지는 않는다.

재현 방법: [reproduce.md](reproduce.md). 이번 원천 접근 범위: [source-inventory.json](source-inventory.json).
