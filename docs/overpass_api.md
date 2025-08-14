========================
CODE SNIPPETS
========================
TITLE: Pub Tour in Dublin (Overpass API)
DESCRIPTION: This example demonstrates finding a sequence of pubs in Dublin, where each subsequent pub is within 500m of the previous one, starting from a specific node. It uses the `complete` statement to find a chain of features.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_API_by_Example

LANGUAGE: Overpass API
CODE:
```
node(3470507586);   // starting here...
complete(100) { nwr[amenity=pub](around:500); };
out center;

```

----------------------------------------

TITLE: Pub Tour in Dublin (Overpass API)
DESCRIPTION: This example demonstrates finding a sequence of pubs in Dublin, where each subsequent pub is within 500m of the previous one, starting from a specific node. It uses the `complete` statement to find a chain of features.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_by_Example

LANGUAGE: Overpass API
CODE:
```
node(3470507586);   // starting here...
complete(100) { nwr[amenity=pub](around:500); };
out center;

```

----------------------------------------

TITLE: Install NGINX and fcgiwrap
DESCRIPTION: Installs NGINX web server and fcgiwrap, enabling them to start automatically on boot and starting them immediately.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Installation

LANGUAGE: bash
CODE:
```
sudo apt-get install nginx fcgiwrap
sudo systemctl enable --now nginx fcgiwrap
```

----------------------------------------

TITLE: Pub Tour in Dublin (Overpass API)
DESCRIPTION: This example demonstrates finding a sequence of pubs in Dublin, where each subsequent pub is within 500m of the previous one, starting from a specific node. It uses the `complete` statement to find a chain of features.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Advanced_examples

LANGUAGE: Overpass API
CODE:
```
node(3470507586);   // starting here...
complete(100) { nwr[amenity=pub](around:500); };
out center;

```

----------------------------------------

TITLE: Overpass API XML Output Example
DESCRIPTION: An example of the XML output format from the Overpass API, showing POI nodes followed by their associated area IDs, and finally the full details of those areas.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_by_Example

LANGUAGE: XML
CODE:
```
<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="Overpass API">
  <node id="691566183" lat="49.7982193" lon="13.4686623">
    <tag k="ele" v="295"/>
    <tag k="information" v="guidepost"/>
    <tag k="name" v="Dolanský most (pravý břeh)"/>
    <tag k="tourism" v="information"/>
  </node>
  <area id="3600435511"/>
  <area id="3600442466"/>
  <node id="691566191" lat="49.8003120" lon="13.4679726">
    <tag k="ele" v="295"/>
    <tag k="information" v="guidepost"/>
    <tag k="name" v="Dolanský most (levý břeh)"/>
    <tag k="tourism" v="information"/>
  </node>
  <area id="3600435511"/>
  <area id="3600442466"/>
[
  <area id="3600435511">
    <tag k="admin_level" v="4"/>
    <tag k="boundary" v="administrative"/>
    <tag k="name" v="Jihozápad"/>
    <tag k="name:cs" v="Jihozápad"/>
    <tag k="name:de" v="Südwesten"/>
    <tag k="population" v="1209298"/>
    <tag k="ref" v="CZ03"/>
    <tag k="ref:NUTS" v="CZ03"/>
    <tag k="source" v="cuzk:ruian"/>
    <tag k="source:population" v="csu:uir-zsj"/>
    <tag k="type" v="boundary"/>
    <tag k="wikipedia" v="cs:NUTS Jihozápad"/>
  </area>
  <area id="3600442466">
    <tag k="ISO3166-2" v="CZ-PL"/>
    <tag k="admin_level" v="6"/>
    <tag k="boundary" v="administrative"/>
    <tag k="name" v="Plzeňský kraj"/>
    <tag k="name:cs" v="Plzeňský kraj"/>
    <tag k="name:de" v="Region Pilsen"/>
    <tag k="name:ru" v="Пльзенский край"/>
    <tag k="population" v="572687"/>
    <tag k="ref" v="PL"/>
    <tag k="ref:NUTS" v="CZ032"/>
    <tag k="source" v="cuzk:ruian"/>
    <tag k="source:population" v="csu:uir-zsj"/>
    <tag k="type" v="boundary"/>
    <tag k="wikipedia" v="cs:Plzeňský kraj"/>
  </area>
]

```

----------------------------------------

TITLE: Overpass API XML Output Example
DESCRIPTION: An example of the XML output format from the Overpass API, showing POI nodes followed by their associated area IDs, and finally the full details of those areas.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_API_by_Example

LANGUAGE: XML
CODE:
```
<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="Overpass API">
  <node id="691566183" lat="49.7982193" lon="13.4686623">
    <tag k="ele" v="295"/>
    <tag k="information" v="guidepost"/>
    <tag k="name" v="Dolanský most (pravý břeh)"/>
    <tag k="tourism" v="information"/>
  </node>
  <area id="3600435511"/>
  <area id="3600442466"/>
  <node id="691566191" lat="49.8003120" lon="13.4679726">
    <tag k="ele" v="295"/>
    <tag k="information" v="guidepost"/>
    <tag k="name" v="Dolanský most (levý břeh)"/>
    <tag k="tourism" v="information"/>
  </node>
  <area id="3600435511"/>
  <area id="3600442466"/>
[
  <area id="3600435511">
    <tag k="admin_level" v="4"/>
    <tag k="boundary" v="administrative"/>
    <tag k="name" v="Jihozápad"/>
    <tag k="name:cs" v="Jihozápad"/>
    <tag k="name:de" v="Südwesten"/>
    <tag k="population" v="1209298"/>
    <tag k="ref" v="CZ03"/>
    <tag k="ref:NUTS" v="CZ03"/>
    <tag k="source" v="cuzk:ruian"/>
    <tag k="source:population" v="csu:uir-zsj"/>
    <tag k="type" v="boundary"/>
    <tag k="wikipedia" v="cs:NUTS Jihozápad"/>
  </area>
  <area id="3600442466">
    <tag k="ISO3166-2" v="CZ-PL"/>
    <tag k="admin_level" v="6"/>
    <tag k="boundary" v="administrative"/>
    <tag k="name" v="Plzeňský kraj"/>
    <tag k="name:cs" v="Plzeňský kraj"/>
    <tag k="name:de" v="Region Pilsen"/>
    <tag k="name:ru" v="Пльзенский край"/>
    <tag k="population" v="572687"/>
    <tag k="ref" v="PL"/>
    <tag k="ref:NUTS" v="CZ032"/>
    <tag k="source" v="cuzk:ruian"/>
    <tag k="source:population" v="csu:uir-zsj"/>
    <tag k="type" v="boundary"/>
    <tag k="wikipedia" v="cs:Plzeňský kraj"/>
  </area>
]

```

----------------------------------------

TITLE: Overpass QL: Route Geometry and Symbols
DESCRIPTION: This example demonstrates querying for hiking routes, outputting their geometry and center points. It includes MapCSS styling to display route symbols, linking to an external tool for symbol generation.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_by_Example

LANGUAGE: Overpass QL
CODE:
```
[bbox:{{bbox}}];

relation[route=hiking];
out geom center;
>;
out;

{{style:
relation {
  color:gray;
}

relation[colour] {
  color: eval("tag('colour')");
  text: ref;
}

way, node[!route] {
  fill-color: transparent;
  color:transparent;
}
node[route] {
  fill-color: eval("tag('colour')");
  color: eval("tag('colour')");
  text: eval("concat(tag('name'), ' - (', tag('from'), ' - ', tag('to'), ')  -  ', tag('ref'))");
  icon-image: eval("concat('url', '(\'', 'https://osm.janmichel.eu/osmc/generate.pl?osmc=', tag('osmc:symbol'), '\')')");
}
}}
```

----------------------------------------

TITLE: Overpass QL: Route Geometry and Symbols
DESCRIPTION: This example demonstrates querying for hiking routes, outputting their geometry and center points. It includes MapCSS styling to display route symbols, linking to an external tool for symbol generation.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_API_by_Example

LANGUAGE: Overpass QL
CODE:
```
[bbox:{{bbox}}];

relation[route=hiking];
out geom center;
>;
out;

{{style:
relation {
  color:gray;
}

relation[colour] {
  color: eval("tag('colour')");
  text: ref;
}

way, node[!route] {
  fill-color: transparent;
  color:transparent;
}
node[route] {
  fill-color: eval("tag('colour')");
  color: eval("tag('colour')");
  text: eval("concat(tag('name'), ' - (', tag('from'), ' - ', tag('to'), ')  -  ', tag('ref'))");
  icon-image: eval("concat('url', '(\'', 'https://osm.janmichel.eu/osmc/generate.pl?osmc=', tag('osmc:symbol'), '\')')");
}
}}
```

----------------------------------------

TITLE: Overpass API XML Output Example
DESCRIPTION: An example of the XML output format from the Overpass API, showing POI nodes followed by their associated area IDs, and finally the full details of those areas.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Advanced_examples

LANGUAGE: XML
CODE:
```
<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="Overpass API">
  <node id="691566183" lat="49.7982193" lon="13.4686623">
    <tag k="ele" v="295"/>
    <tag k="information" v="guidepost"/>
    <tag k="name" v="Dolanský most (pravý břeh)"/>
    <tag k="tourism" v="information"/>
  </node>
  <area id="3600435511"/>
  <area id="3600442466"/>
  <node id="691566191" lat="49.8003120" lon="13.4679726">
    <tag k="ele" v="295"/>
    <tag k="information" v="guidepost"/>
    <tag k="name" v="Dolanský most (levý břeh)"/>
    <tag k="tourism" v="information"/>
  </node>
  <area id="3600435511"/>
  <area id="3600442466"/>
[
  <area id="3600435511">
    <tag k="admin_level" v="4"/>
    <tag k="boundary" v="administrative"/>
    <tag k="name" v="Jihozápad"/>
    <tag k="name:cs" v="Jihozápad"/>
    <tag k="name:de" v="Südwesten"/>
    <tag k="population" v="1209298"/>
    <tag k="ref" v="CZ03"/>
    <tag k="ref:NUTS" v="CZ03"/>
    <tag k="source" v="cuzk:ruian"/>
    <tag k="source:population" v="csu:uir-zsj"/>
    <tag k="type" v="boundary"/>
    <tag k="wikipedia" v="cs:NUTS Jihozápad"/>
  </area>
  <area id="3600442466">
    <tag k="ISO3166-2" v="CZ-PL"/>
    <tag k="admin_level" v="6"/>
    <tag k="boundary" v="administrative"/>
    <tag k="name" v="Plzeňský kraj"/>
    <tag k="name:cs" v="Plzeňský kraj"/>
    <tag k="name:de" v="Region Pilsen"/>
    <tag k="name:ru" v="Пльзенский край"/>
    <tag k="population" v="572687"/>
    <tag k="ref" v="PL"/>
    <tag k="ref:NUTS" v="CZ032"/>
    <tag k="source" v="cuzk:ruian"/>
    <tag k="source:population" v="csu:uir-zsj"/>
    <tag k="type" v="boundary"/>
    <tag k="wikipedia" v="cs:Plzeňský kraj"/>
  </area>
]

```

----------------------------------------

TITLE: Combined Query (Nodes, Ways, Relations)
DESCRIPTION: This example shows how to query for nodes, ways, and relations tagged 'amenity=restaurant' sequentially and output them with 'out center;'. It illustrates fetching different element types in separate statements.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_API_by_Example

LANGUAGE: Overpass QL
CODE:
```
node["amenity"="restaurant"]({{bbox}});
out;
way["amenity"="restaurant"]({{bbox}});
out center;
relation["amenity"="restaurant"]({{bbox}});
out center;
```

----------------------------------------

TITLE: Overpass QL: Route Geometry and Symbols
DESCRIPTION: This example demonstrates querying for hiking routes, outputting their geometry and center points. It includes MapCSS styling to display route symbols, linking to an external tool for symbol generation.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Advanced_examples

LANGUAGE: Overpass QL
CODE:
```
[bbox:{{bbox}}];

relation[route=hiking];
out geom center;
>;
out;

{{style:
relation {
  color:gray;
}

relation[colour] {
  color: eval("tag('colour')");
  text: ref;
}

way, node[!route] {
  fill-color: transparent;
  color:transparent;
}
node[route] {
  fill-color: eval("tag('colour')");
  color: eval("tag('colour')");
  text: eval("concat(tag('name'), ' - (', tag('from'), ' - ', tag('to'), ')  -  ', tag('ref'))");
  icon-image: eval("concat('url', '(\'', 'https://osm.janmichel.eu/osmc/generate.pl?osmc=', tag('osmc:symbol'), '\')')");
}
}}
```

----------------------------------------

TITLE: Query Restaurants (Ways)
DESCRIPTION: This example shows how to query for ways tagged with 'amenity=restaurant' within a bounding box. It highlights that ways require specific output modifiers to resolve geometry.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_API_by_Example

LANGUAGE: Overpass QL
CODE:
```
way["amenity"="restaurant"]({{bbox}});
out;
```

----------------------------------------

TITLE: Query Restaurants (Ways)
DESCRIPTION: This example shows how to query for ways tagged with 'amenity=restaurant' within a bounding box. It highlights that ways require specific output modifiers to resolve geometry.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_by_Example

LANGUAGE: Overpass QL
CODE:
```
way["amenity"="restaurant"]({{bbox}});
out;
```

----------------------------------------

TITLE: Concise Union Query with 'nwr'
DESCRIPTION: This example demonstrates a more concise way to query for nodes, ways, and relations using the 'nwr' shortcut within a union statement, combined with a global bounding box setting.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_API_by_Example

LANGUAGE: Overpass QL
CODE:
```
[bbox:{{bbox}}];
nwr["amenity"="restaurant"];
out center;
```

----------------------------------------

TITLE: Concise Union Query with 'nwr'
DESCRIPTION: This example demonstrates a more concise way to query for nodes, ways, and relations using the 'nwr' shortcut within a union statement, combined with a global bounding box setting.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_by_Example

LANGUAGE: Overpass QL
CODE:
```
[bbox:{{bbox}}];
nwr["amenity"="restaurant"];
out center;
```

----------------------------------------

TITLE: Combined Query (Nodes, Ways, Relations)
DESCRIPTION: This example shows how to query for nodes, ways, and relations tagged 'amenity=restaurant' sequentially and output them with 'out center;'. It illustrates fetching different element types in separate statements.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Advanced_examples

LANGUAGE: Overpass QL
CODE:
```
node["amenity"="restaurant"]({{bbox}});
out;
way["amenity"="restaurant"]({{bbox}});
out center;
relation["amenity"="restaurant"]({{bbox}});
out center;
```

----------------------------------------

TITLE: Concise Union Query with 'nwr'
DESCRIPTION: This example demonstrates a more concise way to query for nodes, ways, and relations using the 'nwr' shortcut within a union statement, combined with a global bounding box setting.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Advanced_examples

LANGUAGE: Overpass QL
CODE:
```
[bbox:{{bbox}}];
nwr["amenity"="restaurant"];
out center;
```

----------------------------------------

TITLE: Combined Query (Nodes, Ways, Relations)
DESCRIPTION: This example shows how to query for nodes, ways, and relations tagged 'amenity=restaurant' sequentially and output them with 'out center;'. It illustrates fetching different element types in separate statements.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_by_Example

LANGUAGE: Overpass QL
CODE:
```
node["amenity"="restaurant"]({{bbox}});
out;
way["amenity"="restaurant"]({{bbox}});
out center;
relation["amenity"="restaurant"]({{bbox}});
out center;
```

----------------------------------------

TITLE: Query Restaurants (Ways)
DESCRIPTION: This example shows how to query for ways tagged with 'amenity=restaurant' within a bounding box. It highlights that ways require specific output modifiers to resolve geometry.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Advanced_examples

LANGUAGE: Overpass QL
CODE:
```
way["amenity"="restaurant"]({{bbox}});
out;
```

----------------------------------------

TITLE: Create Table of Object Versions (with Member Count)
DESCRIPTION: Extends the previous example by adding a count of relation members for each version of the specified relation. This helps in identifying versions with a large number of members.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_API_by_Example

LANGUAGE: Overpass QL
CODE:
```
[out:csv(version,timestamp,changeset,count)];
timeline(relation,2632934);
for (t["created"])
{
  retro(_.val)
  {
    rel(2632934);
    make stat version=u(version()),timestamp=u(timestamp()),changeset=u(changeset()),count=u(count_members());
    out;
  }
}
```

----------------------------------------

TITLE: Overpass QL: Step-by-step data retrieval with relation resolution
DESCRIPTION: A more detailed query demonstrating step-by-step data retrieval. It starts with nodes in a bounding box, then explicitly fetches member nodes of ways (bn), member ways of relations (bw), and then collects ways and nodes related to previously found elements.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_API_by_Example

LANGUAGE: Overpass QL
CODE:
```
(
  node(50.746,7.154,50.748,7.157);
  rel(bn)->.x;
  way(bn);
  rel(bw);
);
(
  ._;
  way(r);
);
(
  ._;
  node(r)->.x;
  node(w);
);
out meta;

```

----------------------------------------

TITLE: Overpass QL: Mailboxes by Collection Time
DESCRIPTION: This example queries for post boxes (`amenity=post_box`) and styles them based on the presence of the `collection_times` tag. Green indicates availability of collection times, while red signifies its absence.

SOURCE: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_API_by_Example

LANGUAGE: Overpass QL
CODE:
```
node[amenity=post_box]
    //[!"collection_times"]
  ({{bbox}}); 
out;

{{style:
node
{ color:red; fill-color: red;}

node[collection_times]
{ color:green; fill-color:green; }
}}
```