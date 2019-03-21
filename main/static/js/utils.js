var Utils={
    genUID:function(length){
        return Number(Math.random().toString().substr(3,length) + Date.now()).toString(36);
    },
    Trim:function(str){ 
        return str.replace(/(^\s*)|(\s*$)/g, ""); 
    },
    _attriDic:{
        "name":"名称"
    },//记录属性代号和真正名称的对应关系
    //根据feature的属性信息动态组织弹出的内容
    setAttributes:function(feature){
        var content="";
        if(feature.properties){
            for(var key in feature.properties){
                if(key!="style"&&this._attriDic[key]){
                    content=content+this._attriDic[key]+":"+feature.properties[key]+"</br>";
                }
            }
        }
        return content;
    }
}