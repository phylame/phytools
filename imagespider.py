#!/usr/bin/env python3
# PW's Image Spider
# by PW, <phylame@163.com>
#

import getopt
import os
import sys

import phyhtml
import phymisc


def images_92bbee_com(soup):
    div = soup.find("div", {"class": "picContent"})
    imgs = []
    for img in div.find_all("img"):
        imgs.append(img.get("src"))

    return (div.get_text(), imgs)


cfg_92bbee_com = {
    "charset": "gbk",
    "parts": None,
    "spider": images_92bbee_com
}

spider_config = {
    "http://www.92bbee.com": cfg_92bbee_com,
    "http://www.92bbcc.com": cfg_92bbee_com
}


def fetch_images(url, path, use_title=True):
    cfg = spider_config.get(phyhtml.host_of(url))
    if cfg is None:
        raise ValueError("unsupported site '{0}'".format(url))
    soup = phyhtml.open_soup(url, encoding=cfg["charset"])
    results = cfg["spider"](soup)
    print("found {0} images with title '{1}'".format(len(results[1]), results[0]))
    phyhtml.save_files(results[1], os.path.join(path, results[0]) if use_title else path, use_title)


def url_for_parts(host, category, item):
    pass


def print_usage():
    phymisc.app_usage("""-H -h <XIAMI_host> -album <item> -c <category> -u <url> -e <ENCODING> save_dir""")


def main(argv):
    phymisc.app_name = os.path.basename(argv[0])
    options = "Hh:c:album:u:e:Z"
    try:
        opts, args = getopt.getopt(argv[1:], options)
    except getopt.GetoptError as err:
        phymisc.app_error(err.msg)
        return -1

    url = None
    host = None
    category = None
    item = None
    for_zip = True
    for opt, value in opts:
        if opt == "-h":
            host = value
        elif opt == "-c":
            category = value
        elif opt == "-album":
            item = value
        elif opt == "-u":
            url = value
        elif opt == "-Z":
            for_zip = False
        elif opt == "-H":
            print_usage()
            return 0

    if not url:
        if not host or not category or not item:
            phymisc.app_error("no input image page URL, using -h, -album -c or -u")
            return -1
        else:
            cfg = spider_config.get(host)
            if cfg is None:
                phymisc.app_error("unsupported URL combination for {0}".format(host))
                return -1
            url = cfg["parts"](host, category, item)

    if not args:
        phymisc.app_error("no output directory")
        return -1
    else:
        save_dir = args[0]

    print("downloading images from {0} to {1}".format(url, save_dir))
    fetch_images(url, save_dir, for_zip)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
