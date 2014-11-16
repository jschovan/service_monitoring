"""
    sls_topology
    
"""
import commands
import ConfigParser
import json
import re
import sys
from datetime import datetime
from os import listdir
from os.path import join, pardir, abspath, dirname, split, isfile
from BeautifulSoup import BeautifulSoup
from graphviz import Digraph


class SLSTopology(object):
    CONFIG_FILE = join(abspath(dirname(__file__)), 'settings', 'settings-sls-topology.cfg')
    
    def __init__(self, config_file=None):
        if config_file is not None:
            self.CONFIG_FILE = config_file
        self.configure()
    
    
    def configure(self):
        """
            configure: Read configuration from config_file.
            :param config_file: config file in the ini format
        """
        config = ConfigParser.SafeConfigParser()
        config.read(self.CONFIG_FILE)

        self.STATUS = config.get('Data', 'status')
        self.DIR_SOURCE_XML = config.get('Data', 'dir_source_xml')
        self.DIR_SOURCE_GROUP = []
        try:
            self.DIR_SOURCE_GROUP = re.sub('\n', '', config.get('Data', 'groups')).split(',')
        except:
            self.DIR_SOURCE_GROUP = []
        self.DIR_OUTPUT = config.get('Data', 'dir_output')
        self.TAGS=[]
        try:
            self.TAGS = re.sub('\n', '', config.get('Document', 'tags')).split(',')
        except:
            self.TAGS = []
        self.TOPOLOGY = {}
        self.DOT = None
        if self.STATUS == 'prod':
            self.TIMESTAMP = ''
        else:
            self.TIMESTAMP = '-' + datetime.utcnow().strftime('%F.%H%M%S')


    def list_xml_files(self, group='empty'):
        files = []
        files = [ join(self.DIR_SOURCE_XML, group, f) \
                    for f in listdir(join(self.DIR_SOURCE_XML, group)) \
                    if isfile(join(self.DIR_SOURCE_XML, group, f)) ]
        return files


    def read_xml(self, file):
        f_data = None
        f = open(file, 'r')
        f_data = f.read()
        f.close()
        return f_data


    def get_document_data(self, document):
        document_data = {}
        ### prepare document for parsing
        page_html = BeautifulSoup(document)
        structured_tags = [ x for x in self.TAGS \
                            if re.search(':', x) is not None ]
        simple_tags = [ x for x in self.TAGS \
                            if re.search(':', x) is None ]
        ### loop through listed tags
        for tag in simple_tags:
            ### simple, not structured tag
            tag_data = page_html.findAll(tag)
            tag_data_list = []
            for tag_data_item in tag_data:
                text = tag_data_item.text
                if len(text):
                    tag_data_list.append(text)
            if len(tag_data_list):
                document_data[tag] = tag_data_list[0]
        for tag in structured_tags:
            parent_tag = tag.split(':')[0]
            document_data[parent_tag] = {}
            child_tags = tag.split(':')[1].split('|')
            child_tag_data_list = []
            for child_tag in child_tags:
                child_tag_data = page_html.findAll(child_tag)
                for child_tag_data_item in child_tag_data:
                    text = child_tag_data_item.text
                    if len(text):
                        child_tag_data_list.append(text)
                if len(child_tag_data_list):
                    document_data[parent_tag][child_tag] = child_tag_data_list
        return document_data


    def parse_xml(self, file):
        document = self.read_xml(file)
        document_data = self.get_document_data(document)
        document_id = document_data['id']
        return document_id, document_data


    def process_xml(self, file, group):
        key, document_data = self.parse_xml(file)
        if group not in self.TOPOLOGY.keys():
            self.TOPOLOGY[group] = {}
        self.TOPOLOGY[group][key] = document_data


    def safe_group(self, group):
        return group.replace('/', '.')


    def save_topology_json(self, group='empty'):
        file_topology = join(abspath(dirname(self.DIR_OUTPUT)), \
                    'sls_topology-' + 'gr_' + self.safe_group(group) \
                    + self.TIMESTAMP + '.json')
        print 'file_topology:', file_topology
        f = open(file_topology, 'w')
        f.write(json.dumps(self.TOPOLOGY[group], indent=2, sort_keys=True))
        f.close()


    def get_digraph(self, group='empty'):
        dot = Digraph(comment='SLS Topology for metaservice group' + group, \
                      name='sls_topology__gr_' + group, engine='circo', \
                      node_attr={'fontsize':'14'}, \
                      graph_attr={'overlap':'false'})
        for node_id in self.TOPOLOGY[group].keys():
            ### get node name
            try:
                node_name = self.TOPOLOGY[group][node_id]['fullname']
            except:
                node_name = node_id
            ### get node subservices
            node_subservices_list = []
            try:
                node_subservices = self.TOPOLOGY[group][node_id]['subservices']
                node_subservices_list = self.TOPOLOGY[group][node_id]['subservices']['subservice']
            except:
                node_subservices = None
            ### add node to the directed graph
            dot.node(str(node_id), str(node_name))
            ### add edges to the directed graph
            if len(node_subservices_list):
                edges = []
                for node_subservice in node_subservices_list:
                    dot.edge(str(node_subservice), str(node_id))
        self.DOT = dot


    def save_topology_dot(self, group='empty'):
        file_topology_base = join(abspath(dirname(self.DIR_OUTPUT)), \
                    'sls_topology-' + 'gr_' + self.safe_group(group) \
                    + self.TIMESTAMP)
        file_topology_dot = '%s.dot' % (file_topology_base)
        print 'file_topology_dot:', file_topology_dot
        f = open(file_topology_dot, 'w')
        f.write(self.DOT.source)
        f.close()
        ### dump PDF file
        file_topology_pdf = '%s.pdf' % (file_topology_base)
        print 'file_topology_pdf:', file_topology_pdf
#        self.DOT.render(file_topology_pdf, view=True)
        cmd = 'sfdp -x -Goverlap=scale -T%(extension)s %(dotfile)s > %(outfile)s' % \
            {'extension': 'pdf', 'outfile': file_topology_pdf, \
             'dotfile': file_topology_dot}
        status, output = commands.getstatusoutput(cmd)
        ### dump PNG file
        file_topology_png = '%s.png' % (file_topology_base)
        print 'file_topology_png:', file_topology_png
        cmd = 'sfdp -x -Goverlap=scale -T%(extension)s %(dotfile)s > %(outfile)s' % \
            {'extension': 'png', 'outfile': file_topology_png, \
             'dotfile': file_topology_dot}
        status, output = commands.getstatusoutput(cmd)


    def run(self):
        for group in self.DIR_SOURCE_GROUP:
            print '### Processing group %s' % (group)
            for xml_file in self.list_xml_files(group):
                self.process_xml(xml_file, group)
            self.save_topology_json(group)
            self.get_digraph(group)
            self.save_topology_dot(group)
            print '### Finished processing group %s' % (group)



if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 1:
        topology = SLSTopology(args[0])
    else:
        topology = SLSTopology()
    topology.run()


