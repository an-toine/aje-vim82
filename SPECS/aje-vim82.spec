# Define common SCL variables
%global scl_vendor aje
%global _scl_prefix /opt/%{scl_vendor}
%global scl_name_prefix aje-
%global scl_name_base vim
%global scl_name_version 82

%global scl %{scl_name_prefix}%{scl_name_base}%{scl_name_version}

# Disable debug packages
%global debug_package %{nil}

# Define SCL macros
%scl_package %scl

# SCL package metadatas
Summary: Package that install %{scl} Software Collection
Name: %scl_name
Version: 1
Release: 1%{dist}
License: GPLv2+
Group: Applications/File
Source0: README.md
Source1: LICENSE

Requires: scl-utils

BuildRequires: scl-utils-build

%description
This package is the metapackage for scl %{scl} which installs all required dependancies
to use package %{scl_name_base}.

%package runtime
Summary: Package installing %{scl} activation scripts
Group: Applications/File
Requires: scl-utils

%description runtime
Package installing essential activation script to use %{scl}.

%package build
Summary: Package installing basic build conf for %{scl}
Group: Development/Libraries
Requires: scl-utils-build

%description build
Package installing configuration macros to build %{scl} Software Collection

%package scldevel
Summary: Package development files for %{scl}
Group: Development/Libraries

%description scldevel
Package development files for %{scl} Software Collection

# Prepare metapackage build
%prep

# Sources should not be uncompressed and are not in a subdirectory
%setup -c -T

# Copy in current working directory License and Readme files
cp %{SOURCE0} .
cp %{SOURCE1} .

%build
echo "No build required"

%install
%scl_install

# Generate enable file
cat <<'EOF' | tee -a %{buildroot}%{_scl_scripts}/enable
export PATH="%{_bindir}:%{_sbindir}${PATH:+:${PATH}}"
export LD_LIBRARY_PATH="%{_libdir}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
export LIBRARY_PATH="%{_libdir}${LIBRARY_PATH:+:${LIBRARY_PATH}}"
export MANPATH="%{_mandir}:${MANPATH:-}"
export PKG_CONFIG_PATH="%{_libdir}/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}"
export XDG_CONFIG_DIRS="%{_sysconfdir}/xdg:${XDG_CONFIG_DIRS:-/etc/xdg}"
export XDG_DATA_DIRS="%{_datadir}${XDG_DATA_DIRS:+:${XDG_DATA_DIRS}}"
EOF

# Generate rpm macros file
cat << 'EOF' | tee -a %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

# Create register/unregister scripts skeleton
mkdir -p %{buildroot}%{?_scl_scripts}/register.content
mkdir -p %{buildroot}%{?_scl_scripts}/register.d

cat <<EOF | tee %{buildroot}%{?_scl_scripts}/register
#!/bin/sh
ls %{?_scl_scripts}/register.d/* | while read file ; do
    [ -x \$f ] && source \$(readlink -f \$file)
done
EOF

mkdir -p %{buildroot}%{?_scl_scripts}/deregister.d
cat <<EOF | tee %{buildroot}%{?_scl_scripts}/deregister
#!/bin/sh
ls %{?_scl_scripts}/deregister.d/* | while read file ; do
    [ -x \$f ] && source \$(readlink -f \$file)
done
EOF

# Copy root SElinux perms to SCL hierarchy
cat <<EOF | tee %{buildroot}%{?_scl_scripts}/register.d/30.selinux-set
#!/bin/sh
semanage fcontext -a -e / %{?_scl_root} >/dev/null 2>&1 || :
semanage fcontext -a -e %{_root_sysconfdir} %{_sysconfdir} >/dev/null 2>&1 || :
semanage fcontext -a -e %{_root_localstatedir} %{_localstatedir} >/dev/null 2>&1 || :
selinuxenabled && load_policy || :
EOF
cat <<EOF | tee %{buildroot}%{?_scl_scripts}/register.d/70.selinux-restore
restorecon -R %{?_scl_root} >/dev/null 2>&1 || :
restorecon -R %{_sysconfdir} >/dev/null 2>&1 || :
restorecon -R %{_localstatedir} >/dev/null 2>&1 || :
EOF

mkdir -p %{buildroot}%{?_scl_scripts}/register.content%{_unitdir}
mkdir -p %{buildroot}%{?_scl_scripts}/register.content%{_sysconfdir}

%post runtime
# When installing SCL, run manually SElinux scripts
%{?_scl_scripts}/register.d/30.selinux-set
%{?_scl_scripts}/register.d/70.selinux-restore

%files

%files runtime -f filelist
%scl_files
%doc README.md LICENSE
%attr(0755,root,root) %{?_scl_scripts}/register
%attr(0755,root,root) %{?_scl_scripts}/deregister
%{?_scl_scripts}/register.content
%dir %{?_scl_scripts}/register.d
%dir %{?_scl_scripts}/deregister.d
%attr(0755,root,root) %{?_scl_scripts}/register.d/*

%files build
%doc LICENSE
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Sun Dec 13 2020 Antoine Jouve <ant.jouve@gmail.com> 1.1
- First go at building %{scl} metapackage
