"""
    MediMind AI - Animated Day/Night Toggle Switch Component
Native Streamlit Custom Component connecting the Sun/Moon/Stars Day-Night
toggle directly into Streamlit session state and python execution.
"""
import os
import streamlit.components.v1 as components

_COMPONENT_PATH = os.path.join(os.path.dirname(__file__), "theme_toggle_widget")
_theme_toggle_component = components.declare_component("theme_toggle_switch", path=_COMPONENT_PATH)

def theme_toggle_switch(is_dark: bool = False, key: str = "theme_toggle_switch") -> bool:
    """
    Renders the Sun & Moon animated switch and returns the boolean dark mode state directly.
    """
    val = _theme_toggle_component(is_dark=is_dark, key=key, default=is_dark)
    return bool(val)
