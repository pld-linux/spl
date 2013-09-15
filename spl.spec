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
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif
Summary:	Solaris Porting Layer
Summary(pl.UTF-8):	Solaris Porting Layer - warstwa do portowania kodu z Solarisa
%define	pname	spl
Name:		%{pname}%{_alt_kernel}
Version:	0.6.2
%define	rel	1
Release:	%{rel}
License:	GPL v2+
Group:		Applications/System
Source0:	http://archive.zfsonlinux.org/downloads/zfsonlinux/spl/%{pname}-%{version}.tar.gz
# Source0-md5:	f00535bf89a7fde0e08f44a14a1f1e03
URL:		http://zfsonlinux.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Solaris Porting Layer.

%description -l pl.UTF-8
Solaris Porting Layer - warstwa do portowania kodu z Solarisa.

%package -n kernel%{_alt_kernel}-spl
Summary:	Solaris Porting Layer - Linux kernel modules
Summary(pl.UTF-8):	Solaris Porting Layer - moduły jądra Linuksa
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-spl
Solaris Porting Layer - Linux kernel modules.

%description -n kernel%{_alt_kernel}-spl -l pl.UTF-8
Solaris Porting Layer - moduły jądra Linuksa.

%package -n kernel%{_alt_kernel}-spl-devel
Summary:	Solaris Porting Layer - Linux kernel headers
Summary(pl.UTF-8):	Solaris Porting Layer - pliki nagłówkowe jądra Linuksa
Release:	%{rel}@%{_kernel_ver_str}
Group:		Development/Building
%{?with_dist_kernel:Requires:	kernel%{_alt_kernel}-headers}

%description -n kernel%{_alt_kernel}-spl-devel
Solaris Porting Layer - Linux kernel headers configured for PLD
kernel%{_alt_kernel}, version %{_kernel_ver}.

%description -n kernel%{_alt_kernel}-spl-devel -l pl.UTF-8
Solaris Porting Layer - pliki nagłówkowe jądra Linuksa skonfigurowane
dla jądra PLD z pakietu kernel%{_alt_kernel} w wersji %{_kernel_ver}.

%prep
%setup -q

%build
%configure \
	--disable-silent-rules \
	--with-config="%{?with_kernel:%{?with_userspace:all}}%{!?with_kernel:user}%{!?with_userspace:kernel}" \
	--with-linux=%{_kernelsrcdir}

%{__make} \
	%{?with_verbose:V=1}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	INSTALL_MOD_DIR=misc

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc AUTHORS DISCLAIMER
%attr(755,root,root) %{_sbindir}/splat
%{_mandir}/man1/splat.1*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-spl
%defattr(644,root,root,755)
%dir /lib/modules/%{_kernel_ver}/misc/spl
/lib/modules/%{_kernel_ver}/misc/spl/spl.ko*
%dir /lib/modules/%{_kernel_ver}/misc/splat
/lib/modules/%{_kernel_ver}/misc/splat/splat.ko*

%files -n kernel%{_alt_kernel}-spl-devel
%defattr(644,root,root,755)
/usr/src/spl-%{version}
%endif
