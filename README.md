# collectd-solr
Collectd Solr Plugin in Python

# Installation
1. Place collectd-solr.py in /usr/share/collectd/collectd-solr
2. Configure the plugin (see below).
3. Restart collectd.

# Configuration
```
LoadPlugin python
<Plugin python>
  ModulePath "/usr/share/collectd/collectd-solr"
  Import "collectd-solr"
  <Module "collectd-solr">
    Host "localhost"
    Port 8983
    Interval 10
    Instance "solr1"
  </Module>
</Plugin>
```
