import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pyproj import Proj, Transformer
from geopandas.tools import sjoin

# 위도 경도 좌표를 UTM-K(GRS80 타원체) 좌표로 변환하는 함수
def convert_to_utm_k(lat, lon):
    transformer = Transformer.from_crs("epsg:4326", "epsg:5179", always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y

# 가공된 데이터 가져오기
df1 = pd.read_csv('./Filtered_Data/서대문구 대여소별 이용정보(2304).csv', index_col=False)
df2 = pd.read_csv('./Filtered_Data/서대문구 따릉이대여소 위치정보.csv', index_col=False)
seodaemungu_geo = gpd.read_file('./Filtered_Data/seodaemun_gu.shp', encoding='UTF-8')

# 대여반납차이가 큰 상위 10개의 대여소 추출
top_10_diff = df1.sort_values(by='대여반납차이', ascending=False).head(10)

# top_10_diff의 대여소명을 기반으로 df2에서 해당 대여소의 위도와 경도를 추출
top_10_loc = df2[df2['대여소명'].isin(top_10_diff['대여소명'])]
top_10_loc_copy = top_10_loc.copy()

# 상위 10개를 제외한 나머지 대여소들의 위치정보 추출
remain_loc = df2[~df2['대여소명'].isin(top_10_diff['대여소명'])]
remain_loc_copy = remain_loc.copy()

# 위도와 경도를 WGS 84에서 UTM-K로 변환
for idx, row in top_10_loc_copy.iterrows():
    x, y = convert_to_utm_k(row['위도'], row['경도'])
    top_10_loc_copy.loc[idx, 'UTM-K_X'] = x
    top_10_loc_copy.loc[idx, 'UTM-K_Y'] = y

for idx, row in remain_loc_copy.iterrows():
    x, y = convert_to_utm_k(row['위도'], row['경도'])
    remain_loc_copy.loc[idx, 'UTM-K_X'] = x
    remain_loc_copy.loc[idx, 'UTM-K_Y'] = y

# 위도와 경도를 기반으로 GeoDataFrame 생성
gdf = gpd.GeoDataFrame(
    top_10_loc, 
    geometry=gpd.points_from_xy(top_10_loc_copy['UTM-K_X'], top_10_loc_copy['UTM-K_Y'])
)

# 나머지 대여소의 GeoDataFrame 생성
remain_gdf = gpd.GeoDataFrame(
    remain_loc, 
    geometry=gpd.points_from_xy(remain_loc_copy['UTM-K_X'], remain_loc_copy['UTM-K_Y'])
)

# 모든 대여소의 위치 정보를 포함하는 GeoDataFrame 생성
all_loc_copy = df2.copy()
for idx, row in all_loc_copy.iterrows():
    x, y = convert_to_utm_k(row['위도'], row['경도'])
    all_loc_copy.loc[idx, 'UTM-K_X'] = x
    all_loc_copy.loc[idx, 'UTM-K_Y'] = y

all_gdf = gpd.GeoDataFrame(
    all_loc_copy, 
    geometry=gpd.points_from_xy(all_loc_copy['UTM-K_X'], all_loc_copy['UTM-K_Y'])
)

# 상위 10개 대여소 주변의 버퍼 생성
buffer_radius = 300  # 300미터, 한 대여소 기준 300미터 아느이 대여소 개수를 판별하고자 함
top_10_gdf_buffer = gdf.copy()
top_10_gdf_buffer['geometry'] = top_10_gdf_buffer.geometry.buffer(buffer_radius)

# 공간 조인을 사용하여 버퍼 내의 나머지 대여소 식별
within_buffer = sjoin(all_gdf, top_10_gdf_buffer, how="inner", predicate='intersects')

# 버퍼 내의 대여소 수 계산
buffer_counts = within_buffer.groupby('index_right').size()

# 버퍼 내의 대여소가 특정 임계값보다 적은 지점 식별, 자신 포함 3개 미만이면 대여소가 부족한 것으로 판단
low_density_areas = buffer_counts[buffer_counts < 3].index.tolist()

# 낮은 밀도 지역의 대여소 식별
low_density_station = top_10_gdf_buffer.loc[low_density_areas]

# 시각화
fig, ax = plt.subplots()
seodaemungu_geo.plot(ax=ax, color='white', edgecolor='black')

# 상위 10개 대여소에 버퍼 영역 표시 (녹색으로 표시)
top_10_gdf_buffer.plot(ax=ax, color='green', alpha=0.1, edgecolor='green')

# low_density_station에 해당하는 대여소의 버퍼를 붉은색으로 표시 (이미 버퍼가 적용된 지오메트리를 사용)
low_density_station.plot(ax=ax, color='red', alpha=0.5, edgecolor='red')

# 각 대여소 위치에 대여소의 인덱스 레이블을 텍스트로 마킹
for idx, row in gdf.iterrows():
    ax.text(row.geometry.x, row.geometry.y, str(idx), fontsize=12, ha='right')

# 각 대여소 마커 표시
gdf.plot(ax=ax, color='red', markersize=50)  # 상위 10개 대여소
remain_gdf.plot(ax=ax, color='blue', markersize=20)  # 나머지 대여소

plt.show()
