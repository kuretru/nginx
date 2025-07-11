#
%define nginx_home %{_localstatedir}/cache/nginx
%define nginx_user nginx
%define nginx_group nginx
%define nginx_loggroup adm

BuildRequires: systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%if 0%{?rhel}
%define _group System Environment/Daemons
%endif

%if (0%{?rhel} == 7) && (0%{?amzn} == 0)
%define epoch 1
Epoch: %{epoch}
Requires(pre): shadow-utils
Requires: openssl >= 1.0.2
Requires: procps-ng
BuildRequires: openssl-devel >= 1.0.2
BuildRequires: perl-IPC-Cmd
%define dist .el7
%endif

%if (0%{?rhel} == 7) && (0%{?amzn} == 2)
%define epoch 1
Epoch: %{epoch}
Requires(pre): shadow-utils
Requires: openssl11 >= 1.1.1
Requires: procps-ng
BuildRequires: openssl11-devel >= 1.1.1
%endif

%if 0%{?rhel} == 8
%define epoch 1
Epoch: %{epoch}
Requires(pre): shadow-utils
Requires: procps-ng
BuildRequires: openssl-devel >= 1.1.1
%define _debugsource_template %{nil}
%endif

%if 0%{?rhel} == 9
%define epoch 2
Epoch: %{epoch}
Requires(pre): shadow-utils
Requires: procps-ng
BuildRequires: openssl-devel
BuildRequires: gcc
%define _debugsource_template %{nil}
%endif

%if 0%{?rhel} == 10
%define epoch 2
Epoch: %{epoch}
Requires(pre): shadow-utils
Requires: procps-ng
BuildRequires: openssl-devel
%define _debugsource_template %{nil}
%endif

%if 0%{?suse_version} >= 1315
%define _group Productivity/Networking/Web/Servers
%define nginx_loggroup trusted
Requires(pre): shadow
Requires: procps
BuildRequires: libopenssl-devel
%define _debugsource_template %{nil}
%endif

# This also applies to Amazon Linux 2023
%if 0%{?fedora}
%define _debugsource_template %{nil}
%global _hardened_build 1
%define _group System Environment/Daemons
Requires: procps-ng
BuildRequires: openssl-devel
Requires(pre): shadow-utils
%endif

# end of distribution specific definitions

%define openssl_version 3.1.7-quic1

%define base_version 1.29.0
%define base_release 1%{?dist}.ngx

%define bdir %{_builddir}/%{name}-%{base_version}

%define WITH_CC_OPT $(echo %{optflags} $(pcre2-config --cflags)) -fPIC
%define WITH_LD_OPT -Wl,-z,relro -Wl,-z,now -pie

%define BASE_CONFIGURE_ARGS $(echo "--prefix=%{_sysconfdir}/nginx --sbin-path=%{_sbindir}/nginx --modules-path=%{_libdir}/nginx/modules --conf-path=%{_sysconfdir}/nginx/nginx.conf --error-log-path=%{_localstatedir}/log/nginx/error.log --http-log-path=%{_localstatedir}/log/nginx/access.log --pid-path=%{_localstatedir}/run/nginx.pid --lock-path=%{_localstatedir}/run/nginx.lock --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp --user=%{nginx_user} --group=%{nginx_group} --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-http_stub_status_module --with-http_sub_module --with-http_v2_module $( if [ 0%{?rhel} -eq 7 ] || [ 0%{?suse_version} -eq 1315 ]; then continue; else echo "--with-http_v3_module"; fi; ) --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module")

Summary: High performance web server
Name: nginx
Version: %{base_version}
Release: %{base_release}
Vendor: NGINX Packaging <nginx-packaging@f5.com>
URL: https://nginx.org/
Group: %{_group}

Source0: https://nginx.org/download/%{name}-%{version}.tar.gz
Source1: logrotate
Source2: nginx.conf
Source3: nginx.default.conf
Source4: nginx.service
Source5: nginx.upgrade.sh
Source6: nginx.suse.logrotate
Source7: nginx-debug.service
Source8: nginx.copyright
Source9: nginx.check-reload.sh
Source10: https://github.com/quictls/openssl/archive/refs/tags/openssl-%{openssl_version}.tar.gz



License: 2-clause BSD-like license

BuildRoot: %{_tmppath}/%{name}-%{base_version}-%{base_release}-root
BuildRequires: zlib-devel
BuildRequires: pcre2-devel
BuildRequires: perl

Provides: webserver
Provides: nginx-r%{base_version}

%if !(0%{?rhel} == 7)
Recommends: logrotate
%endif

%description
nginx [engine x] is an HTTP and reverse proxy server, as well as
a mail proxy server.

%if 0%{?suse_version} >= 1315
%debug_package
%endif

%prep
%autosetup -p1
tar -zxf %{SOURCE10}

%build
./configure %{BASE_CONFIGURE_ARGS} \
    --with-openssl=./openssl-openssl-%{openssl_version}/ \
    --with-cc-opt="%{WITH_CC_OPT}" \
    --with-ld-opt="%{WITH_LD_OPT}" \
    --with-debug
make %{?_smp_mflags}
%{__mv} %{bdir}/objs/nginx \
    %{bdir}/objs/nginx-debug
./configure %{BASE_CONFIGURE_ARGS} \
    --with-openssl=./openssl-openssl-%{openssl_version}/ \
    --with-cc-opt="%{WITH_CC_OPT}" \
    --with-ld-opt="%{WITH_LD_OPT}"
make %{?_smp_mflags}

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__make} DESTDIR=$RPM_BUILD_ROOT INSTALLDIRS=vendor install

%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/nginx
%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/html $RPM_BUILD_ROOT%{_datadir}/nginx/

%{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/nginx/*.default
%{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/nginx/fastcgi.conf

%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/log/nginx
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/run/nginx
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/cache/nginx

%{__mkdir} -p $RPM_BUILD_ROOT%{_libdir}/nginx/modules
cd $RPM_BUILD_ROOT%{_sysconfdir}/nginx && \
    %{__ln_s} ../..%{_libdir}/nginx/modules modules && cd -

%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/doc/%{name}-%{base_version}
%{__install} -m 644 -p %{SOURCE8} \
    $RPM_BUILD_ROOT%{_datadir}/doc/%{name}-%{base_version}/COPYRIGHT

%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/nginx.conf
%{__install} -m 644 -p %{SOURCE2} \
    $RPM_BUILD_ROOT%{_sysconfdir}/nginx/nginx.conf
%{__install} -m 644 -p %{SOURCE3} \
    $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d/default.conf

%{__install} -p -D -m 0644 %{bdir}/objs/nginx.8 \
    $RPM_BUILD_ROOT%{_mandir}/man8/nginx.8

%{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}
%{__install} -m644 %SOURCE4 \
    $RPM_BUILD_ROOT%{_unitdir}/nginx.service
%{__install} -m644 %SOURCE7 \
    $RPM_BUILD_ROOT%{_unitdir}/nginx-debug.service
%{__mkdir} -p $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/nginx
%{__install} -m755 %SOURCE5 \
    $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/nginx/upgrade
%{__install} -m755 %SOURCE9 \
    $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/nginx/check-reload

# install log rotation stuff
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
%if 0%{?suse_version}
%{__install} -m 644 -p %{SOURCE6} \
    $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/nginx
%else
%{__install} -m 644 -p %{SOURCE1} \
    $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/nginx
%endif

%{__install} -m755 %{bdir}/objs/nginx-debug \
    $RPM_BUILD_ROOT%{_sbindir}/nginx-debug

%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/koi-utf
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/koi-win
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/win-utf

%check
%{__rm} -rf $RPM_BUILD_ROOT/usr/src
cd %{bdir}
grep -v 'usr/src' debugfiles.list > debugfiles.list.new && mv debugfiles.list.new debugfiles.list
cat /dev/null > debugsources.list
%if 0%{?suse_version} >= 1500
cat /dev/null > debugsourcefiles.list
%endif

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%{_sbindir}/nginx
%{_sbindir}/nginx-debug

%dir %{_sysconfdir}/nginx
%dir %{_sysconfdir}/nginx/conf.d
%{_sysconfdir}/nginx/modules

%config(noreplace) %{_sysconfdir}/nginx/nginx.conf
%config(noreplace) %{_sysconfdir}/nginx/conf.d/default.conf
%config(noreplace) %{_sysconfdir}/nginx/mime.types
%config(noreplace) %{_sysconfdir}/nginx/fastcgi_params
%config(noreplace) %{_sysconfdir}/nginx/scgi_params
%config(noreplace) %{_sysconfdir}/nginx/uwsgi_params

%config(noreplace) %{_sysconfdir}/logrotate.d/nginx
%{_unitdir}/nginx.service
%{_unitdir}/nginx-debug.service
%dir %{_libexecdir}/initscripts/legacy-actions/nginx
%{_libexecdir}/initscripts/legacy-actions/nginx/*

%attr(0755,root,root) %dir %{_libdir}/nginx
%attr(0755,root,root) %dir %{_libdir}/nginx/modules
%dir %{_datadir}/nginx
%dir %{_datadir}/nginx/html
%{_datadir}/nginx/html/*

%attr(0755,root,root) %dir %{_localstatedir}/cache/nginx
%attr(0755,root,root) %dir %{_localstatedir}/log/nginx

%dir %{_datadir}/doc/%{name}-%{base_version}
%doc %{_datadir}/doc/%{name}-%{base_version}/COPYRIGHT
%{_mandir}/man8/nginx.8*

%pre
# Add the "nginx" user
getent group %{nginx_group} >/dev/null || groupadd -r %{nginx_group}
getent passwd %{nginx_user} >/dev/null || \
    useradd -r -g %{nginx_group} -s /sbin/nologin \
    -d %{nginx_home} -c "nginx user"  %{nginx_user}
exit 0

%post
# Register the nginx service
if [ $1 -eq 1 ]; then
    /usr/bin/systemctl preset nginx.service >/dev/null 2>&1 ||:
    /usr/bin/systemctl preset nginx-debug.service >/dev/null 2>&1 ||:
    # print site info
    cat <<BANNER
----------------------------------------------------------------------

Thanks for using nginx!

Please find the official documentation for nginx here:
* https://nginx.org/en/docs/

Please subscribe to nginx-announce mailing list to get
the most important news about nginx:
* https://nginx.org/en/support.html

Commercial subscriptions for nginx are available on:
* https://nginx.com/products/

----------------------------------------------------------------------
BANNER

    # Touch and set permisions on default log files on installation

    if [ -d %{_localstatedir}/log/nginx ]; then
        if [ ! -e %{_localstatedir}/log/nginx/access.log ]; then
            touch %{_localstatedir}/log/nginx/access.log
            %{__chmod} 640 %{_localstatedir}/log/nginx/access.log
            %{__chown} nginx:%{nginx_loggroup} %{_localstatedir}/log/nginx/access.log
        fi

        if [ ! -e %{_localstatedir}/log/nginx/error.log ]; then
            touch %{_localstatedir}/log/nginx/error.log
            %{__chmod} 640 %{_localstatedir}/log/nginx/error.log
            %{__chown} nginx:%{nginx_loggroup} %{_localstatedir}/log/nginx/error.log
        fi
    fi
fi

%preun
if [ $1 -eq 0 ]; then
    /usr/bin/systemctl --no-reload disable nginx.service >/dev/null 2>&1 ||:
    /usr/bin/systemctl stop nginx.service >/dev/null 2>&1 ||:
fi

%postun
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 ||:
if [ $1 -ge 1 ]; then
    /sbin/service nginx status  >/dev/null 2>&1 || exit 0
    /sbin/service nginx upgrade >/dev/null 2>&1 || echo \
        "Binary upgrade failed, please check nginx's error.log"
fi

%changelog
* Tue Jun 24 2025 Nginx Packaging <nginx-packaging@f5.com> - 1.29.0-1%{?dist}.ngx
- 1.29.0-1

* Wed Apr 16 2025 Nginx Packaging <nginx-packaging@f5.com> - 1.27.5-1%{?dist}.ngx
- 1.27.5-1

* Wed Feb  5 2025 Nginx Packaging <nginx-packaging@f5.com> - 1.27.4-1%{?dist}.ngx
- 1.27.4-1

* Tue Nov 26 2024 Nginx Packaging <nginx-packaging@f5.com> - 1.27.3-1%{?dist}.ngx
- 1.27.3-1
 
* Wed Nov 20 2024 Nginx Packaging <nginx-packaging@f5.com> - 1.27.2-2%{?dist}.ngx
- RHEL 9 only: bumped Epoch to override appstream version.

* Wed Oct  2 2024 Nginx Packaging <nginx-packaging@f5.com> - 1.27.2-1%{?dist}.ngx
- 1.27.2-1

* Wed Aug 14 2024 Nginx Packaging <nginx-packaging@f5.com> - 1.27.1-1%{?dist}.ngx
- 1.27.1-1

* Wed May 29 2024 Nginx Packaging <nginx-packaging@f5.com> - 1.27.0-2%{?dist}.ngx
- Packages were updated to account for a change in CHANGES wording in
  1.27.0. No functional changes.

* Tue May 28 2024 Nginx Packaging <nginx-packaging@f5.com> - 1.27.0-1%{?dist}.ngx
- 1.27.0-1

* Tue Apr 16 2024 Nginx Packaging <nginx-packaging@f5.com> - 1.25.5-1%{?dist}.ngx
- 1.25.5-1

* Wed Feb 14 2024 Nginx Packaging <nginx-packaging@f5.com> - 1.25.4-1%{?dist}.ngx
- 1.25.4-1

* Tue Oct 24 2023 Nginx Packaging <nginx-packaging@f5.com> - 1.25.3-1%{?dist}.ngx
- 1.25.3-1

* Tue Aug 15 2023 Nginx Packaging <nginx-packaging@f5.com> - 1.25.2-1%{?dist}.ngx
- 1.25.2-1

* Tue Jun 13 2023 Nginx Packaging <nginx-packaging@f5.com> - 1.25.1-1%{?dist}.ngx
- 1.25.1-1

* Tue May 23 2023 Nginx Packaging <nginx-packaging@f5.com> - 1.25.0-1%{?dist}.ngx
- 1.25.0-1

* Tue Mar 28 2023 Nginx Packaging <nginx-packaging@f5.com> - 1.23.4-1%{?dist}.ngx
- 1.23.4-1

* Tue Dec 13 2022 Nginx Packaging <nginx-packaging@f5.com> - 1.23.3-1%{?dist}.ngx
- 1.23.3-1

* Wed Oct 19 2022 Nginx Packaging <nginx-packaging@f5.com> - 1.23.2-1%{?dist}.ngx
- 1.23.2-1

* Tue Jul 19 2022 Nginx Packaging <nginx-packaging@f5.com> - 1.23.1-1%{?dist}.ngx
- 1.23.1-1

* Tue Jun 21 2022 Nginx Packaging <nginx-packaging@f5.com> - 1.23.0-1%{?dist}.ngx
- 1.23.0-1

* Tue Jan 25 2022 Mikhail Isachenkov <mikhail.isachenkov@nginx.com> - 1.21.6-1%{?dist}.ngx
- 1.21.6-1

* Tue Dec 28 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.5-1%{?dist}.ngx
- 1.21.5-1
- built with PCRE2

* Tue Nov  2 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.4-1%{?dist}.ngx
- 1.21.4-1

* Tue Sep  7 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.3-1%{?dist}.ngx
- 1.21.3-1

* Tue Aug 31 2021 Andrei Belov <defan@nginx.com> - 1.21.2-1%{?dist}.ngx
- 1.21.2-1

* Tue Jul  6 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.1-1%{?dist}.ngx
- 1.21.1-1

* Tue May 25 2021 Konstantin Pavlov <thresh@nginx.com> - 1.21.0-1%{?dist}.ngx
- 1.21.0-1

* Tue Apr 13 2021 Andrei Belov <defan@nginx.com> - 1.19.10-1%{?dist}.ngx
- 1.19.10-1

* Tue Mar 30 2021 Konstantin Pavlov <thresh@nginx.com> - 1.19.9-1%{?dist}.ngx
- 1.19.9-1

* Tue Mar  9 2021 Konstantin Pavlov <thresh@nginx.com> - 1.19.8-1%{?dist}.ngx
- 1.19.8-1

* Tue Feb 16 2021 Konstantin Pavlov <thresh@nginx.com> - 1.19.7-1%{?dist}.ngx
- 1.19.7-1

* Tue Dec 15 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.6-1%{?dist}.ngx
- 1.19.6-1

* Tue Nov 24 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.5-1%{?dist}.ngx
- 1.19.5-1

* Tue Oct 27 2020 Andrei Belov <defan@nginx.com> - 1.19.4-1%{?dist}.ngx
- 1.19.4-1

* Tue Sep 29 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.3-1%{?dist}.ngx
- 1.19.3

* Tue Aug 11 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.2-1%{?dist}.ngx
- 1.19.2

* Tue Jul  7 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.1-1%{?dist}.ngx
- 1.19.1

* Tue May 26 2020 Konstantin Pavlov <thresh@nginx.com> - 1.19.0-1%{?dist}.ngx
- 1.19.0

* Tue Apr 14 2020 Konstantin Pavlov <thresh@nginx.com> - 1.17.10-1%{?dist}.ngx
- 1.17.10

* Tue Mar  3 2020 Konstantin Pavlov <thresh@nginx.com> - 1.17.9-1%{?dist}.ngx
- 1.17.9

* Tue Jan 21 2020 Konstantin Pavlov <thresh@nginx.com> - 1.17.8-1%{?dist}.ngx
- 1.17.8

* Tue Dec 24 2019 Konstantin Pavlov <thresh@nginx.com> - 1.17.7-1%{?dist}.ngx
- 1.17.7

* Tue Nov 19 2019 Konstantin Pavlov <thresh@nginx.com> - 1.17.6-1%{?dist}.ngx
- 1.17.6

* Tue Oct 22 2019 Andrei Belov <defan@nginx.com> - 1.17.5-1%{?dist}.ngx
- 1.17.5

* Tue Sep 24 2019 Konstantin Pavlov <thresh@nginx.com> - 1.17.4-1%{?dist}.ngx
- 1.17.4

* Tue Aug 13 2019 Andrei Belov <defan@nginx.com> - 1.17.3-1%{?dist}.ngx
- 1.17.3

* Tue Jul 23 2019 Konstantin Pavlov <thresh@nginx.com> - 1.17.2-1%{?dist}.ngx
- 1.17.2

* Tue Jun 25 2019 Andrei Belov <defan@nginx.com> - 1.17.1-1%{?dist}.ngx
- 1.17.1

* Tue May 21 2019 Konstantin Pavlov <thresh@nginx.com> - 1.17.0-1%{?dist}.ngx
- 1.17.0

* Tue Apr 16 2019 Konstantin Pavlov <thresh@nginx.com> - 1.15.12-1%{?dist}.ngx
- 1.15.12

* Tue Apr  9 2019 Konstantin Pavlov <thresh@nginx.com> - 1.15.11-1%{?dist}.ngx
- 1.15.11

* Tue Mar 26 2019 Konstantin Pavlov <thresh@nginx.com> - 1.15.10-1%{?dist}.ngx
- 1.15.10

* Tue Feb 26 2019 Konstantin Pavlov <thresh@nginx.com> - 1.15.9-1%{?dist}.ngx
- 1.15.9

* Tue Dec 25 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.8-1%{?dist}.ngx
- 1.15.8

* Tue Nov 27 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.7-1%{?dist}.ngx
- 1.15.7

* Tue Nov  6 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.6-1%{?dist}.ngx
- 1.15.6
- Security: fixes CVE-2018-16843.
- Security: fixes CVE-2018-16844.
- Security: fixes CVE-2018-16845.

* Tue Oct  2 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.5-1%{?dist}.ngx
- 1.15.5

* Tue Sep 25 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.4-1%{?dist}.ngx
- 1.15.4

* Tue Aug 28 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.3-1%{?dist}.ngx
- 1.15.3

* Tue Jul 24 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.2-1%{?dist}.ngx
- 1.15.2

* Tue Jul  3 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.1-1%{?dist}.ngx
- 1.15.1

* Tue Jun  5 2018 Konstantin Pavlov <thresh@nginx.com> - 1.15.0-1%{?dist}.ngx
- 1.15.0

* Mon Apr  9 2018 Konstantin Pavlov <thresh@nginx.com> - 1.13.12-1%{?dist}.ngx
- 1.13.12

* Tue Apr  3 2018 Konstantin Pavlov <thresh@nginx.com> - 1.13.11-1%{?dist}.ngx
- 1.13.11

* Tue Mar 20 2018 Konstantin Pavlov <thresh@nginx.com> - 1.13.10-1%{?dist}.ngx
- 1.13.10

* Tue Feb 20 2018 Konstantin Pavlov <thresh@nginx.com> - 1.13.9-1%{?dist}.ngx
- 1.13.9

* Tue Dec 26 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.8-1%{?dist}.ngx
- 1.13.8

* Tue Nov 21 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.7-1%{?dist}.ngx
- 1.13.7

* Thu Sep 14 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.6-1%{?dist}.ngx
- 1.13.6
- Bugfix: in systemd service support
  (https://trac.nginx.org/nginx/ticket/1380).

* Thu Sep 14 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.5-1%{?dist}.ngx
- 1.13.5

* Tue Aug  8 2017 Sergey Budnevitch <sb@nginx.com> - 1.13.4-1%{?dist}.ngx
- 1.13.4

* Tue Jul 11 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.3-1%{?dist}.ngx
- 1.13.3
- Security: fixes CVE-2017-7529.

* Tue Jun 27 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.2-1%{?dist}.ngx
- 1.13.2

* Tue May 30 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.1-1%{?dist}.ngx
- 1.13.1

* Tue Apr 25 2017 Konstantin Pavlov <thresh@nginx.com> - 1.13.0-1%{?dist}.ngx
- 1.13.0

* Tue Apr  4 2017 Konstantin Pavlov <thresh@nginx.com> - 1.11.13-1%{?dist}.ngx
- 1.11.13
- Made upgrade loops/timeouts configurable via /etc/defaults/nginx.

* Fri Mar 24 2017 Konstantin Pavlov <thresh@nginx.com> - 1.11.12-1%{?dist}.ngx
- 1.11.12

* Tue Mar 21 2017 Konstantin Pavlov <thresh@nginx.com> - 1.11.11-1%{?dist}.ngx
- 1.11.11

* Tue Feb 14 2017 Konstantin Pavlov <thresh@nginx.com> - 1.11.10-1%{?dist}.ngx
- 1.11.10

* Tue Jan 24 2017 Konstantin Pavlov <thresh@nginx.com> - 1.11.9-1%{?dist}.ngx
- 1.11.9
- Extended hardening build flags.
- Added check-reload target to init script / systemd service.

* Tue Dec 27 2016 Konstantin Pavlov <thresh@nginx.com> - 1.11.8-1%{?dist}.ngx
- 1.11.8

* Tue Dec 13 2016 Konstantin Pavlov <thresh@nginx.com> - 1.11.7-1%{?dist}.ngx
- 1.11.7

* Fri Nov 25 2016 Konstantin Pavlov <thresh@nginx.com> - 1.11.6-1%{?dist}.ngx
- 1.11.6

* Mon Oct 10 2016 Andrei Belov <defan@nginx.com> - 1.11.5-1%{?dist}.ngx
- 1.11.5

* Tue Sep 13 2016 Konstantin Pavlov <thresh@nginx.com> - 1.11.4-1%{?dist}.ngx
- 1.11.4
- njs updated to 0.1.2.

* Tue Jul 26 2016 Konstantin Pavlov <thresh@nginx.com> - 1.11.3-1%{?dist}.ngx
- 1.11.3
- njs updated to 0.1.0.
- njs stream dynamic module added to nginx-module-njs package.
- geoip stream dynamic module added to nginx-module-geoip package.

* Tue Jul  5 2016 Konstantin Pavlov <thresh@nginx.com> - 1.11.2-1%{?dist}.ngx
- 1.11.2
- njs updated to ef2b708510b1.

* Tue May 31 2016 Konstantin Pavlov <thresh@nginx.com> - 1.11.1-1%{?dist}.ngx
- 1.11.1

* Tue May 24 2016 Sergey Budnevitch <sb@nginx.com> - 1.11.0-1%{?dist}.ngx
- 1.11.0
- Bugfix: fixed logrotate error if nginx is not running.

* Tue Apr 19 2016 Konstantin Pavlov <thresh@nginx.com> - 1.9.15-1%{?dist}.ngx
- 1.9.15
- njs updated to 1c50334fbea6.

* Tue Apr  5 2016 Konstantin Pavlov <thresh@nginx.com> - 1.9.14-1%{?dist}.ngx
- 1.9.14

* Tue Mar 29 2016 Konstantin Pavlov <thresh@nginx.com> - 1.9.13-1%{?dist}.ngx
- 1.9.13
- Fixed modules path
- Added perl and njs dynamic modules subpackages

* Wed Feb 24 2016 Sergey Budnevitch <sb@nginx.com> - 1.9.12-1%{?dist}.ngx
- 1.9.12
- common configure args are now in variable
- xslt, image-filter and geoip dynamic modules added

* Tue Feb  9 2016 Sergey Budnevitch <sb@nginx.com> - 1.9.11-1%{?dist}.ngx
- 1.9.11
- dynamic modules path and symlink in /etc/nginx added

* Tue Jan 26 2016 Konstantin Pavlov <thresh@nginx.com> - 1.9.10-1%{?dist}.ngx
- 1.9.10

* Wed Dec  9 2015 Konstantin Pavlov <thresh@nginx.com> - 1.9.9-1%{?dist}.ngx
- 1.9.9

* Tue Dec  8 2015 Konstantin Pavlov <thresh@nginx.com> - 1.9.8-1%{?dist}.ngx
- 1.9.8
- http_slice module enabled

* Tue Nov 17 2015 Konstantin Pavlov <thresh@nginx.com> - 1.9.7-1%{?dist}.ngx
- 1.9.7

* Tue Oct 27 2015 Sergey Budnevitch <sb@nginx.com> - 1.9.6-1%{?dist}.ngx
- 1.9.6

* Tue Sep 22 2015 Andrei Belov <defan@nginx.com> - 1.9.5-1%{?dist}.ngx
- 1.9.5
- http_spdy module replaced with http_v2 module

* Tue Aug 18 2015 Konstantin Pavlov <thresh@nginx.com> - 1.9.4-1%{?dist}.ngx
- 1.9.4

* Tue Jul 14 2015 Sergey Budnevitch <sb@nginx.com> - 1.9.3-1%{?dist}.ngx
- 1.9.3

* Tue Jun 16 2015 Sergey Budnevitch <sb@nginx.com> - 1.9.2-1%{?dist}.ngx
- 1.9.2

* Tue May 26 2015 Sergey Budnevitch <sb@nginx.com> - 1.9.1-1%{?dist}.ngx
- 1.9.1

* Tue Apr 28 2015 Sergey Budnevitch <sb@nginx.com> - 1.9.0-1%{?dist}.ngx
- 1.9.0
- thread pool support added
- stream module added
- example_ssl.conf removed

* Tue Apr  7 2015 Sergey Budnevitch <sb@nginx.com> - 1.7.12-1%{?dist}.ngx
- 1.7.12

* Tue Mar 24 2015 Sergey Budnevitch <sb@nginx.com> - 1.7.11-1%{?dist}.ngx
- 1.7.11

* Tue Feb 10 2015 Sergey Budnevitch <sb@nginx.com> - 1.7.10-1%{?dist}.ngx
- 1.7.10

* Tue Dec 23 2014 Sergey Budnevitch <sb@nginx.com> - 1.7.9-1%{?dist}.ngx
- 1.7.9
- init-script now sends signal only to the PID derived from pidfile

* Tue Dec  2 2014 Sergey Budnevitch <sb@nginx.com> - 1.7.8-1%{?dist}.ngx
- 1.7.8
- package with debug symbols added

* Tue Oct 28 2014 Sergey Budnevitch <sb@nginx.com> - 1.7.7-1%{?dist}.ngx
- 1.7.7

* Tue Sep 30 2014 Sergey Budnevitch <sb@nginx.com> - 1.7.6-1%{?dist}.ngx
- 1.7.6

* Tue Sep 16 2014 Sergey Budnevitch <sb@nginx.com> - 1.7.5-1%{?dist}.ngx
- 1.7.5

* Tue Aug  5 2014 Sergey Budnevitch <sb@nginx.com> - 1.7.4-1%{?dist}.ngx
- 1.7.4
- init-script now returns 0 on stop command if nginx is not running

* Tue Jul  8 2014 Sergey Budnevitch <sb@nginx.com> - 1.7.3-1%{?dist}.ngx
- 1.7.3

* Tue Jun 17 2014 Sergey Budnevitch <sb@nginx.com> - 1.7.2-1%{?dist}.ngx
- 1.7.2

* Tue May 27 2014 Sergey Budnevitch <sb@nginx.com> - 1.7.1-1%{?dist}.ngx
- 1.7.1

* Thu Apr 24 2014 Konstantin Pavlov <thresh@nginx.com> - 1.7.0-1%{?dist}.ngx
- 1.7.0

* Tue Apr  8 2014 Sergey Budnevitch <sb@nginx.com> - 1.5.13-1%{?dist}.ngx
- 1.5.13

* Tue Mar 18 2014 Sergey Budnevitch <sb@nginx.com> - 1.5.12-1%{?dist}.ngx
- 1.5.12
- warning added when binary upgrade returns non-zero exit code

* Tue Mar  4 2014 Sergey Budnevitch <sb@nginx.com> - 1.5.11-1%{?dist}.ngx
- 1.5.11

* Tue Feb  4 2014 Sergey Budnevitch <sb@nginx.com> - 1.5.10-1%{?dist}.ngx
- 1.5.10

* Wed Jan 22 2014 Sergey Budnevitch <sb@nginx.com> - 1.5.9-1%{?dist}.ngx
- 1.5.9

* Tue Dec 17 2013 Sergey Budnevitch <sb@nginx.com> - 1.5.8-1%{?dist}.ngx
- 1.5.8

* Fri Nov 29 2013 Sergey Budnevitch <sb@nginx.com> - 1.5.7-1%{?dist}.ngx
- 1.5.7
- init script now honours additional options sourced from /etc/default/nginx

* Tue Oct  1 2013 Sergey Budnevitch <sb@nginx.com> - 1.5.6-1%{?dist}.ngx
- 1.5.6

* Tue Sep 17 2013 Andrei Belov <defan@nginx.com> - 1.5.5-1%{?dist}.ngx
- 1.5.5

* Tue Aug 27 2013 Sergey Budnevitch <sb@nginx.com> - 1.5.4-1%{?dist}.ngx
- 1.5.4
- auth request module added

* Tue Jul 30 2013 Sergey Budnevitch <sb@nginx.com> - 1.5.3-1%{?dist}.ngx
- 1.5.3

* Tue Jul  2 2013 Sergey Budnevitch <sb@nginx.com> - 1.5.2-1%{?dist}.ngx
- 1.5.2

* Tue Jun  4 2013 Sergey Budnevitch <sb@nginx.com> - 1.5.1-1%{?dist}.ngx
- 1.5.1
- dpkg-buildflags options now passed by --with-{cc,ld}-opt

* Mon May  6 2013 Sergey Budnevitch <sb@nginx.com> - 1.5.0-1%{?dist}.ngx
- 1.5.0
- fixed openssl version detection with dash as /bin/sh

* Tue Apr 16 2013 Sergey Budnevitch <sb@nginx.com> - 1.3.16-1%{?dist}.ngx
- 1.3.16

* Tue Mar 26 2013 Sergey Budnevitch <sb@nginx.com> - 1.3.15-1%{?dist}.ngx
- 1.3.15
- gunzip module added
- spdy module added if openssl version >= 1.0.1
- set permissions on default log files at installation
