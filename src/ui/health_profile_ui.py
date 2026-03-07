"""
Health Profile UI Component
"""

from typing import Callable
import streamlit as st

from src.models import HealthProfile


class HealthProfileUI:
    """Renders health condition selection with beautiful card design"""
    
    def render(
        self,
        current_profile: HealthProfile,
        on_profile_change: Callable[[HealthProfile], None]
    ) -> HealthProfile:
        """Render health profile controls with elegant card layout"""
        
        # Section header with icon
        st.markdown("""
        <div style="text-align: center; margin: 1rem 0 1.5rem 0;">
            <h2 style="color: #2c3e50; font-size: 2rem; font-weight: 600; margin-bottom: 0.5rem;">
                🩺 Select Your Health Conditions
            </h2>
            <p style="color: #7f8c8d; font-size: 1rem;">
                Choose one or multiple conditions for personalized recommendations
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Health conditions data with icons
        conditions_data = [
            ("Diabetes", "🩸", "High blood sugar"),
            ("Hypertension", "💓", "High blood pressure"),
            ("Heart Disease", "❤️", "Cardiovascular health"),
            ("Kidney Disease", "🫘", "Kidney function"),
            ("Obesity", "⚖️", "Weight management"),
            ("High Cholesterol", "🧈", "Cholesterol levels"),
            ("Thyroid", "🦋", "Thyroid function"),
            ("Liver Disease", "🫀", "Liver health"),
            ("Celiac Disease", "🌾", "Gluten intolerance"),
            ("Lactose Intolerance", "🥛", "Dairy sensitivity"),
            ("Gout", "🦴", "Uric acid buildup"),
            ("IBS", "🔄", "Digestive health"),
            ("Depression", "🧠", "Mental wellness"),
            ("Anxiety", "😰", "Stress management"),
            ("Osteoporosis", "🦴", "Bone health"),
            ("Anemia", "🩸", "Iron levels")
        ]
        
        # Create grid layout - 4 columns with actual working checkboxes
        conditions = []
        for i in range(0, len(conditions_data), 4):
            cols = st.columns(4)
            for j, col in enumerate(cols):
                if i + j < len(conditions_data):
                    condition_name, icon, description = conditions_data[i + j]
                    with col:
                        # Create a container for the card
                        is_selected = condition_name in current_profile.conditions
                        
                        # Use checkbox with custom label
                        selected = st.checkbox(
                            f"{icon} {condition_name}",
                            value=is_selected,
                            key=f"health_{condition_name}",
                            help=description
                        )
                        
                        if selected:
                            conditions.append(condition_name)
        
        # Show selected conditions summary
        st.write("")
        if conditions:
            st.success(f"✅ Selected: {', '.join(conditions)}")
        else:
            st.info("ℹ️ Select one or more health conditions above")
        
        # Create updated profile
        updated_profile = HealthProfile(mode="Individual", conditions=conditions)
        
        # Check if profile changed
        if set(updated_profile.conditions) != set(current_profile.conditions):
            on_profile_change(updated_profile)
        
        return updated_profile
