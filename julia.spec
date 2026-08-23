%define _disable_lto 1
%define _disable_ld_no_undefined 1

# Public SONAME is libjulia.so.1.12
%define major 1.12
%define libname %mklibname julia %{major}
%define devname %mklibname julia -d

Name:		julia
Version:	1.12.7
Release:	1
Summary:	High-level, high-performance dynamic language for technical computing
Group:		Development/Other
# Julia is MIT; bundled SuiteSparse/GMP bits can be GPL when not using system copies
License:	MIT and GPLv2+ and LGPLv2+
Url:		https://julialang.org/
# Full tarball includes LLVM 18.1.7+patches and other deps (ABF has no network)
Source0:	https://github.com/JuliaLang/julia/releases/download/v%{version}/julia-%{version}-full.tar.gz

BuildRequires:	make
BuildRequires:	cmake
BuildRequires:	python
BuildRequires:	perl
BuildRequires:	m4
BuildRequires:	patch
BuildRequires:	gcc-gfortran
BuildRequires:	%{_lib}atomic-devel
BuildRequires:	patchelf
BuildRequires:	which
BuildRequires:	7zip
BuildRequires:	desktop-file-utils
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(libpcre2-8)
BuildRequires:	pkgconfig(libgit2)
BuildRequires:	pkgconfig(libssh2)
BuildRequires:	pkgconfig(libnghttp2)
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	pkgconfig(libssl)
BuildRequires:	pkgconfig(gmp)
BuildRequires:	pkgconfig(gmpxx)
BuildRequires:	pkgconfig(mpfr)
BuildRequires:	pkgconfig(openblas)
BuildRequires:	pkgconfig(libutf8proc)
BuildRequires:	suitesparse-devel

%ifarch znver1
%global march znver1
%global julia_cpu generic;znver1
%endif
%ifarch x86_64
%global march x86-64
%global julia_cpu generic;sandybridge,-xsaveopt,clone_all;haswell,-rdrnd,base(1)
%endif
%ifarch aarch64
%global march armv8-a
%global julia_cpu generic;cortex-a57;thunderx2t99
# Bundled LLVM libunwind misses outline-atomic helpers on aarch64
%global julia_sys_unwind 1
%endif
%{!?julia_sys_unwind:%global julia_sys_unwind 0}

Requires:	7zip
Requires:	%{libname} = %{EVRD}

%description
Julia is a high-level, high-performance dynamic programming language
for technical computing, with syntax familiar to users of other
technical computing environments. It provides a JIT compiler,
distributed parallel execution, numerical accuracy, and an extensive
mathematical function library.

%package -n %{libname}
Summary:	Julia shared library
Group:		System/Libraries

%description -n %{libname}
The libjulia shared library used to embed the Julia runtime.

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
Headers and the unversioned libjulia.so symlink for embedding Julia
in other programs (for example Cantor's Julia backend).

%prep
%autosetup -p1 -n %{name}-%{version}

# LLVM is bundled (Julia 1.12 needs patched 18.1.7; cooker LLVM is 23).
# libuv, openlibm, dSFMT, libunwind, and libblastrampoline are Julia forks
# or not packaged here.
cat > Make.user << 'EOF'
prefix=%{_prefix}
bindir=%{_bindir}
# Julia's install/rpath logic assumes prefix/lib; move to lib64 after install
libexecdir=%{_libexecdir}
datarootdir=%{_datadir}
includedir=%{_includedir}
sysconfdir=%{_sysconfdir}
MARCH=%{march}
JULIA_CPU_TARGET=%{julia_cpu}
USE_BINARYBUILDER=0
USE_SYSTEM_CSL=1
USE_SYSTEM_LLVM=0
USE_SYSTEM_LLD=0
USE_SYSTEM_LIBUNWIND=0
USE_SYSTEM_PCRE=1
USE_SYSTEM_LIBM=0
USE_SYSTEM_OPENLIBM=0
USE_SYSTEM_DSFMT=0
USE_SYSTEM_LIBBLASTRAMPOLINE=0
USE_SYSTEM_BLAS=1
USE_SYSTEM_LAPACK=1
USE_SYSTEM_GMP=1
USE_SYSTEM_MPFR=1
USE_SYSTEM_LIBSUITESPARSE=1
USE_SYSTEM_LIBUV=0
USE_SYSTEM_UTF8PROC=1
USE_SYSTEM_OPENSSL=1
USE_SYSTEM_LIBSSH2=1
USE_SYSTEM_NGHTTP2=1
USE_SYSTEM_CURL=1
USE_SYSTEM_LIBGIT2=1
USE_SYSTEM_PATCHELF=1
USE_SYSTEM_LIBWHICH=0
USE_SYSTEM_ZLIB=1
USE_SYSTEM_P7ZIP=1
USE_BLAS64=0
LIBBLAS=-lopenblas
LIBBLASNAME=libopenblas
LIBLAPACK=-lopenblas
LIBLAPACKNAME=libopenblas
VERBOSE=1
override TAGGED_RELEASE_BANNER="OpenMandriva cooker build"
CXXFLAGS+=-include cstdint -Wno-error=c2y-extensions -Wno-unknown-warning-option
EOF
# LLVM 18's bundled google-benchmark treats __COUNTER__ as -Werror=c2y with Clang 23
sed -i '/^LLVM_CMAKE :=/a LLVM_CMAKE += -DLLVM_INCLUDE_BENCHMARKS=OFF -DLLVM_INCLUDE_TESTS=OFF' deps/llvm.mk

%build
export CC=%{__cc}
export CXX=%{__cxx}
export FC=gfortran
# LLVM 18 headers assume uint64_t is visible; Clang 23 / libstdc++ 16 no longer leak it
export CXXFLAGS="${CXXFLAGS:-} -include cstdint -Wno-error=c2y-extensions -Wno-unknown-warning-option"
export CFLAGS="${CFLAGS:-} -Wno-error=c2y-extensions"
%make_build

%install
export CC=%{__cc}
export CXX=%{__cxx}
export FC=gfortran
export CXXFLAGS="${CXXFLAGS:-} -include cstdint -Wno-error=c2y-extensions -Wno-unknown-warning-option"
export CFLAGS="${CFLAGS:-} -Wno-error=c2y-extensions"
%make_install

# Julia installs public/private libs under prefix/lib and bakes
# JL_SYSTEM_IMAGE_PATH=../lib/julia/sys.so. Keep that path via a symlink.
if [ -d %{buildroot}/usr/lib ] && [ "%{_lib}" != "lib" ]; then
	mkdir -p %{buildroot}%{_libdir}
	cp -a %{buildroot}/usr/lib/. %{buildroot}%{_libdir}/
	rm -rf %{buildroot}/usr/lib
	mkdir -p %{buildroot}/usr/lib
	ln -s ../%{_lib}/julia %{buildroot}/usr/lib/julia
	ln -s ../%{_lib}/libjulia.so.%{version} %{buildroot}/usr/lib/libjulia.so.%{version}
	ln -s ../%{_lib}/libjulia.so.%{major} %{buildroot}/usr/lib/libjulia.so.%{major}
	ln -s ../%{_lib}/libjulia.so %{buildroot}/usr/lib/libjulia.so
fi

# Drop empty debug julia if the build did not request it
rm -f %{buildroot}%{_bindir}/julia-debug
rm -f %{buildroot}%{_libdir}/libjulia-debug.so*
# Test helpers ship a .so and a .so.debug with the same build-id
rm -f %{buildroot}%{_libdir}/julia/libccalltest.so*
rm -f %{buildroot}%{_libdir}/julia/libccalllazy*.so*
rm -f %{buildroot}%{_libdir}/julia/libllvmcalltest.so*

# Upstream install does not place the icon
if [ -f contrib/julia.svg ]; then
	install -Dm644 contrib/julia.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/julia.svg
fi
mkdir -p %{buildroot}%{_docdir}/julia
cp -a README.md NEWS.md %{buildroot}%{_docdir}/julia/ 2>/dev/null || :

%files
%license LICENSE.md
%{_bindir}/julia
%{_libdir}/julia/
/usr/lib/julia
%{_libexecdir}/julia/
%{_datadir}/julia/
%{_docdir}/julia/
%{_mandir}/man1/julia.1*
%{_datadir}/applications/julia.desktop
%{_datadir}/icons/hicolor/*/apps/julia.*
%{_datadir}/metainfo/julia.appdata.xml
%dir %{_sysconfdir}/julia
%config(noreplace) %{_sysconfdir}/julia/startup.jl

%files -n %{libname}
%{_libdir}/libjulia.so.%{major}*
/usr/lib/libjulia.so.%{major}
/usr/lib/libjulia.so.%{version}

%files -n %{devname}
%{_libdir}/libjulia.so
/usr/lib/libjulia.so
%{_includedir}/julia/
