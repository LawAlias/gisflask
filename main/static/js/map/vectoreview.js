var html2Escape=function (deh) {
    var reg = new RegExp( '&#34;' , "g" );
    return deh.replace( reg , "'" );
   }
var map=L.map('mapcontainer',{zoomControl:false}).setView([37,120],20);
var geoLayers=L.layerGroup();
geoLayers.addTo(map);
$.ajax({
    url:getGeos_url,
    type:'POST',
    data:{"role_id":role_id},
    success:function(response){
        response=JSON.parse(response)
        if(response.code==200){
            
            geoms=response.data
            var features=geoms;
            for(var index in features){
                var fea=features[index]
                fea=JSON.parse(JSON.stringify(fea))
                var style=fea['properties']['style'];
                style=style?style:{color:'blue'}
                if(fea['properties']['uid']==uid){
                    style={color:'red'}
                }
                var geoLayer=L.geoJson(fea['geometry'],style).bindPopup("名称:"+fea['properties']['name']+"</br>"+"创建时间:"+fea['properties']['create_time']);
                geoLayers.addLayer(geoLayer);
                if(fea['properties']['uid']==uid){
                    map.fitBounds(geoLayer.getBounds());
                }
            }
        }
    }
});

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

    var baseMaps = {
        '街道图': imgLayer,
        '卫星图': staLayer
    };
     var overLayers={
         "矢量数据":geoLayers
     }
    L.control.layers(baseMaps, overLayers,{collapsed:false}).addTo(map);