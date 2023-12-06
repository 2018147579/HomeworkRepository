import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

# 가공된 데이터 가져오기
df1 = pd.read_csv('./Filtered_Data/서대문구 대여소별 이용정보(2304).csv', index_col=False)
df2 = pd.read_csv('./Filtered_Data/서대문구 따릉이대여소 위치정보.csv', index_col=False)
seodaemungu_geo = gpd.read_file('./Filtered_Data/seodaemun_gu.shp', encoding='UTF-8')

# 대여반납차이가 큰 상위 10개의 대여소 추출
top_10_diff = df1.sort_values(by='대여반납차이', ascending=False).head(10)

# top_10_diff의 대여소명을 기반으로 df2에서 해당 대여소의 위도와 경도를 추출
top_10_locations = df2[df2['대여소명'].isin(top_10_diff['대여소명'])]

# 위도와 경도를 기반으로 GeoDataFrame 생성
gdf = gpd.GeoDataFrame(
    top_10_locations, 
    geometry=gpd.points_from_xy(top_10_locations['경도'], top_10_locations['위도'])
)

# CRS 설정 (WGS 84)
gdf.set_crs(epsg=5179, inplace=True)

# 시각화
fig, ax = plt.subplots()
seodaemungu_geo.plot(ax=ax, color='white', edgecolor='black')
gdf.plot(ax=ax, color='red', markersize=50)

plt.show()