import json
import csv
import io
import streamlit as st


def geojson_to_csv(geojson_bytes):
    data = json.loads(geojson_bytes)
    features = data.get("features", [])

    rows = []
    for feature in features:
        geom = feature.get("geometry", {})
        props = feature.get("properties", {})

        geom_type = geom.get("type", "")
        coords = geom.get("coordinates", [])

        if geom_type == "LineString":
            lon, lat = coords[0][0], coords[0][1]
        elif geom_type == "MultiLineString":
            lon, lat = coords[0][0][0], coords[0][0][1]
        elif geom_type == "Point":
            lon, lat = coords[0], coords[1]
        else:
            st.warning(f"Skipping unsupported geometry type: {geom_type}")
            continue

        row = {"latitude": lat, "longitude": lon}
        row.update(props)
        rows.append(row)

    if not rows:
        return None

    fieldnames = list(rows[0].keys())
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


st.title("GeoJSON Line → Point CSV converter")

uploaded_file = st.file_uploader("Upload a GeoJSON file", type=["geojson", "json"])

if uploaded_file is not None:
    csv_data = geojson_to_csv(uploaded_file.read())

    if csv_data:
        st.success("Conversion successful.")
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="output.csv",
            mime="text/csv",
        )
    else:
        st.error("No valid features found in the uploaded file.")
