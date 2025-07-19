#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Portal da Transparência
Modern Interface Following Mockups - Refactored for Production
"""

# Import the new modern interface
from apps.gradio_app import create_interface
import os

if __name__ == "__main__":
    print("🚀 Iniciando Cidadão.AI - Interface Moderna...")
    
    # Check API status
    TRANSPARENCY_API_KEY = os.getenv("TRANSPARENCY_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    api_status = "✅" if TRANSPARENCY_API_KEY else "❌"
    ai_status = "✅" if GROQ_API_KEY else "⚠️"
    
    print(f"📊 Portal da Transparência API: {api_status}")
    print(f"🤖 GROQ AI API: {ai_status}")
    
    # Create and launch the modern interface
    app = create_interface()
    
    # Launch with production settings for HuggingFace Spaces
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False,
        show_api=False
    )