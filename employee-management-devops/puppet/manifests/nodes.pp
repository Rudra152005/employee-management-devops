# Node Classification Definitions (nodes.pp)

# Base class applied to all nodes in the infrastructure
class base_node {
  package { ['chrony', 'sudo', 'ufw']:
    ensure => installed,
  }

  service { 'chrony':
    ensure     => running,
    enable     => true,
    hasrestart => true,
    require    => Package['chrony'],
  }
}

# Node 1: Web Server 01 (Runs Application + MySQL DB)
node /.*(172\.31\.41\.56|web-01|ip-172-31-41-56).*/ {
  include base_node
  include db_server
  include app_server

  notify { "Configuring Primary Web & Database Node: ${::fqdn}": }
}

# Node 2: Web Server 02 (Runs Application)
node /.*(172\.31\.44\.210|web-02|ip-172-31-44-210).*/ {
  include base_node
  include app_server

  notify { "Configuring Secondary Web Node: ${::fqdn}": }
}

# Fallback node classification
node default {
  include base_node
}
