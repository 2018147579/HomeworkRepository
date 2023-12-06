import pandas as pd         # .csv 파일을 가공하기 위함
import geopandas as gpd     # .shp 파일을 가공하기 위함

# 1. 서울특별시 공공자전거 대여소별 정보를 서대문구 한정의 정보로 가공하기
# 원본 데이터셋 불러오기
df = pd.read_csv('./Original_Data/서울특별시 공공자전거 대여소별 이용정보(월별)_23.1-6.csv', index_col=False, encoding='cp949')

# 지역을 서대문구로 한정해서 데이터 추출하곡 이름 형식 정렬하기
df1 = df.loc[(df.자치구 == '서대문구'), :]
df1_copy = df1.copy()
extracted_st_name = df1_copy['대여소명'].str.extract(r'(\d+)\.\s*(.*)')
df1_copy['대여소명'] = extracted_st_name[0] + ". " + extracted_st_name[1]

# '대여건수'와 '반납건수' 열의 데이터를 정수형으로 변환
df1_copy['대여건수'] = df1_copy['대여건수'].str.replace(',', '').astype(int)
df1_copy['반납건수'] = df1_copy['반납건수'].str.replace(',', '').astype(int)

# '기준년월'이 202304인 행 필터링
filtered_df1 = df1_copy[df1_copy['기준년월'] == 202304].copy()

# 대여건수와 반납건수의 차이 & 대여소별 유동인구 계산
filtered_df1['대여반납차이'] = filtered_df1['대여건수'] - filtered_df1['반납건수']
filtered_df1['이용건수'] = filtered_df1['대여건수'] + filtered_df1['반납건수']

# 가공된 데이터 내보내기
filtered_df1.to_csv('./Filtered_Data/서대문구 대여소별 이용정보(2304).csv', encoding="utf-8-sig", index=False)

# 서대문구 내 대여소 이름 가져오기
unique_stations = filtered_df1['대여소명'].unique()

# 2. 서울시 따릉이대여소 마스터 정보를 서대문구 한정의 정보로 가공하기
# 원본 데이터셋 불러오기
df_loc = pd.read_csv('./Original_Data/공공자전거 대여소 정보(23.06월 기준).csv', index_col=False, encoding='cp949')

# 필요없는 행과 열 잘라내기
filtered_df_loc = df_loc.iloc[4: , :6]

# 1번에서는 대여소명에 대여소 번호와 이름이 합쳐져있는데 2번의 원본 데이터는 번호와 이름이 다른 컬럼에 들어가있다.
# 따라서 두 데이터셋의 포맷을 같게 해주기 위해 컬럼을 합쳐 기존의 두 컬럼과 바꿔준다.
filtered_df_loc['대여소\n번호'] = filtered_df_loc['대여소\n번호'].astype(str)
filtered_df_loc['보관소(대여소)명'] = filtered_df_loc['보관소(대여소)명'].astype(str)
filtered_df_loc['대여소명'] = filtered_df_loc['대여소\n번호'].str.split('.').str[0] + '. ' + filtered_df_loc['보관소(대여소)명']

# 정규 표현식을 사용하여 숫자와 이름 분리
extracted_st_name2 = filtered_df_loc['대여소명'].str.extract(r'(\d+)\.\s*(.*)')

# 숫자와 이름을 결합하여 새로운 '대여소명' 형식 생성
filtered_df_loc['대여소명'] = extracted_st_name2[0] + ". " + extracted_st_name2[1]

# 필요없는 컬럼 삭제 후 대여소명을 제일 첫 컬럼으로 옮겨주기
filtered_df_loc = filtered_df_loc.iloc[: , 2:]
filtered_df_loc = filtered_df_loc.drop(columns=['Unnamed: 3'])
column_order = ['대여소명'] + [col for col in filtered_df_loc.columns if col != '대여소명']
filtered_df_loc = filtered_df_loc[column_order]

# 다른 컬럼명 올바르게 수정하기
filtered_df_loc.rename(columns={'소재지(위치)': '자치구'}, inplace=True)
filtered_df_loc.rename(columns={'Unnamed: 4': '위도'}, inplace=True)
filtered_df_loc.rename(columns={'Unnamed: 5': '경도'}, inplace=True)

# 자치구를 서대문구로 한정하기
filtered_df_loc = filtered_df_loc.loc[(filtered_df_loc.자치구 == '서대문구'), :]

# 가공된 데이터 내보내기
filtered_df_loc.to_csv('./Filtered_Data/서대문구 따릉이대여소 위치정보.csv', encoding="utf-8-sig", index=False)

# 3. 전국 시군구 단위의 지리적 정보를 서대문구 한정의 정보로 가공하기
# 원본 데이터셋 가져오기
sig = gpd.read_file('./Original_Data/sig.shp', encoding='ANSI')

# 서대문구 지역만 필터링
seodaemun_gu = sig[sig['SIG_KOR_NM'] == '서대문구']

# 서대문구 데이터를 새로운 SHP 파일로 저장
seodaemun_gu.to_file('./Filtered_Data/seodaemun_gu.shp', encoding='UTF-8')