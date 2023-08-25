%ifarch riscv64
%bcond_with check
%else
%bcond_without check
%endif

Summary:       Compiler and toolchain infrastructure library for WebAssembly
Name:          binaryen
Version:       111
Release:       2.rv64%{?dist}

URL:           https://github.com/WebAssembly/binaryen
Source0:       %{url}/archive/version_%{version}/%{name}-version_%{version}.tar.gz
Patch0:        %{name}-use-system-gtest.patch
Patch1:        https://github.com/WebAssembly/binaryen/pull/5317.patch
# backported from https://github.com/WebAssembly/binaryen/pull/5349
Patch2:        5349.patch
Patch3:        5458.patch
License:       ASL 2.0

# tests fail on big-endian
# https://github.com/WebAssembly/binaryen/issues/2983
ExcludeArch:   ppc64 s390x
BuildRequires: cmake3
BuildRequires: gcc-c++
%if %{with check}
BuildRequires: gtest-devel
BuildRequires: nodejs
BuildRequires: python3dist(filecheck)
BuildRequires: python3dist(lit)
%endif

# filter out internal shared library
%global __provides_exclude_from ^%{_libdir}/%{name}/.*$
%global __requires_exclude ^libbinaryen\\.so.*$

%description
Binaryen is a compiler and toolchain infrastructure library for WebAssembly,
written in C++. It aims to make compiling to WebAssembly easy, fast, and
effective:

* Easy: Binaryen has a simple C API in a single header, and can also be used
  from JavaScript. It accepts input in WebAssembly-like form but also accepts
  a general control flow graph for compilers that prefer that.

* Fast: Binaryen's internal IR uses compact data structures and is designed for
  completely parallel codegen and optimization, using all available CPU cores.
  Binaryen's IR also compiles down to WebAssembly extremely easily and quickly
  because it is essentially a subset of WebAssembly.

* Effective: Binaryen's optimizer has many passes that can improve code very
  significantly (e.g. local coloring to coalesce local variables; dead code
  elimination; precomputing expressions when possible at compile time; etc.).
  These optimizations aim to make Binaryen powerful enough to be used as a
  compiler backend by itself. One specific area of focus is on
  WebAssembly-specific optimizations (that general-purpose compilers might not
  do), which you can think of as wasm minification , similar to minification for
  JavaScript, CSS, etc., all of which are language-specific (an example of such
  an optimization is block return value generation in SimplifyLocals).

%prep
%setup -q -n %{name}-version_%{version}
%patch0 -p1 -b .gtest
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%cmake3 \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_INSTALL_LIBDIR=%{_libdir}/%{name} \
    -DCMAKE_INSTALL_RPATH=\\\$ORIGIN/../%{_lib}/%{name} \
    -DENABLE_WERROR=OFF \

%cmake3_build

%install
%cmake3_install
rm -v %{buildroot}%{_bindir}/binaryen-unittests

%if %{with check}
%check
# https://github.com/WebAssembly/binaryen/issues/5353
%ifarch i686
rm -v test/passes/multi_unit_abbrev_noprint.{bin.txt,passes,wasm}
%endif
install -pm755 %{__cmake_builddir}/bin/binaryen-{lit,unittests} %{buildroot}%{_bindir}
./check.py \
    --binaryen-bin %{buildroot}%{_bindir} \
    --binaryen-lib %{buildroot}%{_libdir}/%{name} \

rm -v %{buildroot}%{_bindir}/binaryen-{lit,unittests}
%endif

%files
%license LICENSE
%doc README.md
%{_bindir}/wasm-as
%{_bindir}/wasm-ctor-eval
%{_bindir}/wasm-dis
%{_bindir}/wasm-emscripten-finalize
%{_bindir}/wasm-fuzz-types
%{_bindir}/wasm-metadce
%{_bindir}/wasm-opt
%{_bindir}/wasm-reduce
%{_bindir}/wasm-shell
%{_bindir}/wasm-split
%{_bindir}/wasm2js
%{_includedir}/binaryen-c.h
%{_includedir}/wasm-delegations.def
%{_libdir}/%{name}/libbinaryen.so

%changelog
* Fri Aug 25 2023 Liu Yang <Yang.Liu.sn@gmail.com> - 111-2.rv64
- Skip failed test on riscv64.

* Fri Apr 07 2023 David Abdurachmanov <davidlt@rivosinc.com> - 111-2.rv64
- Backport fix for GCC 13

* Wed Jan 18 2023 Fedora Release Engineering <releng@fedoraproject.org> - 111-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Tue Dec 13 2022 Dominik Mierzejewski <dominik@greysector.net> 111-1
- update to 111 (#2144160)
- backport upstream fixes for OOB reads in string_view
- disable multi_unit_abbrev_noprint.wasm test running out of memory on i686

* Wed Sep 21 2022 Dominik Mierzejewski <rpm@greysector.net> 110-1
- update to 110 (#2081423)
- fix building with external gtest

* Wed Jul 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 105-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Wed Jan 19 2022 Fedora Release Engineering <releng@fedoraproject.org> - 105-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Sun Jan 16 2022 Dominik Mierzejewski <rpm@greysector.net> 105-1
- update to 105 (#2040105)

* Tue Jan 11 2022 Dominik Mierzejewski <rpm@greysector.net> 104-1
- update to 104 (#2033827)
- fixes CVE-2021-45290 (#2037323, #2037325)
- fixes CVE-2021-45293 (#2037324, #2037326)

* Sun Dec 05 2021 Dominik Mierzejewski <rpm@greysector.net> 103-1
- update to 103 (#2028875)

* Sun Sep 12 2021 Dominik Mierzejewski <rpm@greysector.net> 102-1
- update to 102 (#2003235)

* Wed Jul 21 2021 Fedora Release Engineering <releng@fedoraproject.org> - 101-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Sat May 15 2021 Dominik Mierzejewski <rpm@greysector.net> 101-1
- update to 101 (#1950518)

* Wed Mar 17 2021 Dominik Mierzejewski <rpm@greysector.net> 100-1
- update to 100 (#1914377)
- drop obsolete patch

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 98-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Tue Nov 10 2020 Dominik Mierzejewski <rpm@greysector.net> 98-1
- update to 98 (#1887966)

* Wed Oct 07 2020 Dominik Mierzejewski <rpm@greysector.net> 97-1
- update to 97 (#1880087)

* Tue Aug 18 2020 Dominik Mierzejewski <rpm@greysector.net> 96-1
- update to 96
- drop obsolete patch

* Wed Jul 29 2020 Dominik Mierzejewski <rpm@greysector.net> 95-3
- fix build on F31/F32

* Tue Jul 28 2020 Dominik Mierzejewski <rpm@greysector.net> 95-2
- use built binaries in tests
- fix (r)paths to internal shared library
- filter internal shared library from Provides/Requires

* Tue Jul 21 2020 Dominik Mierzejewski <rpm@greysector.net> 95-1
- initial build
