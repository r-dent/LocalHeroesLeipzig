## Local Heroes Leipzig - Map

This repository consists of 2 parts:

1. A python script that parses data from the website and adds location data to it.
2. A JavaScript class that renders an HTML map that displays the data

You can embed the map on your own website by adding the following code:

```html
<div id="mapid" style="height: 200px;"></div>
<script src="https://cdn.jsdelivr.net/gh/r-dent/LocalHeroesLeipzig@master/docs/map.js" onload="new LocalHeroesMap('mapid')"></script>
```

If you have customized your own map style with [Mapbox](https://www.mapbox.com/), you can use it for rendering by providing your key and style like this:

```html
<div id="mapid" style="height: 200px;"></div>
<script src="https://cdn.jsdelivr.net/gh/r-dent/LocalHeroesLeipzig@master/docs/map.js"></script>
<script>
    new LocalHeroesMap('mapid', {
        mapBoxKey: 'your_mapbox_key',
        mapBoxStyle: 'username/your_style_id'
    })
</script>
```

Please [file an issue](https://github.com/r-dent/LocalHeroesLeipzig/issues/new) or [contact me](https://romangille.com/#contact) if you have feedback.
