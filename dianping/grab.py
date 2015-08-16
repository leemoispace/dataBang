# -*- Encoding: utf-8 -*-
import re
import os

import sys
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent)

from crawler.download import RecursiveJob, builk_single
from crawler.model import install, Peer


# config
BASE_DIR = os.path.dirname(__file__)
shop_prof_dir = os.path.join(BASE_DIR, 'cache/shop_prof')

for path in [shop_prof_dir]:
    if not os.path.exists(path):
        os.makedirs(path)

# const
sid_ptn = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"')


class ShopProfPeer(Peer):
    __tablename__ = 'ShopProfPeer'


def init_shop_prof_job(session):
    fn_key = lambda fn: fn.endswith('.html') and fn[:-5]

    jobs = RecursiveJob(sid_ptn, ShopProfPeer, session)
    jobs.build_idx(shop_prof_dir, fn_key)


def grab_shop_prof(session):
    page_name = 'DianPing Shop Profile'
    url = 'http://www.dianping.com/shop/{}'
    jobs = RecursiveJob(sid_ptn, ShopProfPeer, session)

    todo = jobs.get_todo()
    if not todo:
        init_shop_prof_job(session)
        todo = jobs.get_todo()

    while todo:
        print 'grabbing shop prof. total: {}'.format(len(todo))
        builk_single(todo, url, shop_prof_dir, jobs.feed, page_name)
        todo = jobs.get_todo()
    else:
        print 'no shop id found'


if __name__ == '__main__':
    db_pf = 'sqlite:///cache/db_profile.sqlite3'
    Session = install(db_pf)
    session = Session()

    if len(sys.argv) > 1 and sys.argv[1] == 'init':
        init_shop_prof_job(session)
    else:
        grab_shop_prof(session)

    session.close()
