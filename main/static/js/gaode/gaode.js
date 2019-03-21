$("#getPoiBt").unbind('click').bind('click',function(){
    $.ajax({
        url:"http://restapi.amap.com/v3/place/text",
        data:{
            "key":$("#key").val(),
            "keywords":$("#keywords").val(),
            "city":$("#city").val(),
            "offset":$("#offset").val(),
            'children':'1',
            'page':'1',
            'extensions': 'all'
        },
        type:"POST",
        success:function(response){
            var pois = response['pois']
            var features=[]
            for(var i=0;i<pois.length;i++){
                var location=pois[i]['location'].split(',')
                var fea={
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                location[0]*1,
                                location[1]*1
                            ]
                        },
                        "properties": {
                            "name": pois[i]['name'],
                            "address":pois[i]['address'],
                            "tel":pois[i]['tel'],
                            "adname":pois[i]['adname']
                        }
                    }
                features.push(fea)
            }
            var featureCollection={
                "type":"FeatureCollection",
                "features":features
            }
            featureCollection=JSON.stringify(featureCollection)
            $("#poicontent").html(featureCollection)
        }
    })
})