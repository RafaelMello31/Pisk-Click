#!/usr/bin/env python3
"""
Converte logo.png para pisk_and_click_icon.ico
"""

from PIL import Image
import os

def converter_logo():
    """Converte PNG para ICO com múltiplos tamanhos (preferindo assets/)."""
    
    assets_logo = os.path.join(os.getcwd(), "assets", "logo.png")
    logo_path = assets_logo if os.path.exists(assets_logo) else "logo.png"
    
    if not os.path.exists(logo_path):
        print("❌ Erro: assets/logo.png não encontrado!")
        return False
    
    try:
        # Abrir logo
        img = Image.open(logo_path)
        
        # Converter para RGBA se necessário
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Criar ícone com múltiplos tamanhos
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Salvar como ICO diretamente em assets
        assets_dir = os.path.join(os.getcwd(), "assets")
        os.makedirs(assets_dir, exist_ok=True)
        out_path = os.path.join(assets_dir, "pisk_and_click.ico")
        img.save(out_path, format='ICO', sizes=icon_sizes)
        
        print("✅ Ícone criado com sucesso: assets/pisk_and_click.ico")
        print(f"   Tamanhos incluídos: {', '.join([f'{w}x{h}' for w, h in icon_sizes])}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao converter: {e}")
        return False

if __name__ == "__main__":
    print("🎨 Convertendo logo para ícone (assets)...")
    print()
    
    if converter_logo():
        print()
        print("✨ Pronto! Agora recompile o instalador.")
    else:
        print()
        print("⚠️  Falha na conversão!")
    
    input("\nPressione Enter para sair...")
