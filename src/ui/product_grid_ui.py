"""
Product Grid UI Component
"""

from typing import List, Callable
import streamlit as st

from src.models import Product, HealthProfile


class ProductGridUI:
    """Renders the 3-column product grid with modern cards"""
    
    def render(
        self,
        products: List[Product],
        swasth_mode: bool,
        health_profile: HealthProfile,
        on_add_to_cart: Callable[[Product], None],
        risk_scores: dict = None
    ) -> None:
        """Render product grid with risk badges if swasth_mode is enabled"""
        
        if not products:
            st.info("No products available")
            return
        
        st.markdown("---")
        st.markdown("### 🛍️ Browse Products")
        
        # Display products in 3-column grid
        cols_per_row = 3
        for i in range(0, len(products), cols_per_row):
            cols = st.columns(cols_per_row, gap="medium")
            
            for j, col in enumerate(cols):
                if i + j < len(products):
                    product = products[i + j]
                    with col:
                        self._render_product_card(
                            product,
                            swasth_mode,
                            on_add_to_cart,
                            risk_scores.get(product.product_id) if risk_scores else None
                        )
    
    def _render_product_card(
        self,
        product: Product,
        swasth_mode: bool,
        on_add_to_cart: Callable[[Product], None],
        risk_score=None
    ) -> None:
        """Render individual product card with modern styling"""
        
        # Card container
        with st.container():
            # Product image with fallback
            if product.image_url:
                st.image(product.image_url)
            else:
                # Use placeholder with product name
                st.image(f"https://via.placeholder.com/300x200/667eea/ffffff?text={product.name.replace(' ', '+')}")
            
            # Product name with risk badge
            if swasth_mode and risk_score:
                risk_class = f"risk-{risk_score.risk_level.lower().replace(' ', '-')}"
                st.markdown(f"""
                <div style="margin: 0.5rem 0;">
                    <strong style="font-size: 1.1rem;">{product.name}</strong>
                    <span class="risk-badge {risk_class}">{risk_score.badge}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"**{product.name}**")
            
            # Price and category
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"<p class='price'>₹{product.price:.2f}</p>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<span class='category'>{product.category}</span>", unsafe_allow_html=True)
            
            # Nutritional highlights
            if swasth_mode:
                st.caption(f"🧂 Sodium: {product.sodium_mg}mg | 🍬 Sugar: {product.sugar_g}g")
            
            # Add to cart button
            if st.button(f"🛒 Add to Cart", key=f"add_{product.product_id}", width='stretch', type="primary"):
                on_add_to_cart(product)
                st.success(f"✅ Added to cart!")
            
            # Detailed info expandable
            if swasth_mode and risk_score:
                with st.expander("📊 Why this score?"):
                    st.markdown(f"**Risk Level:** {risk_score.risk_level}")
                    st.progress(risk_score.value / 100)
                    st.markdown(f"**Score:** {risk_score.value:.0f}/100")
                    
                    # Detailed explanation
                    st.markdown("**Analysis:**")
                    st.write(risk_score.reasoning)
                    
                    # Ingredient breakdown
                    if product.ingredients:
                        st.markdown("**Key Ingredients:**")
                        for ing in product.ingredients[:5]:
                            st.write(f"• {ing}")
                    
                    # Nutritional facts
                    st.markdown("**Nutritional Facts:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Sodium", f"{product.sodium_mg}mg")
                        st.metric("Sugar", f"{product.sugar_g}g")
                    with col2:
                        st.metric("Preservatives", "Yes" if product.has_preservatives else "No")
                        st.metric("Allergens", len(product.allergens))
            
            st.markdown("<br>", unsafe_allow_html=True)
