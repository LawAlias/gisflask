
var isCustomDrawing=false;
var Draw = {
    styleEdit: null,//样式设置

    drawMeasureTip: null,    
    contextMenuItem: null,
    //右键菜单
    contextMenu: {
        edit: function (e) {
            e.relatedTarget.toggleEdit();
        },
        setStyle: function (e) {
            Draw.styleEdit.showGeoStyle(e.relatedTarget,e.containerPoint);
        },
        delete: function (e) {
            Draw.deleteGra(e.relatedTarget);
        }
    },
    /**
     * 初始化绘制工具
     */
    Initialization: function () {
        this.styleEdit = new DrawStyle();//绘制样式的初始化
        this.bindLyEvt();
        this.bindDomEvt();
      
        draw_toolbar.clearLayers();
    },
    /**
     * 绑定地图事件
     */
    bindLyEvt: function () {
        var _this = this;
        map.on('layeradd', function (e) {
            if (!_this.isInDrawLayer(e.layer)) return;
            if (e.layer instanceof L.Path || e.layer instanceof L.Marker )
            e.layer.on('dblclick', L.DomEvent.stop).on('dblclick', function () {
            
                    e.layer.toggleEdit();
                });
            e.layer.bindContextMenu({
                contextmenu: true,
                contextmenuItems: [{
                    text: '编辑/取消编辑',
                    index: 0,
                    callback: _this.contextMenu.edit
                }, {
                    text: '修改样式',
                    index: 1,
                    callback: _this.contextMenu.setStyle
                }, {
                    text: '删除',
                    index: 2,
                    callback: _this.contextMenu.delete
                }]
            });
        });
        
        map.editTools.on('editable:enable', function (e) {
            if (this.currentPolygon)
                this.currentPolygon.disableEdit();
            this.currentPolygon = e.layer;
            this.fire('editable:enabled');
            isCustomDrawing = true;
            //MapOp.removeMapClick();
            //MapOp.removeOverLayerEnvent();
        });
        map.on('layerremove', function (e) {
            if (e.layer instanceof L.Polygon)
                e.layer.off('dblclick', L.DomEvent.stop).off('dblclick', e.layer.toggleEdit);
        });

        map.editTools.on('editable:disable', function (e) {
            delete this.currentPolygon;
            isCustomDrawing = false;
            // $("#panel_drawtool a").removeClass("active");  
        });
    },
    /**
     * 绑定Dom事件
     */
    bindDomEvt: function () {
        var _this = this;        
        //关闭工具条
        $("#btn_close_drawtool").unbind("click").bind("click",function(){
            $("#panel_drawtool").fadeOut();
        });
        //绘制点
        $("#point").unbind("click").bind("click", function () {
            if(draw_toolbar&&draw_toolbar.uid){
                var pointOpt = _this.styleEdit.getDrawStyle("point");
                $(this).addClass("active");
                map.editTools.options.markerClass = L.Marker.extend({
                    options: pointOpt
                });
                map.editTools.startMarker();
                //stopDrawing的作用：判断是否进行连续绘制的
                map.editTools.options.stopDrawing = false;
            }
           else{
               alert("请选择编辑图层")
           }
       
           
        });
        //绘制线
        $("#line").unbind("click").bind("click", function () {
            if(draw_toolbar&&draw_toolbar.uid){
            var lineOpt = _this.styleEdit.getDrawStyle("line");
            $(this).addClass("active");
            map.editTools.options.polylineClass = L.Polyline.extend({
                options: lineOpt
            });
            map.editTools.startPolyline();
            map.editTools.options.stopDrawing = false;
        }
        else{
            alert("请选择编辑图层")
        }
        });
       
        //绘制矩形
        $("#rectangle").unbind("click").bind("click", function () {
           
            $(this).addClass("active");
            map.editTools.options.rectangleClass = L.Rectangle.extend({
               
            });
            map.editTools.startRectangle();
            map.editTools.options.stopDrawing = false;
        });
        
        //取消绘制
        $("#cancelDraw").unbind("click").bind("click", function () {
            map.editTools.options.stopDrawing = true;
            map.editTools.currentPolygon.editor.disable();
            delete map.editTools.currentPolygon;
        });

      
        //清空
        $("#clear").unbind("click").bind("click", function () {
            draw_toolbar.clearLayers();
           
            $("#clear").blur();
        });
       
     
    },   
    /**
     * 判断图层是否在绘制图层组中
     */
    isInDrawLayer: function (layer) {
        var isIn = false;
        draw_toolbar.eachLayer(function (ly) {
            if (ly instanceof L.FeatureGroup) {
                if (ly.hasLayer(layer))
                    isIn = true;
            } else {
                if (ly._leaflet_id == layer._leaflet_id)
                    isIn = true;
            }
        });
        return isIn;
    },
    /**
     * 删除几何图形
     * @param {Layer} ly  删除的图形所在的图层
     */
    deleteGra: function (ly) {
        if (draw_toolbar.hasLayer(ly))
            draw_toolbar.removeLayer(ly);
        else {
            draw_toolbar.eachLayer(function (layer) {
                if (layer.hasLayer(ly))
                    layer.removeLayer(ly);
            });
        }
    }
     
   
}
Draw.Initialization()




