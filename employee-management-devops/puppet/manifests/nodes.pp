# Node Classification Definitions (nodes.pp)

# Base class applied to all nodes in the infrastructure
class base_node {
  package { ['chrony', 'sudo', 'ufw', 'fail2ban']:
    ensure => installed,
  }

  service { 'chrony':
    ensure     => running,
    enable     => true,
    hasrestart => true,
    require    => Package['chrony'],
  }
}

# Application Servers classification (matches app-server-01, app-01.internal, etc.)
node /^app.*\.internal$/ {
  include base_node
  include app_server

  notify { "Configuring Application Node: ${::fqdn}": }
}

# Database Servers classification (matches db-server-01, db-01.internal, etc.)
node /^db.*\.internal$/ {
  include base_node
  include db_server

  notify { "Configuring Database Node: ${::fqdn}": }
}
