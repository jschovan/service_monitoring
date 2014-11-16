"""
    sls_scraper
    
"""
import commands
import ConfigParser
import json
import re
import sys
from datetime import datetime
from os.path import join, pardir, abspath, dirname, split
from BeautifulSoup import BeautifulSoup


class Scraper(object):
    CONFIG_FILE = join(abspath(dirname(__file__)), 'settings', 'settings-sls.cfg')
    
    def __init__(self, config_file=None):
        if config_file is not None:
            self.CONFIG_FILE = config_file
        self.configure()
    
    
    def configure(self):
        """
            configure: Read configuration from config_file.
            :param config_file: config file in the ini format
        """
#        printv(u'###### %s() IN' % (inspect.stack()[0][3]), VERB_STANDARD)

        config = ConfigParser.SafeConfigParser()
        config.read(self.CONFIG_FILE)

        self.PAGE_ADDRESS = config.get('AddressInfo', 'page_address')
        self.PAGE_CONTENT_DIRECTORY = config.get('Debugging', 'page_content_directory')
        self.PAGE_URL_PREFIX = config.get('Debugging', 'page_url_prefix')
#        try:
#            self.IGNORED_ERRORS = re.sub('\n', '', config.get('Errors', 'ignored_errors')).split(',')
#        except:
#            self.IGNORED_ERRORS = []
        self.ALL_ANCHORS = []
        self.ALL_CLICKABLE_ANCHORS = []
        self.COOKIES_LOCATION = config.get('CookiesInfo', 'cookies_location')
        self.URLS_LIST_FILE = join(abspath(dirname(self.CONFIG_FILE)), \
                                   'URL-list', config.get('URLs', 'urls_list'))
        self.URLS_LIST = []
        try:
            f = open(self.URLS_LIST_FILE, 'r')
            self.URLS_LIST = [x.replace('\n', '')  for x in f.readlines() if x != '\n']
            f.close()
        except:
            pass
        self.URLS_PREFIXES = []
        try:
            self.URLS_PREFIXES = re.sub('\n', '', config.get('URLs', 'urls_prefixes')).split(',')
        except:
            self.URLS_PREFIXES = []
        print 'URLS_PREFIXES:', self.URLS_PREFIXES
        self.URLS = {}


    def fetch_url(self, url):
        ### get CERN SSO cookie
        cmd = 'cern-get-sso-cookie --krb -r -u "%(url)s" -o %(cookie_file)s ' % \
            {'url': url, 'cookie_file': self.COOKIES_LOCATION}
        print 'cmd:[%s]' % (cmd)
        status, output = commands.getstatusoutput(cmd)
        ### get the URL
        out_file = join(abspath(dirname(self.PAGE_CONTENT_DIRECTORY)), \
                    str(url).replace(':', '').replace('/', '__')).replace('&', '__').replace('=', '_eq_')
        cmd = 'wget --load-cookies %(cookie_file)s "%(url)s" -O %(out_file)s' % \
            {'cookie_file': self.COOKIES_LOCATION, 'url': url, \
             'out_file': out_file}
        print 'cmd:[%s]' % (cmd)
        status, output = commands.getstatusoutput(cmd)
        ### return the output file path
        return out_file


    def get_url_list_from_page(self, page_file):
        f = open(page_file, 'r')
        document = f.read()
        f.close()
        page_html = BeautifulSoup(document)
        all_anchors = page_html.findAll('a')
        anchors = []
        for an in all_anchors:
            if an is not None:
                href = None
                text = None
                try:
                    href = an['href']
                except:
                    href = None
                if href is not None:
                    for href_prefix in self.URLS_PREFIXES:
                        if href.startswith(href_prefix) and \
                            re.search('reload=', href) is None:
                            text = an.text
                if href is not None and text is not None:
                    anchors.append({'href': href, 'text': text})
        print 'anchors for %s:' % page_file, anchors
        return anchors


    def visit_children(self, url):
        if url.startswith('http://sls.cern.ch/sls/static/'):
            url_short = url.replace('http://sls.cern.ch/sls/static/', 'static/')
        else:
            url_short = str(url).replace(self.PAGE_ADDRESS, '')
        if url_short in self.URLS.keys():
            for child_url_item in self.URLS[url_short]:
                child_url_short = child_url_item['href']
                if child_url_short not in self.URLS.keys():
                    self.process_url(child_url_short)


    def process_url(self, url):
        url_short = str(url).replace(self.PAGE_ADDRESS, '')
        url_long = url
        if not url.startswith('https:') and not url.startswith('http:'):
            url_long = '%s%s' % (self.PAGE_ADDRESS, url)
        print '### Processing URL: short[%s] long[%s]' % (url_short, url_long)
        out_file = self.fetch_url(url_long)
        anchors = self.get_url_list_from_page(out_file)
        self.URLS[url_short] = anchors
        self.visit_children(url_short)
    
    
    def save_visited_urls(self):
        file_visited_urls = join(abspath(dirname(self.PAGE_CONTENT_DIRECTORY)), \
                    'visited_urls.json', datetime.utcnow().strftime('%F.%H%M%S'))
        f = open(file_visited_urls, 'w')
        f.write(json.dumps(self.URLS_LIST, indent=2, sort_keys=True))
        f.close()
    

    def run(self):
        for url in self.URLS_LIST:
            self.process_url(url)
        self.save_visited_urls()


if __name__ == '__main__':
    args = sys.argv[1:]
    print ':66'
    if len(args) == 1:
        scraper = Scraper(args[0])
    else:
        scraper = Scraper()
    print ':71'
    scraper.run()
    print ':73'


