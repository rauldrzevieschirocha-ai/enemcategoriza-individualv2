from PIL import Image
import os

Image.MAX_IMAGE_PIXELS = None

def encontrar_faixa_vertical(imagem, cor_alvo, tolerancia=15, altura_base=31, margem_altura=5):
    """
    Encontra posições onde há um padrão visual vertical de largura 10px (x de 290 a 300)
    e altura de 31px (com margem de erro de +/- 5px, ou seja, entre 26px e 36px).
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Limites de altura com a margem de erro
    altura_minima = altura_base - margem_altura  # 26px
    altura_maxima = altura_base + margem_altura  # 36px
    
    y = 0
    while y < altura - altura_minima:
        # Conta quantos pixels consecutivos para baixo correspondem ao padrão na faixa x=[290..300]
        altura_encontrada = 0
        
        while (y + altura_encontrada) < altura:
            y_atual = y + altura_encontrada
            bloco_valido = True
            
            # Verifica a faixa de largura de 290 a 300 (10 pixels de largura)
            for x in range(290, 301):
                if x >= largura:
                    bloco_valido = False
                    break
                    
                pixel = pixels[x, y_atual]
                r, g, b = pixel[:3]
                
                # Verifica se a cor está dentro da tolerância
                if (abs(r - cor_alvo[0]) > tolerancia or 
                    abs(g - cor_alvo[1]) > tolerancia or 
                    abs(b - cor_alvo[2]) > tolerancia):
                    bloco_valido = False
                    break
            
            if bloco_valido:
                altura_encontrada += 1
            else:
                break
        
        # Verifica se a altura da faixa encontrada está dentro da margem aceita (26px a 36px)
        if altura_minima <= altura_encontrada <= altura_maxima:
            # Corta 2 pixels antes do padrão começar, de modo que esses 2 pixels permaneçam
            posicao_corte = y - 2
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append((posicao_corte, y, altura_encontrada))
            print(f"Padrão encontrado em y={y} (altura de {altura_encontrada}px). Cortando em y={posicao_corte}")
            
            # Avança o loop pulando a faixa encontrada
            y += altura_encontrada
        else:
            y += 1
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando no ponto calculado.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições dos padrões
    deteccoes = encontrar_faixa_vertical(imagem, cor_alvo)
    
    if not deteccoes:
        print("Nenhum padrão visual encontrado na imagem!")
        return
    
    posicoes_corte = [d[0] for d in deteccoes]
    print(f"Encontradas {len(posicoes_corte)} ocorrências do padrão para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, (posicao_corte, y_inicio_padrao, altura_padrao) in enumerate(deteccoes):
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta da posição anterior até o ponto de corte (2px antes do padrão)
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa a partir da posição deste corte
        posicao_anterior = posicao_corte
    
    # Corta a última seção restante
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(deteccoes)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "colunas"           # Substitua pelo nome da pasta de saída
    
    # Cor RGB (76, 76, 78) especificada
    cor_do_padrao = (76, 76, 78)
    print(f"Cor procurada: RGB{cor_do_padrao}")
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")