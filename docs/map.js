// MIT License

// Copyright (c) 2020 Roman Gille

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

class LocalHeroesMap {

    constructor(mapElementId, options = {}) {
        this.categories = new Array();
        this.categoryLayers = [];
        this.map = undefined
        this.isLocal = location.hostname == 'localhost'
        this.repositoryBaseUrl = 'https://cdn.jsdelivr.net/gh/r-dent/LocalHeroesLeipzig@master/'
        this.clusterZoom = options.clusterBelowZoom 
        this.clusterLayer = undefined
        this.useClustering = (this.clusterZoom !== undefined && typeof(this.clusterZoom) == 'number')
        this.showLocateButton = (options.showLocateButton !== undefined)

        // Add loading layer DOM.
        var mapContainer = document.getElementById(mapElementId)
        mapContainer.classList.add('lh-mp-ctnr')
        mapContainer.innerHTML = '<div id="loading"><svg height="100" width="100" class="spinner"><circle cx="50" cy="50" r="20" class="inner-circle" /></svg></div>'

        const dataUrl = (this.isLocal ? '../' : this.repositoryBaseUrl) +'local-heroes-leipzig.geojson';
        const cssUrl = (this.isLocal ? '' : this.repositoryBaseUrl +'docs/') +'map-style.css'

        LocalHeroesHelper.loadCss(cssUrl)
        LocalHeroesHelper.loadCss('https://use.fontawesome.com/releases/v5.8.1/css/all.css')
        LocalHeroesHelper.loadCss('https://unpkg.com/leaflet@1.6.0/dist/leaflet.css')
        LocalHeroesHelper.loadScript('https://unpkg.com/leaflet@1.6.0/dist/leaflet.js', () => {
            this.map = this.createMap(mapElementId, options);
            LocalHeroesHelper.loadUrl(dataUrl, (data) => this.applyGeoData(data)); 
        })
        // Add cluster css when clustering is enabled.
        if (this.clusterZoom !== undefined && typeof(this.clusterZoom) == 'number') {
            LocalHeroesHelper.loadCss('https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css')
            LocalHeroesHelper.loadCss('https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css')
        }
        if (this.showLocateButton) {
            LocalHeroesHelper.loadCss('https://cdn.jsdelivr.net/npm/leaflet.locatecontrol@0.71.1/dist/L.Control.Locate.min.css')
        }
    }

    createMap(mapElementId, {mapBoxKey, mapBoxStyle}) {
        const map = L.map(mapElementId, {zoomControl: false}).setView([51.3396955, 12.3730747], 13);
        L.control.zoom({position: 'bottomleft'}).addTo(map)

        if (mapBoxKey !== undefined && typeof(mapBoxKey) == 'string' && mapBoxKey.length > 0) {
            // Use Mapbox if key is provided.
            const mapboxAttribution = 'Data by <a href="http://local-heroes-leipzig.de/" target="_blank">Local Heroes Leipzig</a> | ' +
            '<a href="https://github.com/r-dent/LocalHeroesLeipzig" target="_blank">Code</a> on GitHub' +
            '<br>Map data &copy; <a href="https://www.openstreetmap.org/" target="_blank">OpenStreetMap</a> contributors, ' +
            '<a href="https://creativecommons.org/licenses/by-sa/2.0/" target="_blank">CC-BY-SA</a>, ' + 
            'Imagery © <a href="https://www.mapbox.com/" target="_blank">Mapbox</a>'
            const retinaPart = (window.devicePixelRatio > 1) ? '@2x' : ''
            const useCustomStyle = (mapBoxStyle !== undefined && typeof(mapBoxStyle) == 'string' && mapBoxStyle.length > 0)
    
            L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}'+ retinaPart +'?access_token={accessToken}', {
                attribution: mapboxAttribution,
                maxZoom: 18,
                id: (useCustomStyle ? mapBoxStyle : 'mapbox/streets-v11'),
                tileSize: 512,
                zoomOffset: -1,
                accessToken: mapBoxKey,
            }).addTo(map);
        } else {
            // Use OpenStreetMap as fallback.
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png?{foo}', {
                foo: 'bar', 
                attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'
            }).addTo(map);
        }

        if (this.showLocateButton) {
            LocalHeroesHelper.loadScript('https://cdn.jsdelivr.net/npm/leaflet.locatecontrol@0.71.1/dist/L.Control.Locate.min.js', () => {
                L.control.locate({position: 'bottomleft'}).addTo(map);
            })
        }

        return map
    }

    onEachMapFeature(feature, layer) {
        // does this feature have a property named popupContent?
        if (feature.properties && feature.properties.name && feature.properties.description) {
            layer.bindPopup(
                '<h3>'+ feature.properties.name +'</h3><p>'+ feature.properties.description +'</p>');
        } 
    }

    renderMapMarker(geoJsonPoint, coordinatate) {
        var icon = L.icon({
            iconUrl: geoJsonPoint.properties.image,
            iconSize: [38, 38],
            shadowUrl: (this.isLocal ? '' : this.repositoryBaseUrl +'docs/') +'shadow.svg',
            shadowSize: [50, 50],
            shadowAnchor: [25, 22]
        });
        return L.marker(coordinatate, {icon: icon})
    }

    addLayersToMap(layers, map) {

        if (this.useClustering) {

            const addClusterLayer = (layers, map) => {
                var markers = L.markerClusterGroup({
                    disableClusteringAtZoom: 15
                });
                for (const id in layers) {
                    markers.addLayer(layers[id])
                }
                this.clusterLayer = markers
                map.addLayer(markers)
            }

            if (L.markerClusterGroup === undefined) {
                LocalHeroesHelper.loadScript('https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js', () => {
                    addClusterLayer(layers, map)
                })
            } else {
                addClusterLayer(layers, map)
            }
        } else {
            for (const id in layers) {
                layers[id].addTo(map)
            }
        }
    }

    createCategoryLayers(geoJson) {

        for (const catId in this.categories) {
            const category = this.categories[catId]
            const geoLayer = L.geoJSON(geoJson, {
                onEachFeature: this.onEachMapFeature,
                pointToLayer: (point, coord) => this.renderMapMarker(point, coord),
                filter: function(feature, layer) {
                    return feature.properties.category == category
                }
            })
            this.categoryLayers[category] = geoLayer
        }
        this.addLayersToMap(this.categoryLayers, this.map)
    }

    showLayer(id) {
        var group = this.categoryLayers[id];
        if (!this.map.hasLayer(group)) {
            group.addTo(this.map);   
        }
    }

    hideLayer(id) {
        var lg = this.categoryLayers[id];
        this.map.removeLayer(lg);   
    }

    selectCategory(selectedCategory) {
        console.log(selectedCategory)
        var shownLayers = new Array()

        for (const category in this.categoryLayers) {
            const layer = this.categoryLayers[category]
            this.map.removeLayer(layer)
            if (category == selectedCategory || selectedCategory == 'all') {
                shownLayers.push(layer)
            }
        }
        if (this.useClustering) {
            this.map.removeLayer(this.clusterLayer)
        }
        this.addLayersToMap(shownLayers, this.map)
        this.map.fitBounds(L.featureGroup(shownLayers).getBounds())
    }

    applyGeoData(data) {

        const geoJson = JSON.parse(data);
        const features = geoJson['features'];
        var distinctCategories = new Set()

        for (const feature in features) {
            if (features[feature]['properties'].hasOwnProperty('category')) {
                const category = features[feature]['properties']['category'];
                distinctCategories.add(category)
            }
        }
        this.categories = Array.from(distinctCategories).sort()
        console.log(this.categories);
        
        // Create category selection control.
        var control = L.control({position: 'topright'});
        control.onAdd = (map) => {
            var div = L.DomUtil.create('div', 'command');

            var categorySelection = '<form><div class="select-wrapper fa fa-angle-down"><select id="category-selection" name="category">'
            categorySelection += '<option value="all">Alle</option>'
            for (const catId in this.categories) {
                var category = this.categories[catId]
                categorySelection += '<option value="'+ category +'">'+ category +'</option>'
            }
            categorySelection += '</select></div></form>'

            div.innerHTML = categorySelection; 
            return div;
        };
        control.addTo(this.map);

        document
            .getElementById('category-selection')
            .addEventListener('change', (event) => this.selectCategory(event.target.value), false);

        this.createCategoryLayers(geoJson);
        document.getElementById('loading').remove()
    }
}

class LocalHeroesHelper {

    static loadScript(url, callback = () => {}) {
        var scriptNode = document.createElement("script"); 
        scriptNode.type = 'text/javascript';
        scriptNode.src = url;
        scriptNode.onreadystatechange = callback
        scriptNode.onload = callback
    
        document.head.appendChild(scriptNode);
    }

    static loadCss(url) {
        var cssNode = document.createElement("link"); 
        cssNode.rel = 'stylesheet';
        cssNode.href = url
    
        document.head.appendChild(cssNode);
    }

    static loadUrl(url, handler){
        const request = new XMLHttpRequest();
        request.open("GET", url);
        request.send();

        request.onreadystatechange = (e) => {
            if (request.readyState == 4 && request.status == 200) {
                handler(request.responseText)
            }
        }        
    }
}
