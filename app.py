"""
SwasthCart - Preventive Health Intelligence for Grocery Shopping
AI-powered platform that analyzes products for your specific health conditions
"""

import streamlit as st
import yaml
import uuid
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.models import Cart, HealthProfile, Product, RiskScore
from src.data_layer.dynamodb_client import DynamoDBClient
from src.data_layer.bedrock_client import BedrockClient
from src.data_layer.cloudwatch_client import CloudWatchClient
from src.business_logic.risk_scoring_engine import RiskScoringEngine
from src.business_logic.cart_intelligence import CartIntelligence
from src.business_logic.explanation_generator import ExplanationGenerator
from src.langchain_rag import create_rag_pipeline

def load_config():
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        config['aws']['region'] = os.getenv('AWS_REGION', config['aws']['region'])
        config['aws']['s3']['bucket_name'] = os.getenv('AWS_S3_BUCKET', config['aws']['s3']['bucket_name'])
        config['aws']['dynamodb']['table_name'] = os.getenv('AWS_DYNAMODB_TABLE', config['aws']['dynamodb']['table_name'])
        config['aws']['cloudwatch']['log_group'] = os.getenv('AWS_CLOUDWATCH_LOG_GROUP', config['aws']['cloudwatch']['log_group'])
        config['aws']['bedrock']['model_id'] = os.getenv('AWS_BEDROCK_MODEL_ID', config['aws']['bedrock']['model_id'])
        config['aws']['bedrock']['embedding_model_id'] = os.getenv('AWS_BEDROCK_EMBEDDING_MODEL_ID', config['aws']['bedrock']['embedding_model_id'])
        config['aws']['bedrock']['timeout'] = int(os.getenv('AWS_BEDROCK_TIMEOUT', config['aws']['bedrock']['timeout']))
        config['app']['session_ttl_hours'] = int(os.getenv('APP_SESSION_TTL_HOURS', config['app']['session_ttl_hours']))
        config['app']['max_products_display'] = int(os.getenv('APP_MAX_PRODUCTS_DISPLAY', config['app']['max_products_display']))
        return config
    except Exception as e:
        st.error(f"Config error: {str(e)}")
        st.stop()

PRODUCT_IMAGES_DIR = "product_images"

def load_local_products():
    try:
        with open('data/products.json', 'r') as f:
            data = json.load(f)
        products = []
        for p in data.get('products', []):
            folder = p.get('folder', '')
            display_path = os.path.join(PRODUCT_IMAGES_DIR, folder, p.get('display_image', ''))
            ingredients_path = os.path.join(PRODUCT_IMAGES_DIR, folder, p.get('ingredients_image', ''))
            products.append(Product(
                product_id=p['product_id'], name=p['name'], price=p['price'],
                display_image=display_path,
                ingredients_image=ingredients_path,
                ingredients=p['ingredients'],
                sodium_mg=p['sodium_mg'], sugar_g=p['sugar_g'],
                has_preservatives=p['has_preservatives'], category=p['category'],
                allergens=p.get('allergens', [])
            ))
        return products
    except Exception as e:
        print(f"ERROR loading products: {e}")
        return []

def initialize_clients(config):
    try:
        aws = config['aws']
        credentials = {}
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        if aws_access_key and aws_secret_key:
            credentials = {'aws_access_key_id': aws_access_key, 'aws_secret_access_key': aws_secret_key}
        bedrock_cfg = aws['bedrock']
        return {
            'dynamodb': DynamoDBClient(table_name=aws['dynamodb']['table_name'], region=aws['region'], ttl_hours=config['app']['session_ttl_hours'], **credentials),
            'bedrock': BedrockClient(
                region=aws['region'],
                model_id=bedrock_cfg['model_id'],
                embedding_model_id=bedrock_cfg['embedding_model_id'],
                timeout=bedrock_cfg['timeout'],
                vision_model_id=bedrock_cfg.get('vision_model_id'),
                text_model_id=bedrock_cfg.get('text_model_id'),
                vision_region=bedrock_cfg.get('vision_region'),
                text_region=bedrock_cfg.get('text_region'),
                **credentials
            ),
            'cloudwatch': CloudWatchClient(region=aws['region'], log_group=aws['cloudwatch']['log_group'], **credentials),
        }
    except Exception:
        return None

def initialize_business_logic(clients):
    bedrock = clients['bedrock'] if clients else None
    rse = RiskScoringEngine(bedrock)
    return {
        'risk_scoring': rse,
        'cart_intelligence': CartIntelligence(rse),
        'explanation_generator': ExplanationGenerator(bedrock),
    }

def init_state(config):
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'cart' not in st.session_state:
        st.session_state.cart = Cart()
    if 'health_profile' not in st.session_state:
        st.session_state.health_profile = HealthProfile(mode="Individual", conditions=[])
    if 'order_placed' not in st.session_state:
        st.session_state.order_placed = False
    if 'swasth_mode' not in st.session_state:
        st.session_state.swasth_mode = False
    if 'page' not in st.session_state:
        st.session_state.page = "browse"

    st.session_state.products = load_local_products()[:config['app']['max_products_display']]

    if 'risk_scores' not in st.session_state:
        st.session_state.risk_scores = {}
    if 'rag_chain' not in st.session_state:
        rag_chain, agent_graph = create_rag_pipeline()
        st.session_state.rag_chain = rag_chain
        st.session_state.agent_graph = agent_graph


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LIGHT THEME CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Poppins:wght@600;700;800;900&family=Outfit:wght@700;800;900&family=Lobster&display=swap');

body, p, div, li, td, th, input, textarea, select, button, label, h1, h2, h3, h4, h5, h6, a {
    font-family: 'Inter', sans-serif !important;
}
span:not([data-testid="stIconMaterial"]):not(.material-symbols-outlined):not(.material-symbols-rounded):not(.material-icons) {
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stIconMaterial"],
[data-testid="stIcon"],
[data-testid="stExpanderToggleIcon"] span,
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarContent"] [data-testid="stIconMaterial"],
.material-symbols-outlined,
.material-symbols-rounded,
.material-icons,
.streamlit-expanderHeader span[data-testid] {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
}
#MainMenu, footer, .stDeployButton, header { visibility: hidden; display: none; }

.stApp {
    background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 50%, #ecfdf5 100%);
    background-attachment: fixed;
}
body {
    background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 50%, #ecfdf5 100%) !important;
}

section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(255,255,255,0.1) !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.15) !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stMarkdown li {
    color: #ffffff !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
section[data-testid="stSidebar"] .stCaption {
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.85rem !important;
}
section[data-testid="stSidebar"] .stCheckbox label span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stToggle label span,
section[data-testid="stSidebar"] .stToggle label p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label {
    color: #6ee7b7 !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
}
section[data-testid="stSidebar"] .stMultiSelect > div > div,
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.15) !important;
    backdrop-filter: blur(10px) !important;
    border-color: rgba(255,255,255,0.25) !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    font-size: 0.9rem !important;
}
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: rgba(255,255,255,0.25) !important;
    color: #ffffff !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
}

.stButton > button {
    background: linear-gradient(135deg, rgba(16,185,129,0.85) 0%, rgba(5,150,105,0.9) 100%) !important;
    backdrop-filter: blur(12px) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 14px !important;
    padding: 0.65rem 1.5rem !important;
    font-weight: 900 !important;
    font-size: 0.92rem !important;
    box-shadow: 0 4px 16px rgba(16,185,129,0.25), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    text-shadow: 0 1px 3px rgba(0,0,0,0.15) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    background: linear-gradient(135deg, rgba(5,150,105,0.95) 0%, rgba(4,120,87,1) 100%) !important;
    box-shadow: 0 8px 28px rgba(16,185,129,0.4), inset 0 1px 0 rgba(255,255,255,0.25) !important;
    border-color: rgba(255,255,255,0.35) !important;
}

/* Sidebar buttons - white glass */
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.18) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.2) !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.3) !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.3) !important;
    border-color: rgba(255,255,255,0.45) !important;
}

div[data-testid="stImage"] > img {
    border-radius: 12px !important;
}

/* Product card image fixed height */
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stImage"] > img {
    height: 180px !important;
    width: 100% !important;
    object-fit: contain !important;
    background: #fafafa;
    border-radius: 10px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
    border-color: #e5e7eb !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 8px 24px rgba(16,185,129,0.12) !important;
    transform: translateY(-3px);
}

div[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    display: flex !important;
    flex-direction: column !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}
/* Push Add to Cart button to bottom of card */
div[data-testid="stVerticalBlockBorderWrapper"] > div > div {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] .stButton {
    margin-top: auto !important;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, rgba(245,158,11,0.85) 0%, rgba(217,119,6,0.9) 100%) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    box-shadow: 0 4px 16px rgba(245,158,11,0.3), inset 0 1px 0 rgba(255,255,255,0.25) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(135deg, rgba(217,119,6,0.95) 0%, rgba(180,83,9,1) 100%) !important;
    box-shadow: 0 8px 28px rgba(245,158,11,0.45), inset 0 1px 0 rgba(255,255,255,0.3) !important;
    border-color: rgba(255,255,255,0.4) !important;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #d1fae5;
    border-radius: 20px;
    padding: 1.5rem !important;
    box-shadow: 0 4px 16px rgba(16,185,129,0.08);
}
[data-testid="stMetricValue"] {
    color: #059669 !important;
    font-weight: 900 !important;
    font-size: 2.2rem !important;
}
[data-testid="stMetricLabel"] {
    color: #6b7280 !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-size: 0.75rem !important;
}

h1, h2, h3 {
    font-family: 'Poppins', sans-serif !important;
    color: #064e3b !important;
    -webkit-text-fill-color: #064e3b !important;
    font-weight: 900 !important;
}
h4, h5 { color: #1f2937 !important; font-weight: 700 !important; }
p, span, li, div { color: #374151; }
hr { border-color: #d1fae5 !important; }

[data-testid="column"] { background: transparent !important; box-shadow: none !important; padding: 0 !important; }
[data-testid="column"]:hover { transform: none !important; }

.streamlit-expanderHeader {
    background: white !important;
    border-radius: 16px !important;
    border: 1px solid #d1fae5 !important;
    box-shadow: 0 2px 8px rgba(16,185,129,0.08) !important;
}
.streamlit-expanderHeader p, .streamlit-expanderHeader span {
    color: #1f2937 !important;
    font-weight: 600 !important;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #34d399, #10b981, #059669) !important;
}

.stSelectbox > div > div, .stMultiSelect > div > div {
    background: white !important;
    border: 1px solid #d1fae5 !important;
    color: #1f2937 !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 8px rgba(16,185,129,0.08) !important;
}

.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; }
.stTabs [data-baseweb="tab"] {
    background: white !important;
    border-radius: 16px !important;
    color: #6b7280 !important;
    border: 1px solid #d1fae5 !important;
    padding: 10px 24px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    transition: all 0.3s ease !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important;
    box-shadow: 0 8px 24px rgba(16,185,129,0.35) !important;
    transform: translateY(-2px) !important;
}

.stAlert { border-radius: 16px !important; border: 1px solid #d1fae5 !important; }

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #f0fdf4; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #34d399, #10b981);
    border-radius: 10px;
}

.stToast { border-radius: 16px !important; box-shadow: 0 8px 32px rgba(0,0,0,0.15) !important; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 50%, #ecfdf5 100%) !important;
}

@keyframes successPulse {
    0%, 100% { transform: scale(1); box-shadow: 0 12px 40px rgba(16,185,129,0.4); }
    50% { transform: scale(1.05); box-shadow: 0 16px 56px rgba(16,185,129,0.6); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.stApp > div { animation: fadeInUp 0.5s ease-out; }

</style>
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PRODUCT CARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CATEGORY_EMOJI = {
    'beverages': '🥤', 'dairy': '🥛', 'snacks': '🍪', 'grains': '🌾',
    'frozen': '🧊', 'cooking': '🫒',
}

def render_product_card(product, risk_score=None):
    emoji = CATEGORY_EMOJI.get(product.category, '🍽️')

    with st.container(border=True):
        img1, img2 = st.columns(2, gap="small")
        with img1:
            st.image(product.display_image, use_container_width=True)
        with img2:
            st.image(product.ingredients_image, use_container_width=True)

        st.caption(f"{emoji} {product.category.upper()}")
        st.markdown(f"**{product.name}**")
        st.markdown(f"### :green[₹{product.price:.0f}]")

        info = f"Sodium {product.sodium_mg:.0f}mg · Sugar {product.sugar_g}g"
        if product.has_preservatives:
            info += " · :red[Preservatives]"
        st.caption(info)

        if risk_score:
            if risk_score.value <= 40:
                st.success(f"SAFE  {risk_score.value:.0f}/100", icon="✅")
            elif risk_score.value <= 70:
                st.warning(f"CAUTION  {risk_score.value:.0f}/100", icon="⚠️")
            else:
                st.error(f"AVOID  {risk_score.value:.0f}/100", icon="🚫")

        # Check if already in cart
        in_cart = any(item.product.product_id == product.product_id for item in st.session_state.cart.items)
        if in_cart:
            st.success("In Cart", icon="✅")
        else:
            if st.button("Add to Cart", key=f"add_{product.product_id}", use_container_width=True, type="primary"):
                try:
                    st.session_state.cart = st.session_state.business_logic['cart_intelligence'].add_product(
                        st.session_state.cart, product, st.session_state.health_profile
                    )
                except Exception:
                    # Fallback: add with default risk score
                    from src.models import CartItem
                    risk = st.session_state.risk_scores.get(product.product_id, RiskScore(value=30, badge="🟢", reasoning="Default assessment"))
                    st.session_state.cart.items.append(CartItem(product=product, risk_score=risk))
                st.rerun()

    if risk_score:
        with st.expander(f"{risk_score.badge} {product.name} - Risk Analysis"):
            st.progress(min(risk_score.value / 100, 1.0))
            st.markdown(f"**{risk_score.risk_level}** for your health profile")
            st.markdown(risk_score.reasoning)
            st.caption(f"Ingredients: {', '.join(product.ingredients[:6])}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: BROWSE PRODUCTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_browse_page():
    cart = st.session_state.cart

    # Hero Banner (only when cart is empty and no health mode)
    if not cart.items and not st.session_state.swasth_mode:
        import base64
        with open("groceries.JPG", "rb") as img_file:
            hero_b64 = base64.b64encode(img_file.read()).decode()
        st.markdown(f"""
        <div style="
            position:relative;
            border-radius:24px;
            overflow:hidden;
            margin-bottom:1.5rem;
            box-shadow:0 12px 40px rgba(0,0,0,0.15);
            height:300px;
        ">
            <img src="data:image/jpeg;base64,{hero_b64}" style="
                width:100%;height:100%;object-fit:cover;
                filter:brightness(0.45);
            "/>
            <div style="
                position:absolute;top:0;left:0;right:0;bottom:0;
                background:linear-gradient(135deg, rgba(6,78,59,0.7) 0%, rgba(5,150,105,0.4) 100%);
            "></div>
            <div style="
                position:absolute;top:0;left:0;right:0;bottom:0;
                display:flex;flex-direction:column;justify-content:center;
                padding:2.5rem 3rem;
            ">
                <div style="font-family:'Lobster',cursive;font-size:3.2rem;color:white;line-height:1.2;margin-bottom:0.5rem;
                    text-shadow:
                        0 2px 0 rgba(5,150,105,0.6),
                        0 4px 0 rgba(4,120,87,0.4),
                        0 6px 12px rgba(0,0,0,0.3);">
                    Shop Smart. Eat Right.<br>Live Healthy.
                </div>
                <div style="font-size:1rem;color:rgba(255,255,255,0.9);font-weight:500;max-width:550px;line-height:1.6;margin-bottom:1.2rem;">
                    AI-powered preventive health intelligence that analyzes every grocery product for your specific health conditions.
                </div>
                <div style="display:flex;gap:10px;flex-wrap:wrap;">
                    <span style="background:rgba(255,255,255,0.2);backdrop-filter:blur(8px);color:white;padding:8px 18px;border-radius:30px;font-size:0.78rem;font-weight:700;border:1px solid rgba(255,255,255,0.3);">🧠 AI Vision Analysis</span>
                    <span style="background:rgba(255,255,255,0.2);backdrop-filter:blur(8px);color:white;padding:8px 18px;border-radius:30px;font-size:0.78rem;font-weight:700;border:1px solid rgba(255,255,255,0.3);">🎯 Risk Scoring</span>
                    <span style="background:rgba(255,255,255,0.2);backdrop-filter:blur(8px);color:white;padding:8px 18px;border-radius:30px;font-size:0.78rem;font-weight:700;border:1px solid rgba(255,255,255,0.3);">💚 Smart Alternatives</span>
                    <span style="background:rgba(255,255,255,0.2);backdrop-filter:blur(8px);color:white;padding:8px 18px;border-radius:30px;font-size:0.78rem;font-weight:700;border:1px solid rgba(255,255,255,0.3);">🇮🇳 Indian Products</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Header with status
    hcol1, hcol2 = st.columns([3, 1])
    with hcol1:
        if st.session_state.swasth_mode and st.session_state.health_profile.conditions:
            cstr = ', '.join(st.session_state.health_profile.conditions)
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <span style="font-family:'Poppins',sans-serif;font-size:2rem;font-weight:900;color:#064e3b;">AI Health Intelligence</span>
                <span style="background:linear-gradient(135deg,#10b981,#059669);color:white;padding:6px 16px;border-radius:20px;font-size:0.72rem;font-weight:800;margin-left:12px;vertical-align:middle;letter-spacing:0.8px;box-shadow:0 4px 12px rgba(16,185,129,0.3);">ACTIVE</span>
            </div>
            <div style="font-size:0.88rem;color:#64748b;font-weight:500;">Analyzing products for: <strong style="color:#059669;">{cstr}</strong></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="margin-bottom:6px;">
                <span style="font-family:'Poppins',sans-serif;font-size:2rem;font-weight:900;color:#064e3b;">Browse Products</span>
            </div>
            <div style="font-size:0.88rem;color:#64748b;font-weight:500;">Enable Swasth Mode for AI-powered preventive health analysis</div>
            """, unsafe_allow_html=True)

    with hcol2:
        if cart.items:
            st.markdown(f"""<div style="text-align:right;padding-top:12px;">
                <span style="background:#f0fdf4;border:1px solid #d1fae5;padding:8px 16px;border-radius:14px;font-size:0.9rem;font-weight:700;color:#059669;">
                    🛍️ {len(cart.items)} items &middot; ₹{cart.total_price:.0f}
                </span>
            </div>""", unsafe_allow_html=True)

    # Stats
    if st.session_state.swasth_mode and st.session_state.risk_scores:
        safe = sum(1 for r in st.session_state.risk_scores.values() if r.value <= 40)
        caution = sum(1 for r in st.session_state.risk_scores.values() if 41 <= r.value <= 70)
        avoid = sum(1 for r in st.session_state.risk_scores.values() if r.value > 70)
        total = len(st.session_state.risk_scores)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("📦 Products", total)
        with c2:
            st.metric("✅ Safe", safe)
        with c3:
            st.metric("⚠️ Caution", caution)
        with c4:
            st.metric("❌ Avoid", avoid)

    st.markdown("---")

    # Category Filter
    st.markdown('<div style="font-size:0.75rem;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">Filter by Category</div>', unsafe_allow_html=True)

    products = st.session_state.products
    categories = sorted(set(p.category for p in products))
    cat_labels = ["All Products"] + [f"{CATEGORY_EMOJI.get(c, '')} {c.title()}" for c in categories]

    selected_cat = st.radio("Filter", cat_labels, horizontal=True, label_visibility="collapsed", key="cat_filter")

    if selected_cat != "All Products":
        cat_val = selected_cat.split(" ", 1)[1].lower() if " " in selected_cat else selected_cat.lower()
        products = [p for p in products if p.category == cat_val]

    # Product Grid – manually ordered so similar-height images share a row
    swasth_active = st.session_state.swasth_mode and bool(st.session_state.risk_scores)

    # Preferred display order (square images first, taller images last)
    _PREFERRED_ORDER = [
        'prod_006', 'prod_007', 'prod_009',  # Row 1: Epigamia, Maggi, McCain (square)
        'prod_010', 'prod_011', 'prod_012',  # Row 2: Amul Ice Cream, Tata Sampann, Coca-Cola (square)
        'prod_003', 'prod_004', 'prod_013',  # Row 3: Lays, Good Day, MTR Rava Idli (square)
        'prod_005', 'prod_008', 'prod_001',  # Row 4: Aashirvaad, Kelloggs, Tropicana
    ]
    _order_map = {pid: idx for idx, pid in enumerate(_PREFERRED_ORDER)}
    products = sorted(products, key=lambda p: _order_map.get(p.product_id, 999))

    cols_per_row = 3
    for i in range(0, len(products), cols_per_row):
        cols = st.columns(cols_per_row, gap="medium")
        for j, col in enumerate(cols):
            if i + j < len(products):
                product = products[i + j]
                risk = st.session_state.risk_scores.get(product.product_id) if swasth_active else None
                with col:
                    render_product_card(product, risk)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: CART
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_cart_page():
    cart = st.session_state.cart

    if not cart.items:
        st.markdown("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align:center;padding:3rem 0;">
                <div style="font-size:4rem;margin-bottom:1rem;">🛍️</div>
                <h2 style="font-family:'Poppins',sans-serif;color:#064e3b !important;-webkit-text-fill-color:#064e3b !important;">Your cart is empty</h2>
                <p style="color:#64748b;font-size:1rem;margin-bottom:2rem;">Browse our products and add healthy items to your cart</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🏪 Browse Products", key="empty_cart_browse", use_container_width=True):
                st.session_state.page = "browse"
                st.rerun()
        return

    st.markdown('<h3 style="font-family:Poppins,sans-serif;font-size:1.8rem;font-weight:900;color:#064e3b !important;-webkit-text-fill-color:#064e3b !important;margin-bottom:1rem;">🛍️ Your Cart</h3>', unsafe_allow_html=True)

    # Health Score + Total summary bar
    hs = cart.health_score
    st.markdown(f"""
    <div style="background:white;border:1px solid #d1fae5;border-radius:20px;padding:20px 24px;margin-bottom:18px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 8px 32px rgba(16,185,129,0.12);">
        <div>
            <div style="font-size:0.7rem;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Cart Health Score</div>
            <div style="font-size:2.2rem;font-weight:900;color:#059669;">{hs:.0f}<span style="font-size:1rem;color:#94a3b8;font-weight:500;">/100</span></div>
        </div>
        <div style="text-align:center;">
            <div style="font-size:0.7rem;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Items</div>
            <div style="font-size:2.2rem;font-weight:900;color:#1e293b;">{len(cart.items)}</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:0.7rem;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Total</div>
            <div style="font-size:2.2rem;font-weight:900;color:#1e293b;">₹{cart.total_price:.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Cart items
    for item in cart.items:
        rv = item.risk_score.value
        rc = "#059669" if rv <= 40 else "#d97706" if rv <= 70 else "#dc2626"

        with st.container(border=True):
            ic1, ic2, ic3, ic4 = st.columns([1, 3, 2, 1])
            with ic1:
                if os.path.exists(item.product.display_image):
                    st.image(item.product.display_image, use_container_width=True)
            with ic2:
                st.markdown(f"**{item.product.name}**")
                st.caption(f"{CATEGORY_EMOJI.get(item.product.category, '')} {item.product.category.title()} · Na: {item.product.sodium_mg:.0f}mg · Sugar: {item.product.sugar_g}g")
            with ic3:
                st.markdown(f"### ₹{item.product.price:.0f}")
                st.markdown(f'<span style="color:{rc};font-weight:800;font-size:0.9rem;">{item.risk_score.badge} Risk: {rv:.0f}/100</span>', unsafe_allow_html=True)
            with ic4:
                st.markdown("")
                if st.button("❌", key=f"rm_{item.product.product_id}", help="Remove from cart"):
                    st.session_state.cart = st.session_state.business_logic['cart_intelligence'].remove_product(
                        st.session_state.cart, item.product.product_id
                    )
                    st.rerun()

    st.markdown("---")

    # Healthier Alternatives
    if st.session_state.health_profile.conditions and cart.high_risk_count > 0:
        with st.expander("💡 Healthier Alternatives"):
            suggestions = st.session_state.business_logic['cart_intelligence'].suggest_improvements(
                cart, st.session_state.products, st.session_state.health_profile
            )
            if suggestions:
                for s in suggestions[:3]:
                    st.markdown(f"**{s.original_product.name}** ➜ **{s.suggested_product.name}** *(-{s.risk_reduction:.0f}% risk)*")
            else:
                st.success("Your cart looks healthy!")

    # Action buttons
    st.markdown("")
    bcol1, bcol2, bcol3 = st.columns([1, 2, 1])
    with bcol1:
        if st.button("🏪 Continue Shopping", key="continue_shopping_btn", use_container_width=True):
            st.session_state.page = "browse"
            st.rerun()
    with bcol2:
        st.markdown(f"""
        <div style="background:white;border:1px solid #d1fae5;border-radius:16px;padding:16px;text-align:center;margin-bottom:8px;">
            <div style="font-size:0.7rem;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Order Total</div>
            <div style="font-size:2rem;font-weight:900;color:#059669;">₹{cart.total_price:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"💳 Place Order  ·  ₹{cart.total_price:.0f}", key="pay_btn", use_container_width=True, type="primary"):
            st.session_state.order_placed = True
            st.session_state.page = "order_placed"
            st.rerun()
    with bcol3:
        if st.button("🗑️ Clear Cart", key="clear_cart_btn", use_container_width=True):
            st.session_state.cart = Cart()
            st.session_state.page = "browse"
            st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: ORDER PLACED
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_order_placed():
    cart = st.session_state.cart

    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/logo.png", width=120)

        st.markdown(f"""
        <div style="text-align:center;padding:1rem 0;">
            <div style="
                width:100px;height:100px;border-radius:50%;
                background:linear-gradient(135deg,#10b981,#059669);
                display:flex;align-items:center;justify-content:center;
                margin:0 auto 1.5rem;font-size:3rem;color:white;
                box-shadow:0 12px 40px rgba(16,185,129,0.4);
                animation: successPulse 2s ease-in-out infinite;
            ">&#10003;</div>
            <h1 style="font-family:'Lobster',cursive !important;font-size:3rem;margin-bottom:0.5rem;color:#064e3b !important;-webkit-text-fill-color:#064e3b !important;
                text-shadow:0 2px 0 rgba(5,150,105,0.2), 0 4px 8px rgba(0,0,0,0.08);">Order Placed!</h1>
            <p style="font-family:'Lobster',cursive;font-size:1.4rem;color:#059669;margin-bottom:0.5rem;">
                Shop Smart. Eat Right. Live Healthy.
            </p>
            <p style="color:#64748b;margin-bottom:2rem;font-weight:500;">Your healthy groceries are on the way</p>
            <div style="
                background:white;border:1px solid #d1fae5;border-radius:24px;
                padding:2rem;text-align:left;box-shadow:0 8px 32px rgba(16,185,129,0.12);
            ">
                <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                    <span style="color:#94a3b8;font-weight:600;">Order ID</span>
                    <span style="color:#1e293b;font-weight:800;">#{st.session_state.session_id[:8].upper()}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                    <span style="color:#94a3b8;font-weight:600;">Items</span>
                    <span style="color:#1e293b;font-weight:800;">{len(cart.items)}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                    <span style="color:#94a3b8;font-weight:600;">Health Score</span>
                    <span style="color:#059669;font-weight:900;">{cart.health_score:.0f}/100</span>
                </div>
                <hr style="border-color:rgba(209,250,229,0.5);margin:16px 0;">
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:#1e293b;font-weight:900;font-size:1.1rem;">Total Paid</span>
                    <span style="color:#059669;font-weight:900;font-size:1.5rem;">₹{cart.total_price:.0f}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Order items summary
        with st.expander(f"📦 Order Items ({len(cart.items)})"):
            for item in cart.items:
                st.markdown(f"**{item.product.name}** — ₹{item.product.price:.0f} {item.risk_score.badge}")

        st.markdown(f"""
        <div style="margin-top:1rem;background:#f0fdf4;border:1px solid #d1fae5;border-radius:16px;padding:14px;color:#047857;font-weight:700;font-size:0.88rem;text-align:center;">
            🧠 SwasthCart — Preventive Health Intelligence Powered by AWS Bedrock
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        if st.button("🏪 Continue Shopping", key="continue_btn", use_container_width=True):
            st.session_state.order_placed = False
            st.session_state.cart = Cart()
            st.session_state.page = "browse"
            st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: ROADMAP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_roadmap_page():
    st.markdown("""
    <div style="text-align:center;margin-bottom:2rem;">
        <div style="font-family:'Poppins',sans-serif;font-size:0.75rem;font-weight:800;text-transform:uppercase;
            letter-spacing:3px;color:#10b981;margin-bottom:8px;">What's Next</div>
        <div style="font-family:'Poppins',sans-serif;font-size:2.2rem;font-weight:900;color:#064e3b;">
            SwasthCart Roadmap</div>
        <div style="font-size:0.95rem;color:#64748b;margin-top:6px;">
            From app to ecosystem — our vision for preventive health in grocery shopping</div>
    </div>
    """, unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3, gap="large")

    with r1:
        st.markdown("""
        <div style="background:white;border-radius:20px;padding:30px 24px;text-align:center;
            box-shadow:0 4px 20px rgba(0,0,0,0.06);border:1px solid rgba(16,185,129,0.15);height:100%;">
            <div style="width:64px;height:64px;background:linear-gradient(135deg,#d1fae5,#a7f3d0);
                border-radius:16px;display:flex;align-items:center;justify-content:center;
                margin:0 auto 16px;font-size:1.8rem;">🧩</div>
            <div style="font-family:'Poppins',sans-serif;font-weight:800;font-size:1.1rem;color:#064e3b;margin-bottom:8px;">
                Chrome Extension</div>
            <div style="font-size:0.85rem;color:#64748b;line-height:1.6;">
                A browser plugin for <b>Amazon Fresh</b>, <b>BigBasket</b> & <b>JioMart</b>.
                Get real-time health risk badges overlaid on product cards while you shop online.
                No app switching needed.</div>
            <div style="margin-top:16px;display:inline-block;background:#ecfdf5;color:#059669;font-size:0.72rem;
                font-weight:800;padding:5px 14px;border-radius:20px;text-transform:uppercase;letter-spacing:1px;">
                Phase 1</div>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        st.markdown("""
        <div style="background:white;border-radius:20px;padding:30px 24px;text-align:center;
            box-shadow:0 4px 20px rgba(0,0,0,0.06);border:1px solid rgba(16,185,129,0.15);height:100%;">
            <div style="width:64px;height:64px;background:linear-gradient(135deg,#dbeafe,#bfdbfe);
                border-radius:16px;display:flex;align-items:center;justify-content:center;
                margin:0 auto 16px;font-size:1.8rem;">📱</div>
            <div style="font-family:'Poppins',sans-serif;font-weight:800;font-size:1.1rem;color:#064e3b;margin-bottom:8px;">
                Mobile App</div>
            <div style="font-size:0.85rem;color:#64748b;line-height:1.6;">
                Scan product <b>barcodes in-store</b> with your phone camera.
                Instant AI-powered ingredient analysis and health risk scoring.
                Works offline with cached product database.</div>
            <div style="margin-top:16px;display:inline-block;background:#eff6ff;color:#2563eb;font-size:0.72rem;
                font-weight:800;padding:5px 14px;border-radius:20px;text-transform:uppercase;letter-spacing:1px;">
                Phase 2</div>
        </div>
        """, unsafe_allow_html=True)

    with r3:
        st.markdown("""
        <div style="background:white;border-radius:20px;padding:30px 24px;text-align:center;
            box-shadow:0 4px 20px rgba(0,0,0,0.06);border:1px solid rgba(16,185,129,0.15);height:100%;">
            <div style="width:64px;height:64px;background:linear-gradient(135deg,#fef3c7,#fde68a);
                border-radius:16px;display:flex;align-items:center;justify-content:center;
                margin:0 auto 16px;font-size:1.8rem;">🤝</div>
            <div style="font-family:'Poppins',sans-serif;font-weight:800;font-size:1.1rem;color:#064e3b;margin-bottom:8px;">
                Doctor Integration</div>
            <div style="font-size:0.85rem;color:#64748b;line-height:1.6;">
                Share your <b>grocery health reports</b> directly with doctors.
                Get personalized diet recommendations synced with your prescriptions
                and medical history.</div>
            <div style="margin-top:16px;display:inline-block;background:#fffbeb;color:#d97706;font-size:0.72rem;
                font-weight:800;padding:5px 14px;border-radius:20px;text-transform:uppercase;letter-spacing:1px;">
                Phase 3</div>
        </div>
        """, unsafe_allow_html=True)

    # Tech stack highlight
    st.markdown("")
    st.markdown("""
    <div style="background:linear-gradient(135deg, rgba(6,78,59,0.06) 0%, rgba(16,185,129,0.08) 100%);
        border:1px solid rgba(16,185,129,0.2);border-radius:20px;padding:2rem;text-align:center;margin-top:1rem;">
        <div style="font-family:'Poppins',sans-serif;font-weight:800;font-size:1rem;color:#064e3b;margin-bottom:16px;">
            Built With</div>
        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:12px;">
            <span style="background:rgba(255,153,0,0.12);color:#d97706;padding:8px 18px;border-radius:12px;font-size:0.82rem;font-weight:700;border:1px solid rgba(255,153,0,0.2);">AWS Bedrock</span>
            <span style="background:rgba(255,153,0,0.12);color:#d97706;padding:8px 18px;border-radius:12px;font-size:0.82rem;font-weight:700;border:1px solid rgba(255,153,0,0.2);">Amazon S3</span>
            <span style="background:rgba(255,153,0,0.12);color:#d97706;padding:8px 18px;border-radius:12px;font-size:0.82rem;font-weight:700;border:1px solid rgba(255,153,0,0.2);">DynamoDB</span>
            <span style="background:rgba(255,153,0,0.12);color:#d97706;padding:8px 18px;border-radius:12px;font-size:0.82rem;font-weight:700;border:1px solid rgba(255,153,0,0.2);">CloudWatch</span>
            <span style="background:rgba(16,185,129,0.12);color:#059669;padding:8px 18px;border-radius:12px;font-size:0.82rem;font-weight:700;border:1px solid rgba(16,185,129,0.2);">LangChain</span>
            <span style="background:rgba(16,185,129,0.12);color:#059669;padding:8px 18px;border-radius:12px;font-size:0.82rem;font-weight:700;border:1px solid rgba(16,185,129,0.2);">LangGraph</span>
            <span style="background:rgba(16,185,129,0.12);color:#059669;padding:8px 18px;border-radius:12px;font-size:0.82rem;font-weight:700;border:1px solid rgba(16,185,129,0.2);">FAISS</span>
            <span style="background:rgba(99,102,241,0.12);color:#6366f1;padding:8px 18px;border-radius:12px;font-size:0.82rem;font-weight:700;border:1px solid rgba(99,102,241,0.2);">Streamlit</span>
            <span style="background:rgba(99,102,241,0.12);color:#6366f1;padding:8px 18px;border-radius:12px;font-size:0.82rem;font-weight:700;border:1px solid rgba(99,102,241,0.2);">Claude Vision</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_sidebar():
    with st.sidebar:
        import base64
        with open("groceries.JPG", "rb") as img_file:
            sidebar_b64 = base64.b64encode(img_file.read()).decode()
        with open("assets/logo.png", "rb") as logo_file:
            logo_b64 = base64.b64encode(logo_file.read()).decode()

        # Set groceries as full sidebar background
        st.markdown(f"""
        <style>
            section[data-testid="stSidebar"] > div:first-child {{
                background: linear-gradient(180deg, rgba(6,78,59,0.85) 0%, rgba(5,150,105,0.75) 50%, rgba(6,78,59,0.9) 100%),
                            url("data:image/jpeg;base64,{sidebar_b64}") center/cover no-repeat !important;
            }}
        </style>
        """, unsafe_allow_html=True)

        # Logo + branding header
        st.markdown(f"""
        <div style="text-align:center;padding:1rem 0 1.2rem;">
            <img src="data:image/png;base64,{logo_b64}" style="width:180px;height:180px;object-fit:contain;margin-bottom:14px;filter:drop-shadow(0 8px 24px rgba(0,0,0,0.5));"/>
            <div style="font-family:'Lobster',cursive;font-size:2.6rem;color:white;
                text-shadow:
                    0 2px 0 rgba(5,150,105,0.8),
                    0 4px 0 rgba(4,120,87,0.6),
                    0 6px 0 rgba(6,78,59,0.4),
                    0 8px 16px rgba(0,0,0,0.3);
                letter-spacing:1px;">SwasthCart</div>
            <div style="font-family:'Outfit',sans-serif;font-size:0.7rem;font-weight:700;color:rgba(255,255,255,0.85);letter-spacing:3px;text-transform:uppercase;margin-top:8px;">Preventive Health Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        nav1, nav2 = st.columns(2)
        with nav1:
            if st.button("🏠 Home", key="nav_browse", use_container_width=True):
                st.session_state.page = "browse"
                st.rerun()
        with nav2:
            cart_nav = st.session_state.cart
            item_count = len(cart_nav.items)
            cart_label = f"Cart ({item_count})" if item_count > 0 else "Cart"
            if st.button(cart_label, key="nav_cart", use_container_width=True):
                st.session_state.page = "cart"
                st.rerun()
        if st.button("🚀 Roadmap", key="nav_roadmap", use_container_width=True):
            st.session_state.page = "roadmap"
            st.rerun()

        st.markdown("---")

        # Swasth Mode
        st.markdown('<div style="font-size:0.85rem;color:rgba(255,255,255,0.9);font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">🛒 AI Health Analysis</div>', unsafe_allow_html=True)
        swasth = st.toggle("Enable Health Intelligence", value=st.session_state.swasth_mode, key="swasth_toggle")
        st.session_state.swasth_mode = swasth

        if swasth:
            st.markdown('<div style="font-size:0.85rem;color:rgba(255,255,255,0.9);font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-top:16px;margin-bottom:8px;">Your Health Conditions</div>', unsafe_allow_html=True)

            all_conditions = [
                "Diabetes", "Hypertension", "Heart Disease", "Kidney Disease",
                "Obesity", "High Cholesterol", "Thyroid", "Liver Disease",
                "Celiac Disease", "Lactose Intolerance", "Gout", "IBS",
                "Depression", "Anxiety", "Osteoporosis", "Anemia"
            ]

            selected = st.multiselect("Conditions", all_conditions, default=st.session_state.health_profile.conditions, label_visibility="collapsed", key="conditions_select")
            st.session_state.health_profile = HealthProfile(mode="Individual", conditions=selected)

            if selected:
                ctext = ", ".join(selected)
                st.markdown(f'<div style="background:rgba(255,255,255,0.15);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.2);border-radius:10px;padding:12px 14px;font-size:0.88rem;color:white;font-weight:600;margin-top:8px;">🎯 Analyzing for: {ctext}</div>', unsafe_allow_html=True)

                if st.button("🧠 Run AI Analysis", key="analyze_btn", use_container_width=True):
                    bar = st.progress(0)
                    status = st.empty()
                    bedrock = st.session_state.clients['bedrock'] if st.session_state.clients else None
                    conditions_str = ", ".join(selected)

                    for idx, product in enumerate(st.session_state.products):
                        status.caption(f"Analyzing {product.name}...")

                        if bedrock and product.ingredients_image and os.path.exists(product.ingredients_image):
                            try:
                                vision_prompt = f"""You are a preventive health nutrition expert.
Analyze this ingredients label image for a person with: {conditions_str}.

Product: {product.name}
Category: {product.category}

Read the ingredients from the image carefully. Then:
1. Identify harmful ingredients for the given health conditions
2. Give a risk score from 0 (safe) to 100 (dangerous)
3. Explain in 2-3 sentences why

Respond ONLY in JSON:
{{"score": <0-100>, "reasoning": "<explanation>"}}"""

                                result = bedrock.analyze_image(
                                    product.ingredients_image, vision_prompt,
                                    max_tokens=400, temperature=0.3
                                )
                                score = float(result.get('score', 50))
                                reasoning = result.get('reasoning', 'AI vision analysis complete.')
                                score = min(100, max(0, score))
                                badge = "🟢" if score <= 40 else "🟡" if score <= 70 else "🔴"
                                risk = RiskScore(value=score, badge=badge, reasoning=reasoning)
                            except Exception as e:
                                print(f"Bedrock vision failed for {product.name}: {e}")
                                risk = st.session_state.business_logic['risk_scoring'].calculate_risk_score(
                                    product, st.session_state.health_profile, use_bedrock=False
                                )
                        else:
                            risk = st.session_state.business_logic['risk_scoring'].calculate_risk_score(
                                product, st.session_state.health_profile, use_bedrock=False
                            )

                        st.session_state.risk_scores[product.product_id] = risk
                        bar.progress((idx + 1) / len(st.session_state.products))

                    bar.empty()
                    status.empty()
                    st.rerun()
        else:
            st.session_state.risk_scores = {}
            st.markdown('<div style="background:rgba(255,255,255,0.1);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.15);border-radius:12px;padding:12px 14px;font-size:0.88rem;color:rgba(255,255,255,0.9);margin-top:8px;">💡 Enable to get personalized health risk scores for each product</div>', unsafe_allow_html=True)

        # Cart summary in sidebar
        cart = st.session_state.cart
        if cart.items:
            st.markdown("---")
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.12);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.2);border-radius:20px;padding:18px;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.1);">
                <div style="font-size:2rem;font-weight:900;color:white;">🛍️ {len(cart.items)}</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.75);margin-bottom:6px;font-weight:600;text-transform:uppercase;letter-spacing:1px;">items in cart</div>
                <div style="font-size:1.5rem;font-weight:900;color:#6ee7b7;">₹{cart.total_price:.0f}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")
            if st.button("View Cart & Pay", key="sidebar_cart_btn", use_container_width=True):
                st.session_state.page = "cart"
                st.rerun()

        st.markdown("---")

        # AWS status
        aws_ok = st.session_state.clients is not None
        dot = "🟢" if aws_ok else "🟡"
        label = "AWS Connected" if aws_ok else "Local Mode"
        st.caption(f"{dot} {label}")
        st.markdown("""
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;">
            <span style="background:rgba(255,153,0,0.3);backdrop-filter:blur(8px);color:white;padding:5px 12px;border-radius:8px;font-size:0.72rem;font-weight:700;border:1px solid rgba(255,153,0,0.4);">Bedrock</span>
            <span style="background:rgba(255,153,0,0.3);backdrop-filter:blur(8px);color:white;padding:5px 12px;border-radius:8px;font-size:0.72rem;font-weight:700;border:1px solid rgba(255,153,0,0.4);">S3</span>
            <span style="background:rgba(255,153,0,0.3);backdrop-filter:blur(8px);color:white;padding:5px 12px;border-radius:8px;font-size:0.72rem;font-weight:700;border:1px solid rgba(255,153,0,0.4);">DynamoDB</span>
            <span style="background:rgba(16,185,129,0.3);backdrop-filter:blur(8px);color:white;padding:5px 12px;border-radius:8px;font-size:0.72rem;font-weight:700;border:1px solid rgba(16,185,129,0.4);">LangChain</span>
            <span style="background:rgba(16,185,129,0.3);backdrop-filter:blur(8px);color:white;padding:5px 12px;border-radius:8px;font-size:0.72rem;font-weight:700;border:1px solid rgba(16,185,129,0.4);">LangGraph</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown('<div style="text-align:center;font-size:0.85rem;color:rgba(255,255,255,0.7);font-weight:600;">Team TrinityForge | Hack2Bharat 2025</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    st.set_page_config(page_title="SwasthCart - Preventive Health Intelligence", page_icon="🛒", layout="wide", initial_sidebar_state="expanded")

    st.markdown(CSS, unsafe_allow_html=True)

    config = load_config()
    if 'clients' not in st.session_state:
        st.session_state.clients = initialize_clients(config)
    if 'business_logic' not in st.session_state:
        st.session_state.business_logic = initialize_business_logic(st.session_state.clients)
    init_state(config)

    # Sidebar
    render_sidebar()

    # Page routing
    page = st.session_state.page

    if page == "order_placed" and st.session_state.order_placed:
        render_order_placed()
    elif page == "cart":
        render_cart_page()
    elif page == "roadmap":
        render_roadmap_page()
    else:
        render_browse_page()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 1rem;">
        <div style="font-family:'Lobster',cursive;font-size:1.8rem;color:#059669;margin-bottom:6px;
            text-shadow:0 1px 0 rgba(5,150,105,0.3), 0 2px 4px rgba(0,0,0,0.08);">SwasthCart</div>
        <div style="font-size:0.9rem;color:#64748b;font-weight:500;">
            Preventive Health Intelligence | Powered by AWS Bedrock | Team TrinityForge
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
