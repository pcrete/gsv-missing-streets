# Street View Image Metadata

The **Street View API metadata** requests provide data about Street View panoramas. Using the metadata, you can find out if a Street View image is available at a given location which **No quota is consumed** .


### Example of metadata
* street view available
```json
{"copyright": "© Google, Inc.",
 "date": "2016-06",
 "location": {"lat": 8.601592312833652, "lng": 99.80298133747272},
 "pano_id": "u5Hn4GeNtMtk1EvLOa-N5w",
 "status": "OK"}
```
* street view *unavailable*
```json
{"status": "ZERO_RESULTS"}
```

### Example of missing streets
* Original points (left) & Missing Points (right), version 1
![Example of missing streets](pics/missing-points.png)

* version2
![Example of missing streets](pics/roads.png)
**Ref:** [Gooogle street view matedata api](https://developers.google.com/maps/documentation/streetview/metadata)