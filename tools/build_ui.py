#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青岛导览地图 v3 —— 双菜单 UI
  菜单1 总览      : 分类手风琴 -> 地点名单 -> 点击缩放定位
  菜单2 今天怎么玩 : 选天气(晴/阴/雨) -> 上午/下午/晚上 三时段
     晴 = 全部显示
     阴 = 户外全留，登高观景类降权(排末尾+提示)
     雨 = 默认隐藏户外，仅室内(可一键临时显示)
  天气可随时切换：晴了 / 阴了 / 下雨了
已按用户要求移除"餐饮"分类。
"""
import json, base64, os, csv, math, re

BASE = os.path.dirname(os.path.abspath(__file__))
LEAFLET_JS  = open(os.path.join(BASE,"leaflet.js"), encoding="utf-8").read()
LEAFLET_CSS = open(os.path.join(BASE,"leaflet.css"), encoding="utf-8").read()

# ---- 瘦身：本项目用不到的 Leaflet 资源一律不打包 ----
# 1) sourceMap 注释指向不存在的 leaflet.js.map，浏览器每次都会白跑一趟
LEAFLET_JS = re.sub(r"//# sourceMappingURL=\S+\s*$", "", LEAFLET_JS).rstrip() + "\n"
# 2) 图层控件已删除（只有高德一个底图），它的两张 PNG 不必再 base64 内联
LEAFLET_CSS = LEAFLET_CSS.replace("url(images/marker-icon.png)","none")
# 3) 移除只服务于图层控件 / 默认 marker 图片的 CSS 规则
_DROP = ("leaflet-control-layers","leaflet-default-icon-path")
_keep=[]
for _rule in re.split(r"(?<=\})", LEAFLET_CSS):
    if any(k in _rule.split("{")[0] for k in _DROP):   # 只看选择器部分
        continue
    _keep.append(_rule)
LEAFLET_CSS = "".join(_keep)

HOTEL = (36.06344, 120.31192)

# name, lat, lon, cat, src, desc, price, timetxt, traffic, slots, outdoor, elevated
#   slots: m=上午(含清晨) a=下午(含正午) e=晚上(含傍晚)   ""=不进"怎么玩"菜单
#   outdoor: 1=户外(雨天默认隐藏)  0=室内/可避雨
#   elevated: 1=登高观景/依赖能见度(阴天降权)
from data_new import P, CATS, PEOPLE   # 单一数据源
from i18n_ru import UI, CATS_RU, price_ru, time_ru, traf_ru, EMERGENCY, PHRASES, CONSUL
from i18n_poi import NAME as NAME_RU, DESC as DESC_RU, PEOPLE_RU

def dist(a,b):
    R=6371;p=math.pi/180
    x=math.sin((b[0]-a[0])*p/2)**2+math.cos(a[0]*p)*math.cos(b[0]*p)*math.sin((b[1]-a[1])*p/2)**2
    return R*2*math.asin(math.sqrt(x))

pts=[]
for (n,la,lo,c,s,d,pr,t,tr,sl,od,ev,url,ppl) in P:
    dd=dist(HOTEL,(la,lo))
    pts.append({"name":n,"lat":la,"lon":lo,"cat":c,"src":s,"desc":d,"price":pr,
                "time":t,"traffic":tr,"slots":sl,"out":od,"elev":ev,"url":url,"ppl":ppl,
                "name_ru":NAME_RU.get(n,n),"desc_ru":DESC_RU.get(n,d),
                "price_ru":price_ru(pr),"time_ru":time_ru(t),"traffic_ru":traf_ru(tr),
                "km":round(dd,2),"walk":round(dd/0.075) if dd<2.5 else 0})
print(f"点位 {len(pts)} 个（已移除餐饮分类）")
for k in ("m","a","e"):
    print(f"  {k} 时段: {sum(1 for p in pts if k in p['slots'])} 个")
print(f"  室内(雨天可用): {sum(1 for p in pts if not p['out'] and p['slots'])} 个")
print(f"  登高观景(阴天降权): {sum(1 for p in pts if p['elev'])} 个")

from ui_tpl import HTML

html=(HTML.replace("__LEAFLET_CSS__",LEAFLET_CSS).replace("__LEAFLET_JS__",LEAFLET_JS)
        .replace("__PTS__",json.dumps(pts,ensure_ascii=False))
        .replace("__CATS__",json.dumps(CATS,ensure_ascii=False))
        .replace("__PEOPLE__",json.dumps(PEOPLE,ensure_ascii=False))
        .replace("__PEOPLE_RU__",json.dumps(PEOPLE_RU,ensure_ascii=False))
        .replace("__UI_RU__",json.dumps(UI,ensure_ascii=False))
        .replace("__CATS_RU__",json.dumps(CATS_RU,ensure_ascii=False))
        .replace("__EMERG__",json.dumps(EMERGENCY,ensure_ascii=False))
        .replace("__PHRASES__",json.dumps(PHRASES,ensure_ascii=False))
        .replace("__CONSUL__",json.dumps(CONSUL,ensure_ascii=False)))
# 输出到 site/ 与 docs/（GitHub Pages 直接托管 site/index.html）
SITE=os.path.join(BASE,"..","site"); DOCS=os.path.join(BASE,"..","docs")
os.makedirs(SITE,exist_ok=True); os.makedirs(DOCS,exist_ok=True)
out=os.path.join(SITE,"index.html")
open(out,"w",encoding="utf-8").write(html)
print("已生成:",out,f"{len(html)/1024:.0f} KB")

with open(os.path.join(DOCS,"青岛景点坐标.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f)
    w.writerow(["名称","纬度","经度","分类","价格","建议时段","上午","下午","晚上",
                "室内可避雨","登高观景","交通","距酒店km","步行分钟","说明","官网","坐标来源"])
    for p in pts:
        w.writerow([p["name"],p["lat"],p["lon"],CATS[p["cat"]][1],p["price"],p["time"],
                    "✓" if "m" in p["slots"] else "","✓" if "a" in p["slots"] else "",
                    "✓" if "e" in p["slots"] else "","✓" if not p["out"] else "",
                    "✓" if p["elev"] else "",p["traffic"],p["km"],p["walk"] or "",
                    p["desc"],p["url"],"OSM实测" if p["src"]=="osm" else "地址推定"])
print("CSV 已更新")
