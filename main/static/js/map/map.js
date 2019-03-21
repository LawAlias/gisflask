var draw_toolbar=L.layerGroup()//实际上的当前编辑图层
var map=L.map('mapcontainer',{zoomControl:false,
    contextmenu: true,
    contextmenuWidth: 140,
        contextmenuItems: ['-', {
            text: '前视图',
            callback: function(e) {
                map.zoomIn();
            }
        }, {
            text: '后视图',
            callback: function(e) {
                map.zoomOut();
            }
        }],
    editable: true,/*是否可以编辑图形 */
    editOptions: {
      lineGuideOptions: {
        color: 'red',
        weight: 1
      },

      featuresLayer:draw_toolbar
    }}).setView([36.090699,120.386564],10);
    draw_toolbar.addTo(map);
    map.on('mousemove', function(e){
        $('#currMouseLng').html((e.latlng.lng).toFixed(6));
        $('#currMouseLat').html((e.latlng.lat).toFixed(6));
    })
    map.on('zoomend',function(e){
        $('#currZoom').html(map.getZoom());
    })
    L.control.zoom({zoomInTitle: '放大', zoomOutTitle: '缩小', position: 'bottomright'}).addTo(map);
    L.control.scale({imperial: false}).addTo(map);
    var satellite = L.tileLayer.chinaProvider('GaoDe.Satellite.Map', {
        maxZoom: 18,
        minZoom: 4
    });
    var annotion = L.tileLayer.chinaProvider('GaoDe.Satellite.Annotion', {
        maxZoom: 18,
        minZoom: 4
    });
    var staLayer = L.layerGroup([satellite, annotion]);
    var image = L.tileLayer.chinaProvider('GaoDe.Normal.Map', {
        maxZoom: 18,
        minZoom: 4
    });
    var imgLayer = L.layerGroup([image]).addTo(map);
    var layers=L.layerGroup();//记录所有的图层
    layers.addTo(map);
    var baseMaps = {
        '街道图': imgLayer,
        '卫星图': staLayer
    };
   
    

//其他
/**
 * 隐现属性框
 * @param {objtype} 属性框要素类型 line/point/polygon
 */
var toggleAttriForm=function(objtype){
    $("#attriFormContainer").toggle()
    $("#attriForm1").hide()

    switch(objtype){
   
        case 'line':
        $("#attriForm1").toggle()
        break;
    
    }
}
/**
 * 显示属性框
 * @param {objtype} 属性框要素类型 line/point/polygon
 */
var showAttriForm=function(objtype){
    $("#attriFormContainer").show()
    switch(objtype){
        case 'line':
        $("#attriForm1").show()
        break;
    
    }
}
var queryAllLayers=function(){
    $.ajax({
        url:getLayers_url,
        type:"POST",
        data:{
        },
        success:function(response){
            response=JSON.parse(response)
            if(response.code==200){
                var layers=response.data;
                feaCollectionsHandle(layers);
            }
        }
    });
};
queryAllLayers();

var layerDict={};
var feaCollectionsHandle=function(feaCollections){
    for(var i=0;i<feaCollections.length;i++){
        var layer=L.layerGroup();//记录单个的图层
        feaCollection=feaCollections[i];
        features=feaCollection.features;
        for(var j=0;j<features.length;j++){
            var fea=features[j];
            var feaLayer=EditTool.geojsonToDrawLayer(fea);
            layer.addLayer(feaLayer);
        }
        layer.uid=feaCollection.properties.uid;
        layerDict[feaCollection.properties.name]=layer;//组合叠加图层控件
        layers.addLayer(layer);
    }

    L.control.layers(baseMaps, layerDict,{collapsed:false}).addTo(map);
    $(function(){
        $(".leaflet-control-layers-overlays:eq(0) label div span").addClass("context-menu-one");//给图层控制增加右键功能
        $('.context-menu-one').on('contextmenu', function(e){
            var name=this.innerHTML;
            name=Utils.Trim(name);
            EditTool.clickedLayer=layerDict[name];//记录下被右键点击的图层对象
        })
    });
   
}
$(function(){//一些事件的添加
    $("#attriclose").click(function(){//要素属性框隐现
        $("#attriFormContainer").hide()
        $("#attriForm1").hide()
    })
    $("#layerSubmit").unbind("click").click(function(){//新添图层
        var layerName=$("#layerName").val();
        var uid=Utils.genUID();
        $.ajax({
            url:layer_url,
            data:{
                uid:uid,
                name:layerName
            },
            type:"POST",
            success:function(response){
                alert("成功")
                var layerDom="<li class='nav-item second-item vec-child'>"+
                    "<a href='/vectoreview?uid="+uid+"&role_id="+role_id+"' class='nav-link'>"+
                        "<i class='icon icon-speedometer'></i> "+layerName+
                    "</a>"+
                "</li>";
                $(".vec-child:eq(0)").before(layerDom);
                // $(".vec-child").before(la    yerDom);
                window.location.reload();
            }
        }
        )
    });
    // 图层右键事件
    $.contextMenu({
        selector: '.context-menu-one', 
        callback: function(key, options) {
            switch(key){
                case "edit":
                    if(EditTool.clickedLayer){
                        draw_toolbar=EditTool.clickedLayer;
                    }
                break;
                case "cancelEdit":
                    EditTool.clickedLayer=null;
                    draw_toolbar=L.layerGroup();
                break;
                case "add":
                $("#layermodal").toggle();
                $("#layerClose").unbind('click').bind('click',function(){
                    $("#layermodal").hide();
                })
                break;
                case "delete":
                alert("delete");
                break;
                case "centerat":
                alert("centerat");
                break;
            }
                

        },
        items: {
            "edit": {name: "编辑", icon: "edit"},
            "cancelEdit": {name: "取消编辑", icon: function(){
                return 'context-menu-icon context-menu-icon-quit';
            }},
           "add": {name: "新添图层", icon: "copy"},
            "delete": {name: "删除图层", icon: "delete"},
            "centerat": {name: "定位", icon: "delete"}
        
        }
    });
    
   
    
})