# Database Server Puppet Module
class db_server {

  package { ['mysql-server', 'mysql-client']:
    ensure => installed,
  }

  file { '/etc/mysql/mysql.conf.d/mysqld.cnf':
    ensure  => file,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => template('db_server/my.cnf.erb'),
    require => Package['mysql-server'],
    notify  => Service['mysql'], # Trigger automatic restart on drift
  }

  service { 'mysql':
    ensure     => running,
    enable     => true,
    hasrestart => true,
    hasstatus  => true,
    require    => Package['mysql-server'],
  }
}
