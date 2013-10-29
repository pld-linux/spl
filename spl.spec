#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)
#
%if %{without kernel}
%undefine	with_dist_kernel
%endif

# The goal here is to have main, userspace, package built once with
# simple release number, and only rebuild kernel packages with kernel
# version as part of release number, without the need to bump release
# with every kernel change.
%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if "%{_alt_kernel}" != "%{nil}"
%if 0%{?build_kernels:1}
%{error:alt_kernel and build_kernels are mutually exclusive}
exit 1
%endif
%undefine	with_userspace
%global		_build_kernels		%{alt_kernel}
%else
%global		_build_kernels		%{?build_kernels:,%{?build_kernels}}
%endif

%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		_duplicate_files_terminate_build	0

%define		kbrs	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo "BuildRequires:kernel%%{_alt_kernel}-module-build >= 3:2.6.20.2" ; done)
%define		kpkg	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo %%kernel_pkg ; done)
%define		bkpkg	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo %%build_kernel_pkg ; done)

%define		pname	spl
%define		rel	6
Summary:	Solaris Porting Layer
Summary(pl.UTF-8):	Solaris Porting Layer - warstwa do portowania kodu z Solarisa
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	0.6.2
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	GPL v2+
Group:		Applications/System
Source0:	http://archive.zfsonlinux.org/downloads/zfsonlinux/spl/%{pname}-%{version}.tar.gz
# Source0-md5:	f00535bf89a7fde0e08f44a14a1f1e03
URL:		http://zfsonlinux.org/
BuildRequires:	rpmbuild(macros) >= 1.678
%{?with_dist_kernel:%{expand:%kbrs}}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Solaris Porting Layer.

%description -l pl.UTF-8
Solaris Porting Layer - warstwa do portowania kodu z Solarisa.

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-spl\
Summary:	Solaris Porting Layer - Linux kernel modules\
Summary(pl.UTF-8):	Solaris Porting Layer - moduły jądra Linuksa\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%if %{with dist_kernel}\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
%endif\
\
%description -n kernel%{_alt_kernel}-spl\
Solaris Porting Layer - Linux kernel modules.\
\
%description -n kernel%{_alt_kernel}-spl -l pl.UTF-8\
Solaris Porting Layer - moduły jądra Linuksa.\
\
%package -n kernel%{_alt_kernel}-spl-devel\
Summary:	Solaris Porting Layer - Linux kernel headers\
Summary(pl.UTF-8):	Solaris Porting Layer - pliki nagłówkowe jądra Linuksa\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Development/Building\
%{?with_dist_kernel:Requires:	kernel%{_alt_kernel}-headers}\
\
%description -n kernel%{_alt_kernel}-spl-devel\
Solaris Porting Layer - Linux kernel headers configured for PLD\
kernel%{_alt_kernel}, version %{_kernel_ver}.\
\
%description -n kernel%{_alt_kernel}-spl-devel -l pl.UTF-8\
Solaris Porting Layer - pliki nagłówkowe jądra Linuksa skonfigurowane\
dla jądra PLD z pakietu kernel%{_alt_kernel} w wersji %{_kernel_ver}.\
\
%files -n kernel%{_alt_kernel}-spl\
%defattr(644,root,root,755)\
%dir /lib/modules/%{_kernel_ver}/misc/spl\
/lib/modules/%{_kernel_ver}/misc/spl/spl.ko*\
%dir /lib/modules/%{_kernel_ver}/misc/splat\
/lib/modules/%{_kernel_ver}/misc/splat/splat.ko*\
\
%files -n kernel%{_alt_kernel}-spl-devel\
%defattr(644,root,root,755)\
%dir /usr/src/spl-%{version}\
/usr/src/spl-%{version}/spl*.in\
/usr/src/spl-%{version}/include\
/usr/src/spl-%{version}/%{_kernel_ver}\
\
%post	-n kernel%{_alt_kernel}-spl\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-spl\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%configure \\\
	--disable-silent-rules \\\
	--with-config="kernel" \\\
	--with-linux=%{_kernelsrcdir}\
\
%{__make} clean\
%{__make} %{?with_verbose:V=1}\
p=`pwd`\
%{__make} install DESTDIR=$p/installed INSTALL_MOD_DIR=misc\
%{nil}

%{?with_kernel:%{expand:%kpkg}}

%prep
%setup -q -n %{pname}-%{version}

%build
%{?with_kernel:%{expand:%bkpkg}}

%if %{with userspace}
%configure \
	--disable-silent-rules \
	--with-config="user"

%{__make} \
	%{?with_verbose:V=1}
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT
cp -a installed/* $RPM_BUILD_ROOT
%endif

%if %{with userspace}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc AUTHORS DISCLAIMER
%attr(755,root,root) %{_sbindir}/splat
%{_mandir}/man1/splat.1*
%endif
