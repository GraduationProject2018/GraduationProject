%global _hardened_build 1

%global _for_fedora_koji_builds 0

# uncomment and add '%' to use the prereltag for pre-releases
# %%global prereltag beta2

##-----------------------------------------------------------------------------
## All argument definitions should be placed here and keep them sorted
##

# if you wish to compile an rpm without rdma support, compile like this...
# rpmbuild -ta glusterfs-3.6.9.tar.gz --without rdma
%{?_without_rdma:%global _without_rdma --disable-ibverbs}

# No RDMA Support on s390(x)
%ifarch s390 s390x
%global _without_rdma --disable-ibverbs
%endif

# if you wish to compile an rpm without epoll...
# rpmbuild -ta glusterfs-3.6.9.tar.gz --without epoll
%{?_without_epoll:%global _without_epoll --disable-epoll}

# if you wish to compile an rpm without fusermount...
# rpmbuild -ta glusterfs-3.6.9.tar.gz --without fusermount
%{?_without_fusermount:%global _without_fusermount --disable-fusermount}

# if you wish to compile an rpm without geo-replication support, compile like this...
# rpmbuild -ta glusterfs-3.6.9.tar.gz --without georeplication
%{?_without_georeplication:%global _without_georeplication --disable-georeplication}

# Disable geo-replication on EL5, as its default Python is too old
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_georeplication --disable-georeplication
%endif

# if you wish to compile an rpm without the OCF resource agents...
# rpmbuild -ta glusterfs-3.6.9.tar.gz --without ocf
%{?_without_ocf:%global _without_ocf --without-ocf}

# if you wish to build rpms without syslog logging, compile like this
# rpmbuild -ta glusterfs-3.6.9.tar.gz --without syslog
%{?_without_syslog:%global _without_syslog --disable-syslog}

# disable syslog forcefully as rhel <= 6 doesn't have rsyslog or rsyslog-mmcount
# Fedora deprecated syslog, see
#  https://fedoraproject.org/wiki/Changes/NoDefaultSyslog
# (And what about RHEL7?)
%if ( 0%{?fedora} && 0%{?fedora} >= 20 ) || ( 0%{?rhel} && 0%{?rhel} <= 6 )
%global _without_syslog --disable-syslog
%endif

# if you wish to compile an rpm without the BD map support...
# rpmbuild -ta glusterfs-3.6.9.tar.gz --without bd
%{?_without_bd:%global _without_bd --disable-bd-xlator}

%if ( 0%{?rhel} && 0%{?rhel} < 6 || 0%{?sles_version} )
%define _without_bd --disable-bd-xlator
%endif

# if you wish to compile an rpm without the qemu-block support...
# rpmbuild -ta glusterfs-3.6.9.tar.gz --without qemu-block
%{?_without_qemu_block:%global _without_qemu_block --disable-qemu-block}

%if ( 0%{?rhel} && 0%{?rhel} < 6 )
# xlators/features/qemu-block fails to build on RHEL5, disable it
%define _without_qemu_block --disable-qemu-block
%endif

##-----------------------------------------------------------------------------
## All %global definitions should be placed here and keep them sorted
##

%if ( 0%{?fedora} && 0%{?fedora} > 16 ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
%global _with_systemd true
%endif

# there is no systemtap support! Perhaps some day there will be
%global _without_systemtap --enable-systemtap=no

# From https://fedoraproject.org/wiki/Packaging:Python#Macros
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
%{!?python_sitelib: %global python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%if ( 0%{?_with_systemd:1} )
%define _init_enable()  /bin/systemctl enable %1.service ;
%define _init_disable() /bin/systemctl disable %1.service ;
%define _init_restart() /bin/systemctl try-restart %1.service ;
%define _init_start()   /bin/systemctl start %1.service ;
%define _init_stop()    /bin/systemctl stop %1.service ;
%define _init_install() install -D -p -m 0644 %1 %{buildroot}%{_unitdir}/%2.service ;
# can't seem to make a generic macro that works
%define _init_glusterd   %{_unitdir}/glusterd.service
%define _init_glusterfsd %{_unitdir}/glusterfsd.service
%else
%define _init_enable()  /sbin/chkconfig --add %1 ;
%define _init_disable() /sbin/chkconfig --del %1 ;
%define _init_restart() /sbin/service %1 condrestart &>/dev/null ;
%define _init_start()   /sbin/service %1 start &>/dev/null ;
%define _init_stop()    /sbin/service %1 stop &>/dev/null ;
%define _init_install() install -D -p -m 0755 %1 %{buildroot}%{_sysconfdir}/init.d/%2 ;
# can't seem to make a generic macro that works
%define _init_glusterd   %{_sysconfdir}/init.d/glusterd
%define _init_glusterfsd %{_sysconfdir}/init.d/glusterfsd
%endif

%if ( 0%{_for_fedora_koji_builds} )
%if ( 0%{?_with_systemd:1} )
%global glusterfsd_service glusterfsd.service
%else
%global glusterfsd_service glusterfsd.init
%endif
%endif

%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

%if ( 0%{?rhel} && 0%{?rhel} < 6 )
   # _sharedstatedir is not provided by RHEL5
   %define _sharedstatedir /var/lib
%endif

# We do not want to generate useless provides and requires for xlator
# .so files to be set for glusterfs packages.
# Filter all generated:
#
# TODO: RHEL5 does not have a convenient solution
%if ( 0%{?rhel} == 6 )
    # filter_setup exists in RHEL6 only
    %filter_provides_in %{_libdir}/glusterfs/%{version}/
    %global __filter_from_req %{?__filter_from_req} | grep -v -P '^(?!lib).*\.so.*$'
    %filter_setup
%else
    # modern rpm and current Fedora do not generate requires when the
    # provides are filtered
    %global __provides_exclude_from ^%{_libdir}/glusterfs/%{version}/.*$
%endif


##-----------------------------------------------------------------------------
## All package definitions should be placed here and keep them sorted
##
Summary:          Cluster File System
%if ( 0%{_for_fedora_koji_builds} )
Name:             glusterfs
Version:          3.6.0
Release:          0.3%{?prereltag:.%{prereltag}}%{?dist}
Vendor:           Fedora Project
%else
Name:             glusterfs
Version:          3.6.9
Release:          0.0%{?dist}
Vendor:           glusterfs.org
%endif
License:          GPLv2 or LGPLv3+
Group:            System Environment/Base
URL:              http://www.gluster.org/docs/index.php/GlusterFS
%if ( 0%{_for_fedora_koji_builds} )
Source0:          http://bits.gluster.org/pub/gluster/glusterfs/src/glusterfs-%{version}%{?prereltag}.tar.gz
Source1:          glusterd.sysconfig
Source2:          glusterfsd.sysconfig
Source3:          glusterfs-fuse.logrotate
Source4:          glusterd.logrotate
Source5:          glusterfsd.logrotate
Source6:          rhel5-load-fuse-modules
Source7:          glusterfsd.service
Source8:          glusterfsd.init
%else
Source0:          glusterfs-3.6.9.tar.gz
%endif

BuildRoot:        %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
BuildRequires:    python-simplejson
%endif
%if ( 0%{?_with_systemd:1} )
BuildRequires:    systemd-units
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%else
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/service
Requires(preun):  /sbin/chkconfig
Requires(postun): /sbin/service
%endif

Requires:         %{name}-libs%{?_isa} = %{version}-%{release}
BuildRequires:    bison flex
BuildRequires:    gcc make automake libtool
BuildRequires:    ncurses-devel readline-devel
BuildRequires:    libxml2-devel openssl-devel
BuildRequires:    libaio-devel
BuildRequires:    python-devel
BuildRequires:    python-ctypes
%if ( 0%{!?_without_systemtap:1} )
BuildRequires:    systemtap-sdt-devel
%endif
%if ( 0%{!?_without_bd:1} )
BuildRequires:    lvm2-devel
%endif
%if ( 0%{!?_without_qemu_block:1} )
BuildRequires:    glib2-devel
%endif
%if ( 0%{!?_without_georeplication:1} )
BuildRequires:    libattr-devel
%endif

Obsoletes:        hekafs
Obsoletes:        %{name}-common < %{version}-%{release}
Obsoletes:        %{name}-core < %{version}-%{release}
Obsoletes:        %{name}-ufo
Provides:         %{name}-common = %{version}-%{release}
Provides:         %{name}-core = %{version}-%{release}

%description
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package includes the glusterfs binary, the glusterfsd daemon and the
gluster command line, libglusterfs and glusterfs translator modules common to
both GlusterFS server and client framework.

%package api
Summary:          Clustered file-system api library
Group:            System Environment/Daemons
Requires:         %{name}%{?_isa} = %{version}-%{release}
# we provide the Python package/namespace 'gluster'
Provides:         python-gluster = %{version}-%{release}

%description api
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the glusterfs libgfapi library.

%package api-devel
Summary:          Development Libraries
Group:            Development/Libraries
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-devel%{?_isa} = %{version}-%{release}

%description api-devel
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the api include files.

%package cli
Summary:          GlusterFS CLI
Group:            Applications/File
Requires:         %{name}-libs%{?_isa} = %{version}-%{release}

%description cli
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the GlusterFS CLI application and its man page

%package devel
Summary:          Development Libraries
Group:            Development/Libraries
Requires:         %{name}%{?_isa} = %{version}-%{release}
# Needed for the Glupy examples to work
Requires:         %{name}-extra-xlators%{?_isa} = %{version}-%{release}

%description devel
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the development libraries and include files.

%package extra-xlators
Summary:          Extra Gluster filesystem Translators
Group:            Applications/File
# We need -api rpm for its __init__.py in Python site-packages area
Requires:         %{name}-api%{?_isa} = %{version}-%{release}
Requires:         python python-ctypes

%description extra-xlators
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides extra filesystem Translators, such as Glupy,
for GlusterFS.

%package fuse
Summary:          Fuse client
Group:            Applications/File
BuildRequires:    fuse-devel

Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         attr

Obsoletes:        %{name}-client < %{version}-%{release}
Provides:         %{name}-client = %{version}-%{release}

%description fuse
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides support to FUSE based clients.

%if ( 0%{!?_without_georeplication:1} )
%package geo-replication
Summary:          GlusterFS Geo-replication
Group:            Applications/File
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-server%{?_isa} = %{version}-%{release}
Requires:         python python-ctypes

%description geo-replication
GlusterFS is a distributed file-system capable of scaling to several
peta-bytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file system in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in userspace and easily manageable.

This package provides support to geo-replication.
%endif

%package libs
Summary:          GlusterFS common libraries
Group:            Applications/File
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
Requires:         rsyslog-mmjsonparse
%endif
%if ( 0%{?rhel} && 0%{?rhel} == 6 )
Requires:         rsyslog-mmcount
%endif
%endif

%description libs
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the base GlusterFS libraries

%if ( 0%{!?_without_rdma:1} )
%package rdma
Summary:          GlusterFS rdma support for ib-verbs
Group:            Applications/File
BuildRequires:    libibverbs-devel
BuildRequires:    librdmacm-devel
Requires:         %{name} = %{version}-%{release}

%description rdma
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides support to ib-verbs library.
%endif

%package regression-tests
Summary:          Development Tools
Group:            Development/Tools
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-fuse%{?_isa} = %{version}-%{release}
Requires:         %{name}-server%{?_isa} = %{version}-%{release}
## thin provisioning support
Requires:         lvm2 >= 2.02.89
Requires:         perl(App::Prove) perl(Test::Harness) gcc util-linux-ng
Requires:         python attr dbench file git libacl-devel mock net-tools
Requires:         nfs-utils xfsprogs yajl

%description regression-tests
The Gluster Test Framework, is a suite of scripts used for
regression testing of Gluster.

%if ( 0%{!?_without_ocf:1} )
%package resource-agents
Summary:          OCF Resource Agents for GlusterFS
License:          GPLv3+
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 || 0%{?sles_version} ) )
# EL5 does not support noarch sub-packages
BuildArch:        noarch
%endif
# this Group handling comes from the Fedora resource-agents package
%if ( 0%{?fedora} || 0%{?centos_version} || 0%{?rhel} )
Group:            System Environment/Base
%else
Group:            Productivity/Clustering/HA
%endif
# for glusterd
Requires:         %{name}-server%{?_isa} = %{version}-%{release}
# depending on the distribution, we need pacemaker or resource-agents
Requires:         %{_prefix}/lib/ocf/resource.d

%description resource-agents
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the resource agents which plug glusterd into
Open Cluster Framework (OCF) compliant cluster resource managers,
like Pacemaker.
%endif

%package server
Summary:          Clustered file-system server
Group:            System Environment/Daemons
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-cli%{?_isa} = %{version}-%{release}
Requires:         %{name}-libs%{?_isa} = %{version}-%{release}
Requires:         %{name}-fuse%{?_isa} = %{version}-%{release}
Requires:         %{name}-api%{?_isa} = %{version}-%{release}
# psmisc for killall, lvm2 for snapshot, and nfs-utils and
# rpcbind/portmap for gnfs server
Requires:         psmisc
Requires:         lvm2
Requires:         nfs-utils
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
Requires:         rpcbind
%else
Requires:         portmap
%endif
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
Obsoletes:        %{name}-geo-replication = %{version}-%{release}
%endif

%description server
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the glusterfs server daemon.

%prep
%setup -q -n %{name}-%{version}%{?prereltag}

%build
# For whatever reason, install-sh is sometimes missing. When this gets fixed,
# there is no need to run ./autogen or have a BuildRequires for automake.
[ -e 'install-sh' -o -e 'install.sh' ] || ./autogen.sh
%configure \
        %{?_without_rdma} \
        %{?_without_epoll} \
        %{?_without_fusermount} \
        %{?_without_georeplication} \
        %{?_without_ocf} \
        %{?_without_syslog} \
        %{?_without_bd} \
        %{?_without_qemu_block} \
        %{?_without_systemtap}

# fix hardening and remove rpath in shlibs
%if ( 0%{?fedora} && 0%{?fedora} > 17 ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
sed -i 's| \\\$compiler_flags |&\\\$LDFLAGS |' libtool
%endif
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|' libtool

make %{?_smp_mflags}

# Build Glupy
pushd xlators/features/glupy/src
FLAGS="$RPM_OPT_FLAGS" python setup.py build
popd

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
# install the Glupy Python library in /usr/lib/python*/site-packages
pushd xlators/features/glupy/src
python setup.py install --skip-build --verbose --root %{buildroot}
popd
# Install include directory
mkdir -p %{buildroot}%{_includedir}/glusterfs
install -p -m 0644 libglusterfs/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/
install -p -m 0644 contrib/uuid/*.h \
    %{buildroot}%{_includedir}/glusterfs/
# Following needed by hekafs multi-tenant translator
mkdir -p %{buildroot}%{_includedir}/glusterfs/rpc
install -p -m 0644 rpc/rpc-lib/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/rpc/
install -p -m 0644 rpc/xdr/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/rpc/
mkdir -p %{buildroot}%{_includedir}/glusterfs/server
install -p -m 0644 xlators/protocol/server/src/*.h \
    %{buildroot}%{_includedir}/glusterfs/server/
%if ( 0%{_for_fedora_koji_builds} )
install -D -p -m 0644 %{SOURCE1} \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterd
install -D -p -m 0644 %{SOURCE2} \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterfsd
%else
install -D -p -m 0644 extras/glusterd-sysconfig \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterd
%endif

%if ( 0%{_for_fedora_koji_builds} )
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
install -D -p -m 0755 %{SOURCE6} \
    %{buildroot}%{_sysconfdir}/sysconfig/modules/glusterfs-fuse.modules
%endif
%endif

mkdir -p %{buildroot}%{_localstatedir}/log/glusterd
mkdir -p %{buildroot}%{_localstatedir}/log/glusterfs
mkdir -p %{buildroot}%{_localstatedir}/log/glusterfsd
mkdir -p %{buildroot}%{_localstatedir}/run/gluster

# Remove unwanted files from all the shared libraries
find %{buildroot}%{_libdir} -name '*.a' -delete
find %{buildroot}%{_libdir} -name '*.la' -delete

# Remove installed docs, the ones we want are included by %%doc, in
# /usr/share/doc/glusterfs or /usr/share/doc/glusterfs-x.y.z depending
# on the distribution
%if ( 0%{?fedora} && 0%{?fedora} > 19 ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
rm -rf %{buildroot}%{_pkgdocdir}/*
%else
rm -rf %{buildroot}%{_defaultdocdir}/%{name}
mkdir -p %{buildroot}%{_pkgdocdir}
%endif
head -50 ChangeLog > ChangeLog.head && mv ChangeLog.head ChangeLog
cat << EOM >> ChangeLog

More commit messages for this ChangeLog can be found at
https://forge.gluster.org/glusterfs-core/glusterfs/commits/v%{version}%{?prereltag}
EOM

# Remove benchmarking and other unpackaged files
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
rm -rf %{buildroot}/benchmarking
rm -f %{buildroot}/glusterfs-mode.el
rm -f %{buildroot}/glusterfs.vim
%else
# make install always puts these in %%{_defaultdocdir}/%%{name} so don't
# use %%{_pkgdocdir}; that will be wrong on later Fedora distributions
rm -rf %{buildroot}%{_defaultdocdir}/%{name}/benchmarking
rm -f %{buildroot}%{_defaultdocdir}/%{name}/glusterfs-mode.el
rm -f %{buildroot}%{_defaultdocdir}/%{name}/glusterfs.vim
%endif

# Create working directory
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd

# Update configuration file to /var/lib working directory
sed -i 's|option working-directory /etc/glusterd|option working-directory %{_sharedstatedir}/glusterd|g' \
    %{buildroot}%{_sysconfdir}/glusterfs/glusterd.vol

# Install glusterfsd .service or init.d file
%if ( 0%{_for_fedora_koji_builds} )
%_init_install %{glusterfsd_service} glusterfsd
%endif

%if ( 0%{_for_fedora_koji_builds} )
# Client logrotate entry
install -D -p -m 0644 %{SOURCE3} \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs-fuse

# Server logrotate entry
install -D -p -m 0644 %{SOURCE4} \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterd
# Legacy server logrotate entry
install -D -p -m 0644 %{SOURCE5} \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfsd
%else
install -D -p -m 0644 extras/glusterfs-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs
%endif

%if ( 0%{!?_without_georeplication:1} )
# geo-rep ghosts
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/geo-replication
touch %{buildroot}%{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
install -D -p -m 0644 extras/glusterfs-georep-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs-georep
%endif

%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
install -D -p -m 0644 extras/gluster-rsyslog-7.2.conf \
    %{buildroot}%{_sysconfdir}/rsyslog.d/gluster.conf.example
%endif

%if ( 0%{?rhel} && 0%{?rhel} == 6 )
install -D -p -m 0644 extras/gluster-rsyslog-5.8.conf \
    %{buildroot}%{_sysconfdir}/rsyslog.d/gluster.conf.example
%endif

%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
install -D -p -m 0644 extras/logger.conf.example \
    %{buildroot}%{_sysconfdir}/glusterfs/logger.conf.example
%endif
%endif

# the rest of the ghosts
touch %{buildroot}%{_sharedstatedir}/glusterd/glusterd.info
touch %{buildroot}%{_sharedstatedir}/glusterd/options
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/stop
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/stop/post
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/stop/pre
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/start
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/start/post
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/start/pre
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/reset
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/reset/post
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/reset/pre
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/remove-brick
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/remove-brick/post
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/remove-brick/pre
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick/post
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick/pre
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/set
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/set/post
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/set/pre
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/create
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/create/post
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/create/pre
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/delete
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/delete/post
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/delete/pre
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/copy-file
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/copy-file/post
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/copy-file/pre
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/gsync-create
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/gsync-create/pre
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/glustershd
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/peers
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/vols
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/nfs/run
touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/nfs-server.vol
touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/run/nfs.pid

%if ( 0%{!?_without_georeplication:1} )
install -p -m 0744 extras/hook-scripts/S56glusterd-geo-rep-create-post.sh \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
%endif
%{__install} -p -m 0744 extras/hook-scripts/start/post/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/start/post
%{__install} -p -m 0744 extras/hook-scripts/stop/pre/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/stop/pre
%{__install} -p -m 0744 extras/hook-scripts/set/post/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/set/post
%{__install} -p -m 0744 extras/hook-scripts/add-brick/post/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick/post
%{__install} -p -m 0744 extras/hook-scripts/add-brick/pre/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/add-brick/pre
%{__install} -p -m 0744 extras/hook-scripts/reset/post/*.sh   \
    %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/reset/post


find ./tests ./run-tests.sh -type f | cpio -pd %{buildroot}%{_prefix}/share/glusterfs

## Install bash completion for cli
install -p -m 0744 -D extras/command-completion/gluster.bash \
    %{buildroot}%{_sysconfdir}/bash_completion.d/gluster


%clean
rm -rf %{buildroot}

##-----------------------------------------------------------------------------
## All %post should be placed here and keep them sorted
##
%post
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%_init_restart rsyslog
%endif
%endif

%post api
/sbin/ldconfig

%post fuse
%if ( 0%{?rhel} == 5 )
modprobe fuse
%endif

%if ( 0%{!?_without_georeplication:1} )
%post geo-replication
#restart glusterd.
if [ $1 -ge 1 ]; then
    %_init_restart glusterd
fi
%endif

%post libs
/sbin/ldconfig

%post server
# Legacy server
%_init_enable glusterd
%_init_enable glusterfsd

# Genuine Fedora (and EPEL) builds never put gluster files in /etc; if
# there are any files in /etc from a prior gluster.org install, move them
# to /var/lib. (N.B. Starting with 3.3.0 all gluster files are in /var/lib
# in gluster.org RPMs.) Be careful to copy them on the off chance that
# /etc and /var/lib are on separate file systems
if [ -d /etc/glusterd -a ! -h %{_sharedstatedir}/glusterd ]; then
    mkdir -p %{_sharedstatedir}/glusterd
    cp -a /etc/glusterd %{_sharedstatedir}/glusterd
    rm -rf /etc/glusterd
    ln -sf %{_sharedstatedir}/glusterd /etc/glusterd
fi

# Rename old volfiles in an RPM-standard way.  These aren't actually
# considered package config files, so %%config doesn't work for them.
if [ -d %{_sharedstatedir}/glusterd/vols ]; then
    for file in $(find %{_sharedstatedir}/glusterd/vols -name '*.vol'); do
        newfile=${file}.rpmsave
        echo "warning: ${file} saved as ${newfile}"
        cp ${file} ${newfile}
    done
fi

# add marker translator
# but first make certain that there are no old libs around to bite us
# BZ 834847
if [ -e /etc/ld.so.conf.d/glusterfs.conf ]; then
    rm -f /etc/ld.so.conf.d/glusterfs.conf
    /sbin/ldconfig
fi
pidof -c -o %PPID -x glusterd &> /dev/null
if [ $? -eq 0 ]; then
    kill -9 `pgrep -f gsyncd.py` &> /dev/null

    killall --wait glusterd &> /dev/null
    glusterd --xlator-option *.upgrade=on -N
    # glusterd _was_ running, we killed it, it exited after *.upgrade=on,
    # so start it again
    %_init_start glusterd
else
    glusterd --xlator-option *.upgrade=on -N
fi

##-----------------------------------------------------------------------------
## All %preun should be placed here and keep them sorted
##
%preun server
if [ $1 -eq 0 ]; then
    if [ -f %_init_glusterfsd ]; then
        %_init_stop glusterfsd
    fi
    %_init_stop glusterd
    if [ -f %_init_glusterfsd ]; then
        %_init_disable glusterfsd
    fi
    %_init_disable glusterd
fi
if [ $1 -ge 1 ]; then
    if [ -f %_init_glusterfsd ]; then
        %_init_restart glusterfsd
    fi
    %_init_restart glusterd
fi

##-----------------------------------------------------------------------------
## All %postun should be placed here and keep them sorted
##
%postun
/sbin/ldconfig
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%_init_restart rsyslog
%endif
%endif

%postun api
/sbin/ldconfig

%postun libs
/sbin/ldconfig

##-----------------------------------------------------------------------------
## All %files should be placed here and keep them sorted
##
%files
%doc ChangeLog COPYING-GPLV2 COPYING-LGPLV3 INSTALL README THANKS
%config(noreplace) %{_sysconfdir}/logrotate.d/*
%config(noreplace) %{_sysconfdir}/sysconfig/*
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%{_sysconfdir}/rsyslog.d/gluster.conf.example
%endif
%endif
%{_libdir}/glusterfs
%{_sbindir}/glusterfs*
%{_mandir}/man8/*gluster*.8*
%exclude %{_mandir}/man8/gluster.8*
%dir %{_localstatedir}/log/glusterfs
%dir %{_localstatedir}/run/gluster
%dir %{_sharedstatedir}/glusterd
%if ( 0%{!?_without_rdma:1} )
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/rdma*
%endif
# server-side, etc., xlators in other RPMs
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/api*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/fuse*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/posix*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/server*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs*
# Glupy files are in the -extra-xlators package
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy*
# sample xlators not generally used or usable
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption/rot-13*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/mac-compat*
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/performance/symlink-cache*
%{_datadir}/glusterfs/scripts/post-upgrade-script-for-quota.sh
%{_datadir}/glusterfs/scripts/pre-upgrade-script-for-quota.sh

%files api
%exclude %{_libdir}/*.so
# Shared Python-GlusterFS files
%{python_sitelib}/gluster/__init__.*
# libgfapi files
%{_libdir}/libgfapi.*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/api*

%files api-devel
%{_libdir}/pkgconfig/glusterfs-api.pc
%{_libdir}/pkgconfig/libgfchangelog.pc
%{_libdir}/libgfapi.so
%{_includedir}/glusterfs/api/*

%files cli
%{_sbindir}/gluster
%{_mandir}/man8/gluster.8*
%{_sysconfdir}/bash_completion.d/gluster

%files devel
%{_includedir}/glusterfs
%exclude %{_includedir}/glusterfs/y.tab.h
%exclude %{_includedir}/glusterfs/api
%exclude %{_libdir}/libgfapi.so
%{_libdir}/*.so
# Glupy Translator examples
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/debug-trace.*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/helloworld.*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/negative.*

%files extra-xlators
# Glupy C shared library
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy.so
# Glupy Python files
%{python_sitelib}/gluster/glupy/__init__.*
# Don't expect a .egg-info file on EL5
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 ) )
%{python_sitelib}/glusterfs_glupy*.egg-info
%endif

%files fuse
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/fuse*
/sbin/mount.glusterfs
%if ( 0%{!?_without_fusermount:1} )
%{_bindir}/fusermount-glusterfs
%endif
%if ( 0%{_for_fedora_koji_builds} )
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
%{_sysconfdir}/sysconfig/modules/glusterfs-fuse.modules
%endif
%endif

%if ( 0%{!?_without_georeplication:1} )
%files geo-replication
%{_sysconfdir}/logrotate.d/glusterfs-georep
%{_libexecdir}/glusterfs/gsyncd
%{_libexecdir}/glusterfs/python/syncdaemon/*
%{_libexecdir}/glusterfs/gverify.sh
%{_libexecdir}/glusterfs/set_geo_rep_pem_keys.sh
%{_libexecdir}/glusterfs/peer_add_secret_pub
%{_libexecdir}/glusterfs/peer_gsec_create
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/geo-replication
%dir %{_sharedstatedir}/glusterd/hooks
%dir %{_sharedstatedir}/glusterd/hooks/1
%dir %{_sharedstatedir}/glusterd/hooks/1/gsync-create
%dir %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
%{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
%{_datadir}/glusterfs/scripts/get-gfid.sh
%{_datadir}/glusterfs/scripts/slave-upgrade.sh
%{_datadir}/glusterfs/scripts/gsync-upgrade.sh
%{_datadir}/glusterfs/scripts/generate-gfid-file.sh
%{_datadir}/glusterfs/scripts/gsync-sync-gfid
%ghost %attr(0644,-,-) %{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
%endif

%files libs
%{_libdir}/*.so.*
%exclude %{_libdir}/libgfapi.*

%if ( 0%{!?_without_rdma:1} )
%files rdma
%{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/rdma*
%endif

%files regression-tests
%{_prefix}/share/glusterfs/*
%exclude %{_prefix}/share/glusterfs/tests/basic/rpm.t

%if ( 0%{!?_without_ocf:1} )
%files resource-agents
# /usr/lib is the standard for OCF, also on x86_64
%{_prefix}/lib/ocf/resource.d/glusterfs
%endif

%files server
%doc extras/clear_xattrs.sh
%if ( 0%{_for_fedora_koji_builds} )
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterd
%endif
%config(noreplace) %{_sysconfdir}/sysconfig/glusterd
%config(noreplace) %{_sysconfdir}/glusterfs
%dir %{_sharedstatedir}/glusterd/groups
%config(noreplace) %{_sharedstatedir}/glusterd/groups/virt
# Legacy configs
%if ( 0%{_for_fedora_koji_builds} )
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfsd
%config(noreplace) %{_sysconfdir}/sysconfig/glusterfsd
%endif
%config %{_sharedstatedir}/glusterd/hooks/1/add-brick/post/disabled-quota-root-xattr-heal.sh
%config %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre/S28Quota-enable-root-xattr-heal.sh
%config %{_sharedstatedir}/glusterd/hooks/1/set/post/S30samba-set.sh
%config %{_sharedstatedir}/glusterd/hooks/1/set/post/S31ganesha-set.sh
%config %{_sharedstatedir}/glusterd/hooks/1/start/post/S29CTDBsetup.sh
%config %{_sharedstatedir}/glusterd/hooks/1/start/post/S30samba-start.sh
%config %{_sharedstatedir}/glusterd/hooks/1/stop/pre/S30samba-stop.sh
%config %{_sharedstatedir}/glusterd/hooks/1/stop/pre/S29CTDB-teardown.sh
%config %{_sharedstatedir}/glusterd/hooks/1/reset/post/S31ganesha-reset.sh
# init files
%_init_glusterd
%if ( 0%{_for_fedora_koji_builds} )
%_init_glusterfsd
%endif
# binaries
%{_sbindir}/glusterd
%{_sbindir}/glfsheal
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/posix*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/server*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt*
%{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs*
%{_sharedstatedir}/glusterd
#hookscripts
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/post
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/post
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/post
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop
%dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/pre

%ghost %attr(0644,-,-) %config(noreplace) %{_sharedstatedir}/glusterd/glusterd.info
%ghost %attr(0600,-,-) %{_sharedstatedir}/glusterd/options
# This is really ugly, but I have no idea how to mark these directories in
# any other way. They should belong to the glusterfs-server package, but
# don't exist after installation. They are generated on the first start...
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/pre
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick/pre
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/pre
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create/pre
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/pre
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/glustershd
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/vols
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/peers
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/nfs
%ghost      %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/nfs-server.vol
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/nfs/run
%ghost      %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/run/nfs.pid

%changelog
* Fri Jan 08 2016 Niels de Vos <ndevos@redhat.com>
- glusterfs-server depends on -api (#1296931)

* Thu Sep 25 2014 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- better logic in %%post server, (#1113543, reopened)

* Wed Sep 24 2014 Balamurugan Arumugam <barumuga@redhat.com>
- remove /sbin/ldconfig as interpreter (#1145992)

* Thu Jun 29 2014 Humble Chirammal <hchiramm@redhat.com>
- Added dynamic loading of fuse module with glusterfs-fuse package installation in el5.

* Fri Jun 27 2014 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- killall --wait in %%post server, (#1113543)

* Thu Jun 12 2014 Varun Shastry <vshastry@redhat.com>
- Add bash completion config to the cli package

* Tue Jun 03 2014 Vikhyat Umrao <vumrao@redhat.com>
- add nfs-utils package dependency for server package (#1065654)

* Thu May 22 2014 Poornima G <pgurusid@redhat.com>
- Rename old hookscripts in an RPM-standard way.

* Tue May 20 2014 Niels de Vos <ndevos@redhat.com>
- Almost drop calling ./autogen.sh

* Fri Apr 25 2014 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- Sync with Fedora spec (#1091408, #1091392)

* Fri Apr 25 2014 Arumugam Balamurugan <barumuga@redhat.com>
- fix RHEL 7 build failure "Installed (but unpackaged) file(s) found" (#1058188)

* Wed Apr 02 2014 Arumugam Balamurugan <barumuga@redhat.com>
- cleanup to rearrange spec file elements

* Wed Apr 02 2014 Arumugam Balamurugan <barumuga@redhat.com>
- add version/release dynamically (#1074919)

* Thu Mar 26 2014 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- attr dependency (#1184626)

* Wed Mar 26 2014 Poornima G <pgurusid@redhat.com>
- Include the hook scripts of add-brick, volume start, stop and set

* Wed Feb 26 2014 Niels de Vos <ndevos@redhat.com>
- Drop glusterfs-devel dependency from glusterfs-api (#1065750)

* Wed Feb 19 2014 Justin Clift <justin@gluster.org>
- Rename gluster.py to glupy.py to avoid namespace conflict (#1018619)
- Move the main Glupy files into glusterfs-extra-xlators rpm
- Move the Glupy Translator examples into glusterfs-devel rpm

* Thu Feb 06 2014 Aravinda VK <avishwan@redhat.com>
- Include geo-replication upgrade scripts and hook scripts.

* Wed Jan 15 2014 Niels de Vos <ndevos@redhat.com>
- Install /var/lib/glusterd/groups/virt by default

* Sat Jan 4 2014 Niels de Vos <ndevos@redhat.com>
- The main glusterfs package should not provide glusterfs-libs (#1048489)

* Tue Dec 10 2013 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- Sync with Fedora glusterfs.spec 3.5.0-0.1.qa3

* Fri Oct 11 2013 Harshavardhana <fharshav@redhat.com>
- Add '_sharedstatedir' macro to `/var/lib` on <= RHEL5 (#1003184)

* Wed Oct 9 2013 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- Sync with Fedora glusterfs.spec 3.4.1-2+

* Wed Oct 9 2013 Niels de Vos <ndevos@redhat.com>
- glusterfs-api-devel requires glusterfs-devel (#1016938, #1017094)

* Mon Sep 30 2013 Niels de Vos <ndevos@redhat.com>
- Package gfapi.py into the Python site-packages path (#1005146)

* Tue Sep 17 2013 Harshavardhana <fharshav@redhat.com>
- Provide a new package called "glusterfs-regression-tests" for standalone
  regression testing.

* Thu Aug 22 2013 Niels de Vos <ndevos@redhat.com>
- Correct the day/date for some entries in this changelog (#1000019)

* Wed Aug 7 2013 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- Sync with Fedora glusterfs.spec
-  add Requires
-  add -cli subpackage,
-  fix other minor differences with Fedora glusterfs.spec

* Tue Jul 30 2013 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- Sync with Fedora glusterfs.spec, add glusterfs-libs RPM for oVirt/qemu-kvm

* Thu Jul 25 2013 Csaba Henk <csaba@redhat.com>
- Added peer_add_secret_pub and peer_gsec_create to %%{_libexecdir}/glusterfs

* Thu Jul 25 2013 Aravinda VK <avishwan@redhat.com>
- Added gverify.sh to %%{_libexecdir}/glusterfs directory.

* Thu Jul 25 2013 Harshavardhana <fharshav@redhat.com>
- Allow to build with '--without bd' to disable 'bd' xlator

* Thu Jun 27 2013 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- fix the hardening fix for shlibs, use %%sed macro, shorter ChangeLog

* Wed Jun 26 2013 Niels de Vos <ndevos@redhat.com>
- move the mount/api xlator to glusterfs-api

* Fri Jun 7 2013 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- Sync with Fedora glusterfs.spec, remove G4S/UFO and Swift

* Mon Mar 4 2013 Niels de Vos <ndevos@redhat.com>
- Package /var/run/gluster so that statedumps can be created

* Wed Feb 6 2013 Kaleb S. KEITHLEY <kkeithle@redhat.com>
- Sync with Fedora glusterfs.spec

* Tue Dec 11 2012 Filip Pytloun <filip.pytloun@gooddata.com>
- add sysconfig file

* Thu Oct 25 2012 Niels de Vos <ndevos@redhat.com>
- Add a sub-package for the OCF resource agents

* Wed Sep 05 2012 Niels de Vos <ndevos@redhat.com>
- Don't use python-ctypes on SLES (from Jörg Petersen)

* Tue Jul 10 2012 Niels de Vos <ndevos@redhat.com>
- Include extras/clear_xattrs.sh in the glusterfs-server sub-package

* Thu Jun 07 2012 Niels de Vos <ndevos@redhat.com>
- Mark /var/lib/glusterd as owned by glusterfs, subdirs belong to -server

* Wed May 9 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- Add BuildRequires: libxml2-devel so that configure will DTRT on for
- Fedora's Koji build system

* Wed Nov 9 2011 Joe Julian <me@joejulian.name> - git master
- Merge fedora specfile into gluster's spec.in.
- Add conditionals to allow the same spec file to be used for both 3.1 and 3.2
- http://bugs.gluster.com/show_bug.cgi?id=2970

* Wed Oct  5 2011 Joe Julian <me@joejulian.name> - 3.2.4-1
- Update to 3.2.4
- Removed the $local_fs requirement from the init scripts as in RHEL/CentOS that's provided
- by netfs, which needs to be started after glusterd.

* Sun Sep 25 2011 Joe Julian <me@joejulian.name> - 3.2.3-2
- Merged in upstream changes
- Fixed version reporting 3.2git
- Added nfs init script (disabled by default)

* Thu Sep  1 2011 Joe Julian <me@joejulian.name> - 3.2.3-1
- Update to 3.2.3

* Tue Jul 19 2011 Joe Julian <me@joejulian.name> - 3.2.2-3
- Add readline and libtermcap dependencies

* Tue Jul 19 2011 Joe Julian <me@joejulian.name> - 3.2.2-2
- Critical patch to prevent glusterd from walking outside of its own volume during rebalance

* Thu Jul 14 2011 Joe Julian <me@joejulian.name> - 3.2.2-1
- Update to 3.2.2

* Wed Jul 13 2011 Joe Julian <me@joejulian.name> - 3.2.1-2
- fix hardcoded path to gsyncd in source to match the actual file location

* Tue Jun 21 2011 Joe Julian <me@joejulian.name> - 3.2.1
- Update to 3.2.1

* Mon Jun 20 2011 Joe Julian <me@joejulian.name> - 3.1.5
- Update to 3.1.5

* Tue May 31 2011 Joe Julian <me@joejulian.name> - 3.1.5-qa1.4
- Current git

* Sun May 29 2011 Joe Julian <me@joejulian.name> - 3.1.5-qa1.2
- set _sharedstatedir to /var/lib for FHS compliance in RHEL5/CentOS5
- mv /etc/glusterd, if it exists, to the new state dir for upgrading from gluster packaging

* Sat May 28 2011 Joe Julian <me@joejulian.name> - 3.1.5-qa1.1
- Update to 3.1.5-qa1
- Add patch to remove optimization disabling
- Add patch to remove forced 64 bit compile
- Obsolete glusterfs-core to allow for upgrading from gluster packaging

* Sat Mar 19 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.3-1
- Update to 3.1.3
- Merge in more upstream SPEC changes
- Remove patches from GlusterFS bugzilla #2309 and #2311
- Remove inode-gen.patch

* Sun Feb 06 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.2-3
- Add back in legacy SPEC elements to support older branches

* Thu Feb 03 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.2-2
- Add patches from CloudFS project

* Tue Jan 25 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.2-1
- Update to 3.1.2

* Wed Jan 5 2011 Dan Horák <dan[at]danny.cz> - 3.1.1-3
- no InfiniBand on s390(x)

* Sat Jan 1 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.1-2
- Update to support readline
- Update to not parallel build

* Mon Dec 27 2010 Silas Sewell <silas@sewell.ch> - 3.1.1-1
- Update to 3.1.1
- Change package names to mirror upstream

* Mon Dec 20 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.0.7-1
- Update to 3.0.7

* Wed Jul 28 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.0.5-1
- Update to 3.0.x

* Sat Apr 10 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.9-2
- Move python version requires into a proper BuildRequires otherwise
  the spec always turned off python bindings as python is not part
  of buildsys-build and the chroot will never have python unless we
  require it
- Temporarily set -D_FORTIFY_SOURCE=1 until upstream fixes code
  GlusterFS Bugzilla #197 (#555728)
- Move glusterfs-volgen to devel subpackage (#555724)
- Update description (#554947)

* Sat Jan 2 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.9-1
- Update to 2.0.9

* Sun Nov 8 2009 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.8-1
- Update to 2.0.8
- Remove install of glusterfs-volgen, it's properly added to
  automake upstream now

* Sat Oct 31 2009 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.7-1
- Update to 2.0.7
- Install glusterfs-volgen, until it's properly added to automake
  by upstream
- Add macro to be able to ship more docs

* Thu Sep 17 2009 Peter Lemenkov <lemenkov@gmail.com> 2.0.6-2
- Rebuilt with new fuse

* Sat Sep 12 2009 Matthias Saou <http://freshrpms.net/> 2.0.6-1
- Update to 2.0.6.
- No longer default to disable the client on RHEL5 (#522192).
- Update spec file URLs.

* Mon Jul 27 2009 Matthias Saou <http://freshrpms.net/> 2.0.4-1
- Update to 2.0.4.

* Thu Jun 11 2009 Matthias Saou <http://freshrpms.net/> 2.0.1-2
- Remove libglusterfs/src/y.tab.c to fix koji F11/devel builds.

* Sat May 16 2009 Matthias Saou <http://freshrpms.net/> 2.0.1-1
- Update to 2.0.1.

* Thu May  7 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-1
- Update to 2.0.0 final.

* Wed Apr 29 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.3.rc8
- Move glusterfsd to common, since the client has a symlink to it.

* Fri Apr 24 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.2.rc8
- Update to 2.0.0rc8.

* Sun Apr 12 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.2.rc7
- Update glusterfsd init script to the new style init.
- Update files to match the new default vol file names.
- Include logrotate for glusterfsd, use a pid file by default.
- Include logrotate for glusterfs, using killall for lack of anything better.

* Sat Apr 11 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.1.rc7
- Update to 2.0.0rc7.
- Rename "libs" to "common" and move the binary, man page and log dir there.

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.1.rc1
- Update to 2.0.0rc1.
- Include new libglusterfsclient.h.

* Mon Feb 16 2009 Matthias Saou <http://freshrpms.net/> 1.3.12-1
- Update to 1.3.12.
- Remove no longer needed ocreat patch.

* Thu Jul 17 2008 Matthias Saou <http://freshrpms.net/> 1.3.10-1
- Update to 1.3.10.
- Remove mount patch, it's been included upstream now.

* Fri May 16 2008 Matthias Saou <http://freshrpms.net/> 1.3.9-1
- Update to 1.3.9.

* Fri May  9 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-1
- Update to 1.3.8 final.

* Wed Apr 23 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.10
- Include short patch to include fixes from latest TLA 751.

* Tue Apr 22 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.9
- Update to 1.3.8pre6.
- Include glusterfs binary in both the client and server packages, now that
  glusterfsd is a symlink to it instead of a separate binary.
* Sun Feb  3 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.8
- Add python version check and disable bindings for version < 2.4.

* Sun Feb  3 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.7
- Add --without client rpmbuild option, make it the default for RHEL (no fuse).
  (I hope "rhel" is the proper default macro name, couldn't find it...)

* Wed Jan 30 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.6
- Add --without ibverbs rpmbuild option to the package.

* Mon Jan 14 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.5
- Update to current TLA again, patch-636 which fixes the known segfaults.

* Thu Jan 10 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.4
- Downgrade to glusterfs--mainline--2.5--patch-628 which is more stable.

* Tue Jan  8 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.3
- Update to current TLA snapshot.
- Include umount.glusterfs wrapper script (really needed? dunno).
- Include patch to mount wrapper to avoid multiple identical mounts.

* Sun Dec 30 2007 Matthias Saou <http://freshrpms.net/> 1.3.8-0.1
- Update to current TLA snapshot, which includes "volume-name=" fstab option.

* Mon Dec  3 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-6
- Re-add the /var/log/glusterfs directory in the client sub-package (required).
- Include custom patch to support vol= in fstab for -n glusterfs client option.

* Mon Nov 26 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-4
- Re-enable libibverbs.
- Check and update License field to GPLv3+.
- Add glusterfs-common obsoletes, to provide upgrade path from old packages.
- Include patch to add mode to O_CREATE opens.

* Thu Nov 22 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-3
- Remove Makefile* files from examples.
- Include RHEL/Fedora type init script, since the included ones don't do.

* Wed Nov 21 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-1
- Major spec file cleanup.
- Add missing %%clean section.
- Fix ldconfig calls (weren't set for the proper sub-package).

* Sat Aug 4 2007 Matt Paine <matt@mattsoftware.com> - 1.3.pre7
- Added support to build rpm without ibverbs support (use --without ibverbs
  switch)

* Sun Jul 15 2007 Matt Paine <matt@mattsoftware.com> - 1.3.pre6
- Initial spec file
