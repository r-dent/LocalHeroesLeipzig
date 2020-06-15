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
        this.mainCategories = new Array();
        this.categories = new Object();
        this.subCategoryControl = undefined
        this.map = undefined
        this.isLocal = location.hostname == 'localhost' || location.hostname == '192.168.2.169'
        this.repositoryBaseUrl = 'https://cdn.jsdelivr.net/gh/r-dent/LocalHeroesLeipzig@master/'
        this.clusterZoom = options.clusterBelowZoom 
        this.markerLayer = undefined
        this.useClustering = (this.clusterZoom !== undefined && typeof(this.clusterZoom) == 'number')
        this.showLocateButton = (options.showLocateButton !== undefined)
        this.showCategorySelection = options.showCategorySelection
        this.onDataReady = options.onDataReady
        this.geoJson = undefined

        // Add loading layer DOM.
        var mapContainer = document.getElementById(mapElementId)
        mapContainer.classList.add('lh-mp-ctnr')
        mapContainer.innerHTML = '<div id="loading"><svg height="100" width="100" class="spinner"><circle cx="50" cy="50" r="20" class="inner-circle" /></svg></div>'
        
        const resourceVersionTag = '20200514'
        const dataUrl = (this.isLocal ? '../' : this.repositoryBaseUrl) +'data/local-heroes-leipzig.geojson?v='+ resourceVersionTag
        const cssUrl = (this.isLocal ? '' : this.repositoryBaseUrl +'docs/') +'map-style.css?v='+ resourceVersionTag

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

    createMap(mapElementId, {mapBoxKey, mapBoxStyle, isFullScreen}) {

        const windowHeight = window.innerHeight
        const mapHeight = document.getElementById(mapElementId).clientHeight

        const map = L.map(mapElementId, {
            zoomControl: false,
            scrollWheelZoom: isFullScreen || (mapHeight / windowHeight) < 0.85,
            dragging: isFullScreen || !L.Browser.mobile, 
            tap: isFullScreen || !L.Browser.mobile,
        }).setView([51.3396955, 12.3730747], 13);

        L.control.zoom({ position: 'bottomleft' }).addTo(map)

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
                L.control.locate({position: 'bottomleft', showCompass: false}).addTo(map);
            })
        }

        return map
    }

    onEachMapFeature(feature, layer) {
        const coord = feature.geometry.coordinates
        const address = '<a onclick="LocalHeroesHelper.navigate('+ coord[1] +','+ coord[0] +',\''+ feature.properties.address +'\')" class="directions-link" title="Route anzeigen">'+
            '<i class="fa fa-directions"></i></a>'+ 
            feature.properties.address.split(', ').join('<br>')
        // does this feature have a property named popupContent?
        if (feature.properties && feature.properties.name && feature.properties.description) {
            layer.bindPopup(
                '<h3>'+ feature.properties.name +'</h3><p>'+ feature.properties.description +'</p><p>'+ address +'</p>');
        } 
    }

    renderMapMarker(geoJsonPoint, coordinatate) {
        var icon = L.icon({
            iconUrl: (this.isLocal ? '../' : this.repositoryBaseUrl) +'data/imagecache/'+ geoJsonPoint.properties.image,
            iconSize: [38, 38],
            shadowUrl: (this.isLocal ? '' : this.repositoryBaseUrl +'docs/') +'shadow.svg',
            shadowSize: [50, 50],
            shadowAnchor: [25, 22]
        });
        return L.marker(coordinatate, {icon: icon})
            .bindTooltip(geoJsonPoint.properties.name, {offset: [0, 16]})
    }

    addLayerToMap(layer, map) {

        if (this.useClustering) {

            const addClusterLayer = (layer, map) => {
                var markers = L.markerClusterGroup({
                    disableClusteringAtZoom: this.clusterZoom
                });
                markers.addLayer(layer)
                this.markerLayer = markers
                map.addLayer(markers)
            }

            if (L.markerClusterGroup === undefined) {
                LocalHeroesHelper.loadScript('https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js', () => {
                    addClusterLayer(layer, map)
                })
            } else {
                addClusterLayer(layer, map)
            }
        } else {
            layer.addTo(map)
            this.markerLayer = layer
        }
    }

    applyFilter(category, subCategories) {

        const geoLayer = L.geoJSON(this.geoJson, {
            onEachFeature: this.onEachMapFeature,
            pointToLayer: (point, coord) => this.renderMapMarker(point, coord),
            filter: function(feature, layer) {
                const matchesCategory = (feature.properties.category == category || category == 'all')
                return matchesCategory
            }
        })
        
        this.addLayerToMap(geoLayer, this.map)
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
        const showAll = (selectedCategory == 'all')

        if (this.subCategoryControl !== undefined) {
            this.subCategoryControl.remove()
        } else {
            this.subCategoryControl = L.control({position: 'topright'});
        }

        if (!showAll) {
            this.subCategoryControl.onAdd = (map) => {
                var div = L.DomUtil.create('div', 'sub-categories')

                var checkboxCount = 0
                var checkboxes = ''
                for (const subCategoryKey in this.categories[selectedCategory]) {
                    const subCategory = this.categories[selectedCategory][subCategoryKey]
                    checkboxCount += 1
                    checkboxes += '<div>'
                    checkboxes += '<input type="checkbox" id="sub-category-'+ checkboxCount +'" name="sub-category-'+ checkboxCount +'" checked></input>'
                    checkboxes += '<label for="sub-category-'+ checkboxCount +'">'+ subCategory +'</label>'
                    checkboxes += '</div>'
                }
            
                div.innerHTML = checkboxes
                return div
            };
            this.subCategoryControl.addTo(this.map)
        }

        this.map.removeLayer(this.markerLayer)
        this.applyFilter(selectedCategory)
        this.map.fitBounds(L.featureGroup([this.markerLayer]).getBounds())
    }

    applyGeoData(data) {

        this.geoJson = JSON.parse(data);
        const features = this.geoJson['features'];

        // Collect categories.
        for (const feature in features) {

            const properties = features[feature]['properties']
            const category = properties['category']

            if (!this.categories.hasOwnProperty(category)) {
                this.categories[category] = new Array()
            }

            for (const subCategoryKey in properties['sub-categories']) {
                const subCategory = properties['sub-categories'][subCategoryKey]
                if (!this.categories[category].includes(subCategory)) {
                    this.categories[category].push(subCategory)
                }
            }
        }
        this.mainCategories = Object.keys(this.categories).sort()
        console.log(this.categories);
        
        if (this.showCategorySelection !== false) {
            // Create category selection control.
            var control = L.control({position: 'topright'});
            control.onAdd = (map) => {
                var div = L.DomUtil.create('div', 'command');

                var categorySelection = '<form><div class="select-wrapper fa fa-angle-down"><select id="category-selection" name="category">'
                categorySelection += '<option value="all">Alle</option>'
                for (const catId in this.mainCategories) {
                    var category = this.mainCategories[catId]
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
        }

        this.applyFilter('all');

        // Remove loading overlay.
        document.getElementById('loading').remove()

        // Call handler.
        if (this.onDataReady !== undefined && typeof(this.onDataReady) == 'function') {
            this.onDataReady(this.mainCategories)
        }
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

    static navigate(lat, lon, address) {
        // If it's an iPhone..
        if( (navigator.platform.indexOf("iPhone") != -1) 
            || (navigator.platform.indexOf("iPod") != -1)
            || (navigator.platform.indexOf("iPad") != -1))
             window.open('https://maps.apple.com/?daddr='+ address);
        else
             window.open('https://www.google.com/maps/dir/?api=1&destination='+ lat +','+ lon);
    }
}
