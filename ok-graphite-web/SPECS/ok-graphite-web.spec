%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define __touch    /bin/touch
%define __service  /sbin/service

#---------------------------------------------------------------------------------------------------
%define graphite_version 0.9.13
%define ok_version 01

Name:           ok-graphite-web
Version:        %{graphite_version}
Release:        %{ok_version}
Summary:        Enterprise scalable realtime graphing
Group:          Applications/Internet
License:        Apache License
URL:            https://launchpad.net/graphite
Vendor:         Chris Davis <chrismd@gmail.com>
Packager:       Dan Carley <dan.carley@gmail.com>

Source0:        graphite-web-%{graphite_version}.tar.gz
Patch0:         navbar-west.patch

BuildArch:      noarch

BuildRequires:  python python-devel python-setuptools
Requires:       Django14 django-tagging httpd mod_wsgi pycairo python-simplejson bitmap-fonts-compat

Requires:       ok-whisper >= 0.9.13-01
Requires:       ok-carbon >= 0.9.13-01

%description
Graphite consists of a storage backend and a web-based visualization frontend.
Client applications send streams of numeric time-series data to the Graphite
backend (called carbon), where it gets stored in fixed-size database files
similar in design to RRD. The web frontend provides 2 distinct user interfaces
for visualizing this data in graphs as well as a simple URL-based API for
direct graph generation.

Graphite's design is focused on providing simple interfaces (both to users and
applications), real-time visualization, high-availability, and enterprise
scalability.

%prep
%setup -q -n graphite-web-%{graphite_version}
%patch0 -p2

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} -c 'import setuptools; execfile("setup.py")' build

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}
%{__python} -c 'import setuptools; execfile("setup.py")' install --skip-build --root %{buildroot}

# Delete examples directory since we already include its contents in docs
%{__rm} -rf %{buildroot}/opt/graphite/examples

# Create config directory and install configuration files
#%{__mkdir_p} %{buildroot}%{_sysconfdir}/graphite-web
#%{__install} -Dp -m0644 conf/dashboard.conf.example %{buildroot}%{_sysconfdir}/graphite-web/dashboard.conf
#%{__install} -Dp -m0644 webapp/graphite/local_settings.py.example %{buildroot}%{_sysconfdir}/graphite-web/local_settings.py

# Install the example wsgi controller and vhost configuration
#%{__install} -Dp -m0755 conf/graphite.wsgi.example %{buildroot}/usr/share/graphite/graphite-web.wsgi
#%{__install} -Dp -m0644 examples/example-graphite-vhost.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/graphite-web.conf

# Create local_settings symlink
#%{__ln_s} %{_sysconfdir}/graphite-web/local_settings.py %{buildroot}%{python_sitelib}/graphite/local_settings.py

%pre
%{__getent} group graphite >/dev/null || %{__groupadd} -r graphite
%{__getent} passwd graphite >/dev/null || %{__useradd} -r -g graphite -d /opt/graphite -s /sbin/nologin -c "Graphite Daemons" graphite
exit 0

%post
# Initialize the database
DJANGO_SETTINGS_MODULE=local_settings.py django-admin syncdb --pythonpath=/opt/graphite/webapp --settings=graphite.settings --noinput >/dev/null
%{__chown} graphite:apache /opt/graphite/storage/graphite.db
%{__chmod} 0664 /opt/graphite/storage/graphite.db

%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc INSTALL LICENSE conf/* examples/*

/opt/graphite/webapp
/opt/graphite/bin/*

%config /opt/graphite/conf/*

%attr(775,graphite,apache) %dir /opt/graphite/storage
%attr(775,graphite,apache) %dir /opt/graphite/storage/log/webapp

%changelog
* Tue Jun 16 2015 Vadzim Tonka <vadim@swiftype.net> - 0.9.13-01
- New graphite-web version

* Mon Mar 24 2014 Oleksiy Kovyrin <alexey@kovyrin.net> - 0.9.12-05
- Add dependencies on new carbon and whisper.

* Mon Mar 24 2014 Oleksiy Kovyrin <alexey@kovyrin.net> - 0.9.12-04
- Apply a patch to make graphite-web compatible with the latest carbon 0.9.12.

* Mon Mar 24 2014 Oleksiy Kovyrin <alexey@kovyrin.net> - 0.9.12-03
- Upgrade to the latest 0.9.x branch version.

* Mon Aug 26 2013 Oleksiy Kovyrin <alexey@kovyrin.net> - 0.9.12-02
- Move navbar to west by default.

* Mon Aug 26 2013 Oleksiy Kovyrin <alexey@kovyrin.net> - 0.9.12-01
- Upgrade to the latest 0.9.x branch revision (0.9.12+).

* Thu Jul 9 2013 Oleksiy Kovyrin <alexey@kovyrin.net> - 0.9.10-05
- Upgrade to the latest 0.9.x branch revision + fix for movingXXX functions (PR#366).

* Thu Oct 4 2012 Dan Carley <dan.carley@gmail.com> - 0.9.10-3
- Require bitmap-fonts on EL6 to resolve MemoryError exception on render.

* Mon Jul 30 2012 Brian Pitts <brian@polibyte.com> - 0.9.10-2
- Do not require pysqlite2 on EL6 since it is already included as sqlite3

* Fri Jun 1 2012 Ben P <ben@g.megatron.org> - 0.9.10-1
- New upstream version.

* Sat Oct 8 2011 Dan Carley <dan.carley@gmail.com> - 0.9.9-1
- New upstream version.

* Mon May 23 2011 Dan Carley <dan.carley@gmail.com> - 0.9.8-2
- Repackage with some tidying.
- Move state directory to /var/lib
- Remove debug print to stdout.
- Don't restart Apache. Kind of obtrusive.

* Tue Apr 19 2011 Chris Abernethy <cabernet@chrisabernethy.com> - 0.9.8-1
- Update source to upstream v0.9.8
- Minor updates to spec file

* Tue Mar 23 2010 Ilya Zakreuski <izakreuski@gmail.com> 0.9.5-1
- Initial release.
