import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# 创建地图
fig = plt.figure(figsize=(10, 8))
m = Basemap(projection='lcc', resolution='i',
            lat_0=35, lon_0=105,
            width=8E6, height=8E6)

# 画出国界、省界和海岸线
m.drawcoastlines(linewidth=0.5)
m.drawcountries(linewidth=1.5)
m.drawstates(linewidth=0.5)

# 填充区域
m.fillcontinents(color='#ddaa66', lake_color='#7777ff')
m.drawmapboundary(fill_color='lightblue')

# 绘制地图
plt.show()