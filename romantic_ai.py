import json
import os
import logging
from typing import Optional
from google import genai
from google.genai import types
import bleach

# IMPORTANT: KEEP THIS COMMENT
# Follow these instructions when using this blueprint:
# - Note that the newest Gemini model series is "gemini-2.5-flash" or gemini-2.5-pro"
#   - do not change this unless explicitly requested by the user

# This API key is from Gemini Developer API Key, not vertex AI API Key
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_romantic_declaration(nome_destinatario: str, tema: str = "apaixonada e animada") -> str:
    """
    Gera uma declaração romântica personalizada usando IA do Gemini
    
    Args:
        nome_destinatario: Nome da pessoa para quem a declaração é direcionada
        tema: Tema da declaração (ex: "apaixonada e animada")
    
    Returns:
        String com a declaração romântica gerada
    """
    try:
        # Sanitizar nome para usar nos prompts da IA
        safe_name = bleach.clean(nome_destinatario)
        prompt = f"""
        Crie uma declaração de amor romântica e apaixonada para {safe_name}.
        
        IMPORTANTE: 
        - Responda APENAS com o conteúdo HTML puro
        - NÃO inclua palavras como "html" ou "```html``` no início ou fim
        - Comece diretamente com o HTML
        
        A declaração deve ter:
        - Linguagem romântica e poética em português brasileiro
        - Máximo 4 parágrafos curtos (2-3 linhas cada)
        - Emojis românticos discretos
        - Personalizada com o nome {safe_name}
        
        Formato: 
        <h2>💕 {safe_name} 💕</h2>
        <p>Primeiro parágrafo romântico... 🌹</p>
        <p>Segundo parágrafo com metáforas... ✨</p>
        <p>Terceiro parágrafo de promessas... 💫</p>
        <p><strong>💖 Com todo meu amor 💖</strong></p>
        """

        # Usar modelo mais rápido e adicionar configurações de timeout
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Modelo mais rápido
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=800,  # Limitar tamanho da resposta
                response_mime_type="text/plain"
            )
        )

        if response.text:
            # Sanitizar conteúdo HTML da IA para segurança
            allowed_tags = ['h2', 'p', 'strong', 'em', 'br', 'span', 'h3', 'h4', 'div']
            allowed_attributes = {'div': ['class'], 'h2': [], 'p': ['class'], 'h4': ['class']}
            sanitized_html = bleach.clean(
                response.text, 
                tags=allowed_tags, 
                attributes=allowed_attributes,
                strip=True
            )
            return sanitized_html
        else:
            # Fallback se a IA não responder
            return generate_fallback_declaration(nome_destinatario)
            
    except Exception as e:
        logging.error(f"Erro ao gerar declaração com IA: {e}")
        # Retorna declaração de fallback em caso de erro
        return generate_fallback_declaration(nome_destinatario)

def generate_fallback_declaration(nome_destinatario: str) -> str:
    """Gera uma declaração de fallback caso a IA falhe"""
    # Sanitizar nome do destinatário
    safe_name = bleach.clean(nome_destinatario)
    return f"""
    <h2>💕 {safe_name} 💕</h2>
    
    <p>🌹 Meu coração se acelera sempre que penso em você, {safe_name}. Você é a razão pela qual cada dia se torna uma nova aventura cheia de amor e alegria. 🌹</p>
    
    <p>✨ Seus olhos são como estrelas que iluminam minha alma nas noites mais escuras. Seu sorriso é o sol que aquece meu coração e faz florescer os sentimentos mais puros dentro de mim. ✨</p>
    
    <p>💫 Quando estou ao seu lado, sinto que posso conquistar o mundo inteiro. Você me faz ser uma pessoa melhor, mais corajosa, mais apaixonada pela vida. 💫</p>
    
    <p>🥰 Prometo estar sempre aqui para você, nos momentos de felicidade e nos desafios que possam surgir. Meu amor por você é infinito como o oceano e eterno como as montanhas. 🥰</p>
    
    <p>💝 Obrigado por existir e por permitir que eu faça parte da sua história. Você é meu grande amor, minha alma gêmea, minha razão de viver. 💝</p>
    
    <p><strong>💖 Com todo meu amor eterno, para sempre sua 💖</strong></p>
    """

def generate_preview_declaration(nome_destinatario: str) -> str:
    """
    Gera uma prévia rápida da declaração para mostrar no formulário
    """
    if not nome_destinatario or not nome_destinatario.strip():
        return '<p>Digite o nome da pessoa especial para ver uma prévia da declaração...</p>'
    
    try:
        # Sanitizar nome para usar nos prompts da IA
        safe_name = bleach.clean(nome_destinatario)
        prompt = f"""
        Crie uma prévia curta de declaração romântica para {safe_name}.
        
        IMPORTANTE: Responda APENAS com HTML puro, sem texto 'html' ou ```
        
        Formato:
        <h4 class="text-romantic mb-3">{safe_name} 💕</h4>
        <p>Uma frase romântica curta... 🌟</p>
        <p>Segunda frase de amor... 💝</p>
        <p class="text-end"><strong>Com amor ❤️</strong></p>
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=300,  # Limitar tamanho da prévia
                response_mime_type="text/plain"
            )
        )

        if response.text:
            # Sanitizar prévia da IA
            allowed_tags = ['h4', 'p', 'strong', 'em', 'br', 'span']
            allowed_attributes = {'h4': ['class'], 'p': ['class'], 'strong': []}
            sanitized_preview = bleach.clean(
                response.text,
                tags=allowed_tags,
                attributes=allowed_attributes,
                strip=True
            )
            return sanitized_preview
        else:
            return generate_fallback_preview(nome_destinatario)
            
    except Exception as e:
        logging.error(f"Erro ao gerar prévia com IA: {e}")
        return generate_fallback_preview(nome_destinatario)

def generate_fallback_preview(nome_destinatario: str) -> str:
    """Gera uma prévia de fallback"""
    # Sanitizar nome do destinatário
    safe_name = bleach.clean(nome_destinatario)
    return f"""
    <h4 class="text-romantic mb-3">{safe_name} 💕</h4>
    <p>Você ilumina minha vida como as estrelas iluminam a noite. Cada momento ao seu lado é um presente que guardo no coração. 🌟</p>
    <p>Meu amor por você cresce a cada dia, como flores que desabrocham em um jardim eterno. Você é minha inspiração, minha alegria, meu grande amor. 🌹</p>
    <p class="text-end"><strong>Com todo meu amor ❤️</strong></p>
    """