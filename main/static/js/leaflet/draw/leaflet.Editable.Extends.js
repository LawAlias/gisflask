
var EditableMixin = L.Editable.EditableMixin;
var keepEditable = L.Editable.keepEditable;
//解决freehandpolygon绘制时没有pxBounds的问题
L.Polygon.include({
    _containsPoint: function (p) {
        var inside = false,
            part, p1, p2, i, j, k, len, len2;

        if (!this._pxBounds || !this._pxBounds.contains(p)) { return false; }/*add by wangshilian 2018/05/10 解决_pxBounds没有赋值导致出错的问题 */

        // ray casting algorithm for detecting if point is in polygon
        for (i = 0, len = this._parts.length; i < len; i++) {
            part = this._parts[i];

            for (j = 0, len2 = part.length, k = len2 - 1; j < len2; k = j++) {
                p1 = part[j];
                p2 = part[k];

                if (((p1.y > p.y) !== (p2.y > p.y)) && (p.x < (p2.x - p1.x) * (p.y - p1.y) / (p2.y - p1.y) + p1.x)) {
                    inside = !inside;
                }
            }
        }

        // also check if it's on polygon stroke
        return inside || L.Polyline.prototype._containsPoint.call(this, p, true);
    }
});
//解决polyline线太细的情况下，不容易选中的问题
L.Polyline.include({
    //这个方法不行，两个点的线会选中不了
    // _updatePath: function () {
    //     this._renderer._updatePoly(this);
    //     if(this._path)//使svg渲染下的线更容易被选中
    //         this._path.style.pointerEvents='fill';
    // },
    _clickTolerance: function () {
        // used when doing hit detection for Canvas layers
        var weight = this.weight>6?this.weight:6;
        return (this.options.stroke ? weight / 2 : 0) + this._renderer.options.tolerance;
    }
});
L.Editable= L.Editable||{};

L.Editable.include({
    options:{
       
        drawingCSSClass: 'leaflet-editable-drawing',
        series:false,
        stopDrawing:false
    },

});
L.Editable.VertexMarker.include({    
    onDrag: function (e) {
        e.vertex = this;
        this.editor.onVertexMarkerDrag(e);
        var iconPos = L.DomUtil.getPosition(this._icon),
            latlng = this._map.layerPointToLatLng(iconPos);
        this.latlng.update(latlng);
        this._latlng = this.latlng;  // Push back to Leaflet our reference.
        this.editor.refresh();
        if (this.middleMarker) this.middleMarker.updateLatLng();
        var next = this.getNext();
        if (next && next.middleMarker) next.middleMarker.updateLatLng();
    },
    
});
L.Editable.BaseEditor.include({
    onDrawingClick: function (e) {
        if (!this.drawing()) return;
        L.Editable.makeCancellable(e);
        // 🍂namespace Editable
        // 🍂section Drawing events
        // 🍂event editable:drawing:click: CancelableEvent
        // Fired when user `click` while drawing, before any internal action is being processed.
        this.fireAndForward('editable:drawing:click', e);
        if (e._cancelled) return;
        if (!this.isConnected()) this.connect(e);
        this.processDrawingClick(e);
   
     
    },
    endDrawing: function () {
        this._drawing = false;
        this.tools.unregisterForDrawing(this);
        this.onEndDrawing();
        this.feature.disableEdit();//added by wangshilian 2018/05/11使绘制完成退出编辑状态;
    },
    onEndDrawing: function () {
        // 🍂namespace Editable
        // 🍂section Drawing events
        // 🍂event editable:drawing:end: Event
        // Fired when a feature is not drawn anymore.
        this.fireAndForward('editable:drawing:end');
    },
    onDrawingMouseMove: function (e) {
        this.onMove(e);
        
        if(this.feature instanceof L.Polygon){
            var latLngs=this.feature.getLatLngs()[0];
            var newLatLngs = [];
            for ( var attr in latLngs) {
                newLatLngs[attr] = latLngs[attr];
            }
            newLatLngs.push(e.latlng);
        }
        else if(this.feature instanceof L.Polyline){
            this._currentLatLng=e.latlng;
 
        } 
    },
    _updateRunningMeasure: function (latlng, added) {//金铭添加
        var markersLength = this._lineLatLngs.length,
            previousMarkerIndex, distance;

        if (this._lineLatLngs.length === 1) {
            this._measurementRunningTotal = 0;
        } else {
            previousMarkerIndex = markersLength - (added ? 2 : 1);
            distance = latlng.distanceTo(this._lineLatLngs[previousMarkerIndex]);

            this._measurementRunningTotal += distance * (added ? 1 : -1);//_measurementRunningTotal记录的是现有的线段长度，不包括mousemove正在绘制的那个
        }
    },
    _getMeasurementLine:function(latlngs){//金铭添加
        var currentLatLng = this._currentLatLng,//记录mousemove时获得的经纬度
        previousLatLng = this._lineLatLngs[this._lineLatLngs.length - 1],//_lineLatLngs记录组成该线的所有点经纬度，不包括mousemove时的还没点下去的那个点
        distance;
        // calculate the distance from the last fixed point to the mouse position
        distance = this._measurementRunningTotal + currentLatLng.distanceTo(previousLatLng);//_measurementRunningTotal记录之前的长度
        return L.GeometryUtil.readableDistance(distance, true);
    },
    _getMeasurementString: function () {
        var area = this._area;

        if (!area) {
            return null;
        }

        return L.GeometryUtil.readableArea(area, true);
    },
});
L.Editable.MarkerEditor.include({

    /*编辑触发 start*/
    onEnable: function () {
        this.fireAndForward('editable:enable');
        if(this.feature&&this.feature._icon)
        this.feature._icon.style.border = "2px solid #0ff";
        
    },

    onDisable: function () {
        this.fireAndForward('editable:disable');
        if(this.feature&&this.feature._icon)
        this.feature._icon.style.border = "";
    },
    endDrawing: function () {
        // if(L.path.touchHelper)
        //     L.path.touchHelper(this.feature, {extraWeight: 5}).addTo(this.map);
        L.Editable.PathEditor.prototype.endDrawing.call(this);
        showAttriForm('line')
    }
   
});
L.Editable.PathEditor.include({
    onVertexRawMarkerClick: function (e) {
        // 🍂namespace Editable
        // 🍂section Vertex events
        // 🍂event editable:vertex:rawclick: CancelableVertexEvent
        // Fired when a `click` is issued on a vertex without any special key and without being in drawing mode.
        this.fireAndForward('editable:vertex:rawclick', e);
        if (e._cancelled) return;
        if (!this.vertexCanBeDeleted(e.vertex)) return;
        e.vertex.delete();
    },
   
    addLatLng: function (latlng) {
        if (this._drawing === L.Editable.FORWARD) this._drawnLatLngs.push(latlng);
        else this._drawnLatLngs.unshift(latlng);
        this.feature._bounds.extend(latlng);
        
        var vertex = this.addVertexMarker(latlng, this._drawnLatLngs);
        this.onNewVertex(vertex);
        this.refresh();
    },
});
L.Editable.PolylineEditor.include({
    endDrawing: function () {
        // if(L.path.touchHelper)
        //     L.path.touchHelper(this.feature, {extraWeight: 5}).addTo(this.map);
        L.Editable.PathEditor.prototype.endDrawing.call(this);
        this.feature.unsave=true;//保存状态为未保存
        this.feature.uid=Utils.genUID();//生成唯一值
        showAttriForm('line');
        EditTool.resetCurrentEditLayer(this.feature);
    },
    onDisable:function(){
        L.Editable.PathEditor.prototype.onDisable.call(this);
        this.feature.unsave=true;
    },
    onEnable:function(){
        L.Editable.PathEditor.prototype.onEnable.call(this);
        showAttriForm('line');
    },
    onEditing:function(){
        L.Editable.PathEditor.prototype.onEditing.call(this);
        EditTool.resetCurrentEditLayer(this.feature);//开始编辑之后
        this.feature.unsave=true;
    }
});
L.Editable.CircleEditor.include({
    onDrawingMouseDown: function (e) {
        L.Editable.PathEditor.prototype.onDrawingMouseDown.call(this, e);
        this._resizeLatLng.update(e.latlng);
        this.feature._latlng.update(e.latlng);
        this.connect();
        // Stop dragging map.
        e.originalEvent._simulated = false;
        this.map.dragging._draggable._onUp(e.originalEvent);
        // Now transfer ongoing drag action to the radius handler.
        this._resizeLatLng.__vertex.dragging._draggable._onDown(e.originalEvent);
        this._circleDrawing=true;//金铭添加，记录当前圆是否开始绘制
    },
    onDrawingMouseUp: function (e) {
        this.commitDrawing(e);
        e.originalEvent._simulated = false;
        L.Editable.PathEditor.prototype.onDrawingMouseUp.call(this, e);
        this._circleDrawing=false;//金铭添加，记录当前圆是否开始绘制
    },
    onDrawingMouseMove: function (e) {
        e.originalEvent._simulated = false;
        L.Editable.PathEditor.prototype.onDrawingMouseMove.call(this, e);
      
    },
});
Object.assign(L.Editable.EditableMixin,{

    createEditor: function (map) {
        map = map || this._map;
        var tools = (this.options.editOptions || {}).editTools || map.editTools;
        if (!tools) throw Error('Unable to detect Editable instance.');
        var Klass = this.options.editorClass || this.getEditorClass(tools);
        
        return new Klass(map, this, this.options.editOptions);
    },

    // 🍂method enableEdit(map?: L.Map): this.editor
    // Enable editing, by creating an editor if not existing, and then calling `enable` on it.
    enableEdit: function (map) {
        if (!this.editor) this.createEditor(map);
        this.editor.enable();
        this.editor.map._container.style.cursor="pointer";
        if(this.editor&&this.editor.map){
            this.editor.map.doubleClickZoom.disable();/* Add by Wangshilian 2018.04.26 strat*/
         
        }
        else if(this._map){
            this._map.doubleClickZoom.disable();
        }
        return this.editor;
    },
    disableEdit: function () {
        if (this.editor) {
            this.editor.map.doubleClickZoom.enable();/* Add by Wangshilian 2018.04.26 strat*/
            this.editor.disable();   
            this.editor.map._container.style.cursor="-webkit-grab";
            //连续绘制图形   
            if(this.editor&&this.editor.tools.options.series&&!this.editor.tools.options.stopDrawing){
                if(this.editor.feature instanceof L.Marker){
                    this.editor.tools.startMarker();
                }else if(this.editor.feature instanceof L.Rectangle){
                    this.editor.tools.startRectangle();
                }else if(this.editor.feature instanceof L.Polygon){
                    this.editor.tools.startPolygon();
                }else if(this.editor.feature instanceof L.Polyline){
                    this.editor.tools.startPolyline();
                }else if(this.editor.feature instanceof L.SemiCircle){
                    this.editor.tools.startSector();
                }else if(this.editor.feature instanceof L.Arc){
                    this.editor.tools.startArc();
                }else if(this.editor.feature instanceof L.Circle){
                    this.editor.tools.startCircle();
                }else if(this.editor.feature instanceof L.Text){
                    this.editor.tools.startText();
                }
            }
            delete this.editor;
            
        }
    }
})
//拐点大小
L.Editable.TouchVertexIcon = L.Editable.VertexIcon.extend({
    options: {
        iconSize: new L.Point(10, 10)
    }
});
//拐点样式
L.Editable.VertexMarker2 = L.Editable.VertexMarker.extend({
    options: {
        draggable: true,//是否可以拖拽编辑
        className: 'leaflet-div-icon-custom leaflet-vertex-icon'
    }
    /*onClick: function (e) {
        e.vertex = this;
        console.log('VertexMarker.Click:');
        console.log(e);
        this.editor.onVertexMarkerClick(e);
    },*/
});
//两拐点的中点样式
L.Editable.MiddleMarker2 = L.Editable.MiddleMarker.extend({
    options: {
        opacity: 0.5,
        className: 'leaflet-div-icon-custom leaflet-middle-icon',
        draggable: true
    }
});
L.Editable.mergeOptions({
    vertexMarkerClass: L.Editable.VertexMarker2,
    middleMarkerClass: L.Editable.MiddleMarker2
});
var semiCircleMixin = {
    getEditorClass: function (tools) {
        return (tools && tools.options.circleEditorClass) ? tools.options.circleEditorClass : L.Editable.SectorEditor;
    }

};

if (L.semiCircle) {
    L.SemiCircle.include(EditableMixin);
    L.SemiCircle.include(semiCircleMixin);
}
