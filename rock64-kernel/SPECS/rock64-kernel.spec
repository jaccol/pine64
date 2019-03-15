%global commit_linux_long  b086cfdc8327f0239f82a5edba1a09a08b1d72ea
%global commit_linux_short %(c=%{commit_linux_long}; echo ${c:0:7})

%define Arch arm64
%define extra_version 2
%define _binaries_in_noarch_packages_terminate_build 0
%define debug_package %{nil}

Name:           rock64-kernel
Version:        4.4.132
Release:        %{extra_version}%{?dist}
BuildArch:	noarch
Summary:        Specific kernel for Rock64

License:        GPLv2
URL:            https://github.com/ayufan-rock64/linux-kernel
Source0:        https://github.com/ayufan-rock64/linux-kernel/tarball/%{commit_linux_long}

Group:          System Environment/Kernel
Provides:       kernel = %{version}-%{release}
Requires:       dracut, coreutils, linux-firmware
BuildRequires:	hostname, bc, python, openssl-devel, lzop

# Compile with SELinux but disable per default
#Patch0:		rock64_selinux_config.patch

%description
Specific kernel for Rock64
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


%package devel
Group:          System Environment/Kernel
Summary:        Development package for building kernel modules to match the kernel
Provides:       kernel-devel = %{version}-%{release}

%description devel
This package provides kernel headers and makefiles sufficient to build modules
against the kernel package.


%prep
%setup -q -n ayufan-rock64-linux-kernel-%{commit_linux_short}
#%patch0 -p1
perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}/" Makefile

%build
export KERNEL=kernel
make rockchip_linux_defconfig
make %{?_smp_mflags} Image modules dtbs

%install
# kernel
mkdir -p %{buildroot}/boot/
mkdir -p %{buildroot}/usr/share/%{name}-kernel/%{version}-%{release}/boot/overlays
cp -p -v COPYING %{buildroot}/boot/COPYING.linux
cp -p -v arch/%{Arch}/boot/dts/rockchip/*.dtb %{buildroot}/usr/share/%{name}-kernel/%{version}-%{release}/boot
cp -p -v arch/%{Arch}/boot/Image %{buildroot}/boot/Image-%{version}-%{release}
make INSTALL_MOD_PATH=%{buildroot} modules_install
rm -rf %{buildroot}/lib/firmware

# kernel-devel
DevelDir=/usr/src/kernels/%{version}-%{release}
mkdir -p %{buildroot}$DevelDir
# first copy everything
cp -p -v Module.symvers System.map %{buildroot}$DevelDir
cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` %{buildroot}$DevelDir
# then drop all but the needed Makefiles/Kconfig files
rm -rf %{buildroot}$DevelDir/Documentation
rm -rf %{buildroot}$DevelDir/scripts
rm -rf %{buildroot}$DevelDir/include
cp .config %{buildroot}$DevelDir
cp -a scripts %{buildroot}$DevelDir
cp -a include %{buildroot}$DevelDir

if [ -d arch/$Arch/scripts ]; then
  cp -a arch/$Arch/scripts %{buildroot}$DevelDir/arch/%{_arch} || :
fi
if [ -f arch/$Arch/*lds ]; then
  cp -a arch/$Arch/*lds %{buildroot}$DevelDir/arch/%{_arch}/ || :
fi
rm -f %{buildroot}$DevelDir/scripts/*.o
rm -f %{buildroot}$DevelDir/scripts/*/*.o
cp -a --parents arch/%{Arch}/include %{buildroot}$DevelDir
# include the machine specific headers for ARM variants, if available.
if [ -d arch/%{Arch}/mach-rockchip/include ]; then
  cp -a --parents arch/%{Arch}/mach-rockchip/include %{buildroot}$DevelDir
fi
cp include/generated/uapi/linux/version.h %{buildroot}$DevelDir/include/linux
touch -r %{buildroot}$DevelDir/Makefile %{buildroot}$DevelDir/include/linux/version.h
ln -T -s $DevelDir %{buildroot}/lib/modules/%{version}-%{release}/build --force
ln -T -s build %{buildroot}/lib/modules/%{version}-%{release}/source --force

%files
%defattr(-,root,root,-)
/lib/modules/%{version}-%{release}
/usr/share/%{name}-kernel/%{version}-%{release}
/usr/share/%{name}-kernel/%{version}-%{release}/boot
/usr/share/%{name}-kernel/%{version}-%{release}/boot/rk3328-rock64.dtb
%attr(0755,root,root) /boot/Image-%{version}-%{release}
%doc /boot/COPYING.linux

%post
cp /boot/Image-%{version}-%{release} /boot/Image
cp /usr/share/%{name}-kernel/%{version}-%{release}/boot/rk3328-rock64.dtb /boot/dtb
/usr/sbin/depmod -a %{version}-%{release}
dracut /boot/initrd.img-%{version}-%{release} %{version}-%{release}
cp /boot/initrd.img-%{version}-%{release} /boot/initrd.img

%preun
rm -f /boot/initrd.img-%{version}-%{release}

%postun
cp $(ls -1 /boot/Image-*-*|tail -1) /boot/Image
cp $(ls -1d /usr/share/%{name}-kernel/*-*/|tail -1)/boot/rk3328-rock64.dtb /boot/dtb


%files devel
%defattr(-,root,root)
/usr/src/kernels/%{version}-%{release}


%changelog
* Fri Jun 15 2018 Jacco Ligthart <jacco@redsleeve.org> - 4.4.132-2.el7
- update to latest git, which is now 'release' version in stead of 'pre-release'

* Fri Jun 15 2018 Jacco Ligthart <jacco@redsleeve.org> - 4.4.132-1.el7
- update to latest git

* Mon May 28 2018 Jacco Ligthart <jacco@redsleeve.org> - 4.4.126-1.el7
- update to latest git

* Tue Apr 03 2018 Jacco Ligthart <jacco@redsleeve.org> - 4.4.120-1.el7
- update to latest git

* Mon Mar 05 2018 Jacco Ligthart <jacco@redsleeve.org> - 4.4.114-1.el7
- update to latest git

* Tue Feb 20 2018 Jacco Ligthart <jacco@redsleeve.org> - 4.4.112-1.el7
- update to latest git

* Mon Jan 29 2018 Jacco Ligthart <jacco@redsleeve.org> - 4.4.103-2.el7
- update to latest git

* Tue Dec 19 2017 Jacco Ligthart <jacco@redsleeve.org> - 4.4.103-1.el7
- updated to version 4.4.103

* Fri Dec 01 2017 Jacco Ligthart <jacco@redsleeve.org> - 4.4.77-1.el7
- initial release for Rock64
