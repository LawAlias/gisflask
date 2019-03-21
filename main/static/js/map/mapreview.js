var html2Escape=function (sHtml) {
    return sHtml.replace(/amp;/g,"")
   }
var map=L.map('mapcontainer',{zoomControl:false}).setView([bounds[1],bounds[0]],20);
var southWest = L.latLng(bounds[1],bounds[0])
var northEast = L.latLng(bounds[3],bounds[2])
bounds = L.latLngBounds(southWest, northEast)
map.setMaxBounds(bounds)
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
    serverUrl=html2Escape(serverUrl);
    var serverlayer=L.tileLayer(serverUrl,{maxZoom:25}).addTo(map);
    var baseMaps = {
        '街道图': imgLayer,
        '卫星图': staLayer
    };
    var overlayMaps = {
    '地图服务':serverlayer
    };
    L.control.layers(baseMaps, overlayMaps,{collapsed:false}).addTo(map);