import os
import pygame
import unicodedata
import math
import random

#ANIMACAO

def ani_explode( tela, explode, sprites, sprites_explosion):

    count = 0
    for ex in explode:
        if count % 3 != 0:
            count += 1
            continue

        elif explode[count] < len(sprites_explosion):
            tela.blit( sprites_explosion[ explode[count] ], [ explode[count+1] - sprites[2].get_width()/2, explode[count+2] - sprites[2].get_height()/2 ] )
            explode[count] += 1
            count += 1

        else:
            explode.pop(count + 2)
            explode.pop(count + 1)
            explode.pop(count)

def ani_background( game_ctrl):
    game_ctrl[4] -= 10 #background move step
    if game_ctrl[4] <= 0:
        game_ctrl[4] += 800
    
    

#GERANDO NOVOS INIMIGOS

def new_enemy( enemy, game_ctrl, config, sprites):
    new_ene = random.randint( 0 ,99 )
    if new_ene >= 100 - 20*game_ctrl[3] - 10:
        position = random.randint(0, config[0])

        count = 0
        for inimigo in enemy:
            if count % 4 != 0:
                count += 1
                continue
            elif enemy[count+3] + 15 <= sprites[2].get_height() and abs( enemy[count+2] - position) < sprites[2].get_width():
                return 0

            count += 1
            
        enemy.append( 5 ) #life
        enemy.append( math.radians(270) ) #angle
        enemy.append( position) #coordx
        enemy.append(-15) #coordy

#DELETANDO INIMIGOS
        
def del_enemy( player, enemy, explode, sprites, audio):
    i = 0
    deletar = False
    
    for inimigos in enemy:
        if i % 4 != 0:
            i += 1
            continue
        
        if enemy[i] <= 0:
            deletar = True
            player[1] += 10

        elif colision_i_p( i, player, enemy, sprites):
            deletar = True
            player[0] -= 1

        if deletar:

            x = enemy[i+2]
            y = enemy[i+3]

            explode.append(0)
            explode.append(x)
            explode.append(y)

            audio[1].play()
            
            enemy.pop( i+3 )
            enemy.pop( i+2 )
            enemy.pop( i+1 )
            enemy.pop( i )

            deletar = False
            
        i += 1

#COLISOES

#inimigos-player
def colision_i_p( i, player, enemy, sprites):
    if abs( player[2] - enemy[i+2] ) <= ( ( ( sprites[1].get_width() + sprites[2].get_width() ) / 2 ) - 10 ):
        if abs( player[3] - enemy[i+3] ) <= ( ( ( sprites[1].get_height() + sprites[2].get_height() ) / 2 ) - 10 ):
            return True
    return False

#inimigos-inimigos
def colision_i_i( i, pos_x, pos_y, enemy, sprites):
    count = 0
    for inimigos in enemy:
        if ( count % 4 != 0 ) or (4*i == count):
            count += 1
            continue

        if pos_x <= enemy[count+2] + ( sprites[2].get_width() - 5 ) and pos_x >= enemy[count+2] - ( sprites[2].get_width() - 5 ):
            if pos_y <= enemy[count+3] + ( sprites[2].get_height() - 5 ) and pos_y >= enemy[count+3] - ( sprites[2].get_height() - 5 ):
                return False
            
        count += 1

    return True    

#Balas-inimigos
def colision( enemy, my_shoot, sprites):

    enemy_count = 0
    
    for inimigo in enemy:

        if enemy_count % 4 != 0:
            enemy_count += 1
            continue
        
        shoot_count = 0
        
        for shoot in my_shoot:

            if shoot_count % 2 != 0:
                shoot_count += 1
                continue
            
            if abs( my_shoot[shoot_count] - enemy[enemy_count + 2] ) <= ( (sprites[2].get_width() + sprites[3].get_width() )/2 - 3):
                if abs( my_shoot[shoot_count + 1] - enemy[enemy_count + 3] ) <= ( (sprites[2].get_height() + sprites[3].get_height() )/2 - 3):

                    #remove a bala
                    my_shoot.remove( my_shoot[shoot_count + 1] )
                    my_shoot.remove( my_shoot[shoot_count] )

                    # Diminui life dos inimigos
                    enemy[enemy_count] -= 1

            shoot_count += 1

        enemy_count += 1
    
#CALCULOS DESCOLAMENTOS

#Calculo Shoots
def desl_shoot( my_shoot, config):
    for i in range( 0, int( len(my_shoot)/2 ) ):
        my_shoot[2*i + 1] -= 35 #shoot move step

    k = 0
    for shoot in my_shoot:
        if k % 2 != 0:
            k += 1
            continue
        
        if my_shoot[k+1] <= 0:
            my_shoot.remove( my_shoot[ k+1] )
            my_shoot.remove( my_shoot[ k] )
        k += 1

#Calculo Naves Inimigas
def desl_enemy( x, y, ang, x_fim, y_fim, width, height, level):

    #Calcula novos valores de X e Y
    
    x_novo = x  + (10+2*level)*math.cos(ang) #enemy x move step

    if x_novo > width:
        x_novo = width
    elif x_novo < 0:
        x_novo = 0

    y_novo = y -  (10+2*level)*math.sin(ang) #enemy y move step

    if y_novo > height: 
        y_novo = height
    elif y_novo < 0 and y >= 0 :
        y_novo = 0
    elif y < -30:
        y_novo = -30
        

    #Calcula o vetor que aponta do objeto para o jogador

    xdif = x_fim - x
    if y > 0:
        ydif = -(y_fim - y)
    else:
        ydif = -(y_fim + y)
        
    if xdif == 0 and ydif == 0:
        return x_novo, y_novo, ang

    xproj = xdif / math.hypot( xdif, ydif)
    yproj = ydif / math.hypot( xdif, ydif)

    #Obtem o angulo do vetor que aponta para o jogador

    if xproj == 0:
        return x_novo, y_novo, ang
    
    angproj = math.atan ( yproj / xproj)

    if (xproj < 0 and yproj < 0) or (xproj < 0 and yproj > 0):
        angproj += math.pi
    elif xproj > 0 and yproj < 0:
        angproj += 2*math.pi

    #Corrige a orientacao do objeto com base no vetor que aposta para o centro

    if angproj > ang:
        dif_ang = math.degrees(angproj - ang)
    else:
        dif_ang = math.degrees(ang - angproj)

    if dif_ang < 5 and dif_ang > 0: #enemy ang move step
        a_ang = dif_ang
    else:
        a_ang = 5
        
    if angproj == ang:
        ang_novo = ang
        
    elif angproj > ang:
        if angproj - ang > math.pi:
            ang_novo = ang - ( math.pi * a_ang / 180 )
            if ang_novo < 0:
                ang_novo += 2*math.pi
        else:
            ang_novo = ang + ( math.pi * a_ang / 180 )
            if ang_novo > 2*math.pi:
                ang_novo = ang_novo - 2*math.pi
            
    else:
        if ang - angproj < math.pi:
            ang_novo = ang - ( math.pi * a_ang / 180 )
            if ang_novo < 0:
                ang_novo += 2*math.pi
        else:
            ang_novo = ang + ( math.pi * a_ang / 180 )
            if ang_novo > 2*math.pi:
                ang_novo = ang_novo - 2*math.pi

    return x_novo, y_novo, ang_novo
    
#MENUS

def menu( tela, config, game_ctrl, player, sprites):

    #CONFIGURACAO FONTE
    fontePadrao = pygame.font.get_default_font()
    
    fonteMenuChecked = pygame.font.SysFont( fontePadrao, 50)
    fonteMenuUnchecked = pygame.font.SysFont( fontePadrao, 35)
    fonteMenuInfo = pygame.font.SysFont( fontePadrao, 25)

    #CORES
    cor_branco = ( 255, 255, 255 )
    cor_cinza = ( 135, 135, 135 )
    cor_azul1 = ( 110, 121, 193 )
    cor_preto = ( 0, 0, 0 )

    

    info = fonteMenuInfo.render( 'Up-Down Arrow Keys: Select         Enter: Choose         Esc: Return/Quit', 1, cor_branco )

    tela.fill( cor_preto )
    tela.blit( info, [ ( tela.get_width() - info.get_width() )/2, tela.get_height() - info.get_height() - 15 ] )

    #menu1 openning
    if game_ctrl[0] == 0:

        if game_ctrl[2] == 0:
            novo = fonteMenuChecked.render( 'New Game', 1, cor_azul1 )
            fim = fonteMenuUnchecked.render( 'Quit', 1, cor_branco )

        else:
            novo = fonteMenuUnchecked.render( 'New Game', 1, cor_branco )
            fim = fonteMenuChecked.render( 'Quit', 1, cor_azul1 )
        
        pos_y = 60
        tela.blit( sprites[4], [ ( tela.get_width() - sprites[4].get_width() )/2, pos_y] )

        pos_y += sprites[4].get_height() + 40
        tela.blit( novo, [ ( tela.get_width() - novo.get_width() )/2, pos_y])

        pos_y += novo.get_height() + 40
        tela.blit( fim, [ ( tela.get_width() - fim.get_width() )/2, pos_y])

        if game_ctrl[2] == 0:
            return 1
        else:
            return 0

    #menu2 level
    elif game_ctrl[0] == 1:

        if game_ctrl[2] == 0:
            facil = fonteMenuChecked.render( 'Easy', 1, cor_azul1 )
            medio = fonteMenuUnchecked.render( 'Medium', 1, cor_branco )
            dificil = fonteMenuUnchecked.render( 'Hard', 1, cor_branco )

        elif game_ctrl[2] == 1:
            facil = fonteMenuUnchecked.render( 'Easy', 1, cor_branco )
            medio = fonteMenuChecked.render( 'Medium', 1, cor_azul1 )
            dificil = fonteMenuUnchecked.render( 'Hard', 1, cor_branco )
            
        elif game_ctrl[2] == 2:
            facil = fonteMenuUnchecked.render( 'Easy', 1, cor_branco )
            medio = fonteMenuUnchecked.render( 'Medium', 1, cor_branco )
            dificil = fonteMenuChecked.render( 'Hard', 1, cor_azul1 )
        
        pos_y = 60
        tela.blit( sprites[4], [ ( tela.get_width() - sprites[4].get_width() )/2, pos_y] )

        pos_y += sprites[4].get_height() + 40
        tela.blit( facil, [ ( tela.get_width() - facil.get_width() )/2, pos_y])

        pos_y += facil.get_height() + 40
        tela.blit( medio, [ ( tela.get_width() - medio.get_width() )/2, pos_y])

        pos_y += medio.get_height() + 40
        tela.blit( dificil, [ ( tela.get_width() - dificil.get_width() )/2, pos_y])

        return game_ctrl[2]

    #menu3 game-over
    elif game_ctrl[0] == 3:

        if game_ctrl[2] == 0:
            novo = fonteMenuChecked.render( 'Restart', 1, cor_azul1 )
            fim = fonteMenuUnchecked.render( 'Quit', 1, cor_branco )

        else:
            novo = fonteMenuUnchecked.render( 'Restart', 1, cor_branco )
            fim = fonteMenuChecked.render( 'Quit', 1, cor_azul1 )

        if game_ctrl[3] == 0:
            resultado = fonteMenuChecked.render('Level: EASY     Score: '+str(player[1]), 1, cor_branco)
        elif game_ctrl[3] == 1:
            resultado = fonteMenuChecked.render('Level: MEDIUM     Score: '+str(player[1]), 1, cor_branco)
        elif game_ctrl[3] == 2:
            resultado = fonteMenuChecked.render('Level: HARD     Score: '+str(player[1]), 1, cor_branco)

        pos_y = 130
        tela.blit( sprites[6], [ ( tela.get_width() - sprites[6].get_width() )/2, pos_y] )

        pos_y += sprites[6].get_height() + 50
        tela.blit( resultado, [ ( tela.get_width() - resultado.get_width() )/2, pos_y])

        pos_y += resultado.get_height() + 50
        tela.blit( novo, [ ( tela.get_width() - novo.get_width() )/2, pos_y])

        pos_y += novo.get_height() + 40
        tela.blit( fim, [ ( tela.get_width() - fim.get_width() )/2, pos_y])

        if game_ctrl[2] == 0:
            return 2
        if game_ctrl[2] == 1:
            return 0

    #menu4 pause
    elif game_ctrl[0] == 4:

        if game_ctrl[2] == 0:
            continuar = fonteMenuChecked.render( 'Continue', 1, cor_azul1 )
            recomecar = fonteMenuUnchecked.render( 'Restart', 1, cor_branco )
            sair = fonteMenuUnchecked.render( 'Quit', 1, cor_branco )

        elif game_ctrl[2] == 1:
            continuar = fonteMenuUnchecked.render( 'Continue', 1, cor_branco )
            recomecar = fonteMenuChecked.render( 'Restart', 1, cor_azul1 )
            sair = fonteMenuUnchecked.render( 'Quit', 1, cor_branco )
            
        elif game_ctrl[2] == 2:
            continuar = fonteMenuUnchecked.render( 'Continue', 1, cor_branco )
            recomecar = fonteMenuUnchecked.render( 'Restart', 1, cor_branco )
            sair = fonteMenuChecked.render( 'Quit', 1, cor_azul1 )

        pos_y = 130
        tela.blit( sprites[5], [ ( tela.get_width() - sprites[5].get_width() )/2, pos_y] )

        pos_y += sprites[5].get_height() + 40
        tela.blit( continuar, [ ( tela.get_width() - continuar.get_width() )/2, pos_y])

        pos_y += continuar.get_height() + 40
        tela.blit( recomecar, [ ( tela.get_width() - recomecar.get_width() )/2, pos_y])

        pos_y += recomecar.get_height() + 40
        tela.blit( sair, [ ( tela.get_width() - sair.get_width() )/2, pos_y])

        if game_ctrl[2] == 0:
            return 3
        elif game_ctrl[2] == 1:
            return 2
        else:
            return 0


#CONFIGURAÇÕES INICIAIS
        
def config_iniciais( player, enemy, my_shoot, explode, game_ctrl, config):

    player.clear()
    enemy.clear()
    my_shoot.clear()
    explode.clear()

    game_ctrl[5] =  config[2]*3 # Time of control instrunctions in game 
                        
    player.append( 5) #life
    player.append( 0) #score
    player.append( config[0]/2) #coordx
    player.append( config[1]/2) #coordy

    for i in range(0, 3):
        enemy.append( 5 ) #life
        enemy.append( math.radians(270) ) #angle
        enemy.append( i * config[0] / 2 ) #coordx
        enemy.append(0) #coordy
        
#JOGO
def fase_jogo( tela, config, game_ctrl, player, enemy, my_shoot, explode, sprites, sprites_explosion, audio):


    #CONFIGURACAO FONTE
    fontePadrao = pygame.font.get_default_font()
    
    fonteMenuChecked = pygame.font.SysFont( fontePadrao, 50)
    fonteMenuUnchecked = pygame.font.SysFont( fontePadrao, 35)
    fonteMenuInfo = pygame.font.SysFont( fontePadrao, 25)


    #CORES
    cor_branco = ( 255, 255, 255 )
    cor_cinza = ( 135, 135, 135 )
    cor_azul1 = ( 110, 121, 193 )


    #SCORE E LIFE
    vida = fonteMenuUnchecked.render( 'LIFE: ' + str(player[0]), 1, cor_branco )
    pontos = fonteMenuUnchecked.render( 'PONTOS: ' + str(player[1]), 1, cor_branco )

    #HELP (Control instrunctions in game)
    info = fonteMenuInfo.render( 'Move mouse: Control the spaceship         Backspace: Shoot (Hold/Press)         Esc: Pause', 1, cor_branco )


    #ATUALIZAR POSICOES

    # jogador
    ( player[2], player[3] ) = pygame.mouse.get_pos()

    player[2] -= sprites[1].get_width()/2
    player[3] -= sprites[1].get_height()/2

    # inimigos
    for i in range( 0, int( len(enemy)/4 ) ):
        pos_x, pos_y, ang = desl_enemy( enemy[ 4*i + 2], enemy[ 4*i + 3], enemy[ 4*i + 1], player[2], player[3], config[0], config[1], game_ctrl[3])

        if colision_i_i( i, pos_x, pos_y, enemy, sprites):
            enemy[ 4*i + 2] = pos_x
            enemy[ 4*i + 3] = pos_y

        enemy[ 4*i + 1] = ang

    # balas
    desl_shoot( my_shoot, config)


    #IMPRIMIR NA TELA

    # plano de fundo
    tela.blit( sprites[0], [ 0, 0 - game_ctrl[4]] )

    if game_ctrl[5]:
        tela.blit( info, [ ( tela.get_width() - info.get_width() )/2, tela.get_height() - info.get_height() - 15 ] )
        game_ctrl[5] -= 1
    
    # jogador    
    tela.blit( sprites[1], [ player[2], player[3] ])

    # inimigos
    for i in range( 0, int( len(enemy)/4 )  ):        
        k = pygame.transform.rotate( pygame.image.load( 'img/enemy.png' ), math.degrees( enemy[4*i+1] ) )
        tela.blit( k, [enemy[ 4*i + 2] - sprites[2].get_width()/2, enemy[ 4*i + 3] - sprites[2].get_height()/2 ])

    # balas
    for i in range( 0, int( len(my_shoot)/2 ) ):
        tela.blit( sprites[3], [ my_shoot[2*i] - sprites[3].get_width()/2 , my_shoot[2*i + 1] - sprites[3].get_height()/2 ] )

    # vida
    tela.blit( vida, [ config[0] - 100, 10])

    # score
    tela.blit( pontos, [ 10, 10])


    #COLISOES
    colision( enemy, my_shoot, sprites)


    #DELETAR INIMIGOS
    del_enemy( player, enemy, explode, sprites, audio)


    #EXECUTAR ANIMACAO
    if len(explode) != 0:
        ani_explode( tela, explode, sprites, sprites_explosion)

    ani_background( game_ctrl)
    

    #ENCERRAMENTO JOGO
    if player[0] <= 0:
        return 3
    else:
        return 2

# LOOP PRINCIPAL

def main():
    
    #INICIALIZACOES
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    
    #POSICAO DA JANELA
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ( 50, 30) 

    #VARIAVEL VIDEOINFO
    videoinfo = pygame.display.Info()

    #VARIAVEIS AMBIENTE
    # 0 - Width | 1 - Height |  2 - FPS
    config = []
    
    config.append ( videoinfo.current_w - 100 )
    config.append ( videoinfo.current_h - 100 )
    config.append ( 20)

    if config[0] > 1920:
        config[0] = 1920
    if config[1] > 1080:
        config[1] = 1080

    #CONFIGURACAO: TAMANHO DA TELA, TITULO E ICON
    tela = pygame.display.set_mode( [ config[0], config[1] ] )
    pygame.display.set_caption( "ALPHA SPACESHIP BATTLEFRONT" )
    pygame.display.set_icon( pygame.image.load( 'img/mainship.png' ) )

    #CONFIGURACAO: CLOCK
    relogio = pygame.time.Clock()

    #CONFIGURACAO: REPEAT KEY
    pygame.key.set_repeat(10, 180)

    #CLOCK EXECUÇÂO DE EVENTO (NOVOS INIMIOS)
    pygame.time.set_timer( pygame.USEREVENT+1, 500)

    #SPRITES
    # 0 - background | 1 - player |  2 - enemy | 3 - shoot | 4 - title | 5 - Pause | 6 - game over |
    sprites = []

    sprites.append( pygame.image.load( 'img/background.png' ) )
    sprites.append( pygame.image.load( 'img/mainship.png' ) )
    sprites.append( pygame.image.load( 'img/enemy.png' ) )
    sprites.append( pygame.image.load( 'img/shoot.png' ) )
    
    sprites.append( pygame.image.load( 'img/title.png' ) )
    sprites.append( pygame.image.load( 'img/pause.png' ) )
    sprites.append( pygame.image.load( 'img/gameover.png' ) )

    sprites_explosion = []

    for f in range( 0, 13):
        if f < 10:
            sprites_explosion.append( pygame.image.load( 'img/explosion/frame00'+str(f)+'.png' ) )
        else:
            sprites_explosion.append( pygame.image.load( 'img/explosion/frame0'+str(f)+'.png' ) )

    #VARIAVEL DA ANIMACAO EXPLOSAO
    # 0 - status | 1 - coord x | 2 - coord y
    explode = []

    #VARIAVEL DE AUDIO
    # 0 - laser | 1 - explode
    # background(space)
    audio = []

    audio.append( pygame.mixer.Sound('sound/laser.ogg') )
    audio.append( pygame.mixer.Sound('sound/explosion.ogg') )

    audio[0].set_volume(0.3)
    audio[1].set_volume(0.8)

    pygame.mixer.music.load('sound/space.ogg')
    pygame.mixer.music.set_volume(0.4)

    background_audio = False


    #VARIAVEIS DO FLUXO DO JOGO
    # 0 - scene | 1 - choose |  2 - select | 3 - level | 4 - Background-move | 5 - Help - Time instructions in game
    game_ctrl = []

    game_ctrl.append( 0)
    game_ctrl.append( 0)
    game_ctrl.append( 0)
    game_ctrl.append( 0)
    game_ctrl.append( 800)
    game_ctrl.append( 0)

    #VARIAVEIS DO JOGADOR
    # 0 - life | 1 - score |  2 - coord x | 3 - coord y
    player = []

    #VARIAVEIS DOS INIMIGOS
    # 0 - life | 1 - angle |  2 - coord x | 3 - coord y
    enemy = []

    #VARIAVEIS DOS TIROS
    # 0 - coord x | 1 - coord y
    my_shoot = []    
    
    jogo = True
    
    while jogo:
        for event in pygame.event.get():            
            if event.type == pygame.QUIT:
                jogo = False
                
            if event.type == pygame.KEYDOWN:

                #MENU CONTROLLER
                if event.key == pygame.K_DOWN:
                    game_ctrl[2] += 1

                    if game_ctrl[0] == 0 or game_ctrl[0] == 3:
                        game_ctrl[2] = game_ctrl[2] % 2
                    elif game_ctrl[0] == 1 or game_ctrl[0] == 4:
                        game_ctrl[2] = game_ctrl[2] % 3
                     
                if event.key == pygame.K_UP:
                    if game_ctrl[0] == 0 or game_ctrl[0] == 3:
                        game_ctrl[2] += 1
                        game_ctrl[2] = game_ctrl[2] % 2
                    elif game_ctrl[0] == 1 or game_ctrl[0] == 4:
                        game_ctrl[2] += 2
                        game_ctrl[2] = game_ctrl[2] % 3
                        
                        
                if event.key == pygame.K_RETURN:
                    if game_ctrl[0] == 0:
                        if game_ctrl[1] == 0:
                            jogo = False
                        else:
                            game_ctrl[0] = game_ctrl[1]
                            game_ctrl[2] = 0
                            game_ctrl[1] = 0

                    elif game_ctrl[0] == 1 or game_ctrl[0] == 3 or game_ctrl[0] == 4:
                        if game_ctrl[0] != 1 and game_ctrl[1] == 0:
                            game_ctrl[0] = game_ctrl[1]
                            game_ctrl[1] = 0
                            game_ctrl[2] = 0
                            break
                        
                        elif game_ctrl[0] != 1 and game_ctrl[1] == 3:
                            game_ctrl[0] = 2
                            game_ctrl[1] = 0
                            game_ctrl[2] = 0
                            break
                            
                        game_ctrl[0] = 2
                        game_ctrl[1] = 0
                        game_ctrl[2] = 0

                        config_iniciais( player, enemy, my_shoot, explode, game_ctrl, config)
                            
                        #CONFIGURANDO POSICAO DO MOUSE
                        pygame.mouse.set_pos( [ tela.get_width()/2, tela.get_height()/2 ] )

                    elif game_ctrl[0] == 2:
                        continue
                        

                if event.key == pygame.K_ESCAPE:
                    if game_ctrl[0] == 0:
                        jogo = False
                        break
                    elif game_ctrl[0] == 1 or game_ctrl[0] == 3:
                        game_ctrl[0] = 0
                    elif game_ctrl[0] == 2:
                        game_ctrl[0] = 4   
                    elif game_ctrl[0] == 4:
                        game_ctrl[0] = 2

                    game_ctrl[1] = 0
                    game_ctrl[2] = 0

                if event.key == pygame.K_SPACE:
                    if game_ctrl[0] == 2:                        
                        x, y = pygame.mouse.get_pos()
                        my_shoot.append( x)
                        my_shoot.append( y - (sprites[1].get_height()/2))
                        audio[0].play()
                        

            if game_ctrl[0] == 2 and event.type == pygame.USEREVENT+1:
                new_enemy( enemy, game_ctrl, config, sprites)


        relogio.tick(config[2])

        if game_ctrl[0] == 1:
            game_ctrl[3] = menu( tela, config, game_ctrl, player, sprites)
        elif game_ctrl[0] == 2:
            game_ctrl[0] = fase_jogo( tela, config, game_ctrl, player, enemy, my_shoot, explode, sprites, sprites_explosion, audio)
            if background_audio == False:
                pygame.mixer.music.play(-1)
                background_audio = True
        else:
            game_ctrl[1] = menu( tela, config, game_ctrl, player, sprites)
            if background_audio:
                pygame.mixer.music.stop()
                background_audio = False

        if len(enemy) == 0:
            new_enemy( enemy, game_ctrl, config, sprites)
            
        pygame.display.update()

    pygame.quit()
    
main()
    
