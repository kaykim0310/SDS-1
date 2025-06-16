import streamlit as st
import pandas as pd
import json
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="MSDS 작성 시스템",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 별표5 - 용도분류체계 데이터
RECOMMENDED_USES = [
    {"code": "1", "category": "원료/중간체", "name": "원료 및 중간체", "description": "새로운 물질의 합성, 혼합물의 배합 등에 사용되는 원료 및 그 과정에서 발생되는 중간체"},
    {"code": "2", "category": "접착/실런트", "name": "접착제 및 실런트", "description": "두 물체의 접촉면을 접합시키거나 두 개의 개체를 결합시키는 물질"},
    {"code": "3", "category": "흡착제", "name": "흡착제", "description": "가스나 액체를 흡착하는 물질"},
    {"code": "4", "category": "방향/탈취제", "name": "방향제 및 탈취제 등", "description": "실내 공기 중에 냄새를 발생시키거나 의류 등의 냄새를 제거하는데 사용되는 물질"},
    {"code": "5", "category": "냉동/해빙제", "name": "냉동방지 및 결빙제거제", "description": "냉각에 의하여 고화되는 것을 방지하거나 얼음을 제거하는 물질"},
    {"code": "6", "category": "금속/합금", "name": "금속(금속 광물 포함) 및 합금", "description": "납, 구리 등 하나의 원소로 이루어진 금속 및 하나의 금속에 한 종류 이상의 금속을 첨가하여 만든 금속"},
    {"code": "7", "category": "살생물제", "name": "살생물제", "description": "농작물 이외의 대상에 대하여 유해생물을 제거, 무해화 또는 억제하기 위해 사용되는 물질(농약 제외)"},
    {"code": "8", "category": "코팅/페인트", "name": "코팅, 페인트, 신너, 페인트 제거제", "description": "표면에 피막을 입히거나 제거하는데 사용되는 물질"},
    {"code": "8.1", "category": "코팅/페인트", "name": "유성 페인트", "description": "신너에 희석하여 사용하는 페인트"},
    {"code": "8.2", "category": "코팅/페인트", "name": "수성 페인트", "description": "물에 희석하여 사용하는 페인트"},
    {"code": "8.3", "category": "코팅/페인트", "name": "신너", "description": "페인트 등을 희석하는데 사용하는 용제"},
    {"code": "8.4", "category": "코팅/페인트", "name": "페인트 제거제", "description": "도색된 페인트를 표면으로부터 제거하는데 사용하는 물질"},
    {"code": "8.5", "category": "코팅/페인트", "name": "경화제", "description": "경도를 높이거나 경화를 촉진시키기 위하여 첨가하는 물질"},
    {"code": "8.6", "category": "코팅/페인트", "name": "기타 코팅 및 도장 관련 제품", "description": "표면에 피막을 입히거나 제거하는데 사용되는 물질 중에서 8.1부터 8.5에 해당되지 않는 물질"},
    {"code": "9", "category": "필러/퍼티", "name": "필러, 퍼티, 점토 등", "description": "빈 틈이나 공간을 메꾸거나 연결하기 위하여 사용되는 물질"},
    {"code": "10", "category": "폭발물", "name": "화약 및 폭발물", "description": "화학적 안전성이 있으나 화학적 변화를 거침으로써 폭발 또는 팽창을 동반한 다량의 에너지 및 가스를 매우 빠르게 발생시키는 물질"},
    {"code": "11", "category": "비료", "name": "비료", "description": "식물에 영양을 주거나 식물의 재배를 돕기 위해 흙에서 화학적 변화를 가져오게 하는 물질"},
    {"code": "12", "category": "연료/첨가제", "name": "연료 및 연료 첨가제", "description": "연소반응을 통해 에너지를 얻을 수 있는 물질 및 연소 효율이나 에너지 효율을 높이기 위하여 연료에 첨가하는 물질(플라스틱 원료는 제외)"},
    {"code": "13", "category": "금속표면처리", "name": "금속 표면 처리제", "description": "금속표면의 세척 및 세정을 위해서 쓰이는 물질 및 도금공정에서 도금강도를 증가시키기 위해 첨가하는 물질"},
    {"code": "14", "category": "비금속표면처리", "name": "비금속 표면 처리제", "description": "금속 이외의 표면의 세척 및 세정을 위해서 쓰이는 물질 및 도금공정에서 도금강도를 증가시키기 위해 첨가하는 물질"},
    {"code": "15", "category": "열전달제", "name": "열전달제", "description": "열을 전달하고 열을 제거하는 물질"},
    {"code": "16", "category": "유압유", "name": "유압유 및 첨가제", "description": "각종 압축기에 넣는 액체(기름류) 및 압력 전달 효율을 높이기 위해 첨가하는 물질"},
    {"code": "17", "category": "잉크/토너", "name": "잉크 및 토너", "description": "프린터나 전자복사기 등에 쓰여 영구적인 이미지 생성에 사용하는 물질"},
    {"code": "18", "category": "공정보조제", "name": "다양한 공정 보조제(pH조절제, 응집제, 침전제, 중화제 등)", "description": "공정의 안정성과 효율을 높이기 위하여 사용되는 각종 물질"},
    {"code": "18.1", "category": "공정보조제", "name": "부식방지제", "description": "공기를 비롯한 화학물질, 옥외노출 등으로 생기는 부식을 방지하기 위해 첨가하는 물질"},
    {"code": "18.2", "category": "공정보조제", "name": "부유제", "description": "광물질의 제련 공정 중에서 광물질을 농축·수거하기 위해 사용하는 물질"},
    {"code": "18.3", "category": "공정보조제", "name": "주물용 융제", "description": "광물질을 녹이는 공정에서 산화물이 형성되는 것을 방지하기 위해 첨가하는 물질"},
    {"code": "18.4", "category": "공정보조제", "name": "발포제 및 기포제", "description": "주로 플라스틱이나 고무 등에 첨가해서 작업공정 중 가스를 발생시켜 기포를 형성하게 하는 물질"},
    {"code": "18.5", "category": "공정보조제", "name": "산화제", "description": "특수한 조건에서 산소를 쉽게 발생시켜 다른 물질을 산화시키는 물질, 수소를 제거하는 물질 또는 화학반응에서 전자를 쉽게 받아들이는 물질"},
    {"code": "19", "category": "실험용", "name": "실험용 화학물질(시약)", "description": "실험실에서 기기분석 등에 사용되는 화학물질"},
    {"code": "20", "category": "가죽처리제", "name": "가죽 처리제", "description": "가죽을 부드럽게 하는 등 다양한 목적을 위하여 가죽처리에 사용되는 물질"},
    {"code": "21", "category": "윤활제", "name": "윤활용제품", "description": "기계의 마찰 부분의 발열이나 마모를 방지하거나 탈부착을 원활하게 하기 위해 사용되는 기름"},
    {"code": "22", "category": "금속가공유", "name": "금속 가공유", "description": "금속재료의 천공, 절삭, 연마 등을 할 때 발생하는 마찰 저항과 온도 및 금속찌꺼기의 제거 등을 목적으로 사용되는 물질"},
    {"code": "23", "category": "종이/보드처리제", "name": "종이 및 보드 처리제", "description": "종이 등의 제조 과정에서 사용되는 각종 물질"},
    {"code": "24", "category": "농약", "name": "식물보호제(농약)", "description": "농작물을 균, 곤충, 응애, 선충, 바이러스, 잡초, 그 밖의 병해충으로부터 방제하는데 사용하는 물질. 다만, 비료는 제외한다."},
    {"code": "25", "category": "향수/향료", "name": "향수 및 향료", "description": "향을 내는 물질"},
    {"code": "26", "category": "의약품", "name": "의약품", "description": "병의 치료나 증상의 완화 등을 목적으로 의료에 사용되는 물질"},
    {"code": "27", "category": "광화학제품", "name": "광화학제품", "description": "영구적인 사진 이미지를 만드는 데 사용하는 물질"},
    {"code": "28", "category": "광택제/왁스", "name": "광택제 및 왁스", "description": "표면의 윤기를 내기 위하여 사용하는 물질"},
    {"code": "29", "category": "폴리머", "name": "폴리머(고무 및 플라스틱) 재료(단량체 제외)", "description": "플라스틱과 고무를 제조하는데 사용되는 원료 및 첨가제 중 단량체물질을 제외한 모든 제품"},
    {"code": "30", "category": "반도체", "name": "반도체", "description": "규소단결정체처럼 절연체와 금속의 중간 정도의 전기저항을 갖는 물질로서 빛, 열 또는 전자기장에 의해 기전력을 발생하는 물질"},
    {"code": "31", "category": "섬유처리제", "name": "섬유용 염료 등 섬유 처리제", "description": "섬유에 색을 입히거나 섬유의 질을 개선하기 위해 첨가하는 물질"},
    {"code": "32", "category": "세정/세척제", "name": "세정 및 세척제", "description": "표면의 오염을 제거하는데 사용되는 액체로서 물이나 용제를 포함"},
    {"code": "33", "category": "경수연화제", "name": "경수 연화제", "description": "물 속의 칼슘이나 마그네슘 등을 제거하여 경수를 연수로 변화시키는 물질"},
    {"code": "34", "category": "수처리제", "name": "수처리제", "description": "오염된 물을 정수 또는 소독하기 위하여 사용되는 물질"},
    {"code": "35", "category": "용접/납땜", "name": "용접, 납땜 재료 및 플럭스", "description": "금속류의 용접 및 납땜질을 할 때 사용하는 물질"},
    {"code": "36", "category": "화장품", "name": "화장품 및 개인위생용품", "description": "인체를 청결, 미화하는 등의 목적으로 사용되는 물질"},
    {"code": "37", "category": "용제/추출제", "name": "용제 및 추출제", "description": "녹이거나 희석시키거나 추출, 탈지를 위해 사용하는 물질"},
    {"code": "38", "category": "배터리전해제", "name": "배터리 전해제", "description": "배터리의 전기 전달을 돕는 물질"},
    {"code": "39", "category": "색소", "name": "색소", "description": "페인트나 잉크 등의 색을 내는 데 사용되는 물질"},
    {"code": "40", "category": "건축재료", "name": "단열재 및 건축용 재료", "description": "열의 소실을 막기 위하여 사용되는 재료 등 건축에 사용되는 재료"},
    {"code": "41", "category": "전기절연제", "name": "전기 절연제", "description": "전기가 통하지 않도록 차단하는 물질"},
    {"code": "42", "category": "추진체", "name": "에어로졸 추진체", "description": "압축가스 또는 액화가스로서 용기에서 가스를 분사함으로써 내용물을 분출시키는 물질"},
    {"code": "43", "category": "응축방지제", "name": "응축방지제", "description": "물체의 표면에서 액체가 응축되는 것을 방지할 목적으로 사용하는 물질"},
    {"code": "44", "category": "접착방지제", "name": "접착방지제", "description": "두 개체 접촉면의 접착을 방지할 목적으로 사용하는 물질"},
    {"code": "45", "category": "정전기방지제", "name": "정전기방지제", "description": "정전기 발생을 방지하거나 저감하는 물질"},
    {"code": "46", "category": "분진결합제", "name": "분진결합제", "description": "분진의 발생·분산을 방지하기 위해 첨가하는 물질"},
    {"code": "47", "category": "식품/식품첨가물", "name": "식품 및 식품첨가물", "description": "식품(의약으로 섭취하는 것은 제외한다) 및 식품을 제조·가공 또는 보존하는 과정에서 식품에 넣거나 첨가하는 물질"},
    {"code": "48", "category": "기타", "name": "기타", "description": "1부터 47에 해당하지 않는 그 밖의 물질"}
]

# 세션 상태 초기화
if 'msds_data' not in st.session_state:
    st.session_state.msds_data = {}

def main():
    # 헤더
    st.title("🛡️ 물질안전보건자료(MSDS) 작성 시스템")
    st.markdown("---")
    
    # 사이드바 - 탭 네비게이션
    with st.sidebar:
        st.header("📋 MSDS 작성 단계")
        selected_tab = st.selectbox(
            "작성할 항목을 선택하세요:",
            [
                "1. 화학제품과 회사정보",
                "2. 유해성·위험성",
                "3. 구성성분의 명칭 및 함유량",
                "4. 응급조치 요령",
                "5. 폭발·화재시 대처방법",
                "6. 누출 사고시 대처방법",
                "7. 취급 및 저장방법",
                "8. 노출방지 및 개인보호구",
                "9. 물리화학적 특성",
                "10. 안정성 및 반응성",
                "11. 독성에 관한 정보",
                "12. 환경에 미치는 영향",
                "13. 폐기시 주의사항",
                "14. 운송에 필요한 정보",
                "15. 법적 규제현황",
                "16. 그 밖의 참고사항"
            ]
        )
        
        st.markdown("---")
        st.subheader("💾 데이터 관리")
        
        # 저장된 데이터 현황
        if st.session_state.msds_data:
            st.success(f"저장된 항목: {len(st.session_state.msds_data)}개")
            for key in st.session_state.msds_data.keys():
                st.write(f"✅ {key}")
        else:
            st.info("저장된 데이터가 없습니다.")
        
        # 데이터 내보내기
        if st.button("📤 Excel로 내보내기"):
            if st.session_state.msds_data:
                df = pd.DataFrame([st.session_state.msds_data])
                st.download_button(
                    label="💾 Excel 파일 다운로드",
                    data=df.to_csv(index=False).encode('utf-8-sig'),
                    file_name=f"MSDS_데이터_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                st.success("Excel 파일이 준비되었습니다!")
            else:
                st.warning("저장된 데이터가 없습니다.")

    # 메인 컨텐츠
    if selected_tab == "1. 화학제품과 회사정보":
        tab1_form()
    elif selected_tab == "2. 유해성·위험성":
        tab2_form()
    else:
        st.info(f"'{selected_tab}' 탭은 준비 중입니다. 곧 추가될 예정입니다!")

def tab1_form():
    """1번 탭: 화학제품과 회사에 관한 정보"""
    
    st.header("1. 화학제품과 회사에 관한 정보")
    
    # 클라이언트 로고 및 MSDS 정보 헤더
    col_logo, col_msds_info = st.columns([1, 2])
    
    with col_logo:
        st.markdown("##### 🏢 클라이언트 로고")
        uploaded_logo = st.file_uploader(
            "로고 파일 업로드", 
            type=['png', 'jpg', 'jpeg', 'svg'],
            help="PNG, JPG, JPEG, SVG 파일을 업로드해주세요"
        )
        
        if uploaded_logo is not None:
            st.image(uploaded_logo, width=200, caption="클라이언트 로고")
            # 로고 파일을 세션에 저장 (실제 구현에서는 파일 시스템에 저장)
            st.session_state.msds_data["1_client_logo"] = uploaded_logo.name
        elif st.session_state.msds_data.get("1_client_logo"):
            st.info(f"저장된 로고: {st.session_state.msds_data.get('1_client_logo')}")
        else:
            st.info("로고를 업로드하면 MSDS 문서에 포함됩니다")
    
    with col_msds_info:
        st.markdown("##### 📋 MSDS 관리정보")
        
        # MSDS 번호 입력
        msds_number = st.text_input(
            "관리번호", 
            value=st.session_state.msds_data.get("1_msds_number", ""),
            help="내부 관리용 번호를 입력해주세요"
        )
        
        # 날짜 입력
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            creation_date = st.date_input(
                "최초작성일",
                value=pd.to_datetime(st.session_state.msds_data.get("1_creation_date", datetime.now().date())).date()
            )
        with col_date2:
            revision_date = st.date_input(
                "최종개정일",
                value=pd.to_datetime(st.session_state.msds_data.get("1_revision_date", datetime.now().date())).date()
            )
        
        # MSDS 정보 표 생성
        st.markdown("##### 📊 MSDS 정보표")
        
        # HTML 테이블로 깔끔하게 표시
        table_html = f"""
        <style>
        .msds-table {{
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
            font-family: Arial, sans-serif;
        }}
        .msds-table th, .msds-table td {{
            border: 2px solid #333;
            padding: 8px 12px;
            text-align: center;
            font-weight: bold;
        }}
        .msds-table th {{
            background-color: #f0f0f0;
            width: 40%;
        }}
        .msds-table td {{
            background-color: white;
            width: 60%;
        }}
        </style>
        
        <table class="msds-table">
            <tr>
                <th>관리번호</th>
                <td>{msds_number if msds_number else ""}</td>
            </tr>
            <tr>
                <th>최초작성일</th>
                <td>{creation_date.strftime("%Y년 %m월 %d일")}</td>
            </tr>
            <tr>
                <th>최종개정일</th>
                <td>{revision_date.strftime("%Y년 %m월 %d일")}</td>
            </tr>
        </table>
        """
        
        st.markdown(table_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 가. 제품명
    st.subheader("가. 제품명")
    product_name = st.text_input(
        "제품명 (경고표지 상에 사용되는 것과 동일한 명칭 또는 분류코드)",
        value=st.session_state.msds_data.get("1_product_name", ""),
        help="경고표지와 동일한 명칭을 사용해주세요"
    )
    
    st.markdown("---")
    
    # 나. 권고용도
    st.subheader("나. 제품의 권고 용도와 사용상의 제한")
    
    # 권고용도 선택 (카테고리별 라디오 버튼)
    st.markdown("##### 권고 용도 선택")
    
    # 카테고리별로 그룹핑
    categories_dict = {}
    for use in RECOMMENDED_USES:
        if use["category"] not in categories_dict:
            categories_dict[use["category"]] = []
        categories_dict[use["category"]].append(use)
    
    # 이전 선택값 복원
    saved_use_code = st.session_state.msds_data.get("1_recommended_use_code", "")
    
    # 카테고리 선택
    category_names = list(categories_dict.keys())
    selected_category = st.selectbox(
        "🎯 1단계: 카테고리 선택",
        ["카테고리를 선택하세요"] + category_names,
        help="먼저 해당하는 대분류를 선택해주세요"
    )
    
    recommended_use_code = ""
    recommended_use_name = ""
    
    if selected_category != "카테고리를 선택하세요":
        st.markdown(f"##### 🎯 2단계: {selected_category} 세부 용도 선택")
        
        # 해당 카테고리의 용도들
        category_uses = categories_dict[selected_category]
        
        # 라디오 버튼 옵션 생성 (용도명 + 작은 설명)
        radio_options = []
        radio_values = []
        
        for use in category_uses:
            # 용도명과 설명을 함께 표시
            display_text = f"{use['code']}. {use['name']}"
            radio_options.append(display_text)
            radio_values.append(use['code'])
        
        # 이전 선택값이 현재 카테고리에 있는지 확인
        default_index = 0
        if saved_use_code in radio_values:
            default_index = radio_values.index(saved_use_code)
        
        # 라디오 버튼으로 선택
        if radio_options:
            selected_radio = st.radio(
                "세부 용도",
                radio_options,
                index=default_index,
                key=f"radio_{selected_category}"
            )
            
            # 선택된 용도의 상세 정보
            selected_index = radio_options.index(selected_radio)
            selected_use = category_uses[selected_index]
            
            # 선택된 용도 아래에 설명 표시
            st.markdown(f"""
            <div style="
                background: #f0f2f6;
                padding: 10px 15px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                margin: 10px 0;
                font-size: 13px;
                color: #333;
                line-height: 1.4;
            ">
                📝 <strong>설명:</strong> {selected_use['description']}
            </div>
            """, unsafe_allow_html=True)
            
            recommended_use_code = selected_use["code"]
            recommended_use_name = selected_use["name"]
            
            # 최종 선택 확인
            st.success(f"✅ **선택됨:** {selected_use['code']}. {selected_use['name']}")
    
    else:
        st.info("⬆️ 위에서 카테고리를 먼저 선택해주세요.")
    
    # 전체 용도 빠른 참조 (접을 수 있는 형태)
    with st.expander("📚 전체 용도 빠른 참조"):
        st.markdown("모든 용도를 한눈에 보고 싶으시면 펼쳐보세요.")
        
        # 검색 기능
        quick_search = st.text_input("🔍 빠른 검색", placeholder="키워드 입력...")
        
        if quick_search:
            filtered_uses = [
                use for use in RECOMMENDED_USES 
                if quick_search.lower() in use["name"].lower() 
                or quick_search.lower() in use["description"].lower()
            ]
        else:
            filtered_uses = RECOMMENDED_USES
        
        # 테이블 형태로 표시
        if filtered_uses:
            for use in filtered_uses:
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button(f"선택", key=f"quick_{use['code']}", type="secondary"):
                        st.session_state.msds_data["1_recommended_use_code"] = use["code"]
                        st.experimental_rerun()
                with col2:
                    st.write(f"**{use['code']}. {use['name']}** ({use['category']})")
                    st.caption(f"📝 {use['description']}")
                st.divider()
    
    # 사용상의 제한
    usage_restrictions = st.text_area(
        "사용상의 제한",
        value=st.session_state.msds_data.get("1_usage_restrictions", "상기 용도외 사용금지"),
        height=100,
        help="제품 사용 시 주의사항이나 제한사항을 입력해주세요"
    )
    
    st.markdown("---")
    
    # 다. 공급자 정보
    st.subheader("다. 공급자 정보")
    
    supplier_type = st.radio(
        "공급자 구분",
        ["제조자와 국내공급자가 동일", "제조자와 국내공급자가 다름"],
        index=0 if st.session_state.msds_data.get("1_supplier_type", "same") == "same" else 1
    )
    
    if supplier_type == "제조자와 국내공급자가 동일":
        st.markdown("##### 🏢 공급자 정보")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input(
                "회사명",
                value=st.session_state.msds_data.get("1_company_name", "")
            )
        with col2:
            emergency_phone = st.text_input(
                "긴급전화번호",
                value=st.session_state.msds_data.get("1_emergency_phone", "")
            )
        
        address = st.text_area(
            "주소",
            value=st.session_state.msds_data.get("1_address", ""),
            height=80
        )
        
        # 제조자 정보는 공급자와 동일하게 설정
        manufacturer_name = company_name
        manufacturer_address = address
        manufacturer_phone = emergency_phone
        domestic_supplier_name = company_name
        domestic_supplier_address = address
        domestic_emergency_phone = emergency_phone
        
    else:
        st.markdown("##### 🏭 제조자 정보")
        
        col1, col2 = st.columns(2)
        with col1:
            manufacturer_name = st.text_input(
                "제조회사명",
                value=st.session_state.msds_data.get("1_manufacturer_name", "")
            )
        with col2:
            manufacturer_phone = st.text_input(
                "제조회사 연락처",
                value=st.session_state.msds_data.get("1_manufacturer_phone", "")
            )
        
        manufacturer_address = st.text_area(
            "제조회사 주소",
            value=st.session_state.msds_data.get("1_manufacturer_address", ""),
            height=80
        )
        
        st.markdown("##### 🏢 국내 공급자 정보")
        
        col1, col2 = st.columns(2)
        with col1:
            domestic_supplier_name = st.text_input(
                "국내공급자명",
                value=st.session_state.msds_data.get("1_domestic_supplier_name", "")
            )
        with col2:
            domestic_emergency_phone = st.text_input(
                "긴급전화번호",
                value=st.session_state.msds_data.get("1_domestic_emergency_phone", "")
            )
        
        domestic_supplier_address = st.text_area(
            "국내공급자 주소",
            value=st.session_state.msds_data.get("1_domestic_supplier_address", ""),
            height=80
        )
        
        # 공급자 정보는 국내공급자와 동일하게 설정
        company_name = domestic_supplier_name
        address = domestic_supplier_address
        emergency_phone = domestic_emergency_phone
    
    st.markdown("---")
    
    # 저장 버튼
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("💾 저장", type="primary", use_container_width=True):
            # 데이터 저장
            st.session_state.msds_data.update({
                "1_msds_number": msds_number,
                "1_creation_date": creation_date.isoformat(),
                "1_revision_date": revision_date.isoformat(),
                "1_product_name": product_name,
                "1_recommended_use_code": recommended_use_code,
                "1_recommended_use_name": recommended_use_name,
                "1_usage_restrictions": usage_restrictions,
                "1_supplier_type": "same" if supplier_type == "제조자와 국내공급자가 동일" else "different",
                "1_company_name": company_name,
                "1_address": address,
                "1_emergency_phone": emergency_phone,
                "1_manufacturer_name": manufacturer_name,
                "1_manufacturer_address": manufacturer_address,
                "1_manufacturer_phone": manufacturer_phone,
                "1_domestic_supplier_name": domestic_supplier_name,
                "1_domestic_supplier_address": domestic_supplier_address,
                "1_domestic_emergency_phone": domestic_emergency_phone,
                "1_saved_at": datetime.now().isoformat()
            })
            
            st.success("✅ 1번 항목이 저장되었습니다!")
            st.balloons()

def tab2_form():
    """2번 탭: 유해성·위험성"""
    
    st.header("2. 유해성·위험성")
    st.info("🚧 2번 탭은 현재 개발 중입니다. 곧 완성될 예정입니다!")
    
    # 미리보기 형태로 구조만 표시
    with st.expander("📋 2번 탭 구성 미리보기"):
        st.write("**가. 유해성·위험성 분류**")
        st.write("- GHS 분류 기준에 따른 유해성 분류")
        st.write("- 물리적 위험성, 건강 유해성, 환경 유해성")
        
        st.write("**나. 예방조치 문구를 포함한 경고 표지 항목**")
        st.write("- 그림문자 (픽토그램)")
        st.write("- 신호어 (위험/경고)")
        st.write("- 유해·위험 문구")
        st.write("- 예방조치 문구")
        
        st.write("**다. 유해성·위험성 분류기준에 포함되지 않는 기타 유해성·위험성**")
        st.write("- 분진 폭발 위험성 등")

if __name__ == "__main__":
    main()