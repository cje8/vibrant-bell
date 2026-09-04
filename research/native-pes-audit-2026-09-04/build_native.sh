#!/bin/sh
# Build unmodified, pinned upstream sources in an isolated scratch directory.
# Prerequisite: micromamba + compiler environment and archives extracted there.
set -eu
task_root=${1:?Supply the absolute scratch directory}
audit_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export XDG_CACHE_HOME="$task_root/cache"
export CONDA_PKGS_DIRS="$task_root/mamba-root/pkgs"
rkhs="$task_root/RKHS-a392786bd3575dec6ae63b485112a40b20b5d1a8/src"
pes="$task_root/CO2-PESs-020c61d365f2f1c3ac44644378901ba0ab3c9406"
compile() {
    "$task_root/bin/micromamba" --no-rc -r "$task_root/mamba-root" run \
        -p "$task_root/compiler" arm64-apple-darwin20.0.0-gfortran \
        -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk "$@"
}
for mode in o0 o2 trap; do
    mkdir -p "$task_root/builds/$mode"
    cd "$task_root/builds/$mode"
    case "$mode" in
        o0) set -- -O0 -g -fbacktrace ;;
        o2) set -- -O2 -g -fbacktrace ;;
        trap) set -- -O0 -g -fbacktrace -ffpe-trap=invalid,zero,overflow ;;
    esac
    compile "$@" -c "$rkhs/RKHS.f90" "$pes/1AP/CO2-1AP-PES.f90"
    compile "$@" RKHS.o CO2-1AP-PES.o "$audit_dir/native_probe.f90" -o native_probe
    compile "$@" RKHS.o CO2-1AP-PES.o "$audit_dir/trace_probe.f90" -o trace_probe
    compile "$@" RKHS.o CO2-1AP-PES.o "$pes/pes_test.f90" -o upstream_test
    if [ "$mode" = o0 ]; then
        compile "$@" RKHS.o "$rkhs/example.f90" -o rkhs_example
    fi
done
