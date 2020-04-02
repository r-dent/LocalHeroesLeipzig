var mymap = L.map('mapid').setView([51.3396955, 12.3730747], 13);
var categories = new Array();
var categoryLayers = [];

function loadUrl(url, handler){
    const request = new XMLHttpRequest();
    request.open("GET", url);
    request.send();

    request.onreadystatechange = (e) => {
        if (request.readyState == 4 && request.status == 200) {
            handler(request.responseText)
        }
    }        
}

function onEachMapFeature(feature, layer) {
    // does this feature have a property named popupContent?
    if (feature.properties && feature.properties.name && feature.properties.description) {
        layer.bindPopup('<p>'+ feature.properties.name +'</p><p>'+ feature.properties.description +'</p>');
    } 
}

function renderMapMarker(geoJsonPoint, coordinatate) {
    var icon = L.icon({
        iconUrl: geoJsonPoint.properties.image,
        iconSize: [38, 38],
        shadowUrl: 'shadow.svg',
        shadowSize: [50, 50],
        shadowAnchor: [25, 22]
    });
    return L.marker(coordinatate, {icon: icon})
}

function createCategoryLayers(geoJson) {

    for (const catId in categories) {
        const category = categories[catId]
        const geoLayer = L.geoJSON(geoJson, {
            onEachFeature: onEachMapFeature,
            pointToLayer: renderMapMarker,
            filter: function(feature, layer) {
                return feature.properties.category == category
            }
        })
        categoryLayers[category] = geoLayer
        geoLayer.addTo(mymap)
    }
}

function showLayer(id) {
    var group = categoryLayers[id];
    if (!mymap.hasLayer(group)) {
        group.addTo(mymap);   
    }
}

function hideLayer(id) {
    var lg = categoryLayers[id];
    mymap.removeLayer(lg);   
}

function selectCategory(selectedCategory) {
    console.log(selectedCategory)
    var shownLayers = new Array()

    for (const category in categoryLayers) {
        if (category == selectedCategory || selectedCategory == 'all') {
            showLayer(category)
            shownLayers.push(categoryLayers[category])
        } else {
            hideLayer(category)
        }
    }
    mymap.fitBounds(L.featureGroup(shownLayers).getBounds())
}

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png?{foo}', {
    foo: 'bar', 
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'
    }
).addTo(mymap);

loadUrl('https://raw.githubusercontent.com/r-dent/LocalHeroesLeipzig/master/local-heroes-leipzig.geojson', function(data){
    const geoJson = JSON.parse(data);
    const features = geoJson['features'];
    var distinctCategories = new Set()

    for (const feature in features) {
        if (features[feature]['properties'].hasOwnProperty('category')) {
            const category = features[feature]['properties']['category'];
            distinctCategories.add(category)
        }
    }
    categories = Array.from(distinctCategories).sort()
    console.log(categories);
    
    // Create category selection control.
    var control = L.control({position: 'topright'});
    control.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'command');

        var categorySelection = '<form><select id="category-selection" name="category">'
        categorySelection += '<option value="all">Alle</option>'
        for (const catId in categories) {
            var category = categories[catId]
            categorySelection += '<option value="'+ category +'">'+ category +'</option>'
        }
        categorySelection += '</select></form>'

        div.innerHTML = categorySelection; 
        return div;
    };
    control.addTo(mymap);

    document
        .getElementById('category-selection')
        .addEventListener('change', function() {
            selectCategory(this.value);
        }, false);

    createCategoryLayers(geoJson);
}); 