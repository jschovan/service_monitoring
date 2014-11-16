ATLAS Service Monitoring - SLS scraper
=====

Scraper visits all SLS monitor pages from the URL configuration file (and their
children pages), and downloads them and configuration XML files. 

Dependencies: CERN SSO COOKIE package: http://linux.web.cern.ch/linux/docs/cernssocookie.shtml


Configuration
-----
URL configuration file:
sls\_scraper/settings/URL-list/list-URLs\_sls.sls.cern.ch.cfg. Urls listed in
this file will be starting point to the all-pages visits. If a page has already
been visited this scraper run, it will not be visited for the 2nd time. 

General configuration file: sls\_scraper/settings/settings-sls.cfg.

  AddressInfo.page\_address represents the base URL of the SLS monitoring pages.
  ```
[AddressInfo]
### base URL 
page_address = https://sls.cern.ch/sls/
 
  ```

  CookiesInfo.cookies\_location represents full path of your CERN SSO cookie
  file. Please note you should store your CERN SSO cookie only in your
  ~/private directory. Cookie expires within 24 hours. A cookie is needed for
  each page (for each page fetch a new cookie is created).  
  ```
[CookiesInfo]
### CERN SSO cookies file location
cookies_location = /afs/cern.ch/user/j/jschovan/private/SLSmon/ssocookie.txt
  ```

  Visited SLS monitor pages are dumped under local directory in 
  Debugging.page\_content\_directory. 
  ```
[Debugging]
### location of the fetched SLSmon pages, local and HTTP-accessible
page_content_directory = /data/jschovan/slsmon/download/sls/
page_url_prefix = 
  
  ```

  We can configure the scraper to download only the service pages, service
  admin tools pages, and the service XML description (static XML). This
  configuration is done in URLs.urls\_prefixes. 

  File name of the configuration file with the list of top level URLs to visit
  can be set up with URLs.urls\_list. However, the URLs.urls\_list file is
  expected to be in sls\_scraper/settings/URL-list/ directory.

  ```
[URLs]
urls_list = list-URLs_sls.sls.cern.ch.cfg
urls_prefixes = service.php,service_adm.php,http://sls.cern.ch/sls/static/
  ```

sls\_scraper/settings/settings-sls.cfg.

How to run
-----
  ```
# cd sls\_scraper/
# ls
__init__.py  README.md  settings  sls\_scraper.py
# export PYTHONPATH=$PWD:$PYTHONPATH
# python sls\_scraper.py
  ```


