var DrawStyle = (function() {  
    // 构造函数
    function _(options) {
        if(options)
            Object.assign(this.options,options);
        // $("#panel_DrawStyle").draggable({containment: '#mapcontainer'}); 
        _bindEvt();
        this.setStyle();
    }  
    /**
     * 私有方法——绑定事件
     */
    function _bindEvt(){
        $("#styleEdit").unbind("click").bind("click",function(){
            $("#panel_DrawStyle").toggle();
        });
        //确定——应用并关闭窗口
        $('#btn_drawstyle_ok').unbind('click').bind('click', function () {
            _.prototype.resetStyle();
            $("#panel_DrawStyle").hide();
        });
        //取消
        $('#btn_drawstyle_cancel').unbind('click').bind('click', function () {
            $("#panel_DrawStyle").hide();
            _.prototype.setStyle();            
        });
        //选择标记
        $("#pStyleSelect").unbind("click").click(function (e) {
            e.stopPropagation();
            if ($("#pointStyles").css("display") == "none") {
                $("#pointStyles").fadeIn();
            }
            else {
                $("#pointStyles").fadeOut();
            }
            $("#pointStyles").children("li").each(function () {
                $(this).unbind("click").click(function (e) {
                    e.stopPropagation();
                    $("#pStyleSelect div").removeClass();
                    $("#pStyleSelect div").attr("class","");
                    $("#pStyleSelect div").addClass($(this).children("a").attr("class"));
                    $("#pointStyles").fadeOut();
                });
            });
        }); 
        //选择标记
        $("#rS_pt_marker").unbind("click").click(function (e) {
            e.stopPropagation();
            if ($("#rS_pt_markerItem").css("display") == "none") {
                $("#rS_pt_markerItem").fadeIn();
            }
            else {
                $("#rS_pt_markerItem").fadeOut();
            }
            $("#rS_pt_markerItem").children("li").each(function () {
                $(this).unbind("click").click(function (e) {
                    e.stopPropagation();
                    $("#rS_pt_marker div").removeClass();
                    $("#rS_pt_marker div").attr("class","");
                    $("#rS_pt_marker div").addClass($(this).children("a").attr("class"));
                    $("#rS_pt_markerItem").fadeOut();
                });
            });
        }); 
        $(document).click(function(){
            $("#pointStyles").fadeOut();
            $("#rS_pt_markerItem").fadeOut();
        });  
        //关闭单个图形样式修改
        $("#btn_cancel_rS").unbind("click").bind("click",function(){
            $("#resetStyle").css({ 
                animation: "cardOutRight 1s both"
            });
        });
    };
    /**
     * 动画显示图形的样式弹窗
     * @param {Point} pt 图形的屏幕坐标点
     */
    function _showStyleWindow(pt){
        // $("#resetStyle").css({ left: (pt.x + 10) + "px", top: (pt.y +10- $("#resetStyle").height() / 2) + "px" });
        // $("#resetStyle").find(".outerPointer").css({ left: -$("#resyle").find(".outerPointer").width() / 2 + "px", top: ($("#resetStyle").height() - $("#resetStyle").find(".outerPointer").height()) / 2 + "px" });
        // $("#resetStyle").find(".outerPointer").css({ "border-right": "none", "border-top": "none" });
        // $("#resetStyle").css({ animation: "cardInRight 1s both" });
    };
    /**
     * 获取点标注的图标属性
     * @param {string} iconClass 图标的样式
     * @param {number} iconSize 图标的大小
     */
    function _getIconStyle(iconClass,iconSize){
        var icon;
        switch (iconClass) {
            case "img_marker02":
                icon = {
                    iconUrl: '../static/img/draw/icon_tbs01_02.png',
                    iconSize: [iconSize, iconSize],
                    iconAnchor: [iconSize / 2, 5],
                };
                break;
            case "img_marker03":
                icon = {
                    iconUrl: '../static/img/draw/icon_tbs01_03.png',
                    iconSize: [iconSize, iconSize],
                    iconAnchor: [iconSize / 2, 5],
                };
                break;
            case "img_marker04":
                icon = {
                    iconUrl: '../static/img/draw/icon_tbs01_04.png',
                    iconSize: [iconSize, iconSize],
                    iconAnchor: [iconSize / 2, 5],
                };
                break;
            default:
                icon = {
                    iconUrl: '../static/img/draw/icon_tbs01_01.png',
                    iconSize: [iconSize, iconSize],
                    iconAnchor: [iconSize / 2, 5],
                };
                break;
        }
        return icon;
    };
    _.prototype.options = {
        style:{
            
            pt_iconClass:'img_marker01',
            pt_iconSize:'1.0',
            line_color:'#428bca',
            line_opacity:1,
            line_weight:4,
            line_dashArray:'',
            fill_color:'#428bca',
            fill_opacity:0.8
        }
    }; 
    /**
     * 将options中的样式应用到相应的dom上
     */
    _.prototype.setStyle = function(){
        // style = style || this.options.style;
        for (let item in this.options.style) {
            if (item.indexOf('color') == -1)
                $('#opt_' + item).val(this.options.style[item]);
            else
                $('#opt_' + item).colorpicker({ color: this.options.style[item] });
        }
        $('#pStyleSelect div').attr("class",this.options.style.pt_iconClass);
    };
    /**
     * 将Dom上设置的样式设置到options的style中
     */
    _.prototype.resetStyle = function(){
        for (let item in this.options.style) {
            this.options.style[item] = $('#opt_' + item).val();
        }
        this.options.style.pt_iconClass = $('#pStyleSelect div').attr("class");
    };    
    /**
     * 获取绘制样式
     * @param {string} key 绘制的类型 
     * @example DrawStyle.getDrawStyle("txt");
     */
    _.prototype.getDrawStyle = function(key){
        var style = {};
        switch (key) {
            case "txt":
                style = {
                    opacity: this.options.style.txt_opacity,
                    color: this.options.style.txt_color,
                    content: this.options.style.txt_content,//导出时注意中文乱码问题
                    size: this.options.style.txt_size,
                    fill: true,
                };
                break;
            case "point":
                var iconSize = parseFloat(this.options.style.pt_iconSize) * 20;
                style = {
                    icon: L.icon(_getIconStyle(this.options.style.pt_iconClass, iconSize)),
                    iconClass: this.options.style.pt_iconClass,
                    iconSize: iconSize
                }
                break;
            case "polygon":
                style.fillColor = this.options.style.fill_color;
                style.fillOpacity = this.options.style.fill_opacity;
            case "line":
                style.color = this.options.style.line_color;
                style.weight = this.options.style.line_weight;
                style.opacity = this.options.style.line_opacity;
                style.dashArray = this.options.style.line_dashArray;
                break;
        }
        return style;
    };    
    /**
     * 显示某个图形的样式
     * @param {Layer} layer 图层对象
     * @param {Point} pt 图层对应的屏幕坐标点
     */
    _.prototype.showGeoStyle = function(layer,pt){
        var obj = this;
        $("#resetStyle .tab_prop").hide();
        $("#rS_pt_markerItem").hide();
        var options = layer.options;
        if(!layer) return;
        if(layer instanceof L.Marker){  
            $("#rS_pt_size").val(parseFloat(options.icon.options.iconSize[0])/20); 
            //$("#rS_pt_markerItem").show(); 
            $("#rS_pt_marker div").attr("class",layer.options.iconClass);         
            $("#tab_rS_pt").show();            
            $("#btn_ok_rS").unbind("click").bind("click",function(){
                var iconSize = $("#rS_pt_size").val()?parseFloat($("#rS_pt_size").val()) * 20:30,
                iconClass = $("#rS_pt_marker div").attr("class");                
                layer.setIcon(L.icon(_getIconStyle(iconClass,iconSize)));   
                layer.options.iconClass = iconClass,
                layer.options.iconSize = iconSize;           
                $("#btn_cancel_rS").click();
            });
        }else if((layer instanceof L.Polyline&&!(layer instanceof L.Polygon))||layer instanceof L.Arc){            
            $("#rS_line_width").val(options.weight);
            $("#rS_line_opacity").val(options.opacity);
            $("#rS_line_color").colorpicker({ color: options.color });
            $("#rS_line_dash").val(options.dashArray);           
            $("#tab_rS_line").show(); 
            $("#btn_ok_rS").unbind("click").bind("click",function(){
                layer.setStyle({
                    weight:$("#rS_line_width").val(),
                    opacity:$("#rS_line_opacity").val(),
                    color:$("#rS_line_color").val(),
                    dashArray:$("#rS_line_dash").val()
                });
                $("#btn_cancel_rS").click();
            });
        }else if(layer instanceof L.Text){
            $("#rS_txt_info").val(options.content);
            $("#rS_txt_size").val(options.size);
            $("#rS_txt_color").colorpicker({ color: options.color });
            $("#rS_txt_opacity").val(options.opacity);
            $("#tab_rS_txt").show();            
            $("#btn_ok_rS").unbind("click").bind("click",function(){
                layer.setStyle({
                    opacity:$("#rS_txt_opacity").val(),
                    color:$("#rS_txt_color").val(),
                    content:$("#rS_txt_info").val(),
                    size:$("#rS_txt_size").val(),
                });
                $("#btn_cancel_rS").click(); 
            });
        }else{   
            $("#rS_pol_linewidth").val(options.weight);
            $("#rS_pol_lineopacity").val(options.opacity);
            $("#rS_pol_linecolor").colorpicker({ color: options.color });
            $("#rS_pol_linedash").val(options.dashArray);
            $("#rS_pol_color").colorpicker({ color: options.fillColor });    
            $("#rS_pol_opacity").val(options.fillOpacity);      
            $("#tab_rS_pol").show();            
            $("#btn_ok_rS").unbind("click").bind("click",function(){
                layer.setStyle({
                    weight:$("#rS_pol_linewidth").val(),
                    opacity:$("#rS_pol_lineopacity").val(),
                    color:$("#rS_pol_linecolor").val(),
                    dashArray:$("#rS_pol_linedash").val(),
                    fillColor:$("#rS_pol_color").val(),
                    fillOpacity:$("#rS_pol_opacity").val()
                });
                $("#btn_cancel_rS").click();                
            });
        }   
        $("#resetStyle").show();    
        _showStyleWindow(pt);    
    }   
    return _;
}) ();