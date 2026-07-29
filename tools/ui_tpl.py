# -*- coding: utf-8 -*-
"""
前端模板 v4
 1 时段改为「分段切换器」，每段独立滚动区，不再长列表翻页
 2 行程顺序 = 点击先后顺序
 3 路线补最后一段「回酒店」
 4 「我的位置」定位（含中国坐标偏移校正开关）
 5 候选列表按「距上一个已选点」由近到远动态重排
"""

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=5">
<title>挑食地图 · 青岛 | Trip à la carte</title>
<style>__LEAFLET_CSS__</style>
<style>
*{box-sizing:border-box}
html,body{margin:0;padding:0;height:100%;width:100%;overflow:hidden;
  font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
  color:#1C2B33}
/* 标题用宋体系衬线：中文里衬线＝书卷气，是"中国风"最直接的信号 */
.hd .ttl,.tpH .ttl,.pcard .pn,.daycard .dh,.rvBar .rvT{
  font-family:"Songti SC","STSong","SimSun",Georgia,serif;letter-spacing:.5px}
#map{position:absolute;inset:0;background:#EDE7D8}
/* 地图整体轻微降饱和，让 UI 的朱砂/墨色跳出来 */
.leaflet-tile-pane{filter:saturate(.88) contrast(.97)}
.loading{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);z-index:400;
  background:rgba(255,255,255,.95);padding:10px 18px;border-radius:20px;font-size:13px;color:#55666F;
  box-shadow:0 2px 10px rgba(0,0,0,.15);transition:opacity .4s}
.loading.hide{opacity:0;pointer-events:none}
.toast{position:absolute;left:50%;bottom:76px;transform:translateX(-50%);z-index:1500;
  background:rgba(28,43,51,.94);color:#F7F4EC;padding:10px 16px;border-radius:5px;font-size:12.5px;
  border-left:2.5px solid #B93A32;
  max-width:78%;line-height:1.5;opacity:0;pointer-events:none;transition:opacity .3s}
.toast.show{opacity:1}

.fab{position:absolute;top:12px;right:12px;z-index:1002;width:52px;height:52px;border-radius:50%;
  background:#1C2B33;color:#fff;border:0;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.35);
  font-size:21px;display:none;align-items:center;justify-content:center;font-family:inherit;
  transition:transform .18s,background .18s}
.fab:hover{transform:scale(1.08);background:#2F4550}
.fab.show{display:flex}
.fab .badge{position:absolute;top:-3px;right:-3px;background:#B93A32;color:#fff;font-size:11px;
  min-width:20px;height:20px;border-radius:10px;display:flex;align-items:center;justify-content:center;
  font-weight:700;padding:0 5px;box-shadow:0 1px 4px rgba(0,0,0,.3)}

.panel{position:absolute;top:14px;right:14px;z-index:1000;width:376px;
  height:calc(100% - 28px);max-height:900px;display:flex;flex-direction:column;
  background:#FBF9F4;border-radius:10px;overflow:hidden;
  /* 宣纸：极淡斜向纹理 + 温润投影，不用图片 */
  background-image:repeating-linear-gradient(135deg,rgba(28,43,51,.014) 0 2px,transparent 2px 5px);
  box-shadow:0 6px 26px rgba(28,43,51,.26),0 0 0 1px rgba(227,220,203,.9);
  transition:opacity .18s,transform .18s}
.panel.hide{opacity:0;transform:scale(.94);pointer-events:none}
.hd{padding:13px 15px;background:#1C2B33;color:#fff;font-size:14.5px;font-weight:600;
  display:flex;align-items:center;gap:8px;flex:none;position:relative}
/* 头部下沿一道朱砂细线：中式书封的"锦边" */
.hd:after,.tpH:after{content:'';position:absolute;left:0;right:0;bottom:0;height:2px;
  background:linear-gradient(90deg,#B93A32 0%,#B93A32 38%,rgba(185,58,50,.15) 100%)}
.hd .ttl{flex:1}
.hd .mini{cursor:pointer;font-weight:400;opacity:.75;font-size:19px;line-height:1;padding:0 2px}
/* 语言键已移到右侧竖栏；桌面隐藏面板内的那两个。
   手机保留：抽屉拉起时竖栏会收掉，没有它就切不了语言。 */
.langsw{display:none;margin-left:auto;margin-right:10px;background:rgba(255,255,255,.13);
  border-radius:7px;padding:2px;flex:none}
.lgbtn{border:0;background:none;color:rgba(255,255,255,.62);font-size:11.5px;font-weight:700;
  padding:3px 9px;border-radius:5px;cursor:pointer;font-family:inherit;transition:.15s;line-height:1.4}
.lgbtn:hover{color:#fff}
.lgbtn.on{background:#fff;color:#1C2B33}
.tripPanel .lgbtn.on{color:#215050}
/* 分段器：允许两行，避免数字被挤出 */
.seg{white-space:normal;overflow:visible}
.seg .c{white-space:nowrap;display:block}
.seg .pk{top:-6px;right:-5px}
/* 俄语模式：整体收紧，防止撑破 */
body.ru .pick .nm,body.ru .item .nm{font-size:12.5px;line-height:1.4}
body.ru .trow .nm2{font-size:12.5px}
body.ru .accH{font-size:12.5px}
body.ru .accH .t{line-height:1.35}
body.ru .seg{font-size:11px;padding:9px 2px 8px}
body.ru .seg .c{font-size:10px}
body.ru .wxb{font-size:11px;padding:9px 2px}
body.ru .hd{font-size:12.5px}
body.ru .tag{font-size:9.5px;padding:1px 4px}
body.ru .lp b{font-size:14px;line-height:1.35}
body.ru .tsec{font-size:10.5px}
body.ru .sortby{white-space:normal;line-height:1.5}
body.ru .hint{font-size:11px}
body.ru .tripF{font-size:11px}
.hd .mini:hover{opacity:1}
/* .tabs 已废弃：桌面用右侧 deskDock、手机用底部 dock，两端都不显示 */

.pane{flex:1;min-height:0;display:flex;flex-direction:column}
.scroll{overflow-y:auto;flex:1;min-height:0;-webkit-overflow-scrolling:touch}
.hint{padding:9px 15px;font-size:11.5px;color:#55666F;background:#F0EADD;line-height:1.6;flex:none}

.acc{border-bottom:1px solid #F0EADD}
.accH{display:flex;align-items:center;gap:10px;padding:12px 15px;cursor:pointer;user-select:none;font-size:14px}
.accH:hover{background:#F7F4EC}
.accH .dot{width:11px;height:11px;border-radius:50%;flex:none;
  box-shadow:0 0 0 1.5px #FBF9F4,0 0 0 2.5px rgba(28,43,51,.18)}
.accH .t{flex:1;line-height:1.3}
.accH .n{font-size:12px;color:#55666F;background:#F0EADD;padding:2px 9px;border-radius:10px;font-weight:600}
.accH .ar{font-size:10px;color:#6B7880;transition:transform .2s}
.acc.open .accH .ar{transform:rotate(90deg)}
.acc.open .accH{background:#F7F4EC;font-weight:600}
.accB{display:none;background:#FBF9F4;padding:2px 0 6px}
.acc.open .accB{display:block}
.item{padding:10px 15px 10px 38px;font-size:13.5px;cursor:pointer;border-left:3px solid transparent;line-height:1.5}
.item:hover{background:#F3EFE4;border-left-color:#C6BFB0}
.item.act{background:#F6E7E3;border-left-color:#B93A32;font-weight:600}
.item .nm{color:#1C2B33}
.item .mt{font-size:11.5px;color:#55666F;margin-top:3px}

/* 行程卡 */
/* ===== 独立的「今日行程」浮动面板（左侧，不再挤压候选列表） ===== */
.tripPanel{position:absolute;left:14px;top:82px;z-index:999;width:310px;
  background:#FBF9F4;border-radius:10px;
  background-image:repeating-linear-gradient(135deg,rgba(28,43,51,.014) 0 2px,transparent 2px 5px);
  box-shadow:0 6px 24px rgba(28,43,51,.24),0 0 0 1px rgba(227,220,203,.9);
  overflow:hidden;display:none;flex-direction:column;
  max-height:calc(100% - 190px)}
.tripPanel.show{display:flex}
/* 关键：中间容器必须参与 flex 收缩，否则内容会撑破面板导致无法滚动 */
#tripBox{flex:1 1 auto;min-height:0;display:flex;flex-direction:column;overflow:hidden}
.tripPanel.fold .tripB,.tripPanel.fold .tripF{display:none}
.tpH{background:#2F4550;color:#fff;padding:13px 15px;font-size:14.5px;font-weight:600;
  display:flex;align-items:center;gap:8px;flex:none;cursor:pointer;user-select:none;position:relative}
.tpH .ttl{flex:1}
.tpH .fold{opacity:.85;font-size:12px;transition:transform .2s}
.tripPanel.fold .tpH .fold{transform:rotate(-90deg)}
/* 清空键：两个面板共用同一套 */
.clr{opacity:.72;font-size:11.5px;cursor:pointer;flex:none;
  padding:3px 9px;border-radius:6px;background:rgba(255,255,255,.14);
  transition:.15s;white-space:nowrap}
.clr:hover{opacity:1;background:rgba(255,255,255,.26)}
/* 语言切换淡入，掩盖 DOM 重建的闪烁 */
.lang-swap .pane,.lang-swap #tripBox{animation:fadeSwap .26s ease}
@keyframes fadeSwap{from{opacity:.35}to{opacity:1}}
/* 没有行程时不显示「清空」——点了也没反应，留着只会让人以为坏了 */
body:not(.hastrip) .clr{display:none}

.trip{border:0;border-radius:0;overflow:hidden;flex:1;min-height:0;display:flex;flex-direction:column}
.tripB{padding:5px 0;background:#F6F2E9;flex:1;min-height:0;overflow-y:auto;overscroll-behavior:contain}
.trow{display:flex;align-items:center;gap:9px;padding:8px 12px;font-size:13.5px;cursor:pointer}
.trow:hover{background:#F3EFE4}
.trow .i{width:23px;height:23px;border-radius:50%;color:#fff;font-size:12px;
  display:flex;align-items:center;justify-content:center;flex:none;font-weight:700}
.trow .nm2{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
body.ru .trow .nm2{white-space:normal;line-height:1.35;text-overflow:clip}
.trow .rm{color:#B93A32;font-size:14px;padding:0 2px;opacity:.55}
.trow .rm:hover{opacity:1}
.trowHome{display:flex;align-items:center;gap:9px;padding:8px 12px;font-size:12.5px;color:#55666F;
  border-top:1px dashed #CFE0D8;margin-top:3px}
.tripF{padding:10px 13px;background:#fff;border-top:1px dashed #CFE0D8;font-size:11.5px;color:#55666F;line-height:1.7}
.tripBtn{display:block;width:100%;margin-top:8px;padding:11px;border:0;border-radius:6px;
  background:#2E6B6B;color:#fff;font-size:13px;cursor:pointer;font-family:inherit;font-weight:600;
  letter-spacing:1px;transition:.15s}
.tripBtn:hover{background:#215050}
.tripBtn.alt{background:#B93A32;margin-top:6px}    /* 导出＝朱砂，像盖印 */
.tripBtn.alt:hover{background:#8F2B25}
.empty{margin:11px 13px 6px;padding:18px 14px;text-align:center;font-size:12.5px;color:#6B7880;
  line-height:1.9;background:#F7F4EC;border-radius:11px;border:1.5px dashed #D9D2C2;flex:none}

/* 时段分段器 */
.segs{display:flex;gap:7px;padding:13px 13px 10px;background:#fff;border-bottom:1px solid #E3DCCB;flex:none}
.seg{flex:1;padding:11px 3px 9px;border:1.5px solid #E3DCCB;background:#FBF9F4;border-radius:7px;
  cursor:pointer;font-family:inherit;font-size:13px;line-height:1.35;color:#55666F;transition:.15s;position:relative}
.seg:hover{border-color:#B93A32;color:#1C2B33}
.seg.on{color:#fff;border-color:transparent;font-weight:700}
.seg.on[data-s=m]{background:#C8862B}
.seg.on[data-s=a]{background:#2E7F86}
.seg.on[data-s=e]{background:#5B4B8A}
.seg[data-s=m]{border-color:#E3C48A}
.seg[data-s=a]{border-color:#A9CBCC}
.seg[data-s=e]{border-color:#BFB6D6}
.seg .c{display:block;font-size:11px;opacity:.8;margin-top:3px;font-weight:400}
.seg .pk{position:absolute;top:-5px;right:-4px;background:#B93A32;color:#fff;font-size:9.5px;
  min-width:17px;height:17px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-weight:700}
.sortby{padding:6px 14px;font-size:11px;color:#55666F;background:#F7F4EC;
  border-bottom:1px solid #F0EADD;flex:none;line-height:1.45;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:help}
.sortby b{color:#1C2B33}
.hid2{color:#96631F;background:#FAF4E4;border:1px solid #E8D6A8;border-radius:4px;
  padding:0 5px;font-size:10.5px;margin-left:3px}
.tsec{padding:6px 12px;font-size:11.5px;font-weight:700;letter-spacing:.4px;transition:.15s}
.tsec .tsecE{font-weight:400;opacity:.6;font-size:9.5px}
.tsec.dz{outline:2px dashed currentColor;outline-offset:-3px}
.dragh{flex:none;width:24px;padding:6px 0;margin:-6px 0;text-align:center;color:#D9D2C2;
  font-size:15px;cursor:grab;touch-action:none;user-select:none;letter-spacing:-1px;
  -webkit-user-select:none;-webkit-touch-callout:none}
.dragh:active{cursor:grabbing;color:#2E6B6B}
.dragh:hover{color:#55666F}
.trow.pressing{background:#F7EDD9}
.trow.ghost{opacity:.32}
.trow .wn{color:#C8862B;font-size:11px;margin-left:3px}
.dragProxy{position:fixed;z-index:3000;pointer-events:none;background:#fff;border-radius:7px;
  box-shadow:0 8px 22px rgba(0,0,0,.3);padding:5px 9px;font-size:12px;display:flex;align-items:center;
  gap:7px;opacity:.96;transform:rotate(-1.5deg)}
.dragProxy .i{width:18px;height:18px;border-radius:50%;color:#fff;font-size:10px;font-weight:700;
  display:flex;align-items:center;justify-content:center}
.dropline{height:0;border-top:2.5px solid #2E6B6B;margin:-1px 0;position:relative}
.dropline:after{content:'';position:absolute;left:4px;top:-4px;width:6px;height:6px;
  border-radius:50%;background:#2E6B6B}

.pick{display:flex;align-items:flex-start;gap:11px;padding:11px 14px;font-size:13.5px;
  cursor:pointer;border-left:3px solid transparent;line-height:1.5;border-bottom:1px solid #F0EADD}
.pick:hover{background:#F3EFE4}
.pick.on{background:#F8EFEC;border-left-color:#B93A32}
.pick .cb{width:19px;height:19px;border:1.5px solid #D9D2C2;border-radius:3px;flex:none;margin-top:2px;
  display:flex;align-items:center;justify-content:center;font-size:13px;color:#fff;background:#fff}
.pick.on .cb{background:#B93A32;border-color:#B93A32}
.pick .info{flex:1;min-width:0}
.pick .nm{color:#1C2B33}
.pick .mt{font-size:11.5px;color:#55666F;margin-top:3px}
.pick .mt2{font-size:11px;color:#55666F;margin-top:2px}
.pick .mt2:before{content:'🚇 ';opacity:.7}
.pick .ord{flex:none;width:23px;height:23px;border-radius:50%;color:#fff;
  font-size:12px;display:none;align-items:center;justify-content:center;font-weight:700;margin-top:0}
.pick.on .ord{display:flex}
.pick.dim{opacity:.55}
.tag{display:inline-block;font-size:10.5px;padding:1px 6px;border-radius:4px;margin-left:5px;vertical-align:1px}
.tag.in{background:#E7F0EC;color:#215050}
.tag.warn{background:#F7E9E6;color:#8F2B25}
.tag.near{background:#DDE7EE;color:#2F5B78}
.alert{display:inline-block;background:#F7E9E6;color:#8F2B25;border:1px solid #E8CFC9;
  font-size:10.5px;font-weight:700;padding:1px 6px;border-radius:4px;margin-left:5px;vertical-align:1px}
.alert.mini{font-size:9.5px;padding:0 4px;margin-left:4px}
.lp .alertbox{margin:7px 0 0;padding:7px 9px;background:#FBF3F1;border-left:3px solid #B93A32;
  border-radius:0 5px 5px 0;color:#8F2B25;font-size:12px;font-weight:600;line-height:1.6}
body.ru .alert{font-size:9.5px}

.wxwrap{flex:none;border-top:1px solid #E3DCCB;background:#F7F4EC}
.wxnote{padding:9px 14px;font-size:11.5px;line-height:1.6}
.wxnote.sunny{background:#FAF4E4;color:#7A4A18}
.wxnote.cloudy{background:#F0EADD;color:#55666F}
.wxnote.rainy{background:#EFF4F7;color:#2F5B78}
.wxbar{display:flex;gap:7px;padding:9px 13px}
.wxb{flex:1;padding:11px 3px;border:1.5px solid #E3DCCB;background:#FBF9F4;border-radius:7px;
  font-size:13px;cursor:pointer;font-family:inherit;transition:.15s;line-height:1.3;font-weight:500;color:#55666F}
.wxb:hover{border-color:#B93A32;color:#1C2B33}
.wxb.on{color:#fff;font-weight:600;border-color:transparent}
.wxb.on[data-w=sunny]{background:#C8862B}
.wxb.on[data-w=cloudy]{background:#55666F}
.wxb.on[data-w=rainy]{background:#3A6B8F}
.rainToggle{display:block;width:calc(100% - 18px);margin:0 9px 6px;padding:5px;font-size:10.5px;
  cursor:pointer;border:1px dashed #A9C4D4;background:#fff;border-radius:5px;color:#2F5B78;font-family:inherit}
.rainToggle:hover{background:#E6EEF4}

.lp{font-size:13px;line-height:1.6;min-width:225px;max-width:290px}
.lp b{font-size:15px;display:block;margin-bottom:5px;color:#1C2B33}
.lp .row{margin:3px 0}
.lp .k{color:#55666F;display:inline-block;min-width:38px}
.lp .desc{margin:6px 0;padding:6px 8px;background:#F7F4EC;border-left:3px solid #D9D2C2;
  border-radius:0 4px 4px 0;color:#3A4A54}
.lp .nav{display:block;margin-top:6px;padding:8px;text-align:center;background:#1C2B33;color:#fff;
  text-decoration:none;border-radius:6px;font-size:12.5px;font-weight:600}
.lp .site{display:block;margin-top:8px;padding:7px;text-align:center;background:#fff;color:#1C2B33;
  text-decoration:none;border:1.5px solid #D9D2C2;border-radius:6px;font-size:12px}
.lp .site:hover{background:#F0EADD}
.lp .addb{display:block;width:100%;margin-top:6px;padding:6px;border:1.5px solid #2E6B6B;background:#fff;
  color:#215050;border-radius:5px;font-size:12px;cursor:pointer;font-family:inherit;font-weight:600}
.lp .addb.on{background:#2E6B6B;color:#fff}
.est{font-size:11px;color:#6B7880;margin-top:6px;border-top:1px dashed #E3DCCB;padding-top:5px}
.leaflet-popup-content{margin:11px 13px}

/* 人物按钮与弹层 */
.lp .ppl{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}
.pbtn{flex:1 1 auto;padding:6px 9px;border:1.5px solid #CFC8E0;background:#EFECF5;color:#5B4B8A;
  border-radius:6px;font-size:12px;cursor:pointer;font-family:inherit;font-weight:600;white-space:nowrap}
.pbtn:hover{background:#E4DFEE;border-color:#B7AFD0}
.pmask{position:fixed;inset:0;background:rgba(28,43,51,.55);z-index:4000;display:none;
  align-items:center;justify-content:center;padding:22px;backdrop-filter:blur(2px)}
.pmask.show{display:flex}
.pcard{background:#fff;border-radius:14px;max-width:420px;width:100%;max-height:78%;overflow-y:auto;
  box-shadow:0 12px 40px rgba(0,0,0,.4);animation:pIn .18s ease-out}
@keyframes pIn{from{opacity:0;transform:translateY(12px) scale(.97)}to{opacity:1;transform:none}}
.pcard .ph{background:#5B4B8A;color:#fff;padding:15px 18px;display:flex;align-items:flex-start;gap:11px}
.pcard .pav{width:42px;height:42px;border-radius:50%;background:rgba(255,255,255,.2);flex:none;
  display:flex;align-items:center;justify-content:center;font-size:21px}
.pcard .pn{font-size:18px;font-weight:700;line-height:1.25}
.pcard .py{font-size:12px;opacity:.85;margin-top:3px}
.pcard .px{margin-left:auto;cursor:pointer;font-size:22px;opacity:.8;line-height:1}
.pcard .px:hover{opacity:1}
.pcard .pr{padding:14px 18px;font-size:13.5px;color:#3A4A54;line-height:1.75}
.pcard .prole{display:inline-block;background:#EFECF5;color:#5B4B8A;padding:3px 9px;border-radius:5px;
  font-size:12px;font-weight:600;margin-bottom:9px}
.pcard .plink{display:block;margin:12px 18px 16px;padding:9px;text-align:center;background:#F0EADD;
  color:#3A4A54;text-decoration:none;border-radius:7px;font-size:12.5px}
.pcard .plink:hover{background:#E3DCCB}
.daycard{background:#fff;border-radius:14px;width:100%;max-width:380px;padding:22px;
  box-shadow:0 12px 40px rgba(0,0,0,.4);animation:pIn .18s ease-out}
.daycard .dh{font-size:16px;font-weight:700;color:#1C2B33;margin-bottom:14px}
.dinput{width:100%;padding:12px 14px;border:2px solid #D9D2C2;border-radius:9px;
  font-size:15px;font-family:inherit;color:#1C2B33;outline:none;transition:.15s}
.dinput:focus{border-color:#2E6B6B}
.dhint{font-size:11.5px;color:#6B7880;margin-top:8px}
.dbtns{display:flex;gap:9px;margin-top:18px}
.dbtn{flex:1;padding:11px;border:0;border-radius:9px;background:#2E6B6B;color:#fff;
  font-size:14px;font-weight:600;cursor:pointer;font-family:inherit}
.dbtn:hover{background:#215050}
.dbtn.ghost{background:#F0EADD;color:#55666F}
.dbtn.ghost:hover{background:#E3DCCB}
/* ===== 手机底部 Tab 栏 ===== */
/* 两个面板共用的把手条（仅手机显示） */
.grip{display:none}
@media(max-width:760px){
  .grip{display:block;position:absolute;top:7px;left:50%;transform:translateX(-50%);
    width:40px;height:4px;border-radius:2px;background:rgba(255,255,255,.38);
    transition:background .15s}
  .panel.dragging .grip,.tripPanel.dragging .grip{background:rgba(255,255,255,.75)}
}
/* ===== 全屏看路线模式：所有 UI 让位给地图 ===== */
body.routeview .mapLbl{opacity:0!important}
body.routeview .panel,body.routeview .tripPanel,body.routeview .rightRail,
body.routeview .dock,body.routeview .fab,
body.routeview .leaflet-control-zoom{
  opacity:0!important;pointer-events:none!important;transition:opacity .22s}
body.routeview .panel{transform:translateY(-50%) translateX(24px)!important}
body.routeview .tripPanel{transform:translateY(-50%) translateX(-24px)!important}
@media(max-width:760px){
  body.routeview .panel,body.routeview .tripPanel{transform:translateY(110%)!important}
}
/* 顶部标题条 + 底部退出条 */
.rvBar{position:absolute;left:0;right:0;top:0;z-index:1400;display:none;
  padding:10px 14px calc(10px + env(safe-area-inset-top,0px));
  background:linear-gradient(180deg,rgba(28,43,51,.92),rgba(28,43,51,0));
  color:#fff;align-items:center;gap:10px;pointer-events:none}
.rvBar.show{display:flex;animation:rvIn .26s ease}
@keyframes rvIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
.rvBar .rvT{flex:1;font-size:13.5px;font-weight:600;line-height:1.45;
  text-shadow:0 1px 4px rgba(0,0,0,.5)}
.rvBar .rvT small{display:block;font-weight:400;font-size:11.5px;opacity:.82;margin-top:2px}
.rvX{pointer-events:auto;flex:none;border:0;cursor:pointer;font-family:inherit;
  background:rgba(255,255,255,.94);color:#1C2B33;font-size:12.5px;font-weight:700;
  padding:8px 14px;border-radius:20px;box-shadow:0 3px 12px rgba(0,0,0,.35);transition:.15s;
  white-space:nowrap}
.rvX:hover{background:#fff;transform:scale(1.04)}
.rvX:active{transform:scale(.96)}
.rvLg{position:absolute;left:50%;bottom:calc(14px + env(safe-area-inset-bottom,0px));
  transform:translateX(-50%);z-index:1400;display:none;gap:12px;
  background:rgba(255,255,255,.95);backdrop-filter:blur(6px);
  padding:8px 15px;border-radius:20px;box-shadow:0 3px 14px rgba(0,0,0,.25);
  font-size:11.5px;font-weight:600;white-space:nowrap;pointer-events:none}
body.routeview .rvLg{display:flex}

/* ===== 桌面三栏按钮条 ===== */
/* ===== 右侧竖栏：视图切换（桌面） + 地图快捷键（两端） ===== */
.rightRail{position:absolute;right:14px;top:50%;transform:translateY(-50%);z-index:1200;
  display:flex;flex-direction:column;align-items:center;gap:10px}
.deskDock{display:flex;flex-direction:column;gap:6px;background:rgba(251,249,244,.97);
  padding:7px;border-radius:10px;
  box-shadow:0 4px 18px rgba(28,43,51,.22),0 0 0 1px rgba(227,220,203,.9)}
.ddk{display:flex;flex-direction:column;align-items:center;gap:3px;width:58px;padding:9px 2px;
  border:0;background:none;border-radius:9px;cursor:pointer;font-family:inherit;
  font-size:10.5px;font-weight:600;color:#55666F;transition:.15s;position:relative}
.ddk:hover{background:#F0EADD;color:#1C2B33}
.ddk.on{background:#1C2B33;color:#fff}
.ddk[data-d=trip].on{background:#2E6B6B}
.ddk.on:before{content:'';position:absolute;left:3px;top:50%;transform:translateY(-50%);
  width:2.5px;height:16px;border-radius:2px;background:#B93A32}
.ddb{position:absolute;top:3px;right:6px;background:#B93A32;color:#fff;font-size:9.5px;
  min-width:16px;height:16px;border-radius:8px;display:none;align-items:center;
  justify-content:center;font-weight:700;padding:0 4px}
.ddb.show{display:flex}
@media(max-width:760px){.deskDock{display:none}}

/* 桌面：右侧主面板 / 左侧行程，均贴边垂直居中 */
@media(min-width:761px){
  /* 竖栏占 right:14px + 72px 宽 = 到 86px，面板再留 14px 间距 */
  .panel{right:100px;left:auto;top:50%;bottom:auto;transform:translateY(-50%) translateX(24px);
    height:auto;max-height:calc(100% - 40px);opacity:0;pointer-events:none;
    transition:transform .26s cubic-bezier(.22,1,.30,1),opacity .2s}
  body.dock-ov .panel,body.dock-menu .panel{transform:translateY(-50%) translateX(0);opacity:1;pointer-events:auto}
  body.dock-ov .panel{max-height:min(560px,calc(100% - 40px))}
  .tripPanel{left:14px;right:auto;top:50%;bottom:auto;transform:translateY(-50%) translateX(-24px);
    max-height:calc(100% - 40px);opacity:0;pointer-events:none;display:flex;
    transition:transform .26s cubic-bezier(.22,1,.30,1),opacity .2s}
  body.dock-trip .tripPanel{transform:translateY(-50%) translateX(0);opacity:1;pointer-events:auto}
}

.dock{display:none;position:absolute;left:0;right:0;bottom:0;z-index:1200;height:56px;
  background:rgba(255,255,255,.97);backdrop-filter:blur(8px);
  border-top:1px solid #E3DCCB;box-shadow:0 -2px 12px rgba(0,0,0,.08)}
.dk{flex:1;border:0;background:none;font-family:inherit;cursor:pointer;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;
  color:#6B7880;font-size:11px;position:relative;transition:.15s;padding:0}
.dk .di{width:21px;height:21px;display:block}
.dk .dt{font-weight:600;letter-spacing:.2px}
.dk.on{color:#1C2B33}
.dk.on .dt{color:#2E6B6B}
.dk:after{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%) scaleX(0);
  width:36px;height:3px;border-radius:0 0 3px 3px;background:#2E6B6B;transition:transform .18s}
.dk.on:after{transform:translateX(-50%) scaleX(1)}
.dbadge{position:absolute;top:5px;right:50%;margin-right:-26px;background:#B93A32;color:#fff;
  font-size:10px;min-width:17px;height:17px;border-radius:9px;display:none;
  align-items:center;justify-content:center;font-weight:700;padding:0 4px}
.dbadge.show{display:flex}

/* ===== 手机：地图上的快捷键 ===== */
/* 桌面：与上方切换卡同款白卡片；手机：独立圆钮（见媒体查询） */
.mapQuick{display:flex;flex-direction:column;gap:4px;background:rgba(251,249,244,.97);
  padding:7px;border-radius:10px;
  box-shadow:0 4px 18px rgba(28,43,51,.22),0 0 0 1px rgba(227,220,203,.9)}
/* 宽度与 .ddk 一致(58+7*2=72px)，两张卡片左右边缘才对得齐 */
.mq{width:58px;height:38px;border-radius:7px;border:0;background:none;color:#55666F;
  font-size:17px;cursor:pointer;display:flex;align-items:center;justify-content:center;
  font-family:inherit;transition:.15s}
.mq:hover{background:#F0EADD;color:#B93A32}
.mq:active{transform:scale(.94)}
.mq.on{background:#3A6B8F;color:#fff}
/* 语言圆钮上的当前语言角标（沿用行程角标的设计语言） */
.mq{position:relative}
/* 角标收进圆内，不突破轮廓：居中偏下，宽度自适应 РУ 两个字母 */
.mqTag{position:absolute;left:50%;transform:translateX(-50%);bottom:3px;
  background:#1C2B33;color:#fff;font-size:8px;font-weight:700;line-height:1;
  padding:1.5px 4px;border-radius:6px;letter-spacing:.2px}
.mqLang svg{margin-top:-6px}          /* 图标上移，给角标让位 */
.mqLang{display:none}                 /* 桌面用下面的 langRail 卡片 */

/* 语言切换卡：与上面两张卡同宽同款 */
.langRail{display:flex;width:72px;gap:3px;background:rgba(251,249,244,.97);
  padding:6px;border-radius:10px;
  box-shadow:0 4px 18px rgba(28,43,51,.22),0 0 0 1px rgba(227,220,203,.9)}
.langRail .lgbtn{flex:1;height:30px;padding:0;border-radius:8px;background:none;
  color:#55666F;font-size:11.5px;font-weight:700;line-height:1;
  display:flex;align-items:center;justify-content:center}
.langRail .lgbtn:hover{background:#F0EADD;color:#1C2B33}
.langRail .lgbtn.on{background:#1C2B33;color:#fff}

/* 手机：竖栏贴右上，快捷键回到独立圆钮造型（必须放在桌面样式之后才能覆盖） */
@media(max-width:760px){
  .langsw{display:flex}          /* 抽屉挡住竖栏时的兜底入口 */
  .rightRail{top:96px;right:10px;transform:none;gap:8px}
  .mapQuick{background:none;box-shadow:none;padding:0;gap:8px}
  .mq{width:42px;height:42px;border-radius:50%;background:rgba(251,249,244,.97);
    box-shadow:0 3px 12px rgba(28,43,51,.24),0 0 0 1px rgba(227,220,203,.85);color:#1C2B33}
  .mq:hover{background:rgba(251,249,244,.97);color:#1C2B33}
  .mq.on{background:#3A6B8F;color:#fff}
  /* 手机：语言并入上面的圆钮组，卡片形态收起 */
  .langRail{display:none}
  .mqLang{display:flex}
  /* 抽屉拉起来时收掉竖栏：手机上面板是全宽 sheet，
     竖栏 z-index 更高会压住面板顶栏的「清空」等按钮 */
  body.dock-ov .rightRail,body.dock-menu .rightRail,body.dock-trip .rightRail{
    opacity:0;pointer-events:none;transform:translateX(12px)}
  .rightRail{transition:opacity .2s,transform .2s}
}

/* ===== 缩放到一定级别后，点位旁自动显示地名 ===== */
.mapLbl{position:absolute;z-index:620;pointer-events:none;
  font-size:11px;line-height:1.25;font-weight:600;color:#1C2B33;
  white-space:nowrap;padding:1.5px 6px;border-radius:3px;
  background:rgba(251,249,244,.9);box-shadow:0 0 0 .5px rgba(28,43,51,.1);
  /* 宣纸色描边：压在深色底图/绿地上也读得清 */
  text-shadow:0 0 2px rgba(251,249,244,.95),0 0 3px rgba(251,249,244,.8);
  opacity:0;transition:opacity .18s;will-change:opacity}
.mapLbl.on{opacity:1}
.mapLbl.trip{color:#8F2B25;background:rgba(251,249,244,.96);font-weight:700;
  box-shadow:0 0 0 .5px rgba(185,58,50,.35)}
/* 俄语名字长，限宽并强制单行；超出用省略号，绝不折行成方块 */
body.ru .mapLbl{font-size:10.5px;max-width:132px;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}
@media(max-width:760px){.mapLbl{font-size:10.5px;padding:1px 4px}}

.numIcon{color:#fff;border:2.5px solid #FBF9F4;border-radius:50%;font-size:12px;font-weight:700;
  display:flex;align-items:center;justify-content:center;box-shadow:0 2px 7px rgba(0,0,0,.45)}
.meDot{width:18px;height:18px;border-radius:50%;background:#3A6B8F;border:3px solid #fff;
  box-shadow:0 0 0 1px rgba(0,0,0,.25),0 2px 7px rgba(0,0,0,.45);animation:mePulse 2.2s infinite}
@keyframes mePulse{0%{box-shadow:0 0 0 0 rgba(26,115,232,.45),0 2px 7px rgba(0,0,0,.45)}
 70%{box-shadow:0 0 0 16px rgba(26,115,232,0),0 2px 7px rgba(0,0,0,.45)}
 100%{box-shadow:0 0 0 0 rgba(26,115,232,0),0 2px 7px rgba(0,0,0,.45)}}

@media(max-width:760px){
  /* ---- 底部双 Tab 栏 ---- */
  .dock{display:flex}

  /* ---- 两个面板：都做成底部抽屉，互斥出现 ---- */
  .panel,.tripPanel{
    left:0;right:0;width:auto;border-radius:18px 18px 0 0;
    top:auto;bottom:56px;
    /* 三档高度：总览 55% / 选地点 85% / 行程 85%；上拉可到 94% */
    height:var(--sheetH,85vh);max-height:94vh;
    background:#fff;overflow:visible;
    transform:translateY(110%);pointer-events:none;
    /* iOS 风格弹性曲线：出场稍慢有回弹感，收起干脆 */
    transition:transform .34s cubic-bezier(.22,1,.30,1);
    box-shadow:0 -8px 32px rgba(0,0,0,.22);border:0;display:flex;
    will-change:transform;touch-action:pan-y}
  body.dock-ov .panel,body.dock-menu .panel,
  body.dock-trip .tripPanel{transform:translateY(0);pointer-events:auto}
  body.dock-ov{--sheetH:50vh}
  body.dock-menu{--sheetH:75vh}
  body.dock-trip{--sheetH:75vh}
  /* 上划后：各栏再长高一档，露出更多列表项 */
  body.sheet-up.dock-ov{--sheetH:75vh}
  body.sheet-up.dock-menu{--sheetH:92vh}
  body.sheet-up.dock-trip{--sheetH:92vh}
  /* 高度变化也要有过渡 */
  .panel,.tripPanel{transition:transform .34s cubic-bezier(.22,1,.30,1),height .3s cubic-bezier(.22,1,.30,1)}
  .panel.dragging,.tripPanel.dragging{transition:none}
  /* 拖动中关闭过渡，跟手 */
  .panel.dragging,.tripPanel.dragging{transition:none}
  .tripPanel{border-top:3px solid #2E6B6B;background:#F6F2E9}
  /* 垫片改用伪元素：只做视觉延伸，不占内容高度 */
  .panel:after,.tripPanel:after{content:'';position:absolute;left:0;right:0;top:100%;
    height:300px;background:inherit;pointer-events:none}

  /* 顶部把手：点一下收起／再点恢复 */
  .panel .hd,.tripPanel .tpH{position:relative;cursor:grab;padding-top:18px;
    touch-action:none;user-select:none;-webkit-user-select:none}
  .panel.dragging .hd,.tripPanel.dragging .tpH{cursor:grabbing}
  .tripPanel .fold{display:none}
  .panel .mini,.tripPanel .mini{display:none}   /* 手机用下滑收起 */

  .fab{display:none!important}
  .toast{bottom:auto;top:64px}
  .daycard,.pcard{max-width:none}
  .segs .seg .c{display:none}              /* 不显示"多少项" */
}

</style>
</head>
<body>
<div id="map"></div>
<div class="loading" id="ld">地图加载中…</div>
<div class="toast" id="toast"></div>
<div class="pmask" id="pmask"><div class="pcard" id="pcard"></div></div>
<div class="pmask" id="dayMask"><div class="daycard">
  <div class="dh" id="dayLabel">这是哪一天的行程？</div>
  <input id="dayInput" class="dinput" maxlength="28" autocomplete="off">
  <div class="dhint" id="dayHint">会印在卡片顶部</div>
  <div class="dbtns">
    <button class="dbtn ghost" id="dayCancel" onclick="closeDay()">取消</button>
    <button class="dbtn" id="dayOk" onclick="closeDay();exportCard(document.getElementById('dayInput').value.trim())">生成图片</button>
  </div></div></div>
<button class="fab" id="fab">🗺<span class="badge" id="fabBadge" style="display:none">0</span></button>
<!-- 全屏看路线模式的顶栏 / 图例 -->
<div class="rvBar" id="rvBar">
  <div class="rvT" id="rvTitle"></div>
  <button class="rvX" id="rvX">✕ <span id="rvXT">退出</span></button>
</div>
<div class="rvLg" id="rvLg">
  <span style="color:#C8862B">■ <span id="rvLm">上午</span></span>
  <span style="color:#2E7F86">■ <span id="rvLa">下午</span></span>
  <span style="color:#5B4B8A">■ <span id="rvLe">晚上</span></span>
  <span style="color:#8C949B">┈ <span id="rvLh">回酒店</span></span>
</div>

<div class="panel" id="pn">
  <div class="hd" id="pnH"><span class="grip"></span>
    <span class="ttl" id="hdTitle">挑食地图 · 青岛</span>
    <span class="langsw"><button class="lgbtn on" data-l="zh" onclick="setLang('zh')">中</button><button class="lgbtn" data-l="ru" onclick="setLang('ru')">РУ</button></span>
    <span class="clr" id="clrTrip1">清空</span>
    <span class="mini" id="cl" title="收起">—</span></div>
  <div class="pane" id="paneOv">
    <div class="hint">点击分类展开 → 点地点名，地图自动缩放定位</div>
    <div class="scroll" id="catList"></div>
  </div>

  <div class="pane" id="panePl" style="display:none">
    <div class="segs" id="segs"></div>
    <div class="sortby" id="sortby"></div>
    <div class="scroll" id="slotList"></div>
  </div>

  <div class="wxwrap" id="wxwrap" style="display:none">
    <div class="wxnote" id="wxnote"></div>
    <div id="rtBox"></div>
    <div class="wxbar">
      <button class="wxb on" data-w="sunny">☀️ 晴了</button>
      <button class="wxb"    data-w="cloudy">⛅ 阴了</button>
      <button class="wxb"    data-w="rainy">🌧️ 下雨了</button>
    </div>
  </div>
</div>
<!-- 右侧竖栏：上=视图切换（仅桌面），下=地图快捷键（两端通用） -->
<div class="rightRail" id="rightRail">
<!-- 桌面：三栏切换按钮（手机隐藏，手机用底部 dock） -->
<div class="deskDock" id="deskDock">
  <button class="ddk" data-d="ov"   title="总览"><svg viewBox="0 0 24 24" width="17" height="17"><path fill="currentColor" d="M3 5h18v2H3zm0 6h18v2H3zm0 6h12v2H3z"/></svg><span id="ddOv">总览</span></button>
  <button class="ddk" data-d="menu" title="选地点"><svg viewBox="0 0 24 24" width="17" height="17"><path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7m0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5"/></svg><span id="ddMenu">选地点</span></button>
  <button class="ddk" data-d="trip" title="今日行程"><svg viewBox="0 0 24 24" width="17" height="17"><path fill="currentColor" d="M19 3h-1V1h-2v2H8V1H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2m0 16H5V9h14zM7 11h5v5H7z"/></svg><span id="ddTrip">行程</span><span class="ddb" id="ddBadge">0</span></button>
</div>
<div class="mapQuick" id="mapQuick">
  <button class="mq" id="mqHotel" title="酒店"><svg viewBox="0 0 24 24" width="19" height="19"><path fill="currentColor" d="M12 3 2 11h3v9h6v-6h2v6h6v-9h3z"/></svg></button>
  <button class="mq" id="mqLoc"   title="我的位置"><svg viewBox="0 0 24 24" width="19" height="19"><path fill="currentColor" d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8m8.94 3A9 9 0 0 0 13 3.06V1h-2v2.06A9 9 0 0 0 3.06 11H1v2h2.06A9 9 0 0 0 11 20.94V23h2v-2.06A9 9 0 0 0 20.94 13H23v-2zM12 19a7 7 0 1 1 0-14 7 7 0 0 1 0 14"/></svg></button>
  <button class="mq" id="mqAll"   title="全部"><svg viewBox="0 0 24 24" width="19" height="19"><path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19zm-6 0A4.5 4.5 0 1 1 14 9.5 4.5 4.5 0 0 1 9.5 14"/></svg></button>
  <!-- 手机专用：语言切换圆钮（桌面用下面的 langRail 卡片） -->
  <button class="mq mqLang" id="mqLang" title="切换语言"><svg viewBox="0 0 24 24" width="19" height="19"><path fill="currentColor" d="M12.87 15.07l-2.54-2.51.03-.03A17.5 17.5 0 0 0 14.07 6H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/></svg><span class="mqTag" id="mqLangTag">中</span></button>
</div>
<!-- 语言切换：放在地图上，不必打开菜单 -->
<div class="langRail" id="langRail">
  <button class="lgbtn on" data-l="zh" onclick="setLang('zh')" title="中文">中</button>
  <button class="lgbtn"    data-l="ru" onclick="setLang('ru')" title="Русский">РУ</button>
</div>
</div><!-- /rightRail -->
<div class="dock" id="dock">
  <button class="dk" data-d="ov">
    <svg class="di" viewBox="0 0 24 24" width="21" height="21"><path fill="currentColor" d="M3 5h18v2H3zm0 6h18v2H3zm0 6h12v2H3z"/></svg>
    <span class="dt" id="dkOvT">总览</span></button>
  <button class="dk" data-d="menu">
    <svg class="di" viewBox="0 0 24 24" width="21" height="21"><path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7m0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5"/></svg>
    <span class="dt" id="dkMenuT">选地点</span></button>
  <button class="dk" data-d="trip">
    <svg class="di" viewBox="0 0 24 24" width="21" height="21"><path fill="currentColor" d="M19 3h-1V1h-2v2H8V1H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2m0 16H5V9h14zM7 11h5v5H7z"/></svg>
    <span class="dt" id="dkTripT">今日行程</span><span class="dbadge" id="dockBadge">0</span></button>
</div>
<div class="tripPanel" id="tripPanel">
  <div class="tpH" id="tpH"><span class="grip"></span>
    <span class="fold">▼</span><span class="ttl">🎯 今日行程</span>
    <span class="langsw"><button class="lgbtn on" data-l="zh" onclick="setLang('zh')">中</button><button class="lgbtn" data-l="ru" onclick="setLang('ru')">РУ</button></span>
    <span class="clr" id="clrTrip2">清空</span>
    <span class="mini deskonly" id="cl2" title="收起">—</span></div>
  <div id="tripBox"></div>
</div>


<script>__LEAFLET_JS__</script>
<script>
const PTS=__PTS__, CATS=__CATS__, PEOPLE=__PEOPLE__, HOTEL=[36.06344,120.31192];
const PEOPLE_RU=__PEOPLE_RU__, UI_RU=__UI_RU__, CATS_RU=__CATS_RU__;
const EMERG=__EMERG__, PHRASES=__PHRASES__, CONSUL=__CONSUL__;
/* ===== 语言 ===== */
let LANG=(()=>{try{return localStorage.getItem('qd_lang')||'zh';}catch(e){return 'zh';}})();
const T=k=>LANG==='ru'?(UI_RU[k]||k):k;                       // 界面词条
const pName=p=>LANG==='ru'?(p.name_ru||p.name):p.name;        // 地点名
const pDesc=p=>LANG==='ru'?(p.desc_ru||p.desc):p.desc;
const pPrice=p=>LANG==='ru'?(p.price_ru||p.price):p.price;
const pTime=p=>LANG==='ru'?(p.time_ru||p.time):p.time;
const pTraf=p=>LANG==='ru'?(p.traffic_ru||p.traffic):p.traffic;
const catName=k=>LANG==='ru'?(CATS_RU[k]||CATS[k][1]):CATS[k][1];
const PPL=k=>LANG==='ru'?(PEOPLE_RU[k]||PEOPLE[k]):PEOPLE[k];
const SLOTLBL=()=>LANG==='ru'
  ? {m:["🌅 "+T("上午"),"05:30–11:30"],a:["☀️ "+T("下午"),"11:30–17:30"],e:["🌃 "+T("晚上"),"17:30–23:00"]}
  : SLOTS;
function setLang(l){
  if(l===LANG)return;
  LANG=l; try{localStorage.setItem('qd_lang',l);}catch(e){}
  document.body.classList.remove('lang-swap');
  void document.body.offsetWidth;
  document.body.classList.add('lang-swap');
  setTimeout(()=>document.body.classList.remove('lang-swap'),300);
  document.body.classList.toggle('ru',l==='ru');
  document.querySelectorAll('.lgbtn').forEach(b=>b.classList.toggle('on',b.dataset.l===l));
  document.documentElement.lang = l==='ru'?'ru':'zh-CN';
  // 重建全部可见文案
  // 语言变了：tooltip 与 popup 全部重新绑定（Leaflet 会缓存已渲染内容）
  PTS.forEach(p=>{
    p._m.unbindTooltip().bindTooltip(pName(p),{direction:'top',offset:[0,-9],opacity:.92});
    p._m.unbindPopup().bindPopup(()=>popupHTML(p),{maxWidth:310});
  });
  applyStatic();
  // 两个视图都要重绘：不可见的那个也得刷，否则切回去还是旧语言。
  // renderPl() 内部会调 renderTripBox()，行程面板一并覆盖。
  const wasOv=isOvPane(), openCat=[...document.querySelectorAll('.acc')].findIndex(a=>a.classList.contains('open'));
  renderOv();
  renderPl();
  if(wasOv){
    // renderPl 会显示天气栏并按时段过滤 marker，停在总览时都要还原
    $('wxwrap').style.display='none';
    if(openCat>=0){                       // 保留展开的分类，并恢复它的 marker 过滤
      const acc=document.querySelectorAll('.acc')[openCat];
      if(acc){acc.classList.add('open');
        const k=Object.keys(CATS).filter(c=>PTS.some(p=>p.cat===c))[openCat];
        syncMap(PTS.filter(p=>p.cat===k));}
    } else syncMap(PTS);                  // 未展开：总览显示全部点位
  }
  syncBadge(); drawTrip();
  if(ROUTEVIEW) rvText();
  PTS.forEach(p=>{if(p._lbl)p._lbl._w=0;});   // 语言变了，标签宽度要重新量
  scheduleLabels();
  // 屏幕上若还挂着旧语言的 toast，直接收掉——重译一条已经过时的提示没意义
  const _t=$('toast'); _t.classList.remove('show'); clearTimeout(_t._h);
  if(map.hasLayer) map.closePopup();
}
window.setLang=setLang;
const SLOTS={m:["🌅 上午","05:30–11:30"],a:["☀️ 下午","11:30–17:30"],e:["🌃 晚上","17:30–23:00"]};
const SLOTCOLOR={m:"#C8862B",a:"#2E7F86",e:"#5B4B8A"};   // 晨曦金 / 正午海青 / 暮夜紫
const SLOTSOFT ={m:"#F7EDD9",a:"#E2EFF0",e:"#EAE6F2"};
const SLOTNAME ={m:"上午",a:"下午",e:"晚上"};
const SLOTRANK ={m:0,a:1,e:2};
const WX={
 sunny :{t:"☀️ 晴天：全部景点开放",d:"紫外线 7–9 级，11:00–15:00 避免暴晒户外。"},
 cloudy:{t:"⛅ 阴天：户外全留，登高类降权",d:"体感舒适适合徒步；登高观景已排末尾。"},
 rainy :{t:"🌧️ 雨天：默认只显示室内",d:"台风时崂山/海上项目/索道全停，勿近海边礁石。"}
};
let WEATHER="sunny", SHOWOUT=false, TRIP=[], PICKSLOT={}, CURSLOT="m",
    ME=null, GCJFIX=false, watchId=null;
const INITVIEW={c:HOTEL,z:13};                       // ② 关闭定位时回到的初始视角
function pickedSlot(p){return PICKSLOT[p._i]||firstSlot(p);}   // 记录"在哪个时段被选中"
function pickedElsewhere(p){return TRIP.includes(p._i)&&pickedSlot(p)!==CURSLOT;} // ① 已选于其它时段

/* ===== GCJ-02 投影：让 WGS84 坐标正确叠加在高德底图上 ===== */
(function(){
  const A=6378245.0, EE=0.00669342162296594323;
  function tl(x,y){let r=-100+2*x+3*y+.2*y*y+.1*x*y+.2*Math.sqrt(Math.abs(x));
    r+=(20*Math.sin(6*x*Math.PI)+20*Math.sin(2*x*Math.PI))*2/3;
    r+=(20*Math.sin(y*Math.PI)+40*Math.sin(y/3*Math.PI))*2/3;
    r+=(160*Math.sin(y/12*Math.PI)+320*Math.sin(y*Math.PI/30))*2/3;return r;}
  function tg(x,y){let r=300+x+2*y+.1*x*x+.1*x*y+.1*Math.sqrt(Math.abs(x));
    r+=(20*Math.sin(6*x*Math.PI)+20*Math.sin(2*x*Math.PI))*2/3;
    r+=(20*Math.sin(x*Math.PI)+40*Math.sin(x/3*Math.PI))*2/3;
    r+=(150*Math.sin(x/12*Math.PI)+300*Math.sin(x/30*Math.PI))*2/3;return r;}
  function outOfChina(lat,lng){return lng<72.004||lng>137.8347||lat<0.8293||lat>55.8271;}
  window.wgs2gcj=function(lat,lng){
    if(outOfChina(lat,lng))return[lat,lng];
    let dLat=tl(lng-105,lat-35), dLng=tg(lng-105,lat-35);
    const rad=lat/180*Math.PI; let m=Math.sin(rad); m=1-EE*m*m; const sq=Math.sqrt(m);
    dLat=(dLat*180)/((A*(1-EE))/(m*sq)*Math.PI);
    dLng=(dLng*180)/(A/sq*Math.cos(rad)*Math.PI);
    return[lat+dLat,lng+dLng];};
  window.gcj2wgsPt=function(lat,lng){const g=wgs2gcj(lat,lng);return[lat*2-g[0],lng*2-g[1]];};
  // 继承球面墨卡托，只在投影前把 WGS84 拧成 GCJ-02
  const GCJ=L.Util.extend({},L.CRS.EPSG3857,{
    code:'GCJ-02',
    projection:L.Util.extend({},L.Projection.SphericalMercator,{
      project:function(ll){const g=wgs2gcj(ll.lat,ll.lng);
        return L.Projection.SphericalMercator.project(L.latLng(g[0],g[1]));},
      unproject:function(pt){const ll=L.Projection.SphericalMercator.unproject(pt);
        const w=gcj2wgsPt(ll.lat,ll.lng);return L.latLng(w[0],w[1]);}
    })
  });
  window.CRS_GCJ=GCJ;
})();

const map=L.map('map',{zoomControl:true,minZoom:9,maxZoom:19,preferCanvas:true,
  fadeAnimation:false, crs:CRS_GCJ, attributionControl:false}).setView(HOTEL,13);
if(innerWidth>760) L.control.scale({imperial:false, position:'bottomleft'}).addTo(map);
// 高德街道图（国内直连，GCJ-02 坐标系）
const TILE_URL='https://wprd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scl=1&style=7&x={x}&y={y}&z={z}';

const ld=document.getElementById('ld');
let cur=L.tileLayer(TILE_URL,{
  maxZoom:19, subdomains:'1234',
  updateWhenIdle:false,      // 拖动中实时加载
  keepBuffer:2,              // 预载一圈，减少空白
  updateWhenZooming:false,
  crossOrigin:true, errorTileUrl:''
}).addTo(map);
let _terr=0, _twarn=false;
cur.on('load',()=>{ _terr=0; ld.classList.add('hide'); });
cur.on('tileerror',()=>{ if(++_terr>8 && !_twarn){ _twarn=true;
  toast(LANG==='ru'?'Карта загружается плохо — проверьте сеть':'地图加载不畅，请检查网络',4000); }});
setTimeout(()=>ld.classList.add('hide'),4000);
const $=id=>document.getElementById(id);   // 轻量缓存入口
function fix(){map.invalidateSize({animate:false});}
requestAnimationFrame(fix);[120,400,1200].forEach(t=>setTimeout(fix,t));
addEventListener('load',fix);addEventListener('resize',fix);
if(window.ResizeObserver)new ResizeObserver(fix).observe(document.getElementById('map'));

function showPerson(k){
  const d=PPL(k); if(!d)return;
  const [name,years,role,story]=d;
  $('pcard').innerHTML=`
    <div class="ph"><div class="pav">👤</div>
      <div><div class="pn">${name}</div><div class="py">${years}</div></div>
      <span class="px" onclick="hidePerson()">×</span></div>
    <div class="pr"><span class="prole">${role}</span><br>${story}</div>
    <a class="plink" href="${LANG==='ru'?`https://ru.wikipedia.org/w/index.php?search=${encodeURIComponent(name)}`:`https://www.baidu.com/s?wd=${encodeURIComponent(name+' 青岛')}`}"
       target="_blank" rel="noopener">${T('🔎 了解更多')}</a>`;
  $('pmask').classList.add('show');
}
function hidePerson(){$('pmask').classList.remove('show');}
window.showPerson=showPerson; window.hidePerson=hidePerson;

function applyStatic(){
  const q=(sel,txt)=>{const e=document.querySelector(sel); if(e)e.textContent=txt;};
  q('#paneOv .hint',T('点击分类展开 → 点地点名，地图自动缩放定位'));
  q('#panePl .hint',T('勾选想去的地点 → 地图按 上午→下午→晚上 顺序画出连线'));
  q('#clrTrip2',T('清空')); q('#clrTrip1',T('清空'));
  q('#dkOvT',   LANG==='ru'?'Обзор':'总览');
  q('#dkMenuT', LANG==='ru'?'Места':'选地点');
  q('#dkTripT', LANG==='ru'?'Маршрут':'今日行程');
  // 桌面右侧竖排按钮此前漏翻（手机底栏有、桌面没有）
  q('#ddOv',    LANG==='ru'?'Обзор':'总览');
  q('#ddMenu',  LANG==='ru'?'Места':'选地点');
  q('#ddTrip',  LANG==='ru'?'Маршрут':'行程');
  const tt=(sel,txt)=>{const e=document.querySelector(sel); if(e)e.title=txt;};
  tt('.ddk[data-d=ov]',   LANG==='ru'?'Обзор':'总览');
  tt('.ddk[data-d=menu]', LANG==='ru'?'Места':'选地点');
  tt('.ddk[data-d=trip]', LANG==='ru'?'Маршрут':'今日行程');
  document.querySelectorAll('.wxb').forEach(b=>{
    b.textContent=T({sunny:'☀️ 晴了',cloudy:'⛅ 阴了',rainy:'🌧️ 下雨了'}[b.dataset.w]);});
  const cl=$('cl'); if(cl)cl.title=T('收起为悬浮球');
  // 语言圆钮：角标显示"当前"语言，title 说明点了会切到哪个
  const lt=$('mqLangTag'); if(lt)lt.textContent=LANG==='ru'?'РУ':'中';
  const lb=$('mqLang');
  if(lb)lb.title=LANG==='ru'?'Переключить на китайский (中文)':'切换到俄语 / Русский';
  const cl2=$('cl2'); if(cl2)cl2.title=T('收起');
  const mq={mqHotel:'🏨 酒店',mqLoc:'📍 我的位置',mqAll:'🔍 全部'};
  Object.entries(mq).forEach(([id,k])=>{const e=$(id); if(e)e.title=T(k).replace(/^[^\s]+\s/,'');});
}
function toast(msg,ms){const t=$('toast');t.innerHTML=msg;t.classList.add('show');
 clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove('show'),ms||3200);}
function hav(a,b){const R=6371,p=Math.PI/180;
 const x=Math.sin((b[0]-a[0])*p/2)**2+Math.cos(a[0]*p)*Math.cos(b[0]*p)*Math.sin((b[1]-a[1])*p/2)**2;
 return R*2*Math.asin(Math.sqrt(x));}
function fmt(km){return km<1?Math.round(km*1000)+' m':km.toFixed(1)+' km';}

function ico(c,b,dim){const s=b?21:15;
 return L.divIcon({className:'',iconSize:[s,s],iconAnchor:[s/2,s/2],
  html:`<div style="width:${s}px;height:${s}px;border-radius:50%;background:${c};opacity:${dim?.45:1};
   border:${b?3:2.5}px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.5)"></div>`});}
function numIco(n,color){return L.divIcon({className:'',iconSize:[27,27],iconAnchor:[13.5,13.5],
  html:`<div class="numIcon" style="width:27px;height:27px;background:${color}">${n}</div>`});}

function popupHTML(p){
  const k=TRIP.indexOf(p._i);
  const rf=refInfo();
  const dd=hav(rf.ll,[p.lat,p.lon]);
  const walkTxt=dd<2.5?`${T('步行约')} ${Math.round(dd/0.075)} ${T('分钟')}`:T('需乘车');
  const estHTML=p.cat==='base'?'':
    `<div class="est">${T('距')}${LANG==='ru'?' ':''}${rf.short} ${fmt(dd)} · ${walkTxt}</div>`;
  const flag=p.src==='addr'
    ? ` <span style="color:#C8862B;font-size:11px">${LANG==='ru'?'⚠ адрес приблизительно':'⚠地址推定'}</span>` : '';
  const btn=p.slots
    ? `<button class="addb ${k>=0?'on':''}" onclick="toggleTrip(${p._i})">${
        k>=0 ? (LANG==='ru'?`✓ №${k+1} — убрать`:`✓ 行程第 ${k+1} 站（点击移除）`)
             : T('＋ 加入今日行程')}</button>`
    : '';
  const pplHTML=(p.ppl&&p.ppl.length)
    ? `<div class="ppl">${p.ppl.map(kk=>PPL(kk)?`<button class="pbtn" onclick="showPerson('${kk}')">👤 ${PPL(kk)[0]}</button>`:'').join('')}</div>`
    : '';
  const siteHTML=p.url
    ? `<a class="site" href="${p.url}" target="_blank" rel="noopener">${T('🌐 官网 / 预约')}</a>` : '';
  const al=alerts(p);
  const alBox=al.length?`<div class="alertbox">⚠ ${al.map(x=>LANG==='ru'?x.ru:x.zh).join(' · ')}</div>`:'';
  return `<div class="lp"><b>${pName(p)}${flag}</b>
    <div class="desc">${pDesc(p)}</div>${alBox}
    <div class="row"><span class="k">${T('💰 价格')}</span> ${pPrice(p)}</div>
    <div class="row"><span class="k">${T('🕐 时段')}</span> ${pTime(p)}</div>
    <div class="row"><span class="k">${T('🚇 到达')}</span> ${pTraf(p)}</div>${estHTML}${btn}
    ${pplHTML}${siteHTML}
    <a class="nav" href="https://uri.amap.com/marker?position=${p.lon},${p.lat}&name=${encodeURIComponent(p.name)}"
       target="_blank" rel="noopener">${T('🧭 用高德地图导航过去')}</a></div>`;
}

PTS.forEach((p,i)=>{
  p._i=i;
  const est=p.cat==='base'?'':`<div class="est" data-est="${p._i}"></div>`;
  const flag=p.src==='addr'?' <span style="color:#C8862B;font-size:11px">⚠地址推定</span>':'';
  const m=L.marker([p.lat,p.lon],{icon:ico(CATS[p.cat][0],p.cat==='base',false),title:p.name,riseOnHover:true});
  m.bindPopup(()=>popupHTML(p),{maxWidth:310});
  m.bindTooltip(()=>pName(p),{direction:'top',offset:[0,-9],opacity:.92});
  p._m=m; m.addTo(map);
});

/* ===== 我的位置（GCJ-02 换算复用上面 CRS 里那份，带 outOfChina 保护） ===== */
let meMarker=null, meCircle=null;
function showMe(lat,lng,acc){
  // 浏览器 geolocation 返回 WGS84；地图 CRS 已处理投影，直接用
  // 少数国产浏览器会返回已偏移的 GCJ-02，此时用 GCJFIX 反算回 WGS84
  let ll=[lat,lng];
  if(GCJFIX)ll=gcj2wgsPt(lat,lng);
  ME=ll;
  if(!meMarker){
    meMarker=L.marker(ll,{icon:L.divIcon({className:'',iconSize:[18,18],iconAnchor:[9,9],html:'<div class="meDot"></div>'}),
      zIndexOffset:2000}).addTo(map);
    meMarker.bindPopup(()=>{
      const d=hav(ll,HOTEL);
      const walk=d<2.5?`（${T('步行约')} ${Math.round(d/0.075)} ${T('分钟')}）`:'';
      return `<div class="lp"><b>📍 ${T('我的当前位置')}</b>
      <div class="row">${T('距酒店')} <b>${fmt(d)}</b>${walk}</div>
      <div class="est">${T('定位精度约')} ${acc?Math.round(acc):'?'} ${T('米')}${GCJFIX?' · '+T('已反算 GCJ-02→WGS84'):''}</div>
      <button class="addb" onclick="toggleGCJ()">${GCJFIX?T('↩ 取消校正'):T('⚙ 蓝点偏了？点此校正')}</button></div>`;},{maxWidth:290});
    meCircle=L.circle(ll,{radius:acc||50,color:'#3A6B8F',weight:1,fillColor:'#3A6B8F',fillOpacity:.13}).addTo(map);
  } else { meMarker.setLatLng(ll); meCircle.setLatLng(ll).setRadius(acc||50); }
  if(!isOvPane())renderPl();
}
function toggleGCJ(){
  GCJFIX=!GCJFIX;
  if(meMarker&&meMarker._raw){const r=meMarker._raw;showMe(r[0],r[1],r[2]);meMarker.openPopup();}
  toast(GCJFIX?T('已启用偏移校正（GCJ-02 → WGS84）'):T('已取消偏移校正'));
}
window.toggleGCJ=toggleGCJ;
function locate(){
  const btn=$('mqLoc');          // 三个按钮已统一到右侧竖栏，原面板内的 #bloc 已移除
  if(!navigator.geolocation){toast(T('此浏览器不支持定位'));return;}
  if(watchId!==null){navigator.geolocation.clearWatch(watchId);watchId=null;
    if(meMarker){map.removeLayer(meMarker);map.removeLayer(meCircle);meMarker=null;meCircle=null;}
    ME=null;btn.classList.remove('on');
    // ② 关闭 → 平滑回到初始视角（有行程则回到整条路线）
    if(TRIP.length){const l=tripList();
      map.flyToBounds(L.latLngBounds([HOTEL,...l.map(p=>[p.lat,p.lon])]).pad(.2),{maxZoom:15,duration:.9});}
    else map.flyTo(INITVIEW.c,INITVIEW.z,{duration:.9});
    toast(T('已关闭定位，视角已复位'));
    if(!isOvPane())renderPl();return;}
  toast(T('正在定位…'));
  watchId=navigator.geolocation.watchPosition(pos=>{
    const{latitude,longitude,accuracy}=pos.coords;
    const first=!meMarker;
    showMe(latitude,longitude,accuracy);
    if(meMarker)meMarker._raw=[latitude,longitude,accuracy];
    btn.classList.add('on');
    if(first){map.flyTo(ME,16,{duration:1.1});   // ② 打开 → 平滑移到我的位置
      toast(T('已定位。若光标位置偏移几百米，点蓝点→「校正偏移」'),5000);}
  },err=>{
    btn.classList.remove('on');watchId=null;
    const m={1:T('定位被拒绝，请在浏览器地址栏允许位置权限'),2:T('无法获取位置（信号或网络问题）'),3:T('定位超时，请重试')};
    toast(m[err.code]||((LANG==='ru'?'Ошибка: ':'定位失败：')+err.message),4500);
  },{enableHighAccuracy:true,timeout:12000,maximumAge:15000});
}

/* ===== 地名标签：缩放到 Z_LABEL 以上自动显示，带避让 =====
   为什么不用 Leaflet 的 permanent tooltip：它没有碰撞检测，点位一密就糊成一片。
   这里自己算屏幕矩形，按优先级贪心放置，放不下的直接不画。 */
const Z_LABEL=15;                    // 从这一级开始显示（15≈街区级）
let lblPane=null, LBLS=[], _lblRaf=0;
function initLabels(){
  lblPane=L.DomUtil.create('div','',map.getPanes().markerPane);
  lblPane.style.cssText='position:absolute;top:0;left:0;width:0;height:0;pointer-events:none';
  PTS.forEach(p=>{
    const el=document.createElement('div');
    el.className='mapLbl'; el.dataset.i=p._i;
    lblPane.appendChild(el);
    p._lbl=el;
  });
  map.on('zoomend moveend zoom', scheduleLabels);
  map.on('zoomstart movestart',()=>{ if(lblPane)lblPane.style.visibility='hidden'; });
  map.on('zoomend moveend',()=>{ if(lblPane)lblPane.style.visibility=''; });
  scheduleLabels();
}
function scheduleLabels(){
  if(_lblRaf)return;
  _lblRaf=requestAnimationFrame(()=>{_lblRaf=0;drawLabels();});
}
function drawLabels(){
  if(!lblPane)return;
  const z=map.getZoom();
  // 缩放不够 / 全屏看路线时不显示（那时有专门的编号，再加名字太挤）
  if(z<Z_LABEL){ PTS.forEach(p=>{
      if(p._lbl)p._lbl.classList.remove('on');
      const tt=p._m.getTooltip(); if(tt)tt.setOpacity(.92);
    }); return; }

  const size=map.getSize();
  const pad=7;                        // 矩形之间的最小空隙（放宽一点更透气）
  const placed=[];                    // 已占用的屏幕矩形
  // 优先级：行程中的站点 > 基点(酒店) > 其它；同级按 y 排，保证结果稳定
  const inTrip=new Set(TRIP);
  const cand=PTS.filter(p=>map.hasLayer(p._m))
    .map(p=>({p,pt:map.latLngToContainerPoint([p.lat,p.lon])}))
    .filter(o=>o.pt.x>-60&&o.pt.x<size.x+60&&o.pt.y>-30&&o.pt.y<size.y+30)
    .sort((a,b)=>{
      const ra=inTrip.has(a.p._i)?0:(a.p.cat==='base'?1:2);
      const rb=inTrip.has(b.p._i)?0:(b.p.cat==='base'?1:2);
      return ra-rb || a.pt.y-b.pt.y;
    });

  PTS.forEach(p=>{
    if(p._lbl)p._lbl.classList.remove('on');
    const tt=p._m.getTooltip(); if(tt)tt.setOpacity(.92);   // 先全部恢复
  });
  const hit=(r)=>placed.some(q=>!(r.x2<q.x1-pad||r.x1>q.x2+pad||r.y2<q.y1-pad||r.y1>q.y2+pad));

  cand.forEach(({p,pt})=>{
    const el=p._lbl; if(!el)return;
    // 地图标签只显俄文名：完整格式「Русское (中文)」在地图上会换行成一大块，
    // 实测 22 个标签全部折行、最高 94px、占屏 6.9%（中文版只有 16px / 2.8%）。
    // 完整名称在弹窗和列表里仍然保留，指给司机看不受影响。
    const txt=LANG==='ru'?pName(p).replace(/\s*[（(][^（()）]*[)）]\s*$/,'').trim()||pName(p):pName(p);
    if(el._txt!==txt){ el.textContent=txt; el._txt=txt; el._w=0; }
    el.classList.toggle('trip',inTrip.has(p._i));
    if(!el._w){ el.style.opacity='0'; el.classList.add('on');
                el._w=el.offsetWidth; el._h=el.offsetHeight; el.classList.remove('on'); el.style.opacity=''; }
    const w=el._w,h=el._h;
    // 图标半径：行程编号 27px，普通 15px，基点 21px
    const r=inTrip.has(p._i)?15:(p.cat==='base'?12:9);
    // 四个候选位：下、上、右、左 —— 依次找不重叠的
    const spots=[
      {x:pt.x-w/2, y:pt.y+r+3},
      {x:pt.x-w/2, y:pt.y-r-3-h},
      {x:pt.x+r+4, y:pt.y-h/2},
      {x:pt.x-r-4-w, y:pt.y-h/2}
    ];
    for(const sp of spots){
      const box={x1:sp.x,y1:sp.y,x2:sp.x+w,y2:sp.y+h};
      if(box.x1<2||box.y1<2||box.x2>size.x-2||box.y2>size.y-2) continue;  // 出界
      if(hit(box)) continue;
      const o=map.containerPointToLayerPoint([sp.x,sp.y]);
      L.DomUtil.setPosition(el,o);
      el.classList.add('on');
      const tt=p._m.getTooltip(); if(tt)tt.setOpacity(0);   // 名字已画在地图上，不再重复弹
      placed.push(box);
      return;
    }
    // 四个位置都被占 → 这一轮不显示，避免叠字
  });
}

/* ===== 行程（点击顺序） ===== */
let tripLayer=L.layerGroup().addTo(map);
function tripList(){                                   // ④ 时段为前置约束，段内保持点击先后
  return TRIP.map((i,k)=>({p:PTS[i],k}))
    .sort((x,y)=>SLOTRANK[pickedSlot(x.p)]-SLOTRANK[pickedSlot(y.p)] || x.k-y.k)
    .map(o=>o.p);
}
function firstSlot(p){return [...'mae'].find(k=>p.slots.includes(k))||'a';}
function drawTrip(){
  tripLayer.clearLayers();
  PTS.forEach(p=>p._m.setIcon(ico(CATS[p.cat][0],p.cat==='base',dimmed(p))));
  const list=tripList(); if(!list.length)return;
  const pathAll=[HOTEL,...list.map(p=>[p.lat,p.lon]),HOTEL];
  // 白色描边，浅底深底都清晰
  L.polyline(pathAll,{color:'#fff',weight:7,opacity:.9,lineJoin:'round'}).addTo(tripLayer);
  // 去程：酒店→①
  L.polyline([HOTEL,[list[0].lat,list[0].lon]],
    {color:SLOTCOLOR[pickedSlot(list[0])],weight:4,opacity:.95}).addTo(tripLayer);
  // 各站之间
  for(let i=0;i<list.length-1;i++)
    L.polyline([[list[i].lat,list[i].lon],[list[i+1].lat,list[i+1].lon]],
      {color:SLOTCOLOR[pickedSlot(list[i+1])],weight:4,opacity:.95}).addTo(tripLayer);
  // ★ 回家线
  const last=list[list.length-1];
  L.polyline([[last.lat,last.lon],HOTEL],
    {color:'#8C949B',weight:3.5,opacity:.9,dashArray:'2,8',lineCap:'round'}).addTo(tripLayer);
  L.marker([(last.lat+HOTEL[0])/2,(last.lon+HOTEL[1])/2],{interactive:false,
    icon:L.divIcon({className:'',iconSize:[LANG==='ru'?66:54,18],iconAnchor:[LANG==='ru'?33:27,9],
      html:'<div style="background:rgba(140,148,155,.94);color:#fff;font-size:10px;border-radius:9px;text-align:center;line-height:18px;box-shadow:0 1px 4px rgba(0,0,0,.3)">'+(LANG==='ru'?'🏨 в отель':'🏨 回酒店')+'</div>'})}).addTo(tripLayer);
  list.forEach((p,i)=>p._m.setIcon(numIco(i+1,SLOTCOLOR[pickedSlot(p)])));
  scheduleLabels();                 // 编号图标更大，标签需重新避让
}
/* ===== 「在地图上看整条路线」：进入全屏看图模式 =====
   旧实现的毛病：桌面端只加了 .hide（被 body.dock-* 覆盖，面板根本没收）、
   手机端 .fold 只藏内容留下 633px 空壳、fitBounds 没有把面板占掉的区域算进去、
   而且 .hide 会残留导致之后再开「选地点」是一片空白。
   现在：统一用 body.routeview 收起全部 UI，退出方式有 ✕ / Esc / 点地图 / 底栏。 */
let ROUTEVIEW=false, _rvPrev=null;
function focusRoute(){
  const list=tripList(); if(!list.length){toast(T('还没选地点'),2200);return;}
  ROUTEVIEW=true;
  _rvPrev={dock:DOCK,desktrip:DESKTRIP,up:document.body.classList.contains('sheet-up')};
  document.body.classList.add('routeview');
  document.body.classList.remove('sheet-up');
  rvText();
  $('rvBar').classList.add('show');
  setTimeout(()=>{ map.invalidateSize({animate:false}); fitRoute(); },300);
}
function rvText(){
  const list=tripList(); if(!list.length)return;
  const km=tripKm().toFixed(1);
  $('rvTitle').innerHTML=LANG==='ru'
    ? `${T('🎯 今日行程')} · ${list.length} ${T('站')} · ${km} km<small>${T('Нажмите на карту или Esc, чтобы выйти')}</small>`
    : `🎯 今日行程 · ${list.length} 站 · ${km} km<small>点地图空白处或按 Esc 退出</small>`;
  $('rvXT').textContent=LANG==='ru'?'Выйти':'退出';
  $('rvLm').textContent=T('上午'); $('rvLa').textContent=T('下午');
  $('rvLe').textContent=T('晚上'); $('rvLh').textContent=LANG==='ru'?T('回程'):'回酒店';
}
function fitRoute(){
  const list=tripList(); if(!list.length)return;
  const b=L.latLngBounds([HOTEL,...list.map(p=>[p.lat,p.lon])]);
  // 上下留出提示条与退出条的高度，避免站点被压在边上
  map.fitBounds(b,{maxZoom:16,paddingTopLeft:[26,74],paddingBottomRight:[26,84],animate:true,duration:.6});
}
function exitRoute(){
  if(!ROUTEVIEW)return;
  ROUTEVIEW=false;
  document.body.classList.remove('routeview');
  $('rvBar').classList.remove('show');
  const p=_rvPrev||{}; _rvPrev=null;
  // 还原进入前的面板状态，而不是把用户丢在一个空界面里
  if(!MOBILE()){
    DESKTRIP=!!p.desktrip; DOCK=p.dock||null;
    document.body.classList.toggle('dock-trip',DESKTRIP);
    document.body.classList.remove('dock-ov','dock-menu');
    if(DOCK)document.body.classList.add('dock-'+DOCK);
    syncDeskBtns();
  }else{
    DOCK=p.dock||null;
    document.body.classList.remove('dock-ov','dock-menu','dock-trip');
    if(DOCK)document.body.classList.add('dock-'+DOCK);
    document.querySelectorAll('.dk').forEach(b=>b.classList.toggle('on',b.dataset.d===DOCK));
  }
  setTimeout(fix,320);
}
window.exitRoute=exitRoute;

/* ===== 行程持久化：刷新或意外关闭不丢失 ===== */
function saveTrip(){try{localStorage.setItem('qd_trip',
  JSON.stringify({t:TRIP,s:PICKSLOT,w:WEATHER}));}catch(e){}}
function loadTrip(){
  try{const d=JSON.parse(localStorage.getItem('qd_trip')||'null');
    if(d&&Array.isArray(d.t)&&d.t.length){
      TRIP=d.t.filter(i=>PTS[i]); PICKSLOT=d.s||{};
      if(d.w&&WX[d.w]){WEATHER=d.w;
        document.querySelectorAll('.wxb').forEach(x=>
          x.classList.toggle('on',x.dataset.w===d.w));}
      drawTrip(); syncBadge();
      // 自动切到「今天我想怎么玩」并渲染行程面板
      showPane(false);
      toast(LANG==='ru'?`${T('已恢复上次的行程')}: ${TRIP.length}`
                        :`已恢复上次的 ${TRIP.length} 站行程`,2600);
    }}catch(e){}
}

function toggleTrip(i){
  const k=TRIP.indexOf(i), p=PTS[i];
  if(k>=0){TRIP.splice(k,1); delete PICKSLOT[i];}
  else{TRIP.push(i); PICKSLOT[i]=p.slots.includes(CURSLOT)?CURSLOT:firstSlot(p);}
  const bd=$('slotList'), sc=bd?bd.scrollTop:0;
  drawTrip(); renderPl(); syncBadge(); saveTrip();
  if(bd&&TRIP.length)bd.scrollTop=0; else if(bd)bd.scrollTop=sc;
  if(map.hasLayer(PTS[i]._m)&&PTS[i]._m.isPopupOpen())PTS[i]._m.openPopup();
}
window.toggleTrip=toggleTrip;

/* ===== 长按拖动排序（支持跨时段） ===== */
let dragS=null;
function bindDrag(){
  const cont=$('tripB'); if(!cont)return;
  cont.querySelectorAll('.dragh').forEach(h=>{
    const row=h.closest('.trow');
    const start=e=>{
      if(e.type==='mousedown'&&e.button!==0)return;
      const pt=e.touches?e.touches[0]:e;
      const st={row,id:+row.dataset.i,x0:pt.clientX,y0:pt.clientY,armed:false,timer:null};
      row.classList.add('pressing');
      st.timer=setTimeout(()=>{arm(st,pt);},250);          // 长按 250ms 激活
      const move=ev=>{
        const p=ev.touches?ev.touches[0]:ev;
        if(!st.armed){
          if(Math.abs(p.clientX-st.x0)>12||Math.abs(p.clientY-st.y0)>12){
            clearTimeout(st.timer);row.classList.remove('pressing');
            document.removeEventListener('mousemove',move);document.removeEventListener('touchmove',move);
            document.removeEventListener('mouseup',end);document.removeEventListener('touchend',end);}
          return;}
        ev.preventDefault(); onDragMove(p);
      };
      const end=()=>{
        clearTimeout(st.timer); row.classList.remove('pressing');
        document.removeEventListener('mousemove',move);document.removeEventListener('touchmove',move);
        document.removeEventListener('mouseup',end);document.removeEventListener('touchend',end);
        if(st.armed)onDragEnd();
      };
      document.addEventListener('mousemove',move,{passive:false});
      document.addEventListener('touchmove',move,{passive:false});
      document.addEventListener('mouseup',end);document.addEventListener('touchend',end);
    };
    h.addEventListener('mousedown',start);
    h.addEventListener('touchstart',start,{passive:true});
  });
}
function arm(st,pt){
  st.armed=true; dragS=st;
  const p=PTS[st.id], sl=pickedSlot(p);
  st.row.classList.remove('pressing'); st.row.classList.add('ghost');
  const px=document.createElement('div'); px.className='dragProxy';
  px.innerHTML=`<span class="i" style="background:${SLOTCOLOR[sl]}">⣿</span><span>${pName(p)}</span>`;
  document.body.appendChild(px); st.proxy=px;
  const ln=document.createElement('div'); ln.className='dropline'; st.line=ln;
  if(navigator.vibrate)navigator.vibrate(18);
  onDragMove(pt);
}
function onDragMove(pt){
  const st=dragS; if(!st)return;
  st.proxy.style.left=(pt.clientX+13)+'px';
  st.proxy.style.top=(pt.clientY-15)+'px';
  const cont=$('tripB'); if(!cont)return;
  const cb=cont.getBoundingClientRect();
  if(pt.clientY<cb.top+18)cont.scrollTop-=9;
  else if(pt.clientY>cb.bottom-18)cont.scrollTop+=9;
  cont.querySelectorAll('.tsec').forEach(t=>t.classList.remove('dz'));

  // 1) 按"时段区"划分：标题及其下属行同属一区
  const kids=[...cont.children].filter(n=>n.classList&&
      (n.classList.contains('tsec')||n.classList.contains('trow')));
  const zones={}; let curSec=null;
  kids.forEach(n=>{
    if(n.classList.contains('tsec')){
      curSec=n.dataset.slot;
      const b=n.getBoundingClientRect();
      zones[curSec]={sec:n,top:b.top,bottom:b.bottom,rows:[]};
    }else if(curSec){
      zones[curSec].rows.push(n);
      zones[curSec].bottom=n.getBoundingClientRect().bottom;
    }
  });
  const order=['m','a','e'].filter(k=>zones[k]);
  let slot=null;
  for(const k of order){ if(pt.clientY<=zones[k].bottom){ slot=k; break; } }
  if(!slot) slot=order[order.length-1];

  // 2) 区内定位插入点
  const z=zones[slot];
  const rs=z.rows.filter(r=>r!==st.row);
  let placed=false;
  for(const r of rs){
    const b=r.getBoundingClientRect();
    if(pt.clientY < b.top+b.height/2){ cont.insertBefore(st.line,r); placed=true; break; }
  }
  if(!placed){
    if(rs.length) cont.insertBefore(st.line, rs[rs.length-1].nextSibling);
    else cont.insertBefore(st.line, z.sec.nextSibling);
  }
  st.slot=slot;
  if(z.sec) z.sec.classList.add('dz');
}

function onDragEnd(){
  const st=dragS; if(!st)return;
  const cont=$('tripB');
  // 依据 dropline 在 DOM 中的位置，重建 TRIP 顺序
  const seq=[]; let inserted=false;
  cont.childNodes.forEach(n=>{
    if(n===st.line){seq.push(st.id);inserted=true;return;}
    if(n.classList&&n.classList.contains('trow')){
      const id=+n.dataset.i; if(id!==st.id)seq.push(id);}
  });
  if(!inserted)seq.push(st.id);
  st.proxy.remove(); st.line.remove(); st.row.classList.remove('ghost');
  const newSlot=st.slot||pickedSlot(PTS[st.id]);
  const old=pickedSlot(PTS[st.id]);
  PICKSLOT[st.id]=newSlot;
  // seq 已按视觉顺序排列；TRIP 需满足"同段内顺序=seq顺序"
  TRIP=seq.slice();
  dragS=null;
  const _sc=cont?cont.scrollTop:0;                 // 记住滚动位置
  drawTrip(); renderPl(); syncBadge(); saveTrip();
  const _nb=$('tripB'); if(_nb)_nb.scrollTop=_sc;  // 重绘后恢复
  const p=PTS[st.id];
  if(newSlot!==old){
    const slotTxt=T(SLOTNAME[newSlot]);
    const warn=!p.slots.includes(newSlot)
      ? `<br><span style="color:#E8B4AE">${T('注意：')}${pName(p)} ${T('通常不在')}${slotTxt}${T('开放')}</span>` : '';
    toast(`${T('已移到')}「${slotTxt}」${warn}`,warn?4200:2200);
  }
}
function syncBadge(){ if(typeof syncDockBadge==='function')syncDockBadge();
  const b=$('fabBadge');
  b.textContent=TRIP.length;b.style.display=TRIP.length?'flex':'none';
  const h=$('hdTitle');
  if(h)h.textContent=TRIP.length
      ? `${T('今日已排')} ${TRIP.length} ${T('站')} · ${tripKm().toFixed(1)} km`
      : T('挑食地图 · 青岛');}
function tripKm(){const l=tripList();if(!l.length)return 0;
  const p=[HOTEL,...l.map(x=>[x.lat,x.lon]),HOTEL];let s=0;
  for(let i=0;i<p.length-1;i++)s+=hav(p[i],p[i+1]);return s;}

/* ===== 关键警示：闭馆 / 预约 / 早关门 —— 统一红字 ===== */
function alerts(p){
  const out=[], tm=p.time||'', ds=p.desc||'';
  if(tm.includes('周一闭馆'))     out.push({k:'mon', zh:'周一闭馆',        ru:'ПН — выходной'});
  if(/需预约|须预约/.test(tm))     out.push({k:'bk',  zh:'须提前预约',      ru:'нужна запись'});
  if(ds.includes('停止售票'))      out.push({k:'early',zh:'17:00 前停止售票', ru:'кассы до 17:00'});
  if(tm.includes('需一早出发'))    out.push({k:'early',zh:'需一早出发',      ru:'выезжать рано'});
  return out;
}
function alertHTML(p,mini){
  const a=alerts(p); if(!a.length)return '';
  return a.map(x=>`<span class="alert${mini?' mini':''}">${LANG==='ru'?x.ru:x.zh}</span>`).join('');
}
function okWeather(p){if(p.cat==='base')return true;
  if(WEATHER==='rainy'&&p.out&&!SHOWOUT)return false;return true;}
function dimmed(p){return WEATHER==='cloudy'&&p.elev;}

function syncMap(list){
  const keep=new Set(list.map(p=>p._i)); TRIP.forEach(i=>keep.add(i));
  PTS.forEach(p=>{const show=p.cat==='base'||keep.has(p._i);
    if(show){if(!map.hasLayer(p._m))p._m.addTo(map);}
    else if(map.hasLayer(p._m))map.removeLayer(p._m);
    if(!show&&p._lbl)p._lbl.classList.remove('on');});
  drawTrip();
  scheduleLabels();                 // 可见点位变了，标签要重排
}
function focus(p,el){
  document.querySelectorAll('.item.act').forEach(e=>e.classList.remove('act'));
  if(el)el.classList.add('act');
  if(!map.hasLayer(p._m))p._m.addTo(map);
  map.flyTo([p.lat,p.lon],p.km>8?13:16,{duration:.7});
  setTimeout(()=>p._m.openPopup(),750);
}
function fitTo(list){if(!list.length)return;
  const g=list.filter(p=>p.km<25),use=g.length?g:list;
  map.fitBounds(L.latLngBounds(use.map(p=>[p.lat,p.lon])).extend(HOTEL).pad(.18),{maxZoom:15});}

/* ===== 总览 ===== */
function renderOv(){
  const box=document.getElementById('catList'); box.innerHTML='';
  Object.entries(CATS).forEach(([k,[color,label]])=>{
    const list=PTS.filter(p=>p.cat===k); if(!list.length)return;
    const acc=document.createElement('div'); acc.className='acc';
    const h=document.createElement('div'); h.className='accH';
    h.innerHTML=`<span class="ar">▶</span><span class="dot" style="background:${color}"></span>
      <span class="t">${catName(k)}</span><span class="n">${list.length}</span>`;
    const b=document.createElement('div'); b.className='accB';
    list.slice().sort((x,y)=>x.km-y.km).forEach(p=>{
      const d=document.createElement('div'); d.className='item';
      d.innerHTML=`<div class="nm">${pName(p)}</div><div class="mt">${pTraf(p)} · ${pPrice(p)}</div>`;
      d.onclick=()=>focus(p,d); b.appendChild(d);
    });
    h.onclick=()=>{const was=acc.classList.contains('open');
      box.querySelectorAll('.acc').forEach(a=>a.classList.remove('open'));
      if(!was){acc.classList.add('open');syncMap(list);fitTo(list);}else syncMap(PTS);};
    acc.append(h,b); box.appendChild(acc);
  });
}

/* ===== 今天怎么玩 ===== */
function refInfo(){
  const L=tripList();
  // 1) 本时段已选的最后一站
  const same=L.filter(p=>pickedSlot(p)===CURSLOT);
  if(same.length){const p=same[same.length-1];
    return{ll:[p.lat,p.lon],name:LANG==='ru'?`${T('本时段上一站')} «${pName(p)}»`:`本时段上一站「${p.name}」`,short:T('本时段上一站')};}
  // 2) 往前回溯：上一个有安排的时段的最后一站
  for(let r=SLOTRANK[CURSLOT]-1;r>=0;r--){
    const k=['m','a','e'][r];
    const seg=L.filter(p=>pickedSlot(p)===k);
    if(seg.length){const p=seg[seg.length-1];
      return{ll:[p.lat,p.lon],name:LANG==='ru'?`${T(SLOTNAME[k])} ${T('最后一站')} «${pName(p)}»`
                                                 :`${SLOTNAME[k]} 最后一站「${p.name}」`,short:T(SLOTNAME[k])};}
  }
  // 3) 定位 / 酒店
  if(ME)return{ll:ME,name:T('我的当前位置'),short:LANG==='ru'?'меня':'我'};
  return{ll:HOTEL,name:T('酒店'),short:T('酒店')};
}
function syncTripFlag(){
  document.body.classList.toggle('hastrip', TRIP.length>0);
}
function renderTripBox(){
  const panel=$('tripPanel');
  const box=$('tripBox');
  const list=tripList();

  // —— 主面板里只留一条摘要 ——
  syncTripFlag();
  if(!list.length){
    // 行程空了：桌面端 .tripPanel 在媒体查询里恒为 display:flex，
    // 只摘 .show 会留下一个 72px 的绿色空壳，所以必须连 dock-trip 一起收。
    // 先退出看图模式：exitRoute 会还原进入前的面板状态，
    // 必须放在收面板之前，否则它会把刚关掉的 dock-trip 又装回去。
    if(ROUTEVIEW){ ROUTEVIEW=false; _rvPrev=null;
      document.body.classList.remove('routeview'); $('rvBar').classList.remove('show'); }
    panel.classList.remove('show','fold');
    box.innerHTML='';
    document.querySelector('#tpH .ttl').textContent=T('🎯 今日行程');   // 别留「3 站 · 7.5 km」
    if(!MOBILE()){
      DESKTRIP=false;
      document.body.classList.remove('dock-trip');
      syncDeskBtns();                    // 按钮熄灯 + 角标归零
      setTimeout(fix,280);
    }
    return;
  }
  // 摘要挂到"今日行程"标题栏，主面板内零占位
  document.querySelector('#tpH .ttl').textContent=
    LANG==='ru'?`${T('🎯 今日行程')} · ${list.length} ${T('站')} · ${tripKm().toFixed(1)} km`
              :`${T('🎯 今日行程')}（${list.length} ${T('站')} · ${tripKm().toFixed(1)} km）`;

  // —— 独立面板内容 ——
  panel.classList.add('show');
  if(!MOBILE()) setTimeout(syncTripOpen,0);   // 手机由 dock 控制显隐
  let n=0,h='';
  ['m','a','e'].forEach(sl=>{
    const seg=list.filter(p=>pickedSlot(p)===sl);
    h+=`<div class="tsec" data-slot="${sl}" style="color:${SLOTCOLOR[sl]};background:${SLOTSOFT[sl]}">${SLOTLBL()[sl][0]} · ${SLOTLBL()[sl][1]}${seg.length?'':` <span class="tsecE">${T('未安排 · 可拖入')}</span>`}</div>`;
    seg.forEach(p=>{n++;
      const warn=!p.slots.includes(sl)?`<span class="wn" title="${T('该地点通常不在此时段开放')}">⚠</span>`:'';
      const cdot=`<span class="cdot" style="background:${CATS[p.cat][0]}" title="${catName(p.cat)}"></span>`;
      h+=`<div class="trow" data-i="${p._i}" data-slot="${sl}">
        <span class="dragh" title="${T('长按拖动排序')}">⣿</span>
        <span class="i" style="background:${SLOTCOLOR[sl]}">${n}</span>
        <span class="nm2">${cdot}${pName(p)}${warn}${alertHTML(p,true)}</span>
        <span class="rm" data-rm="${p._i}" title="${T('移除')}">×</span></div>`;});
  });
  box.innerHTML=`<div class="trip">
   <div class="tripB" id="tripB">${h}
     <div class="trowHome">🏨 ${T('回酒店（汉庭·广西路）')}</div></div>
   <div class="tripF">🚶 ${T('全程约')} <b>${tripKm().toFixed(1)} km</b>${T('（含回程，直线累加）')}<br>
     <span style="color:#C8862B">■${T('上午')}</span> <span style="color:#2E7F86">■${T('下午')}</span>
     <span style="color:#5B4B8A">■${T('晚上')}</span> <span style="color:#8C949B">┈${T('回程')}</span>
     <br><span style="color:#6B7880">${T('长按 ⣿ 拖动可排序，也能拖到其它时段')}</span>
     <button class="tripBtn" id="fitTrip">${T('🔍 在地图上查看整条路线')}</button>
     <button class="tripBtn alt" id="expTrip">${LANG==='ru'?'📤 Сохранить как картинку':'📤 导出行程卡片（图片）'}</button></div></div>`;

  const _ex=box.querySelector('#expTrip'); if(_ex)_ex.onclick=()=>askDayThenExport();
  box.querySelector('#fitTrip').onclick=()=>focusRoute();
  box.querySelectorAll('.trow').forEach(r=>{
    r.onclick=e=>{
      const t=e.target;
      if(t.dataset.rm!==undefined){toggleTrip(+t.dataset.rm);return;}
      if(t.classList.contains('dragh'))return;
      const p=PTS[+r.dataset.i];map.flyTo([p.lat,p.lon],p.km>8?13:16,{duration:.7});
      setTimeout(()=>p._m.openPopup(),750);};
  });
  bindDrag();
}

function renderPl(){
  $('wxwrap').style.display='';
  const w=WX[WEATHER],note=$('wxnote');
  note.className='wxnote '+WEATHER;
  note.innerHTML=`<b>${T(w.t)}</b> ${T(w.d)}`;
  const rtBox=$('rtBox');
  if(WEATHER==='rainy'){
    const n=PTS.filter(p=>p.slots&&p.out).length;
    rtBox.innerHTML=`<button class="rainToggle" id="rt">${SHOWOUT
      ?(LANG==='ru'?`✅ ${UI_RU['正在显示 ${n} 个户外项目 — 点击重新隐藏'].replace('${n}',n)}`:`✅ 正在显示 ${n} 个户外项目 — 点击重新隐藏`)
      :(LANG==='ru'?`☂️ ${UI_RU['已隐藏 ${n} 个户外项目 — 仍要查看'].replace('${n}',n)}`:`☂️ 已隐藏 ${n} 个户外项目 — 仍要查看`)}</button>`;
    rtBox.querySelector('#rt').onclick=()=>{SHOWOUT=!SHOWOUT;renderPl();};
  } else rtBox.innerHTML='';

  renderTripBox();

  // 分段器
  const segs=$('segs'); segs.innerHTML='';
  Object.entries(SLOTS).forEach(([k,[label,sub]])=>{
    const all=PTS.filter(p=>p.slots.includes(k)&&okWeather(p));
    const pk=all.filter(p=>TRIP.includes(p._i)&&pickedSlot(p)===k).length;
    const avail=all.filter(p=>!(TRIP.includes(p._i)&&pickedSlot(p)!==k)).length;
    const b=document.createElement('button');
    b.className='seg'+(CURSLOT===k?' on':''); b.dataset.s=k;
    b.innerHTML=`${SLOTLBL()[k][0]}<span class="c">${avail} ${T('项')}</span>${pk?`<span class="pk">${pk}</span>`:''}`;
    b.onclick=()=>{CURSLOT=k;renderPl();
      const l=PTS.filter(p=>p.slots.includes(k)&&okWeather(p)&&!pickedElsewhere(p));
      syncMap(l); if(!TRIP.length)fitTo(l);};
    segs.appendChild(b);
  });

  // 排序基准
  const ref=refInfo();
  const _L=tripList(), sameSlotLast=_L.filter(p=>pickedSlot(p)===CURSLOT).slice(-1)[0];
  const sb=$('sortby');
  sb.title = sameSlotLast
    ? (LANG==='ru' ? `${T('新选的项会排在本时段最后一站之后')}: ${pName(sameSlotLast)}`
                   : `新选的项会排在本时段「${sameSlotLast.name}」之后`)
    : '';
  sb.innerHTML=`↕ ${T('按距')} <b>${ref.name}</b> ${T('由近到远')}`;

  // 列表
  const box=$('slotList'); box.innerHTML='';
  const hidden=PTS.filter(p=>p.slots.includes(CURSLOT)&&okWeather(p)&&pickedElsewhere(p));
  let list=PTS.filter(p=>p.slots.includes(CURSLOT)&&okWeather(p)&&!pickedElsewhere(p));
  list.forEach(p=>p._d=hav(ref.ll,[p.lat,p.lon]));
  list.sort((x,y)=>(dimmed(x)-dimmed(y))||(x._d-y._d));
  if(hidden.length){
    sb.innerHTML+=` <span class="hid2" title="${hidden.map(p=>pName(p)+'→'+T(SLOTNAME[pickedSlot(p)])).join(LANG==='ru'?', ':'、')}">· ${T('已隐藏')} ${hidden.length} ${T('项')}</span>`;
  }
  if(!list.length){box.insertAdjacentHTML('beforeend',`<div class="empty">${T('该时段暂无可选项目')}</div>`);}
  else list.forEach((p,idx)=>{
    const on=TRIP.includes(p._i);
    const d=document.createElement('div');
    d.className='pick'+(on?' on':'')+(dimmed(p)?' dim':'');
    const cl=CATS[p.cat], _cn=catName(p.cat);
    const _m=_cn.match(/^(\S+)\s+([\s\S]+)$/), cIcon=_m?_m[1]:'', cName=_m?_m[2]:_cn;
    const tags='<span class="tag cat" style="background:'+cl[0]+'1f;color:'+cl[0]+'">'+cIcon+' '+cName+'</span>'
      +(!p.out?'<span class="tag in">'+T('室内')+'</span>':'')
      +(dimmed(p)?'<span class="tag warn">'+T('阴天视野差')+'</span>':'')
      +(!on&&idx<3&&!dimmed(p)?'<span class="tag near">'+T('最近')+'</span>':'')
      +alertHTML(p,true);
    const walkTxt=p._d<2.5?`${T('步行约')} ${Math.round(p._d/0.075)} ${T('分钟')}`:T('需乘车');
    d.innerHTML=`<span class="cb">${on?'✓':''}</span>
      <span class="info"><span class="nm">${pName(p)}</span>${tags}
        <div class="mt">${T('距')}${LANG==='ru'?' ':''}${ref.short} ${fmt(p._d)}${p._d<2.5?' · '+walkTxt:''} · ${pPrice(p)}</div>
        <div class="mt2">${pTraf(p)}</div></span>
      <span class="ord" style="background:${SLOTCOLOR[firstSlot(p)]}">${on?TRIP.indexOf(p._i)+1:''}</span>`;
    d.onclick=e=>{e.stopPropagation();toggleTrip(p._i);};
    box.appendChild(d);
  });
  syncMap(list);
}

/* ===================== 导出行程卡片 v2（Canvas） ===================== */

/* 询问这是哪一天 */
function askDayThenExport(){
  const list=tripList();
  if(!list.length){toast(LANG==='ru'?'Сначала добавьте места':'请先选择地点');return;}
  const RU=LANG==='ru';
  const saved=(()=>{try{return localStorage.getItem('qd_daylabel')||'';}catch(e){return '';}})();
  const d=new Date(), pad=n=>String(n).padStart(2,'0');
  const def = saved || (RU?`День 1 · ${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`
                          :`第 1 天 · ${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`);
  $('dayInput').value=def;
  $('dayLabel').textContent = RU?'Какой это день?':'这是哪一天的行程？';
  $('dayHint').textContent  = RU?'Появится в шапке карточки':'会印在卡片顶部';
  $('dayOk').textContent    = RU?'Создать картинку':'生成图片';
  $('dayCancel').textContent= RU?'Отмена':'取消';
  $('dayMask').classList.add('show');
  setTimeout(()=>$('dayInput').select(),80);
}
function closeDay(){$('dayMask').classList.remove('show');}
window.askDayThenExport=askDayThenExport; window.closeDay=closeDay;

/* 把路线渲染成缩略图：主动加载所需瓦片，保证底图完整 */
function routeThumb(list, W, H){
  return new Promise(resolve=>{
    const cv=document.createElement('canvas'); cv.width=W; cv.height=H;
    const g=cv.getContext('2d');
    g.fillStyle='#EFE9DC'; g.fillRect(0,0,W,H);

    const pts=[HOTEL, ...list.map(p=>[p.lat,p.lon])];
    const lats=pts.map(p=>p[0]), lons=pts.map(p=>p[1]);
    let minLa=Math.min(...lats), maxLa=Math.max(...lats);
    let minLo=Math.min(...lons), maxLo=Math.max(...lons);
    const padLa=Math.max((maxLa-minLa)*0.22,0.003), padLo=Math.max((maxLo-minLo)*0.22,0.003);
    minLa-=padLa; maxLa+=padLa; minLo-=padLo; maxLo+=padLo;

    const crs=map.options.crs;
    let z=17;
    for(z=17; z>=9; z--){
      const a=crs.latLngToPoint(L.latLng(maxLa,minLo),z);
      const b=crs.latLngToPoint(L.latLng(minLa,maxLo),z);
      if((b.x-a.x)<=W && (b.y-a.y)<=H) break;
    }
    const tl=crs.latLngToPoint(L.latLng(maxLa,minLo),z);
    const br=crs.latLngToPoint(L.latLng(minLa,maxLo),z);
    const ox=(tl.x+br.x)/2-W/2, oy=(tl.y+br.y)/2-H/2;
    const toXY=(la,lo)=>{const p=crs.latLngToPoint(L.latLng(la,lo),z);return [p.x-ox,p.y-oy];};

    const TS=256;
    const x0=Math.floor(ox/TS), x1=Math.floor((ox+W)/TS);
    const y0=Math.floor(oy/TS), y1=Math.floor((oy+H)/TS);
    const jobs=[];
    for(let tx=x0;tx<=x1;tx++)for(let ty=y0;ty<=y1;ty++) jobs.push([tx,ty]);

    let left=jobs.length;
    const done=()=>{
      // 提亮，突出线条
      g.fillStyle='rgba(255,255,255,.34)'; g.fillRect(0,0,W,H);
      const path=[HOTEL,...list.map(p=>[p.lat,p.lon]),HOTEL].map(p=>toXY(p[0],p[1]));
      g.lineCap='round'; g.lineJoin='round';
      g.strokeStyle='rgba(255,255,255,.95)'; g.lineWidth=8;
      g.beginPath(); path.forEach((p,i)=>i?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1])); g.stroke();
      for(let i=0;i<path.length-1;i++){
        const last=(i===path.length-2);
        g.strokeStyle=last?'#8C949B':SLOTCOLOR[pickedSlot(list[Math.min(i,list.length-1)])];
        g.lineWidth=last?3.5:5; g.setLineDash(last?[3,7]:[]);
        g.beginPath(); g.moveTo(path[i][0],path[i][1]); g.lineTo(path[i+1][0],path[i+1][1]); g.stroke();
      }
      g.setLineDash([]);
      const h=toXY(HOTEL[0],HOTEL[1]);
      g.fillStyle='#fff'; g.beginPath(); g.arc(h[0],h[1],10,0,7); g.fill();
      g.fillStyle='#1C2B33'; g.beginPath(); g.arc(h[0],h[1],6.5,0,7); g.fill();
      list.forEach((p,i)=>{
        const [x,y]=toXY(p.lat,p.lon);
        g.save(); g.shadowColor='rgba(0,0,0,.25)'; g.shadowBlur=6; g.shadowOffsetY=1.5;
        g.fillStyle='#fff'; g.beginPath(); g.arc(x,y,14,0,7); g.fill(); g.restore();
        g.fillStyle=SLOTCOLOR[pickedSlot(p)]; g.beginPath(); g.arc(x,y,11.5,0,7); g.fill();
        g.fillStyle='#fff'; g.font='700 13px -apple-system,sans-serif';
        g.textAlign='center'; g.textBaseline='middle';
        g.fillText(String(i+1),x,y+.5);
      });
      g.textAlign='left'; g.textBaseline='top';
      resolve(cv);
    };
    if(!left){done();return;}
    const tpl=cur._url, subs=cur.options.subdomains||'1234';
    jobs.forEach(([tx,ty],k)=>{
      const im=new Image(); im.crossOrigin='anonymous';
      im.onload=()=>{ try{g.drawImage(im, tx*TS-ox, ty*TS-oy, TS, TS);}catch(e){} if(--left<=0)done(); };
      im.onerror=()=>{ if(--left<=0)done(); };
      im.src=tpl.replace('{s}',subs[k%subs.length]).replace('{x}',tx).replace('{y}',ty).replace('{z}',z);
    });
    setTimeout(()=>{ if(left>0){left=0;done();} },4000);   // 兜底
  });
}

async function exportCard(dayText){
  const list=tripList(); if(!list.length)return;
  const RU = LANG==='ru';
  try{localStorage.setItem('qd_daylabel',dayText||'');}catch(e){}
  toast(RU?'Готовим картинку…':'正在生成…',1400);

  const W=820, PAD=44, DPR=2;
  const INK='#1C2B33', SUB='#55666F', LINE='#E3DCCB', RED='#B93A32';
  const F=(s,w)=>`${w||400} ${s}px -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif`;
  const probe=document.createElement('canvas').getContext('2d');
  function wrap(text,maxW,font){
    probe.font=font; const out=[]; let line='';
    for(const ch of String(text)){
      if(probe.measureText(line+ch).width>maxW && line){out.push(line);line=ch;}
      else line+=ch;
    }
    if(line)out.push(line); return out;
  }

  const innerW=W-PAD*2;
  const THUMB_H=300;

  /* —— 预排版 —— */
  let H = 132 + THUMB_H + 26;
  const rows=[];
  ['m','a','e'].forEach(sl=>{
    const seg=list.filter(p=>pickedSlot(p)===sl);
    if(!seg.length)return;
    rows.push({t:'slot',sl}); H+=44;
    seg.forEach(p=>{
      const nm=wrap(pName(p),innerW-78,F(17,600));
      const meta=wrap(`${pPrice(p)}　·　${pTraf(p)}`,innerW-78,F(12.5));
      const al=alerts(p);
      const h=12+nm.length*24+meta.length*19+(al.length?24:0)+12;
      rows.push({t:'poi',p,nm,meta,al,h}); H+=h;
    });
  });
  H += 30;                                     // 回程
  const EROWS=Math.ceil(EMERG.length/2);
  const EBOX = 30 + EROWS*28 + 14;             // 紧急电话卡片高
  H += EBOX + 22;
  H += 42;                                     // 页脚

  const cv=document.createElement('canvas');
  cv.width=W*DPR; cv.height=H*DPR;
  const g=cv.getContext('2d'); g.scale(DPR,DPR); g.textBaseline='top';
  const rr=(x,y,w,h,r)=>{g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);
    g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath();};

  g.fillStyle='#FBF9F4'; g.fillRect(0,0,W,H);

  /* —— 页头 —— */
  g.fillStyle=INK; g.fillRect(0,0,W,118);
  // 页头下沿朱砂锦边，与界面呼应
  const gr=g.createLinearGradient(0,0,W,0);
  gr.addColorStop(0,'#B93A32'); gr.addColorStop(.42,'#B93A32'); gr.addColorStop(1,'rgba(185,58,50,.12)');
  g.fillStyle=gr; g.fillRect(0,116,W,2.5);
  // 左侧朱砂竖印，像书口的红签
  g.fillStyle='#B93A32'; g.fillRect(0,0,4,118);
  g.fillStyle='#fff'; g.font=`700 15px "Songti SC","STSong","SimSun",Georgia,serif`;
  g.fillText(RU?'ЦИНДАО':'青　岛', PAD, 30);
  g.fillStyle='rgba(255,255,255,.42)'; g.font=F(11.5,500);
  g.fillText(RU?'МАРШРУТ НА ДЕНЬ':'ONE DAY ROUTE', PAD, 52);
  // 右侧：日期
  if(dayText){
    g.textAlign='right'; g.fillStyle='#fff'; g.font=F(19,700);
    g.fillText(dayText, W-PAD, 34); g.textAlign='left';
  }
  // 底部细横条：站数 / 时段色点
  g.fillStyle='rgba(255,255,255,.55)'; g.font=F(12);
  const cnt=RU?`${list.length} мест`:`${list.length} 个地点`;
  g.fillText(cnt, PAD, 84);
  let dx=PAD+g.measureText(cnt).width+18;
  ['m','a','e'].forEach(sl=>{
    const n=list.filter(p=>pickedSlot(p)===sl).length; if(!n)return;
    g.fillStyle=SLOTCOLOR[sl]; g.beginPath(); g.arc(dx+4,90,4,0,7); g.fill();
    g.fillStyle='rgba(255,255,255,.55)';
    const lb={m:RU?'утро':'上午',a:RU?'день':'下午',e:RU?'вечер':'晚上'}[sl]+' '+n;
    g.fillText(lb, dx+13, 84); dx+=13+g.measureText(lb).width+16;
  });

  /* —— 路线缩略图 —— */
  let y=118;
  try{
    const th=await routeThumb(list, W, THUMB_H);
    g.drawImage(th,0,y,W,THUMB_H);
  }catch(e){
    g.fillStyle='#EFE9DC'; g.fillRect(0,y,W,THUMB_H);
  }
  y+=THUMB_H+26;

  /* —— 站点 —— */
  rows.forEach(r=>{
    if(r.t==='slot'){
      const nm={m:RU?'УТРО':'上午',a:RU?'ДЕНЬ':'下午',e:RU?'ВЕЧЕР':'晚上'}[r.sl];
      const hr={m:'05:30–11:30',a:'11:30–17:30',e:'17:30–23:00'}[r.sl];
      g.fillStyle=SLOTCOLOR[r.sl]; rr(PAD,y+6,3,15,1.5); g.fill();
      g.fillStyle=INK; g.font=F(13,700); g.fillText(nm, PAD+13, y+6);
      const nw=g.measureText(nm).width;
      g.fillStyle=SUB; g.font=F(11.5);
      g.fillText(hr, PAD+13+nw+12, y+8);
      y+=44; return;
    }
    const {p,nm,meta,al,h}=r;
    const n=list.indexOf(p)+1, sl=pickedSlot(p);
    g.fillStyle=SLOTCOLOR[sl]; g.beginPath(); g.arc(PAD+16,y+18,15,0,7); g.fill();
    g.fillStyle='#fff'; g.font=F(14,700); g.textAlign='center';
    g.fillText(String(n), PAD+16, y+10); g.textAlign='left';

    let ty=y+8;
    g.fillStyle=INK; g.font=F(17,600);
    nm.forEach(l=>{g.fillText(l, PAD+48, ty); ty+=24;});
    g.fillStyle=SUB; g.font=F(12.5);
    meta.forEach(l=>{g.fillText(l, PAD+48, ty); ty+=19;});
    if(al.length){
      const txt=al.map(x=>RU?x.ru:x.zh).join(' · ');
      g.font=F(12,700);
      g.fillStyle=RED; g.fillText('●', PAD+48, ty+1);
      g.fillText(txt, PAD+62, ty);
      ty+=24;
    }
    g.strokeStyle=LINE; g.lineWidth=1;
    g.beginPath(); g.moveTo(PAD+48,y+h-1); g.lineTo(W-PAD,y+h-1); g.stroke();
    y+=h;
  });

  /* —— 回程 —— */
  g.fillStyle=SUB; g.font=F(13);
  g.fillText(RU?'· · ·  обратно в отель':'· · ·  返回酒店', PAD+48, y+2);
  y+=30;

  /* —— 紧急电话 —— */
  g.fillStyle='#FBF3F1'; rr(PAD,y,innerW,EBOX,6); g.fill();
  g.strokeStyle='#E8CFC9'; g.lineWidth=1; rr(PAD,y,innerW,EBOX,6); g.stroke();
  g.fillStyle=RED; g.font=F(11.5,700);
  g.fillText(RU?'ЭКСТРЕННЫЕ НОМЕРА':'紧 急 电 话', PAD+18, y+12);
  const colW=(innerW-36)/2;
  EMERG.forEach(([label,num],i)=>{
    const ru=label.split(' / ')[0], zh=label.split(' / ')[1]||ru;
    const bx=PAD+18+(i%2)*colW, by=y+32+Math.floor(i/2)*28;
    g.fillStyle=INK; g.font=F(15,700);
    g.fillText(num, bx, by);
    const nw=g.measureText(num).width;
    g.fillStyle=SUB; g.font=F(11.5);
    g.fillText(RU?ru:zh, bx+nw+12, by+3);
  });
  y += EBOX + 22;

  /* —— 页脚 —— */
  const d=new Date(), pad=n=>String(n).padStart(2,'0');
  const ds=`${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  g.strokeStyle=LINE; g.beginPath(); g.moveTo(PAD,y); g.lineTo(W-PAD,y); g.stroke();
  g.fillStyle=SUB; g.font=F(11);
  g.fillText(RU?`Цены и часы уточняйте на месте · ${ds}`
               :`票价与开放时间以现场为准 · ${ds}`, PAD, y+12);
  g.textAlign='right'; g.fillStyle='#C6BFB0'; g.font=F(11,600);
  g.fillText('QINGDAO', W-PAD, y+12); g.textAlign='left';

  cv.toBlob(bl=>{
    const url=URL.createObjectURL(bl);
    const a=document.createElement('a');
    const tag=(dayText||'route').replace(/[\\/:*?"<>|]/g,'').replace(/\s+/g,'-');
    a.href=url; a.download=`qingdao-${tag}.png`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),4000);
    toast(RU?'Картинка сохранена ✓':'图片已保存 ✓',2400);
  },'image/png');
}
window.exportCard=exportCard;

/* ===== 控件 ===== */
/* 主面板两个视图的切换（原先靠两个隐藏的 tab 按钮 .click() 驱动，
   按钮在任何宽度下都是 display:none，纯属绕路，现在改成直接调函数） */
function showPane(ov){
  $('paneOv').style.display=ov?'':'none';
  $('panePl').style.display=ov?'none':'flex';
  document.querySelectorAll('.acc.open').forEach(a=>a.classList.remove('open'));
  document.querySelectorAll('.item.act').forEach(e=>e.classList.remove('act'));
  $('tripPanel').classList.toggle('show',!ov&&TRIP.length>0);
  if(ov){$('wxwrap').style.display='none';renderOv();syncMap(PTS);}
  else renderPl();
}
function isOvPane(){return $('paneOv').style.display!=='none';}   // 函数声明：会提升，避免暂时性死区
document.querySelectorAll('.wxb').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('.wxb').forEach(x=>x.classList.remove('on'));
  b.classList.add('on');WEATHER=b.dataset.w;SHOWOUT=false;renderPl();saveTrip();});
const pn=$('pn'),fab=$('fab');
document.getElementById('cl').onclick=()=>{
  if(innerWidth>760){ DOCK=null; document.body.classList.remove('dock-ov','dock-menu');
    syncDeskBtns(); return; }
  pn.classList.add('hide'); fab.classList.add('show');
};
document.getElementById('cl2').onclick=e=>{
  e.stopPropagation();
  if(innerWidth<=760){ setDock(null); return; }
  DESKTRIP=false; document.body.classList.remove('dock-trip'); syncDeskBtns();
};
fab.onclick=()=>{pn.classList.remove('hide');fab.classList.remove('show');fix();};

/* ===== 手机底部 Tab：两个抽屉互斥 ===== */
const MOBILE=()=>innerWidth<=760;
let DOCK=null;                       // null=都收起 / 'menu' / 'trip'
let DESKTRIP=false;                       // 桌面：行程面板独立开关
function syncDeskBtns(){
  document.querySelectorAll('.ddk').forEach(b=>{
    const d=b.dataset.d;
    b.classList.toggle('on', d==='trip' ? DESKTRIP : DOCK===d);
  });
  const bd=$('ddBadge');
  if(bd){bd.textContent=TRIP.length; bd.classList.toggle('show',TRIP.length>0);}
}
function setDock(d){
  // 在全屏看路线时点任何一栏 → 只关看图模式，面板状态交给下面的正常流程
  if(ROUTEVIEW){ ROUTEVIEW=false; _rvPrev=null;
    document.body.classList.remove('routeview'); $('rvBar').classList.remove('show'); }
  const desk=innerWidth>760;
  // 桌面：行程是独立开关，可与右侧面板同时打开
  if(desk && d==='trip'){
    DESKTRIP=!DESKTRIP;
    if(DESKTRIP){ $('tripPanel').classList.remove('fold'); renderTripBox(); }
    document.body.classList.toggle('dock-trip', DESKTRIP);
    syncDeskBtns(); setTimeout(fix,280);
    return;
  }
  DOCK=d;
  ['pn','tripPanel'].forEach(id=>{const e=$(id); if(e){e.style.transform='';e.style.height='';}});
  if(d==='ov'||d==='menu'){
    const wantOv=(d==='ov');
    if(isOvPane()!==wantOv) showPane(wantOv);
  }
  if(!desk && d==='trip'){ $('tripPanel').classList.remove('fold'); renderTripBox(); }
  document.body.classList.remove('dock-ov','dock-menu','sheet-up');
  if(!desk) document.body.classList.remove('dock-trip');
  if(d) document.body.classList.add('dock-'+d);
  if(desk && DESKTRIP) document.body.classList.add('dock-trip');
  document.querySelectorAll('.dk').forEach(b=>b.classList.toggle('on',b.dataset.d===d));
  syncDeskBtns();
  setTimeout(fix,300);
}
document.querySelectorAll('.ddk').forEach(b=>{
  b.onclick=()=>{
    const d=b.dataset.d;
    if(d==='trip' && !TRIP.length && !DESKTRIP){
      toast(LANG==='ru'?'Маршрут пуст':'还没选地点',2200); setDock('menu'); return;
    }
    // 桌面：点当前栏不关闭（要关用面板上的「—」），点另一栏直接切换
    setDock(d);
  };
});
function openDock(d){
  if(d==='trip' && !TRIP.length){
    toast(LANG==='ru'?'Маршрут пуст — выберите места':'还没选地点，先去「选地点」吧',2400);
    setDock('menu'); return;
  }
  setDock(DOCK===d?null:d);
}
document.querySelectorAll('.dk').forEach(b=>{
  b.onclick=()=>openDock(b.dataset.d);
  let sy=null;
  b.addEventListener('touchstart',e=>{sy=e.touches[0].clientY;},{passive:true});
  b.addEventListener('touchmove',e=>{
    if(sy===null)return;
    if(sy-e.touches[0].clientY>26){ sy=null; if(DOCK!==b.dataset.d) openDock(b.dataset.d); }
  },{passive:true});
  b.addEventListener('touchend',()=>{sy=null;});
});
/* ===== 顶栏下滑收起（跟手 + 惯性判定），两个面板共用 ===== */
function initSheet(panelId, headId){
  const P=$(panelId), H=$(headId);
  if(!P||!H)return;
  let sy=0, dy=0, t0=0, active=false, h0=0;

  const start=e=>{
    if(!MOBILE())return;
    if(e.target.closest('.langsw')||e.target.closest('.clr')||e.target.closest('.mini'))return;
    const pt=e.touches?e.touches[0]:e;
    sy=pt.clientY; dy=0; t0=Date.now(); active=true;
    h0=P.getBoundingClientRect().height;
    P.classList.add('dragging');
    document.addEventListener('mousemove',move,{passive:false});
    document.addEventListener('touchmove',move,{passive:false});
    document.addEventListener('mouseup',end);
    document.addEventListener('touchend',end);
  };
  const move=e=>{
    if(!active)return;
    const pt=e.touches?e.touches[0]:e;
    dy=pt.clientY-sy;
    if(e.cancelable)e.preventDefault();
    if(dy<0){
      const maxH=innerHeight*0.92;
      P.style.height=Math.min(h0-dy, maxH)+'px';
      P.style.transform='';
    }else{
      P.style.height=h0+'px';
      P.style.transform=`translateY(${dy}px)`;
    }
  };
  const end=()=>{
    if(!active)return;
    active=false;
    P.classList.remove('dragging');
    document.removeEventListener('mousemove',move);
    document.removeEventListener('touchmove',move);
    document.removeEventListener('mouseup',end);
    document.removeEventListener('touchend',end);
    const dt=Math.max(1,Date.now()-t0);
    const v=dy/dt;
    P.style.transform=''; P.style.height='';
    const up=document.body.classList.contains('sheet-up');
    if(dy<-50 || v<-0.4){
      if(!up){ document.body.classList.add('sheet-up'); setTimeout(fix,340); }
      return;
    }
    if(up && dy>40){ document.body.classList.remove('sheet-up'); setTimeout(fix,340); return; }
    if(dy>Math.min(h0*0.22,140) || v>0.5){ setDock(null); }
  };
  H.addEventListener('mousedown',start);
  H.addEventListener('touchstart',start,{passive:true});
  // 轻点不再收起——完全交给滑动
}
initSheet('pn','pnH');
initSheet('tripPanel','tpH');
/* 地图快捷键 */
$('mqHotel').onclick=()=>{map.flyTo(HOTEL,15,{duration:.6});};
$('mqLoc').onclick=locate;      // 高亮状态由 locate() 内部维护
$('mqLang').onclick=()=>setLang(LANG==='zh'?'ru':'zh');   // 手机：一键在中/俄之间切换
$('mqAll').onclick=()=>{
  document.querySelectorAll('.acc').forEach(a=>a.classList.remove('open'));
  syncMap(isOvPane()?PTS:PTS.filter(p=>p.slots&&okWeather(p)));
  fitTo(PTS.filter(p=>p.km<25));
};
function syncDockBadge(){
  const b=$('dockBadge');
  b.textContent=TRIP.length; b.classList.toggle('show',TRIP.length>0);
}


/* 清空行程：两个面板的「清空」按钮共用，保证状态一次清干净 */
function clearTrip(){
  if(!TRIP.length)return;
  TRIP=[];PICKSLOT={};
  drawTrip();          // 擦掉连线与编号图标
  renderPl();          // 内部会调 renderTripBox()，负责收面板/复位标题/熄按钮
  syncBadge();         // FAB 角标 + 主面板标题
  saveTrip();          // 同步到 localStorage，刷新后不会又冒出来
  if(MOBILE())setDock('menu');    // 手机：空面板没意义，直接送回「选地点」
  toast(LANG==='ru'?'Маршрут очищен':'已清空行程',1800);
}
document.getElementById('clrTrip1').onclick=e=>{e.stopPropagation();clearTrip();};
document.getElementById('tpH').onclick=e=>{
  if(e.target.id==='clrTrip2'){ clearTrip(); return; }
  if(innerWidth<=760) return;                    // 手机：由 initSheet 的手势接管
  $('tripPanel').classList.toggle('fold');
  syncTripOpen();
};
function syncTripOpen(){
  const tp=$('tripPanel');
  const open = tp.classList.contains('show') && !tp.classList.contains('fold');
  document.body.classList.toggle('tripopen', open && innerWidth<=760);
}
addEventListener('resize',syncTripOpen);
$('pmask').onclick=e=>{if(e.target.id==='pmask')hidePerson();};
$('dayMask').onclick=e=>{if(e.target.id==='dayMask')closeDay();};
$('dayInput').addEventListener('keydown',e=>{
  if(e.key==='Enter'){closeDay();exportCard($('dayInput').value.trim());}
  if(e.key==='Escape')closeDay();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')hidePerson();});
/* 全屏看路线：退出的三条路 —— ✕ 按钮 / Esc / 点地图空白处 */
$('rvX').onclick=e=>{e.stopPropagation();exitRoute();};
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&ROUTEVIEW)exitRoute();});
// 点地图空白处退出；但如果只是想关掉某个 popup，就不算退出
map.on('click',()=>{
  if(!ROUTEVIEW)return;
  if(document.querySelector('.leaflet-popup')){map.closePopup();return;}
  exitRoute();
});
addEventListener('resize',()=>{if(ROUTEVIEW)setTimeout(fitRoute,120);});

/* 启动时若 localStorage 记着俄语，必须补一次静态文案渲染：
   applyStatic() 以前只在 setLang() 里调用，所以「刷新后半个界面还是中文」。 */
if(LANG==='ru'){
  document.body.classList.add('ru');
  document.documentElement.lang='ru';
  document.querySelectorAll('.lgbtn').forEach(b=>b.classList.toggle('on',b.dataset.l==='ru'));
  PTS.forEach(p=>{
    p._m.unbindTooltip().bindTooltip(pName(p),{direction:'top',offset:[0,-9],opacity:.92});
    p._m.unbindPopup().bindPopup(()=>popupHTML(p),{maxWidth:310});
  });
}
applyStatic();      // 无条件跑一次：语言角标等静态文案不该依赖"是否俄语"分支
initLabels();                                 // 地名标签引擎（需在 marker 建好后）
renderOv(); syncBadge();
loadTrip();                                   // 会在有存档时切到「选地点」视图
if(MOBILE()) setDock(null);
// 桌面：有恢复的行程就停在「选地点」，否则回默认的总览。
// （setDock 会按 isOvPane() 同步面板内容，必须放在 loadTrip 之后判断）
else setDock(isOvPane()?'ov':'menu');
</script>
</body></html>"""
