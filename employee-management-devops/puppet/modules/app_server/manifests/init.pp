# Application Server Puppet Module
class app_server {

  # Enforce runtime dependencies
  $app_packages = ['python3', 'python3-pip', 'python3-venv', 'nginx', 'git']

  package { $app_packages:
    ensure => installed,
  }

  # Ensure Application User and Directory
  user { 'appuser':
    ensure     => present,
    home       => '/opt/employee-app',
    managehome => true,
    shell      => '/bin/bash',
  }

  file { '/opt/employee-app':
    ensure  => directory,
    owner   => 'appuser',
    group   => 'appuser',
    mode    => '0755',
    require => User['appuser'],
  }

  # Nginx Configuration Enforcement (Self-Healing Configuration Drift)
  file { '/etc/nginx/sites-available/default':
    ensure  => file,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => template('app_server/nginx.conf.erb'),
    require => Package['nginx'],
    notify  => Service['nginx'], # Automatic restart on config drift detection
  }

  service { 'nginx':
    ensure     => running,
    enable     => true,
    hasrestart => true,
    hasstatus  => true,
    require    => Package['nginx'],
  }

  # Application Systemd Service State Enforcement
  service { 'employee-app':
    ensure     => running,
    enable     => true,
    hasrestart => true,
    hasstatus  => true,
  }
}
