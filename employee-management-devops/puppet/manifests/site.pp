# Master Puppet site manifest (site.pp)

# Global default file bucket for file backups
filebucket { 'main':
  path   => false,
  server => 'puppet.internal',
}

File { backup => 'main' }

# Global default exec search path
Exec {
  path => ['/usr/bin', '/bin', '/usr/sbin', '/sbin', '/usr/local/bin'],
}

# Import node classifications
import 'nodes.pp'

# Default fallback node
node default {
  notify { "Node ${::trusted['certname']} connected with unclassified role": }

  # Baseline packages
  package { ['curl', 'htop', 'git']:
    ensure => installed,
  }
}
