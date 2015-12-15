#!/usr/bin/env python
#
# Collectd plugin for collecting solr container stats


import collectd
import requests, socket


VERBOSE_LOGGING = True


# setup logging
def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('Collectd-Solr Plugin: {}'.format(msg))


class Solr(object):
    def __init__(self, host='localhost', port=8983, status='OVERSEERSTATUS'):
        self.host = host
        self.port = port
        self.status = status


    def get_status(self):
        """Execute to Solr status command and return JSON object"""
        url = 'http://{}:{}/solr/admin/collections?action={}&wt=json'.format(self.host, self.port, self.status)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                reply = r.json()
        except Exception as e:
            log_verbose('collectd-solr plugin: can\'t get {} info, with error message {}'.format(self.status, e.message))
        return reply


    def get_leader(self):
        return 1 if socket.gethostname() in self.get_status()[u'leader'] else 0

    def get_overseer_queue_size(self):
        return self.get_status()[u'overseer_queue_size']


    def get_overseer_work_queue_size(self):
        return self.get_status()[u'overseer_work_queue_size']


    def get_overseer_collection_queue_size(self):
        return self.get_status()[u'overseer_collection_queue_size']


class SolrPlugin(object):
    def __init__(self):
        self.SOLR_HOST = 'localhost'
        self.SOLR_PORT = 8983
        self.SOLR_STATUS = 'OVERSEERSTATUS'
        self.SOLR_INTERVAL = 1
        self.SOLR_INSTANCE = ""


    def configure_callback(self, conf):
        """Receive configuration block"""
        for node in conf.children:
            if node.key == 'Host':
                self.SOLR_HOST = node.values[0]
            elif node.key == 'Port':
                self.SOLR_PORT = int(node.values[0])
            elif node.key == 'Status':
                self.SOLR_STATUS = node.values[0]
            elif node.key == 'Interval':
                self.SOLR_INTERVAL = int(float(node.values[0]))
            elif node.key == 'Instance':
                self.SOLR_INSTANCE = node.values[0]
            else:
                collectd.warning('collectd-solr plugin: Unknown config key: {}.'.format(node.key))
        log_verbose('Configured: host={}, port={}, status={}, interval={}, instance={}'.format(self.SOLR_HOST, self.SOLR_PORT, self.SOLR_STATUS, self.SOLR_INTERVAL, self.SOLR_INSTANCE))


    def dispatch_value(self, type_instance, value, value_type, plugin_instance):
        val = collectd.Values(plugin='solr')
        val.type_instance = type_instance
        val.type = value_type
        val.values = [value]
        val.plugin_instance = plugin_instance
        val.dispatch()


    def read_callback(self):
        log_verbose('Read Callback Called')
        solr = Solr(self.SOLR_HOST, self.SOLR_PORT, self.SOLR_STATUS)
        self.dispatch_value('leader', solr.get_leader(), 'gauge', self.SOLR_INSTANCE)
        self.dispatch_value('overseer_queue_size', solr.get_overseer_queue_size(), 'gauge', self.SOLR_INSTANCE)
        self.dispatch_value('overseer_work_queue_size', solr.get_overseer_collection_queue_size(), 'gauge', self.SOLR_INSTANCE)
        self.dispatch_value('overseer_collection_queue_size', solr.get_overseer_collection_queue_size(), 'gauge', self.SOLR_INSTANCE)


# register callbacks
plugin = SolrPlugin()
collectd.register_config(plugin.configure_callback)
collectd.register_read(plugin.read_callback, plugin.SOLR_INTERVAL)