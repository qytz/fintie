TODO
=============

股票停复牌数据
------------------
queryType1 -- 所有停牌信息
其他 type 未知
::

    curl 'http://www.cninfo.com.cn/cninfo-new/memo-2?queryDate=2017-06-14&queryType=queryType1' -H 'Host: www.cninfo.com.cn' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Referer: http://www.cninfo.com.cn/cninfo-new/memo-2' -H 'Cookie: JSESSIONID=74E33FB2153B4B12DE227654C18AA7CF; JSESSIONID=62A5434F4C65CBE37E5582D131F49576; cninfo_search_record_cookie=%E8%B4%B5%E5%B7%9E%E8%8C%85%E5%8F%B0' -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1'

雪球实时财经新闻
----------------------

https://xueqiu.com/v4/statuses/public_timeline_by_category.json?category=6

雪球讨论
------------

* 全部-新帖
  https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=SZ002456&hl=0&source=all&sort=time&page=1&q=

* 全部-热帖
  https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=SZ002456&hl=0&source=all&sort=alpha&page=1&q=

* 讨论
  https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=SZ002456&hl=0&source=user&sort=time&page=1&q=

* 交易
  https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=SZ002456&hl=0&source=trans&page=1&q=

* 新闻
  https://xueqiu.com/statuses/stock_timeline.json?symbol_id=SZ002456&count=10&source=自选股新闻&page=1

* 公告
  https://xueqiu.com/statuses/stock_timeline.json?symbol_id=SZ002456&count=10&source=公告&page=1

* 研报
  https://xueqiu.com/statuses/stock_timeline.json?symbol_id=SZ002456&count=10&source=研报&page=1


股票行业、概念数据
------------------

沪深港通成交统计信息
----------------------

上市公司基金持股信息
--------------------------
    http://vip.stock.finance.sina.com.cn/corp/go.php/vci_fundstockholder/stockid/000001/displaytype/30.phtml

上市公司更名数据获取
----------------------
    深交所官网：http://www.szse.cn/main/marketdata/jypz/ssgsgmxx/

融资融券成交统计信息
----------------------

限售解禁信息获取
----------------------

券商研报
----------------------

期货数据
-------------------

宏观数据
----------------------

