import geopandas as gpd
import matplotlib.pyplot as plt


def save_dataframe(rooms, chairs, file_name):
    """Saves geopandas GeoDataFrame ro GeoJson and stores .png file with small visualisation"""
    combined = gpd.GeoDataFrame({
        "geometry": [room['polygon'] for room in rooms] + [chair['point'] for chair in chairs],
        "color": ['white' for _ in rooms] + [chair['type'] for chair in chairs],
        "meta": [{"type": "room", "room_name": room['name']} for room in rooms] +
                [{"type": "chair", "chair_type": chair['type']} for chair in chairs],
    })

    plot = combined.plot(
        column='color',
        cmap='viridis',
        legend=True,
        edgecolor='black'
    )

    for room in rooms:
        centroid_x, centroid_y = room['polygon'].centroid.xy
        plot.annotate(
            room['name'],
            (centroid_x[0], centroid_y[0]),
            xytext=(-15, 0),
            textcoords='offset points',
            color='blue',
            fontsize=6
        )

    combined.to_file(f'./{file_name}.geojson', driver='GeoJSON')
    plt.savefig(f'./{file_name}.png')
