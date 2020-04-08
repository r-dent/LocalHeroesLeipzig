## Local Heroes Leipzig - Map

This project is taking data from the [Local Heroes Leipzig](http://local-heroes-leipzig.de/) project and tries to find geo location info for each entry. The resulting data is displayed in a customizable map that can be embedded on a website.

This repository consists of 2 parts:

1. A python script that parses data from the website and adds location data to it.
2. A JavaScript class that renders an HTML map that displays the data

You can embed the map on your own website by adding the following code:

```html
<div id="mapid" style="height: 200px;"></div>
<script src="https://cdn.jsdelivr.net/gh/r-dent/LocalHeroesLeipzig@master/docs/map.js" onload="new LocalHeroesMap('mapid')"></script>
```

If you want to customize the map, you can pass some options to the initializer.

```html
<div id="mapid" style="height: 200px;"></div>
<script src="https://cdn.jsdelivr.net/gh/r-dent/LocalHeroesLeipzig@master/docs/map.js"></script>
<script>
    var localsMap = new LocalHeroesMap('mapid', {
        mapBoxKey: 'your_mapbox_key',
        mapBoxStyle: 'username/your_style_id',
        clusterBelowZoom: 15,
        showLocateButton: true
    })
</script>
```

 Option | Description
 --- | ---
 `clusterBelowZoom` | You can use clustering to group multiple markers into one for a better overview. To do that just provide a zoom level below which items will get clustered.
 `showLocateButton` | If you want to show a button that let´s the user zoom to his/her own location.
 `mapBoxStyle` | If you have customized your own map style with [Mapbox](https://www.mapbox.com/), you can use it for rendering by providing this parameter together with your Mapbox API key. If your Mapbox Style URL is something like `mapbox://styles/username/your_style_id`, use `username/your_style_id` for this parameter.
 `mapBoxKey` | Your API key from [Mapbox](https://www.mapbox.com/).

Please [file an issue](https://github.com/r-dent/LocalHeroesLeipzig/issues/new) or [contact me](https://romangille.com/#contact) if you have feedback.
