import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 업비트 API를 사용하여 코인들의 가격을 가져오는 함수
def get_prices(market):
    url = f"https://api.upbit.com/v1/ticker?markets={market}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    trade_price = data[0]['trade_price']
    return trade_price

# 코인의 한글 이름과 식별자를 매핑하는 딕셔너리 생성
def create_coin_map():
    url = "https://api.upbit.com/v1/market/all"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()

    coin_map = {}
    for market in data:
        if "KRW-" in market['market']:  
            coin_map[market['korean_name']] = market['market']
    
    return coin_map

# 코인의 일주일치 일봉 캔들 데이터를 가져오는 함수
def get_days_candles(market):
    url = f"https://api.upbit.com/v1/candles/days?market={market}&count=8"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

# 코인의 일년간 월봉 캔들 데이터를 가져오는 함수
def get_monthly_candles(market):
    url = f"https://api.upbit.com/v1/candles/months?market={market}&count=13"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

# 홈 화면 설명
def show_homepage_description():
    st.markdown("""
                
    ### :house: **HOME**
    ---
    이 웹은 실시간 한국시장 코인시세, 일봉/월봉 차트를 보여주기 위해 만들어졌습니다.
    원하는 메뉴를 왼쪽에서 선택해주세요! 
    본인이 가지고있는 코인의 개수와 평단을 입력하면 수익률도 알 수 있습니다.
    """
    )

# 상승 하락 출력
def alert_price_changes(close_prices):
    # 최근 3일의 종가를 가져옴
    recent_prices = close_prices[-4:]  # 최근 3일의 데이터 선택
    current_price = recent_prices.iloc[-1]
    previous_price = recent_prices.iloc[-2]  # 이전 날짜의 가격을 선택

    # 종가 변동률 계산
    price_change_percentage = ((current_price - previous_price) / previous_price) * 100

    # 종가 변동에 따른 알림
    if price_change_percentage > 0:
        st.write(f"{selected_ticker}의 최근 3일간 가격이 {price_change_percentage:.2f}% 상승했습니다!")
        if price_change_percentage > 5:
            st.write("최근 3일간 5% 이상 상승한 코인으로, 거래시 유의가 필요합니다.")
    elif price_change_percentage < 0:
        st.write(f"{selected_ticker}의 최근 3일간 가격이 {price_change_percentage:.2f}% 하락했습니다!")
        if price_change_percentage < -5:
            st.write("최근 3일간 5% 이상 하락한 코인으로, 거래시 유의가 필요합니다.")
    else:
        st.write(f"{selected_ticker}의 최근 3일간 가격이 변동이 없습니다.")


# 코인 목록 가져오기
coin_map = create_coin_map()
tickers = list(coin_map.keys())  # 코인 이름 목록

# 왼쪽 사이드바에 홈과 코인 선택 기능 추가
selected_sidebar = st.sidebar.radio("MENU", ["Home", "코인 목록"])

# 홈을 선택한 경우
if selected_sidebar == "Home":
    show_homepage_description()
else:
    selected_ticker = st.sidebar.selectbox("코인 목록", tickers)

    # 사용자가 코인을 선택한 경우에만 실행
    if selected_ticker:
        market = coin_map.get(selected_ticker)
        price = get_prices(market)
        
        # 코인 화면의 제목
        st.markdown(":moneybag:")
        # 가격 출력 코드에 문자열 포매팅으로 콤마와 "원" 단위 추가, 소수점(.) 제거
        st.write(f"현재 {selected_ticker}의 가격: {price:,.0f} 원")

        # 사용자가 구매한 평균 가격과 보유량을 입력받음
        average_purchase_price = st.sidebar.number_input("평균 구매 가격 (KRW)", min_value=0.0)
        amount_held = st.sidebar.number_input("보유량", min_value=0.0)

        # 코인의 일봉 데이터 가져오기
        days_candles = get_days_candles(market) 

        if days_candles:
            # 일봉 데이터를 DataFrame으로 변환
            df = pd.DataFrame(days_candles)
            df['candle_date_time_kst'] = pd.to_datetime(df['candle_date_time_kst'])
            df.set_index('candle_date_time_kst', inplace=True)

            # 종가 데이터만 추출
            close_prices = df['trade_price']
            close_prices_adjusted = close_prices / 10000000

            # 현재 이익/손실 계산
            if amount_held != 0:
                profit_loss = (price - average_purchase_price) * amount_held
                profit_loss_percentage = (profit_loss / (average_purchase_price * amount_held)) * 100
                st.sidebar.write(f"현재 이익/손실: {profit_loss:,.0f} 원 ({profit_loss_percentage:.2f}%)")
            else:
                st.sidebar.write("보유량을 입력해주세요.")

            # 사용자가 선택한 그래프 종류
            plot_type = st.sidebar.radio("그래프 종류", ["일봉 그래프", "월봉 그래프"])

            if plot_type == "일봉 그래프":
                # 그래프 그리기
                fig, ax = plt.subplots(figsize=(13, 8))
                ax.plot(close_prices.index, close_prices_adjusted , label='종가', color='blue', linestyle='-', linewidth=2)
                ax.set_xlabel('날짜', fontsize=12, fontweight='bold')
                ax.set_ylabel('종가 (KRW)', fontsize=12, fontweight='bold')
                ax.set_title('일봉 7일치 종가 그래프', fontsize=14, fontweight='bold')
                ax.legend(fontsize=10)

                # 그래프 배경 및 테두리 스타일 설정
                ax.set_facecolor('#f7f7f7')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                # 그래프 선 위에 점 추가
                ax.scatter(close_prices.index, close_prices_adjusted, color='red', zorder=5)

                # 그래프 선에 가격을 주석으로 추가
                for date, price in zip(close_prices.index, close_prices_adjusted):
                    ax.annotate(f'{int(price * 10000000):,} 원', (date, price), textcoords="offset points", xytext=(0,10), ha='center')

                # 세로축 단위의 "원" 단위 추가
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,} 원".format(int(x * 10000000))))

                st.pyplot(fig) 
            elif plot_type == "월봉 그래프":
                # 코인의 월봉 데이터 가져오기
                monthly_candles = get_monthly_candles(market)

                if monthly_candles:
                    # 월봉 데이터를 DataFrame으로 변환
                    monthly_df = pd.DataFrame(monthly_candles)
                    monthly_df['candle_date_time_kst'] = pd.to_datetime(monthly_df['candle_date_time_kst'])
                    monthly_df.set_index('candle_date_time_kst', inplace=True)

                    # 월봉 데이터 중 종가만 추출
                    monthly_close_prices = monthly_df['trade_price']
                    monthly_close_prices_adjusted = monthly_close_prices / 10000000

                    # 그래프 그리기
                    fig_monthly, ax_monthly = plt.subplots(figsize=(13, 8))
                    ax_monthly.plot(monthly_close_prices.index, monthly_close_prices_adjusted, label='종가', color='green', linestyle='-', linewidth=2)
                    ax_monthly.set_xlabel('날짜', fontsize=12, fontweight='bold')
                    ax_monthly.set_ylabel('종가 (KRW)', fontsize=12, fontweight='bold')
                    ax_monthly.set_title('월봉 1년치 종가 그래프', fontsize=14, fontweight='bold')
                    ax_monthly.legend(fontsize=10)

                    # 그래프 배경 및 테두리 스타일 설정
                    ax_monthly.set_facecolor('#f7f7f7')
                    ax_monthly.spines['top'].set_visible(False)
                    ax_monthly.spines['right'].set_visible(False)

                    # 그래프 선위에 점추가
                    ax_monthly.scatter(monthly_close_prices.index, monthly_close_prices_adjusted, color='red', zorder=5)

                    # 그래프 선에 가격을 주석으로 추가
                    for date, price in zip(monthly_close_prices.index, monthly_close_prices_adjusted):
                        ax_monthly.annotate(f'{int(price * 10000000):,} 원', (date, price), textcoords="offset points", xytext=(0,10), ha='center')

                    # 세로축 단위의 "원" 단위 추가
                    ax_monthly.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,} 원".format(int(x * 10000000))))

                    st.pyplot(fig_monthly)
                    
        # 가격 급등 및 급락 코인 알림
        alert_price_changes(close_prices)
