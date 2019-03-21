!(function() {
    L.Path.TouchHelper = L[L.Layer ? 'Layer' : 'Class'].extend({
        options: {
            extraWeight: 25
        },

        initialize: function(path, options) {
            L.setOptions(this, options);
            this._sourceLayer = path;
            var touchPathOptions = L.extend({}, path.options, { opacity: 0, fillOpacity: 0 });
            touchPathOptions.weight += this.options.extraWeight;

            if (path.eachLayer) {
                this._layer = L.layerGroup();
                path.eachLayer(function(l) {
                    if (l.eachLayer || l.getLatLngs) {
                        this._layer.addLayer(L.path.touchHelper(l, L.extend({}, options, {parentLayer: this._layer})));
                    }
                }, this);
            } else if (path.getLatLngs) {
                this._layer = new path.constructor(path.getLatLngs(), touchPathOptions);
            } else {
                throw new Error('Unknown layer type, neither a group or a path');
            }
            //Added by wangshilian 2018/07/06 使父层的右键可以与此层关联
            this._layer.options.contextmenu = false;
            this._layer.options.contextmenuItems = [];
            console.log(this._layer);
            this._layer.on('click dblclick mouseover mouseout mousemove contextmenu', function(e) {
                console.log(e.type);
                (this.options.parentLayer ? this.options.parentLayer : path).fire(e.type, e);
            }, this);
        },

        onAdd: function(map) {
            this._map = map;
            this._layer.addTo(map);
            if (!this.options.parentLayer) {
                map.on('layerremove', this._onLayerRemoved, this);
            }
        },

        onRemove: function(map) {
            map.removeLayer(this._layer);
            map.off('layerremove', this._onLayerRemoved, this);
            this._map = null;
        },

        addTo: function(map) {
            map.addLayer(this);
        },

        _onLayerRemoved: function(e) {
            if (e.layer === this._sourceLayer) {
                this._map.removeLayer(this);
            }
        },
    });

    L.path = L.path || {};

    L.path.touchHelper = function(path, options) {
        return new L.Path.TouchHelper(path, options);
    }
})();
