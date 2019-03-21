var EditTool={
    clickedLayer:null,
    _editlayer:null,
    saveGeo:function(json){

    },
  /**
   * 初始化
   * @memberof EditTool
   * @param layer 存储编辑图形的图层组
   * @return null
   * @example FlyData.getAircraftMk(layerGroup, "SC4578")
   */
    Initialization:function(layer){
        this._editlayer=layer
        var _this=this;
        $("#import").click(function(){
            $.ajax({
                type:"POST",
                url:saveGeo_url,
                data:{"geojson":_this.drawLyToGeoJson(_this._editlayer)},
                success:function(data){
                    _this._resetUnSaveStatus();
                }
            })
        });
        $("#attriForm1Apply").unbind( "click" );
        $("#attriForm1Apply").click(function(){
            var name=$("#name").val()
            var layerId=draw_toolbar.uid;
            var geojson=_this.getGeoJSON(_this._editlayer);
            // geojson=json.parse(geojson);
            geojson.properties.field={}
            geojson.properties.field.name=name;
            $.ajax({
                type:"POST",
                url:saveGeo_url,
                data:{"geojson":JSON.stringify(geojson),"layerId":layerId},
                success:function(data){
                    _this._resetUnSaveStatus();//将当前编辑图层的保存状态改为已保存
                    _this.resetCurrentEditLayer();//将当前编辑图层还原为绘制图层
                    toggleAttriForm("line");
                    // window.location.reload();
                }
            })
        });
    },
    /**
     * 将编辑图层中的所有要素保存状态都置为已保存
     */
    _resetUnSaveStatus:function(){
        if (this._editlayer instanceof L.FeatureGroup) {
        this._editlayer.eachLayer(function (layer) {
            if (layer instanceof L.FeatureGroup) {
                layer.eachLayer(function (layer) {
                    layer.unsave=false
                });
            } else {
                layer.unsave=false
            }
        });
    }
    else{
        this._editlayer.unsave=false
    }
    this._editlayer.disableEdit();
    },
    /**
     * 将绘制图层转为geojson
     * @param {featureGroup} featureGroup 绘制的图形所在的图层组
     */
    drawLyToGeoJson: function (featureGroup,isTransform) {
        var jsons = [];
        var _this = this;
        featureGroup.eachLayer(function (layer) {
            if (layer instanceof L.FeatureGroup) {
                layer.eachLayer(function (layer) {
                    if(layer.unsave){
                        jsons.push(_this.getGeoJSON(layer,isTransform));
                    }
                });
            } else {
                if(layer.unsave){
                jsons.push(_this.getGeoJSON(layer,isTransform));
                }
            }
        });

        if (jsons.length === 0)
            return "";
        else
            return JSON.stringify({
                type: 'FeatureCollection',
                features: jsons
            });
    },
    /**
     * geojson转为绘制图层
     * @param {object} data geojson对象
     * @param {FeatureGroup} featureGroup 图形的容器
     */
    geojsonToDrawLayer: function (data) {
        var _this = this;
        var layer = L.geoJSON(data, {
            onEachFeature:function(feature, layer){
                var content=Utils.setAttributes(feature);
                layer.bindPopup(content);
            },
            style: function (feature) {
                // var style="";//样式存储出了些问题，无法序列化读出来的样式字符串
                // //TODO：判断style的有效性
                // if(feature.properties.style!="None"){
                //     style=JSON.parse(feature.properties.style)
                //     delete style.field
                // }
                // else{
                //     style={
                //         "color":"blue"
                //     }
                // }
                // return style;
            },
            pointToLayer: function (geoJsonPoint, latlng) {
                if (!geoJsonPoint.properties) {
                    return L.marker(latlng);
                }  
                var options={};
                // var style=JSON.parse(geoJsonPoint.properties.style)
                // delete style.field
                // if (style.iconUrl) {
                //     style.iconSize = style.iconSize.split(",")
                //     options = {
                //         icon: L.icon(style)
                //     } 
                // } 
                return L.marker(latlng,options);
            },
            
        });
        return layer;
    },
    /**
     * 设置当前编辑图层
     * @param {layer} 要编辑的图层
     */
    resetCurrentEditLayer:function(layer){
        if(layer){
            this._editlayer=layer;
        }
        else{
            this._editlayer=draw_toolbar;//默认的编辑图层就是绘制图层组，每次用完之后就还原回来
        }
    },
     /**
     * 获取图层的JSON，包括类型和样式
     * @param {Layer} layer 需要转成geojson的图形对象
     * @param {bool} isTransform 是否进行坐标转换
     */
    getGeoJSON: function (layer,isTransform) {
        if (layer.toGeoJSON) {
            let json = layer.toGeoJSON();   
            let coors = json.geometry.coordinates;         
           if (layer._latlng) {
               if (isTransform) { 
                   json.geometry.coordinates = coordinateTools.gcj02towgs84(coors[0], coors[1]);
               }
               json.properties = {
                
                type: "Point",
                iconUrl: layer.options.icon.options.iconUrl,
                iconSize: layer.options.icon.options.iconSize[0]+","+layer.options.icon.options.iconSize[1]
                // style: layer.options.icon.options//layer.__proto__.options.icon.options
            };
                } else{               
                json.properties = {
                    uid:layer.uid,
                    type: json.geometry.type,
                    opacity: layer.options.opacity,
                    color: layer.options.color,
                    weight: layer.options.weight,
                    fillColor: layer.options.fillColor,
                    fillOpacity: layer.options.fillOpacity,
                    dashArray: layer.options.dashArray
                };
                if(isTransform){
                    if (layer instanceof L.Polygon) {   
                        for (let o = 0; o < coors[0].length; o++) {
                            let coord = coors[0][o]
                            json.geometry.coordinates[0][o] = coordinateTools.gcj02towgs84(coord[0], coord[1]);
                        }
                    }else{
                        for (let o = 0; o < coors.length; o++) {
                            let coord = coors[o]
                            json.geometry.coordinates[o] = coordinateTools.gcj02towgs84(coord[0], coord[1]);
                        }
                    }
                }  
            } 
            return json;
        } else {
            console.err("该layer没有toGeoJSON方法");
        }
    },

}
EditTool.Initialization(draw_toolbar)