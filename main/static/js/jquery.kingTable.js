(function ($) {
    function KingTable(element,options){
        this.userOptions = options;
        this.defaultOptions = KingTable.defaults;
        this.options = $.extend(true,{},this.defaultOptions,this.userOptions);
        this.options.bodyForSearchBackup = this.options.body;
        this.element = element || $("#"+this.options.id);
        this.initTable(this.options.body);
    }
    KingTable.defaults={
        id:"kingTable",                              //表格id
        head:[],                                      //表头thead
        body:[],                                      //表格tbody数据
        foot:false,                                  //是否显示tfoot分页
        allDataNum:0,                                //分页-所有的tbody数据
        currentPageNum:1,                           //分页-当前页
        displayNum:10,                              //分页-每页显示的数据条数
        maxPageNum:1,                               //分页-最大页码数
        foreAndAft:false,                           //分页-是否显示首页、尾页
        pageNumTip:false,                           //分页-是否显示当前页/总页码
        groupDataNum:10,                            //分页-每组显示的数量
        groupNum:1,                                 //分页-当前组
        search:true,                               //搜索-是否开启搜索
        bodyForSearchBackup:[],                    //搜索-备份的tbody数据
        sort:true,                                 //排序-是否开启排序
        sortContent:[                               //排序-参数（表头索引从0开始）
            {
                index:0,
                compareCallBack:function(a,b){//排序比较的回调函数
                    var a=parseInt(a.id,10);
                    var b=parseInt(b.id,10);
                    if(a < b)
                        return -1;
                    else if(a == b)
                        return 0;
                    else
                        return 1;
                }
            }
        ],
        clickEventCallBack: $.noop,
        lang				  : {
            firstPageText			: '首页',
            firstPageTipText		: '首页',
            lastPageText			: '尾页',
            lastPageTipText		: '尾页',
            prePageText			: '上一页',
            prePageTipText			: '上一页',
            nextPageText			: '下一页',
            nextPageTipText		: '下一页',
            totalPageBeforeText	: '共',
            totalPageAfterText	: '页',
            totalRecordsAfterText	: '条数据',
            gopageBeforeText		: '转到',
            gopageButtonOkText	: '确定',
            gopageAfterText		: '页',
            buttonTipBeforeText	: '第',
            buttonTipAfterText	: '页',
            gopageButtonSearchText: '搜索'
        }
    };
    KingTable.prototype.validateOptions = function(data){
        this.options.body = data;
        this.options.allDataNum = this.getRowNum();
        this.options.maxPageNum = Math.ceil(this.options.allDataNum/this.options.displayNum);
    }
    KingTable.prototype.initTable = function(data){
        this.validateOptions(data);
        this.clearTable();
        this.renderThead();
        this.renderTbody();
        this.renderTfoot();
    }
    KingTable.prototype.clearTable = function(){
        this.element.empty();
    }
    KingTable.prototype.getColNum = function(){//得到列数
        var head = this.options.head,
            colNum = 0;
        if(head && !!head.length){
            colNum = head.length;
        }
        return colNum;
    }
    KingTable.prototype.getRowNum = function(){//得到总数据行数
        var body = this.options.body,
            rowNum = 0;
        if(body && !!body.length){
            rowNum = body.length;
        }
        return rowNum;
    }
    KingTable.prototype.renderThead = function(){
        var colNum = this.getColNum();
        if(!!colNum){
            var $thead = $("<thead>"),
                $tr = $("<tr>"),
                $th;
            for(var i=0;i<colNum;i++){
                $th = $("<th>").html(this.options.head[i]);
                $th.appendTo($tr);
            }
            $tr.appendTo($thead);
            $thead.appendTo(this.element);
            //添加排序功能
            if(!!this.options.sort){
                this.sortEvent();
                this.sortCss();
            }
        }
    }
    KingTable.prototype.renderTbody = function(){
        var rowNum = this.getRowNum();
        if(!!rowNum){

            if(!!this.element.find("tbody").length){this.element.find("tbody").remove();}

            var $tbody = $("<tbody>"),
                $tr,
                $td,
                begin = (this.options.currentPageNum-1) * this.options.displayNum,
                end = this.options.currentPageNum * this.options.displayNum,
                tempDaTa = this.paginationFromBeginToEnd(begin,end),
                len = tempDaTa.length,
                dataIndex = 0,
                trIndex;
            // 循环创建行
            for(var i=0;i<len;i++){
                if(tempDaTa[i]){
                    dataIndex = begin+i;
                    trIndex = i+1;
                    $tr = $("<tr data-tr_index="+trIndex+" data-data_index="+dataIndex+">").appendTo($tbody);
                    if(i%2==1){
                        $tr.addClass("evenrow");
                    }
                    // 循环创建列  取得对象中的键
                    for(var key in tempDaTa[i]){
                        $td = $("<td>").html(tempDaTa[i][key]).appendTo($tr);
                    }
                }
            }
            this.element.append($tbody);
            this.clickEventCallBack();
        }

    }
    KingTable.prototype.renderTfoot = function(){
        var colNum = this.getColNum();
        if(!!this.options.foot){

            if(!!this.element.find("tfoot").length){this.element.find("tfoot").remove();}

            var $tfoot = $("<tfoot>"),
                $tr = $("<tr>"),
                $td = $("<td>").attr("colspan",colNum).addClass("paging");
            $tr.append($td);
            $tfoot.append($tr);
            this.element.append($tfoot);
            this.pagination($td);
            this.paginationEvent($td);
            this.searchEvent();
        }
    }
    //表格分页初始化
    KingTable.prototype.pagination = function(tdCell){
        var $td= typeof(tdCell) == "object" ? tdCell : $("#" + tdCell);
        if(!!this.options.foreAndAft){
            //首页
            var oA = $("<a/>");
            oA.attr({
                href:"#1",
                title:this.options.lang.firstPageTipText
            });
            oA.html(this.options.lang.firstPageText);
            $td.append(oA);
        }
        //上一页
        if(this.options.currentPageNum >= 2){
            var oA = $("<a/>");
            oA.attr({
                href:"#"+(this.options.currentPageNum - 1),
                title:this.options.lang.prePageTipText
            });
            oA.html(this.options.lang.prePageText);
            $td.append(oA);
        }
        //普通显示格式
        if(this.options.maxPageNum <= this.options.groupDataNum){  // 10页以内 为一组
            for(var i = 1;i <= this.options.maxPageNum ;i++){
                var oA = $("<a/>");
                oA.attr({
                    href:"#"+(this.options.currentPageNum - 1),
                    title:this.options.lang.buttonTipBeforeText+i+this.options.lang.buttonTipAfterText
                });
                if(this.options.currentPageNum == i){
                    oA.attr("class","current");
                }
                oA.html(i);
                $td.append(oA);
            }
        }else{//超过10页以后（也就是第一组后）
            if(this.options.groupNum <= 1){//第一组显示
                for(var j = 1;j <= this.options.groupDataNum ;j++){
                    var oA = $("<a/>");
                    oA.attr({
                        href:"#"+j,
                        title:this.options.lang.buttonTipBeforeText+j+this.options.lang.buttonTipAfterText
                    });
                    if(this.options.currentPageNum == j){
                        oA.attr("class","current");
                    }
                    oA.html(j);
                    $td.append(oA);

                }
            }else{//第二组后面的显示
                var begin = (this.options.groupDataNum * (this.options.groupNum-1))+ 1,
                    end ,
                    maxGroupNum = Math.ceil(this.options.maxPageNum/this.options.groupDataNum);
                if(this.options.maxPageNum % this.options.groupDataNum !=0 && this.options.groupNum == maxGroupNum){
                    end = this.options.groupDataNum * (this.options.groupNum-1)+this.options.maxPageNum % this.options.groupDataNum
                }else{
                    end = this.options.groupDataNum * (this.options.groupNum);
                }

                for(var j = begin;j <= end ;j++){
                    var oA = $("<a/>");
                    oA.attr({
                        href:"#"+j,
                        title:this.options.lang.buttonTipBeforeText+j+this.options.lang.buttonTipAfterText
                    });
                    if(this.options.currentPageNum == j){
                        oA.attr("class","current");
                    }
                    oA.html(j);
                    $td.append(oA);
                }
            }
        }
        //下一页
        if( (this.options.maxPageNum - this.options.currentPageNum) >= 1 ){
            var oA = $("<a/>");
            oA.attr({
                href:"#" + (this.options.currentPageNum + 1),
                title:this.options.lang.nextPageTipText
            });
            oA.html(this.options.lang.nextPageText);
            $td.append(oA);
        }
        if(!!this.options.foreAndAft){
            //尾页
            var oA = $("<a/>");
            oA.attr({
                href:"#" + this.options.maxPageNum,
                title:this.options.lang.lastPageTipText
            });
            oA.html(this.options.lang.lastPageText);
            $td.append(oA);
        }
        if(!!this.options.pageNumTip){
            //提示
            var oSpan = $("<span/>");
            oSpan.html(this.options.currentPageNum+this.options.lang.gopageAfterText+"/"+this.options.maxPageNum+this.options.lang.gopageAfterText);
            $td.append(oSpan);
        }
        if(this.options.search){
            //搜索文本
            var oInput = $("<input type='text' class='search-txt'/>");
            $td.append(oInput);
            //搜索btn
            var oInputBtn = $("<input type='button' value='"+this.options.lang.gopageButtonSearchText+"' class='search-btn'/>");
            $td.append(oInputBtn);
        }
    }
    //表格分页绑定事件
    KingTable.prototype.paginationEvent = function(tdCell){
        var $td= typeof(tdCell) == "object" ? tdCell : $("#" + tdCell);
        var page_a = $td.find('a');
        var tempThis = this;
        page_a.unbind("click").bind("click",function(){
            var nowNum =  parseInt($(this).attr('href').substring(1));
            tempThis.goto(nowNum);
        });
    }
    // 实现分页行为
    KingTable.prototype.paginationFromBeginToEnd= function(x,y){
        var arrPage = [];
        for(var i= x;i<y;i++){
            arrPage.push(this.options.body[i]);
        }
        return arrPage;
    }
    //跳到某页
    KingTable.prototype.goto = function(toNum){
        var nowNum =  parseInt(toNum),
            tempThis = this;
        if(tempThis.options.currentPageNum == nowNum){
            return;
        }

        if(nowNum > tempThis.options.currentPageNum){//下一组
            if(tempThis.options.currentPageNum % tempThis.options.groupDataNum == 0){
                tempThis.options.groupNum += 1;

                var maxGroupNum = Math.ceil(tempThis.options.maxPageNum / tempThis.options.groupDataNum);
                if(tempThis.options.groupNum >= maxGroupNum){
                    tempThis.options.groupNum = maxGroupNum;
                }
            }
        }
        if(nowNum < tempThis.options.currentPageNum){//上一组
            if((tempThis.options.currentPageNum-1) % tempThis.options.groupDataNum == 0){
                tempThis.options.groupNum -= 1;
                if(tempThis.options.groupNum <= 1){
                    tempThis.options.groupNum = 1;
                }
            }
        }
        if(nowNum >= tempThis.options.maxPageNum){//直接点击尾页
            var maxGroupNum = Math.ceil(tempThis.options.maxPageNum / tempThis.options.groupDataNum);
            tempThis.options.groupNum = maxGroupNum;
            nowNum = tempThis.options.maxPageNum;
        }
        if(nowNum <= 1){
            tempThis.options.groupNum = 1;
            nowNum = 1;
        }

        tempThis.options.currentPageNum = nowNum;
        tempThis.renderTbody();
        tempThis.renderTfoot();
    }
    //排序功能  给需要排序的thead>th 绑定事件
    KingTable.prototype.sortEvent = function(){
        var tempThis = this,
            sortContent = this.options.sortContent,
            colNum = this.getColNum();
        if( $.isArray(sortContent) && sortContent.length>0){
            $.each(sortContent,function(i,o){
                if(o.index< colNum){
                    tempThis.element.find("thead th").eq(o.index)
                        .off("click")
                        .on("click",function(){
                            if( tempThis.options.ascORdesc === "asc"){
                                if($.isFunction(o.compareCallBack)){
                                    //之前是升序 点击后变为降序
                                    tempThis.sortCss();
                                    $(this).removeClass().addClass("desc");
                                    tempThis.options.ascORdesc = "desc";
                                    tempThis.options.body.reverse();
                                }
                            }else{
                                if($.isFunction(o.compareCallBack)){
                                    tempThis.sortCss();
                                    $(this).removeClass().addClass("asc");
                                    tempThis.options.ascORdesc = "asc";
                                    tempThis.options.body.sort(o.compareCallBack);
                                }
                            }
                            tempThis.renderTbody();
                        })
                }
            })
        }
    }
    //给需要排序的th添加样式
    KingTable.prototype.sortCss = function(){
        var tempThis = this,
            sortContent = this.options.sortContent,
            colNum = this.getColNum();
        if( $.isArray(sortContent) && sortContent.length>0){
            $.each(sortContent,function(i,o){
                if(o.index < colNum){
                    tempThis.element.find("thead th").eq(o.index)
                        .removeClass().addClass("bg");
                }
            })
        }
    }
    //给表格body的tr绑定事件
    KingTable.prototype.clickEventCallBack = function(){
        var _this = this;
        this.element.find("tbody").on("click",'tr',function(e){
            var tr_index = $(this).data("tr_index");       // tr行号  从0开始
            var data_index = $(this).data("data_index");   //数据行号  从0开始
            if(_this.options.clickEventCallBack &&  $.isFunction(_this.options.clickEventCallBack)){
                _this.options.clickEventCallBack(data_index,tr_index);

            }
        })
    }
    //前端搜索 给搜索按钮添加事件
    KingTable.prototype.searchEvent = function(){
        var _this = this;
        var  filter_data_by_search = function(allData,key_val){//通过搜索关键词筛选数据
            var keywords_val=key_val.toLowerCase();
            //筛选相应的数据
            var search_data=new Array();
            var all_data=allData;
            for(var row in all_data){
                var search_flag = false;
                for(var cell in all_data[row]){
                    if(all_data[row][cell] !== undefined){
                        var text =  all_data[row][cell].toString();
                        text = text.replace(/<br>/g,"");
                        text = text.replace(/<br\/>/g,"");
                        var index=text.toLowerCase().indexOf(keywords_val);
                        if(index != -1){
                            search_flag = true;
                        }
                    }
                }
                if(search_flag){
                    search_data.push(all_data[row])
                }
            }
            return search_data;
        }
        this.element.find(".search-btn").off("click").on("click",function(){
            var allData = _this.options.bodyForSearchBackup,
                key_val  = _this.element.find(".search-txt").val();
            var search_data = filter_data_by_search(allData,key_val);
            _this.options.currentPageNum = 1 ;
            _this.options.groupNum = 1 ;
            if(!!search_data.length){
                if(_this.options.searchEventCallBack && $.isFunction(_this.options.searchEventCallBack)){
                    _this.options.searchEventCallBack(search_data);
                }else{
                    _this.initTable(search_data);
                }
            }
        })
    }
    window.KingTable = KingTable;
    $.fn.KingTable = function(options) {
        return this.each(function() {
            if (!$(this).data('KingTable')) {
                $(this).data('KingTable', new KingTable($(this), options));
            }
        });
    };
})(jQuery);
