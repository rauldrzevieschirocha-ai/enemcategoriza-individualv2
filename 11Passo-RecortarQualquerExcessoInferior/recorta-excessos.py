from PIL import Image
import os
import shutil

def encontrar_faixa_cinza(imagem, cor_alvo, tolerancia=15):
    """
    Encontra a faixa cinza (altura de 5px, largura total com margem de até 3px de erro) de baixo para cima.
    Retorna a posição Y onde deve ser feito o corte (acima da faixa) ou None se não encontrar.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Percorre a imagem de baixo para cima (precisa de pelo menos 5 pixels de altura para a faixa)
    for y in range(altura - 1, 4, -1):
        faixa_encontrada = True
        
        # Verifica as 5 linhas que compõem a faixa (de y-4 até y)
        for dy in range(5):
            pixel_y = y - 4 + dy
            if pixel_y < 0:
                faixa_encontrada = False
                break
                
            pixels_validos = 0
            # Percorre a largura da linha
            for x in range(largura):
                pixel = pixels[x, pixel_y]
                if len(pixel) == 4:  # RGBA
                    r, g, b, a = pixel
                else:  # RGB
                    r, g, b = pixel[:3]
                
                # Verifica se o pixel corresponde à cor alvo (dentro da tolerância)
                if (abs(r - cor_alvo[0]) <= tolerancia and 
                    abs(g - cor_alvo[1]) <= tolerancia and 
                    abs(b - cor_alvo[2]) <= tolerancia):
                    pixels_validos += 1
            
            # Margem de erro de até 3px na largura (precisa ter pelo menos largura - 3 pixels da cor)
            if pixels_validos < (largura - 3):
                faixa_encontrada = False
                break
        
        if faixa_encontrada:
            print(f"Faixa cinza encontrada! Cortando na posição y={y-4}")
            return y - 4  # Retorna a posição logo acima da faixa cinza
    
    return None

def processar_imagens(pasta_origem, pasta_destino, cor_alvo):
    """
    Processa todas as imagens da pasta origem, recortando as que têm a faixa cinza inferior
    e copiando todas para a pasta destino
    """
    # Cria a pasta de destino se não existir
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Lista todos os arquivos da pasta origem
    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    print(f"Encontrados {len(arquivos)} arquivos para processar")
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        
        try:
            # Abre a imagem
            with Image.open(caminho_origem) as imagem:
                print(f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})")
                
                # Procura pela faixa cinza inferior
                posicao_corte = encontrar_faixa_cinza(imagem, cor_alvo)
                
                if posicao_corte is not None and posicao_corte > 0:
                    # Se encontrou a faixa, recorta a imagem mantendo o espaço em branco acima dela
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                else:
                    # Se não encontrou faixa, copia a imagem original
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (sem faixa detectada)")
                    
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            # Tenta copiar o arquivo mesmo com erro
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado mesmo com erro")
            except:
                print(f"✗ Não foi possível copiar o arquivo")

# Função principal
if __name__ == "__main__":
    # Configurações
    pasta_origem = "./questoes"
    pasta_destino = "finalizadas"
    cor_alvo = (35, 31, 32)  # Cor cinza solicitada (RGB)
    
    print("Iniciando processamento de imagens...")
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")
    print(f"Cor alvo: RGB{cor_alvo}")
    
    # Verifica se a pasta origem existe
    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        exit(1)
    
    # Executa o processamento
    processar_imagens(pasta_origem, pasta_destino, cor_alvo)
    
    print("\n" + "="*50)
    print("Processamento concluído!")
    print(f"Todas as imagens foram salvas em: {pasta_destino}")