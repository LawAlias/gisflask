$(function(){
    $.contextMenu({
        selector: '.context-menu-compare', 
        callback: function(key, options) {
            switch(key){
                case "compare":
                  $("#selectCompare").toggle();
                break;
            }
        },
        items: {
            "compare": {name: "数据对比", icon: "edit"}
        }
    });

})
//提交影像选择结果
function selectCommited(){
    var htmlIndex=[];
    $("#selectCompare").hide();
    $("#masking").hide();
    
    if(selectImgCount!=2){
     alert("请选择两个影像进行比对");
    }
    else{
        
     $("#tbody>tr").each(function(index){
         if($(this).find("td:eq(0)>input:checkbox").is(":checked") == true){
             htmlIndex.push(index);
         }
     });
    
     var compareWindow=document.getElementById("imageCompareFrame");
     document.getElementById('imageCompareFrame').contentWindow.location.reload(true);
     compareWindow.src="../imageCompare/imageCompareRonghai.html#"+htmlIndex[0]+";"+htmlIndex[1];
     
     $("#imageCompareWindow").show();
    }
 };
var selectImgCount=1;