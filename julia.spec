%global uvcommit 52d72a52cc7ccd570929990f010ed16e2ec604c8
%global uvversion 1.9.0

%global unwindversion 1.1-julia2
%global llvmversion 3.9

%define _disable_lto 1
%define _disable_ld_no_undefined 1

Name:           julia
Version:        0.6.0
Release:        1
Summary:        High-level, high-performance dynamic language for technical computing
Group:          Development/Other
# Julia itself is MIT, with a few LGPLv2+ and GPLv2+ files
# libuv is MIT
License:        MIT and LGPLv2+ and GPLv2+
URL:            http://julialang.org/
Source0:        https://github.com/JuliaLang/julia/releases/download/v%{version}/%{name}-%{version}.tar.gz
# Julia currently uses a custom version of libuv, patches are not yet upstream
Source1:        https://api.github.com/repos/JuliaLang/libuv/tarball/libuv-%{uvcommit}.tar.gz
#Source3:	dsfmt-2.2.3.tar.gz
Source4:	openblas-85636ff1a015d04d3a8f960bc644b85ee5157135.tar.gz
#Source5:	utf8proc-40e605959eb5cb90b2587fa88e3b661558fbc55a.tar.gz
Source100:	julia.rpmlintrc
Provides:       bundled(libuv) = %{uvversion}
BuildRequires:  arpack-devel
BuildRequires:  desktop-file-utils
BuildRequires:  dSFMT-devel
BuildRequires:  fftw-devel >= 3.3.2
BuildRequires:  gcc-c++
# Needed to test package management until the switch to libgit2
BuildRequires:  git
BuildRequires:  gmp-devel >= 5.0
# Needed for libgit2 test
BuildRequires:  hostname
BuildRequires:  imagemagick
BuildRequires:	pkgconfig(atlas)
BuildRequires:  pkgconfig(libgit2)
#BuildRequires:  libunwind-devel
BuildRequires:  llvm-devel >= %llvmversion
BuildRequires:  mpfr-devel >= 3.0
#BuildRequires:  openlibm-devel >= 0.4
BuildRequires:  openspecfun-devel >= 0.4
# Needed for libgit2 test
BuildRequires:  openssl
BuildRequires:  pkgconfig(pcre2)
BuildRequires:  perl
BuildRequires:  suitesparse-devel
BuildRequires:  utf8proc-devel >= 2.1
BuildRequires:  zlib-devel
# Needed for package management until the switch  to libgit2
Requires:       git
Requires:       julia-common = %{version}-%{release}
# Currently, Julia does not work properly architectures other than x86
# https://bugzilla.redhat.com/show_bug.cgi?id=1158024
# https://bugzilla.redhat.com/show_bug.cgi?id=1158026
# https://bugzilla.redhat.com/show_bug.cgi?id=1158025
ExclusiveArch:  %{ix86} x86_64

%description
Julia is a high-level, high-performance dynamic programming language
for technical computing, with syntax that is familiar to users of
other technical computing environments. It provides a sophisticated
compiler, distributed parallel execution, numerical accuracy, and an
extensive mathematical function library. The library, largely written
in Julia itself, also integrates mature, best-of-breed C and Fortran
libraries for linear algebra, random number generation, signal processing,
and string processing.

This package only contains the essential parts of the Julia environment:
the julia executable and the standard library.

%package common
Summary:        Julia architecture-independent files
Group:          Development/Other
BuildArch:      noarch
Requires:       julia = %{version}-%{release}

%description common
Contains architecture-independent files required to run Julia.

%package doc
Summary:        Julia documentation and code examples
Group:          Development/Other
BuildArch:      noarch
Requires:       julia = %{version}-%{release}

%description doc
Contains the Julia manual, the reference documentation of the standard library
and code examples.

%package devel
Summary:        Julia development, debugging and testing files
Group:          Development/Other
Requires:       julia%{?_isa} = %{version}-%{release}

%description devel
Contains library symbolic links and header files for developing applications
linking to the Julia library, in particular embedding it, as well as
tests and a debugging version of Julia. This package is normally not
needed when programming in the Julia language, but rather for embedding
Julia into external programs or debugging Julia itself.

%prep
%setup -q

mkdir -p deps/srccache

pushd deps/srccache
    # Julia downloads tarballs for external dependencies even when the folder is present:
    # we need to copy the tarball and let the build process unpack it
    # https://github.com/JuliaLang/julia/pull/10280
    cp -p %SOURCE1 .
#    cp -p %SOURCE3 .
    cp -p %SOURCE4 .
#    cp -p %SOURCE5 .
popd

# Required so that the image is not optimized for the build CPU
# (i386 does not work yet: https://github.com/JuliaLang/julia/issues/7185)
# Without specifying MARCH, the Julia system image would only work on native CPU
%ifarch %{ix86}
%global march pentium4
%endif
%ifarch x86_64
%global march x86-64
%endif
%ifarch %{arm}
# gcc and LLVM do not support the same targets
%global march $(echo %optflags | grep -Po 'march=\\K[^ ]*')
%endif
%ifarch armv7hl
%global march $(echo %optflags | grep -Po 'march=\\K[^ ]*')
%endif
%ifarch aarch64
%global march armv8-a
%endif

#global blas USE_BLAS64=0 LIBBLAS=-lopenblasp LIBBLASNAME=libopenblasp.so.0 LIBLAPACK=-lopenblasp LIBLAPACKNAME=libopenblasp.so.0
%global blas USE_ATLAS=1 ATLAS_LIBDIR=%{_libdir}/atlas

# About build, build_libdir and build_bindir, see https://github.com/JuliaLang/julia/issues/5063#issuecomment-32628111
%global julia_builddir %{_builddir}/%{name}/build
%global commonopts AT=%_bindir/ar CC=$CC CXX=$CXX USE_SYSTEM_LLVM=1 USE_LLVM_SHLIB=1 LLVM_CONFIG=%{_bindir}/llvm-config USE_SYSTEM_LIBUNWIND=0 USE_SYSTEM_READLINE=1 USE_SYSTEM_PCRE=0 USE_SYSTEM_OPENSPECFUN=1 USE_SYSTEM_BLAS=1 USE_SYSTEM_LAPACK=1 USE_SYSTEM_FFTW=1 USE_SYSTEM_GMP=1 USE_SYSTEM_MPFR=1 USE_SYSTEM_ARPACK=1 USE_SYSTEM_SUITESPARSE=1 USE_SYSTEM_ZLIB=1 USE_SYSTEM_GRISU=1 USE_SYSTEM_DSFMT=1 USE_SYSTEM_LIBUV=0 USE_SYSTEM_UTF8PROC=1 USE_SYSTEM_LIBGIT2=1 USE_SYSTEM_LIBSSH2=1 USE_SYSTEM_MBEDTLS=1 USE_SYSTEM_PATCHELF=1 USE_SYSTEM_LIBM=1 USE_SYSTEM_OPENLIBM=0 VERBOSE=1 MARCH=%{march} %{blas} prefix=%{_prefix} bindir=%{_bindir} libdir=%{_libdir} libexecdir=%{_libexecdir} datarootdir=%{_datarootdir} includedir=%{_includedir} sysconfdir=%{_sysconfdir} build_prefix=%{julia_builddir} build_bindir=%{julia_builddir}%{_bindir} build_libdir=%{julia_builddir}%{_libdir} build_private_libdir=%{julia_builddir}%{_libdir}/julia build_libexecdir=%{julia_builddir}%{_libexecdir} build_datarootdir=%{julia_builddir}%{_datarootdir} build_includedir=%{julia_builddir}%{_includedir} build_sysconfdir=%{julia_builddir}%{_sysconfdir} JULIA_CPU_CORES=$(echo %{?_smp_mflags} | sed s/-j//)

sed -i 's/-rcs/rcs/' src/support/Makefile src/flisp/Makefile
sed -i 's/-lLLVM/$(shell $(LLVM_CONFIG_HOST) --libs)/' src/Makefile
sed -i 's/extern int asprintf(char \*\*str, const char \*fmt, ...);//' src/init.c

%build
%ifarch %ix86
export CC=gcc
export CXX=g++
%endif

# Need to repeat -march here to override i686 from optflags
# USE_ORCJIT needs to be set directly since it's disabled by default with USE_SYSTEM_LLVM=1
%global buildflags CFLAGS="%{optflags} -march=%{march}" CXXFLAGS="%{optflags} -march=%{march}"

# If debug is not built here, it is built during make install
%make -j1 CC=$CC CXX=$CXX %{buildflags} %{commonopts} release debug

%check
# cb this fails to run on abf
#make CC=$CC CXX=$CXX %{commonopts} test

%install
make CC=$CC CXX=$CXX %{commonopts} DESTDIR=%{buildroot} install

# Julia currently needs the unversioned .so files:
# https://github.com/JuliaLang/julia/issues/6742
# By creating symlinks to versioned libraries, we hardcode a dependency
# on the specific SOVERSION so that any breaking update in one of the
# dependencies can be detected (just as what happens with the C linker).
# Automatic dependency detection is smart enough to add Requires as needed.
pushd %{buildroot}%{_libdir}/julia
    for LIB in arpack cholmod git2 fftw3 gmp mpfr umfpack
    do
        ln -s %{_libdir}/$(readelf -d %{_libdir}/lib$LIB.so | sed -n '/SONAME/s/.*\(lib[^ ]*\.so\.[0-9]*\).*/\1/p') lib$LIB.so
        # Raise an error in case of failure
        realpath -e lib$LIB.so
    done
popd

cp -p CONTRIBUTING.md LICENSE.md NEWS.md README.md %{buildroot}%{_docdir}/julia/

pushd %{buildroot}%{_prefix}/share/man/man1/
    ln -s julia.1.gz julia-debug.1.gz
popd

# Install .desktop file and icons
mkdir -p %{buildroot}%{_datarootdir}/icons/hicolor/scalable/apps/
mkdir -p %{buildroot}%{_datarootdir}/icons/hicolor/16x16/apps/
mkdir -p %{buildroot}%{_datarootdir}/icons/hicolor/24x24/apps/
mkdir -p %{buildroot}%{_datarootdir}/icons/hicolor/32x32/apps/
mkdir -p %{buildroot}%{_datarootdir}/icons/hicolor/48x48/apps/
mkdir -p %{buildroot}%{_datarootdir}/icons/hicolor/256x256/apps/
cp -p contrib/julia.svg %{buildroot}%{_datarootdir}/icons/hicolor/scalable/apps/%{name}.svg
convert -scale 16x16 -extent 16x16 -gravity center -background transparent \
    contrib/julia.svg %{buildroot}%{_datarootdir}/icons/hicolor/16x16/apps/%{name}.png
convert -scale 24x24 -extent 24x24 -gravity center -background transparent \
    contrib/julia.svg %{buildroot}%{_datarootdir}/icons/hicolor/24x24/apps/%{name}.png
convert -scale 32x32 -extent 32x32 -gravity center -background transparent \
    contrib/julia.svg %{buildroot}%{_datarootdir}/icons/hicolor/32x32/apps/%{name}.png
convert -scale 48x48 -extent 48x48 -gravity center -background transparent \
    contrib/julia.svg %{buildroot}%{_datarootdir}/icons/hicolor/48x48/apps/%{name}.png
convert -scale 256x256 -extent 256x256 -gravity center -background transparent \
    contrib/julia.svg %{buildroot}%{_datarootdir}/icons/hicolor/256x256/apps/%{name}.png
desktop-file-validate %{buildroot}%{_datarootdir}/applications/%{name}.desktop

%files
%{_bindir}/julia
%{_libdir}/julia/
%{_libdir}/libjulia.so.*
%exclude %{_libdir}/libjulia.so
%exclude %{_libdir}/libjulia-debug.so*
%{_mandir}/man1/julia.1*
%{_datarootdir}/appdata/julia.appdata.xml
%{_datarootdir}/applications/%{name}.desktop
%{_datarootdir}/icons/hicolor/scalable/apps/%{name}.svg
%{_datarootdir}/icons/hicolor/16x16/apps/%{name}.png
%{_datarootdir}/icons/hicolor/24x24/apps/%{name}.png
%{_datarootdir}/icons/hicolor/32x32/apps/%{name}.png
%{_datarootdir}/icons/hicolor/48x48/apps/%{name}.png
%{_datarootdir}/icons/hicolor/256x256/apps/%{name}.png

%files common
%dir %{_datarootdir}/julia/
%{_datarootdir}/julia/*.jl
%{_datarootdir}/julia/base/

%dir %{_sysconfdir}/julia/
%config(noreplace) %{_sysconfdir}/julia/juliarc.jl

%files doc
%doc %{_docdir}/julia/

%files devel
%{_bindir}/julia-debug
%{_libdir}/libjulia.so
%{_libdir}/libjulia-debug.so*
%{_includedir}/julia/
%{_datarootdir}/julia/test/
%{_mandir}/man1/julia-debug.1*
