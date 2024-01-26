import io
import zipfile
import requests
import geopandas as gpd
import matplotlib.pyplot as plt
import school_analysis as sa
import os

class GermanStatesHeatmapPlot:


    local_path = os.path.join(sa.PACKAGE_PATH,"plotting/heatmap_data/")
    re_download = False

    def create_plot(self, state_values, default_state_color, cmap_name='coolwarm', ax=None):
       
        cmap = plt.get_cmap(cmap_name)        

        if self.re_download:
            url = "https://biogeo.ucdavis.edu/data/diva/adm/DEU_adm.zip"
            r = requests.get(url)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(path=self.local_path)

        gdf = gpd.read_file(self.local_path + '/DEU_adm1.shp')

        max_abs_value = max(abs(val) for val in state_values.values() if val is not None)

        normalized_values = {k: (v / max_abs_value if v is not None else None) for k, v in state_values.items()}
    
        gdf['color'] = gdf['NAME_1'].apply(lambda x: cmap(0.5 * (normalized_values.get(x, 0) + 1)) if normalized_values.get(x) is not None else default_state_color)

        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.figure
    
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.set_yticks([])
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=-max_abs_value, vmax=max_abs_value))
        sm._A = []
    
        plt.ioff()
        gdf.plot(color=gdf['color'], ax=ax)

        ax.axis('off')

        return fig, ax, sm