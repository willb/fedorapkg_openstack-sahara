Name:          openstack-sahara
Version:       2014.1.rc1
Release:       1%{?dist}
Provides:      openstack-savanna = %{version}-%{release}
Obsoletes:     openstack-savanna <= 2014.1.b3-2
Summary:       Apache Hadoop cluster management on OpenStack
License:       ASL 2.0
URL:           https://launchpad.net/sahara
Source0:       http://tarballs.openstack.org/sahara/sahara-%{version}.tar.gz
Source1:       openstack-sahara-api.service
BuildArch:     noarch

BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: python-oslo-sphinx
BuildRequires: python-sphinxcontrib-httpdomain
BuildRequires: python-pbr >= 0.5.19
# Need systemd-units for _unitdir macro
BuildRequires: systemd-units
# Needed by check
BuildRequires: python-hacking
BuildRequires: python-unittest2
BuildRequires: mock
BuildRequires: python-docutils >= 0.9.1
BuildRequires: python-sphinx
BuildRequires: python-testrepository >= 0.0.15
BuildRequires: python-fixtures
BuildRequires: python-psycopg2
BuildRequires: MySQL-python
BuildRequires: pylint
BuildRequires: python-migrate
BuildRequires: python-testscenarios
BuildRequires: python-testtools

Requires: python-alembic
#?Babel>=1.3?
Requires: python-eventlet
Requires: python-flask
Requires: python-iso8601
Requires: python-jsonschema >= 1.3.0
Requires: python-oslo-config >= 1.2.0
Requires: python-oslo-messaging
Requires: python-paramiko >= 1.9.0
Requires: python-pbr
Requires: python-cinderclient >= 1.0.5
Requires: python-keystoneclient >= 0.6.0
Requires: python-novaclient >= 2.15.0
Requires: python-swiftclient
Requires: python-neutronclient
Requires: python-six >= 1.4.1
Requires: python-stevedore >= 0.14
Requires: python-sqlalchemy
Requires: python-webob

Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
Requires(pre):    shadow-utils


%description
Sahara provides the ability to elastically manage Apache Hadoop
clusters on OpenStack.


%prep
%setup -q -n sahara-%{version}
rm -rf sahara.egg-info
rm -f test-requirements.txt
# The data_files glob appears broken in pbr 0.5.19, so be explicit
sed -i 's,etc/sahara/\*,etc/sahara/sahara.conf.sample,' setup.cfg


%build
%{__python2} setup.py build

export PYTHONPATH=$PWD:${PYTHONPATH}
# Note: json warnings likely resolved w/ pygments 1.5 (not yet in Fedora)
# make doc build compatible with python-oslo-sphinx RPM
sed -i 's/oslosphinx/oslo.sphinx/' doc/source/conf.py
sphinx-build doc/source html
rm -rf html/.{doctrees,buildinfo}


%install
%{__python2} setup.py install --skip-build --root %{buildroot}

install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/openstack-sahara-api.service

HOME=%{_sharedstatedir}/sahara
install -d -m 700 %{buildroot}$HOME

# TODO: os_admin_username/password/tenant_name
SAMPLE=%{buildroot}%{_datadir}/sahara/sahara.conf.sample
CONF=%{buildroot}%{_sysconfdir}/sahara/sahara.conf
install -d -m 755 $(dirname $CONF)
install -D -m 640 $SAMPLE $CONF
sed -i -e "s,.*connection=.*,connection=sqlite:///$HOME/sahara-server.db," $CONF

# Do not package tests
rm -rf %{buildroot}%{python_sitelib}/sahara/tests

mkdir -p -m0755 %{buildroot}/%{_var}/log/sahara


%check
# Building on koji with virtualenv requires test-requirements.txt and this
# causes errors when trying to resolve the package names, also turning on pep8
# results in odd exceptions from flake8.
sh run_tests.sh --no-virtual-env --no-pep8


%pre
# Origin: http://fedoraproject.org/wiki/Packaging:UsersAndGroups#Dynamic_allocation
USERNAME=sahara
GROUPNAME=$USERNAME
HOMEDIR=%{_sharedstatedir}/sahara
getent group $GROUPNAME >/dev/null || groupadd -r $GROUPNAME
getent passwd $USERNAME >/dev/null || \
  useradd -r -g $GROUPNAME -G $GROUPNAME -d $HOMEDIR -s /sbin/nologin \
  -c "Sahara Daemons" $USERNAME
exit 0


%post
# TODO: if db file then sahara-db-manage update head
%systemd_post openstack-sahara-api.service


%preun
%systemd_preun openstack-sahara-api.service


%postun
%systemd_postun_with_restart openstack-sahara-api.service


%files
%doc html README.rst LICENSE
%dir %{_sysconfdir}/sahara
# Note: this file is not readable because it holds auth credentials
%config(noreplace) %attr(-, root, sahara) %{_sysconfdir}/sahara/sahara.conf
%{_bindir}/sahara-api
%{_bindir}/_sahara-subprocess
%{_bindir}/sahara-db-manage
%{_unitdir}/openstack-sahara-api.service
%dir %attr(-, sahara, sahara) %{_sharedstatedir}/sahara
# Note: permissions on sahara's home are intentially 0700
%dir %{_datadir}/sahara
%{_datadir}/sahara/sahara.conf.sample
%{python_sitelib}/sahara
%{python_sitelib}/sahara-%{version}-py?.?.egg-info
%defattr(-,sahara,sahara,-)
%dir %{_var}/log/sahara



%changelog
* Tue Apr 08 2014 Michael McCune <mimccune@redhat> - 2014.1.rc1-1
- 2014.1.rc1 release and rename from openstack-savanna

* Fri Mar 14 2014 Matthew Farrellee <matt@redhat> - 2014.1.b3-2
- Fixed python-webob dependency version

* Mon Mar 10 2014 Matthew Farrellee <matt@redhat> - 2014.1.b3-1
- 2014.1.b3 release

* Mon Jan 27 2014 Matthew Farrellee <matt@redhat> - 2014.1.b2-3
- Require stevedore >= 0.13

* Mon Jan 27 2014 Matthew Farrellee <matt@redhat> - 2014.1.b2-2
- Added space around paramiko requires

* Mon Jan 27 2014 Matthew Farrellee <matt@redhat> - 2014.1.b2-1
- 2014.1.b2 release

* Sat Jan 18 2014 Matthew Farrellee <matt@redhat> - 2014.1.b1-1
- 2014.1.b1 release

* Tue Oct 22 2013 Matthew Farrellee <matt@redhat> - 0.3-3
- Include Vanilla Plugin SQL files (for EDP)

* Tue Oct 22 2013 Matthew Farrellee <matt@redhat> - 0.3-2
- Fix db connection url

* Sun Oct 20 2013 Matthew Farrellee <matt@redhat> - 0.3-1
- 0.3 release
- Enable logging into /var/log/savanna

* Fri Oct 11 2013 Matthew Farrellee <matt@redhat> - 0.3-0.2
- 0.3 rc3 build

* Mon Aug 12 2013 Matthew Farrellee <matt@redhat> - 0.2-3
- Updates to build on F19,
-  Require systemd-units, allows mockbuild to work
-  Remove setuptools-git from setup.py, no downloads during build

* Fri Aug 09 2013 Matthew Farrellee <matt@redhat> - 0.2-2
- Updates from package review BZ986615

* Mon Jul 15 2013 Matthew Farrellee <matt@redhat> - 0.2-1
- Initial package
