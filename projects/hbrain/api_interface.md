### Query Style
* alias 对应名称, tags 对应分类标签.
* google style: https://developers.google.com/knowledge-graph/
* es style: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html
* 中文里+和|都有特殊字符，容易搞错，所以用AND, OR.


### 知识图谱数据实体接口

/api/v1/entities?q=alias:山药%20OR%20alias:山茱萸&offset=0&limit=20

说明：查出来的东西，比如山药查出来药典和中医世家两条数据，需要按source.confidence 排序。

````
{
    code: 0,
    message: "成功",
    result: [
        {
            id: "57c939affdcdad190ba67c94",
            srank: -1,
            alias: [
                "山药"
            ],
            tags: ["中药"],
            claims: [
                {'p': '', 'o': ''}
            ],
            createdTime: "2016-09-03T17:49:11:549Z",
            updatedTime: "2016-09-03T17:49:11:549Z",
            dataSource: "蒲标网",
            total: 1,
            source: {
                url: "http://www.zysj.com.cn/zhongyaocai/yaocai_s/shanzhuyu.html",
                domain: "www.zysj.com.cn",
                confidence: "0.8",
                trackingId: "8c619e40a735b67111b55c6245ba297aac0658b7"
            }
        },
        {
            id: "57c939affdcdad190ba67c94",
            srank: -1,
            alias: [
                "山茱萸"
            ],
            tags: ["中药"],
            claims: [
                {
                    p: "实体定义",
                    o: "为山茱萸科植物山茱萸的果肉。10～11月间果实成熟变红后采摘，采后除去枝梗和果柄，用文火烘焙，冷后，取下果肉，再晒干或用文火烘干。宜放置阴暗干燥处，以防霉蛀变质。"
                },
                {
                    p: "药材名称",
                    o: "山茱萸"
                },
                {
                    p: "拼音",
                    o: "Shān Zhū Yú"
                },
                {
                    p: "英文名",
                    o: "Asiatic Cornelian Cherry Fruit"
                },
                {
                    p: "别名",
                    o: "蜀枣（《本经》），鼠矢、鸡足（《吴昔本草》），山萸肉（《小儿药证直诀》），实枣儿（《救荒本草》），肉枣（《纲目》），枣皮（《会约医镜》），萸肉（《医学衷中参西录》），药枣（《四川中药志》）。"
                },
                {
                    p: "出处",
                    o: "《本经》"
                },
                {
                    p: "原形态",
                    o: "落叶小乔木，高4米左右。枝皮灰棕色，小枝无毛。单叶对生；叶片椭圆形或长椭圆形，长5～7厘米，宽3～4.5厘米，先端窄，长锐尖形，基部圆形或阔楔形，全缘，上面近光滑，偶被极细毛，下面被白色伏毛，脉腋有黄褐色毛丛，侧脉5～7对，弧形平行排列；叶柄长1厘米左右。花先叶开放，成伞形花序，簇生于小枝顶端，其下具数片芽鳞状苞片；花小；花萼4，不显着；花瓣4，黄色；雄蕊4；于房下位。核果长椭圆形，长1.2～1.5厘米，直径7毫米左右，无毛，成熟后红色；果柄长1.5～2厘米。种子长椭圆形，两端钝圆。花期5～6月。果期8～10月。"
                },
                {
                    p: "生境分部",
                    o: "杂生于山坡灌木林中。有栽培。分布陕西、河南、山西、山东、安徽、浙江、四川等地。产浙江、河南、安徽、陕西、山西、四川等地。"
                },
                {
                    p: "性状",
                    o: "肉质果皮破裂皱缩，不完整或呈扁简状，长约1.5厘米，宽约o.5厘米。新货表面为紫红色，陈久者则多为紫黑色，有光泽，基部有时可见果柄痕，顶端有一四形宿萼痕迹。质柔润不易碎。无臭，味酸而涩苦。以无核、皮肉肥厚、色红油润者佳。"
                },
                {
                    p: "化学成分",
                    o: "含莫罗忍冬甙（morroniside）、7-0-甲基莫罗忍冬甙（7-0-methylmorroniside）、獐牙菜甙（sweroside）、番木鳖甙（Ioganin）、山茱萸鞣质1、2、3、（cornus-tannin 1,2,3）等。"
                },
                {
                    p: "炮制",
                    o: "山萸肉：洗净，除去果核及杂质，晒干。酒山萸：取净山萸肉，用黄酒拌匀，密封容器内，置水锅中，隔水加热，炖至酒吸尽，取出，晾干（山萸肉每100斤，用黄酒20～25斤）。蒸山萸：取净山萸肉，置笼屉内加热蒸黑为度，取出，晒干。"
                },
                {
                    p: "性味",
                    o: "酸，微温。 ①《本经》："味酸，平。" ②《吴普本草》："神农、黄帝、雷公、扁鹊：酸，无毒。岐伯：辛。" ③《别录》："微温，无毒。" ④《药性论》："味咸辛，大热。""
                },
                {
                    p: "归经",
                    o: "入肝、肾经。 ①《汤液本草》："入足厥阴、少阴经。" ②《药品化义》："入肝、心、肾三经。" ⑧《本草经解》："入手太阴肺经、足厥阴肝经。""
                },
                {
                    p: "功能主治",
                    o: "补肝肾，涩精气，固虚脱。治腰膝酸痛，眩晕，耳鸣，阳痿，遗精，小便频数，肝虚寒热，虚汗不止，心摇脉散。 补益肝肾，涩精固脱。用于眩晕耳鸣、腰膝酸痛、阳痿遗精、遗尿尿频、崩漏带下、大汗虚脱、内热消渴。温肝补肾，除一切风，止月经过多，治老人尿频。 ①《本经》："主心下邪气寒热，温中，逐寒湿痹，去三虫。" ②《雷公炮炙论》："壮元气，秘精。" ③《别录》："肠胃风邪，寒热疝瘕，头风，风气去来，鼻塞，目黄，耳聋，面疱，温中，下气，出汗，强阴，益精，安五脏，通九窍，止小便利，明目，强力。" ④《药性论》："治脑骨痛，止月水不定，补肾气；兴阳道，添精髓，疗耳鸣，除面上疮，主能发汗，止老人尿不节。" ⑤《日华子本草》："暖腰膝，助水脏，除一切风，逐一切气，破癥结，治酒皶。" ⑥《珍珠囊》："温肝。" ⑦《本草求原》："止久泻，心虚发热汗出。""
                },
                {
                    p: "摘录",
                    o: "《中药大辞典》"
                }
            ],
            createdTime: "2016-09-03T17:49:11:549Z",
            updatedTime: "2016-09-03T17:49:11:549Z",
            dataSource: "蒲标网",
            total: 18,
            source: {
                url: "http://www.zysj.com.cn/zhongyaocai/yaocai_s/shanzhuyu.html",
                domain: "www.zysj.com.cn",
                confidence: "0.8",
                trackingId: "8c619e40a735b67111b55c6245ba297aac0658b7"
            }
        }
    ],
    total: 1
}
````


### 知识图谱数据价格接口

查alias字段(因为此数据库接口alias为空，所以不能查到)：

/api/v1/price?q=alias:豆油%20AND%20alias:广东广州粮油批发交易市场&offset=0&limit=20

查tags字段：

/api/v1/price?q=tags:豆油%20AND%20tags:广东广州粮油批发交易市场&offset=0&limit=20

查series字段：

/api/v1/price?q=series:豆油_批发价_山东_广东广州粮油批发交易市场_一级&offset=0&limit=20


说明：

1. 查出来的东西，比如山药查出来多条价格数据，需要按updatedTime 排序。

2. 山药有若干种价格系列series，每种价格序列都可以按时间范围查询。


针对若干种价格序列的方案：

1. 元collection 每次插入数据都会去查下是否要插入，单线程插并把元collection数据放内存里，可以提高插入效率，查询就查这个collections.

2. 新加元字段，给这个字段建立索引，插入时可以直接插，查询时需要distinct，查出几种价格，然后按照单种价格查询。


单纯效率考虑，目前应用场景下元collections更好；从方便程度考虑，加元字段比较方便.

按时间范围查询就是查claims.p == validDate 的范围查，不好加字段，只能在updatedTime 同级加入 quotedTime

````
{
    "code": 0,
    "message": "成功",
    "result": [
        {
            id: "57c939affdcdad190ba67c94",
            series: "豆油_批发价_广东广州粮油批发交易市场__一级",
            tags: ["豆油", "广东广州粮油批发交易市场"],
            "claims": [
                {
                    "p": "productName",
                    "o": "豆油"
                },
                {
                    "p": "validDate",
                    "o": "2015-11-19"
                }
            ],
            "createdTime": "2016-09-05T06:31:57.111443",
            "updatedTime": "2016-09-05T06:31:57.111461",
            "deletedTime": "",
            "quotedTime": "2015-11-19T00:00:00.0000000",
            "dataSource": "药通网",
            "source": {
                "url": "http://www.yt1998.com/priceHistory.html?keywords=叶下珠&guige=统&chandi=广东&market=1",
                "domain": "www.yt1998.com",
                "confidence": "0.7",
                "trackingId": "9c7e717b19de083519c00c03ab257ab121737a0f"
            }
        },
        {
            id: "57c939affdcdad190ba67c94",
            "series": "叶下珠__广东_亳州市场_统",
            "tags": [ "叶下珠", "广东", "亳州市场", "统" ],
            "claims": [
                {
                    "p": "productName",
                    "o": "叶下珠"
                },
                {
                    "p": "validDate",
                    "o": "2015-11-19"
                },
                {
                    "p": "price",
                    "o": "7.00"
                },
                {
                    "p": "unitText",
                    "o": "元/千克"
                },
                {
                    "p": "sellerMarket",
                    "o": "亳州市场"
                },
                {
                    "p": "productPlaceOfOrigin",
                    "o": "广东"
                },
                {
                    "p": "productGrade",
                    "o": "统"
                },
                {
                    "p": "priceCurrency",
                    "o": "CNY"
                }
            ],
            "createdTime": "2016-09-05T06:31:57.111443",
            "updatedTime": "2016-09-05T06:31:57.111461",
            "deletedTime": "",
            "quotedTime": "2015-11-19T00:00:00.0000000",
            "dataSource": "药通网",
            "source": {
                "url": "http://www.yt1998.com/priceHistory.html?keywords=叶下珠&guige=统&chandi=广东&market=1",
                "domain": "www.yt1998.com",
                "confidence": "0.7",
                "trackingId": "9c7e717b19de083519c00c03ab257ab121737a0f"
            }
        }
    ],
    "total": 2
}
````

### 知识图谱数据企业接口

/api/v1/enterprises?q=杭州稳健钙业有限公司&offset=0&limit=20

````
{
      "id": "s2f5g6h7j8",
      "srank": 100031,
      "tags": ["公司","实体"],
      "alias": ["杭州稳健钙业有限公司","杭州稳健钙业"],
      "claims": [
            {"p": "实体名称", "o": "杭州稳健钙业有限公司"},
            {"p": "注册号", "o": "330100400039515"},
            {"p": "组织机构代码", "o": "76545909-1"},
            {"p": "经营状态", "o": "存续"},
            {"p": "公司类型", "o": "有限责任公司（中外合资）"},
            {"p": "成立日期", "o": "2004-09-02"},
            {"p": "法定代表", "o": "项建平"},
            {"p": "注册资本", "o": "100 万美元"},
            {"p": "营业期限", "o": "2019-09-01"},
            {"p": "登记机关", "o": "杭州市市场监督管理局"},
            {"p": "发照日期", "o": "2011-06-20"},
            {"p": "企业地址", "o": "建德市大同镇傅家村草坪山（工业功能区）"},
            {"p": "经营范围", "o": "生产：氢氧化钙、氧化钙；销售：本公司生产的产品"},
            {"p": "股东信息", "rid": "_123"},
            {"rid": "_123","p": "股东名称", "o": "澳洲Minatek Pty Ltd"},
            {"rid": "_123","p": "股东职务", "o": "企业法人"},
            {"p": "股东信息", "rid": "_222"},
            {"rid": "_222","p": "股东名称", "o": "建德市建业家纺厂"},
            {"rid": "_222","p": "股东职务", "o": "企业法人"},
            {"p": "变更记录", "rid": "_333"},
            {"rid": "_333","p": "变更项目", "o": "行业代码变更"},
            {"rid": "_333","p": "变更前", "o": "行业: 非金属矿物制品业; \r\n注册号: 企合浙杭总字第006246号;"},
            {"rid": "_333","p": "变更后", "o": "行业: 无机盐制造; \r\n注册号: ******;"},
            {"rid": "_333","p": "变更时间", "o": "2011-06-20"},
            {"p": "主要人员", "rid": "_444"},
            {"rid": "_444","p": "职位", "o": "董事长"},
            {"rid": "_444","p": "姓名", "o": "项建平"},
            {"p": "对外投资", "rid": "_555"},
            {"rid": "_555","p": "公司名称", "o": "建德市建业家纺厂"}
            {"rid": "_555","p": "source.url", "o": "http://www.qichacha.com/company_getinfos?unique=fa31d50f310a6598e36ba97ed7864257&companyname=%E5%BB%BA%E5%BE%B7%E5%B8%82%E5%BB%BA%E4%B8%9A%E5%AE%B6%E7%BA%BA%E5%8E%82&tab=touzi"}
        ],
        "createdTime": "2016-08-24T15:02:20.586Z",
        "updatedTime": "2016-08-24T15:02:20.586Z",
        "deletedTime": "",
        "source": { 
            "url":"http://www.qichacha.com/company_getinfos?unique=1831925bc3d536bacb1fedda6ffe92fb&companyname=%E6%9D%AD%E5%B7%9E%E7%A8%B3%E5%81%A5%E9%92%99%E4%B8%9A%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&tab=base",
            "domain": "www.qichach.com",
            "trackingId": "123890128sadfhsoaiao8",
            "confidence": "0.9" }
}
````

### 知识图谱数据新闻接口

