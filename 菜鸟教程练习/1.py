import pygame
import time
import random

# 初始化Pygame
pygame.init()

# 定义颜色
白色 = (255, 255, 255)
黄色 = (255, 255, 102)
黑色 = (0, 0, 0)
红色 = (213, 50, 80)
绿色 = (0, 255, 0)
蓝色 = (50, 153, 213)

# 定义屏幕尺寸
dis_width = 800
dis_height = 600

# 创建显示对象
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('贪吃蛇游戏')

# 定义时钟
clock = pygame.time.Clock()

# 定义蛇的尺寸和速度
snake_block = 10
snake_speed = 15

# 定义字体样式
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

def 我的分数(score):
    value = score_font.render("你的分数: " + str(score), True, 绿色)
    dis.blit(value, [0, 0])

def 画蛇(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, 黑色, [x[0], x[1], snake_block, snake_block])

def 消息显示(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [dis_width / 6, dis_height / 3])

def 游戏循环():
    game_over = False
    game_close = False

    x1 = dis_width / 2
    y1 = dis_height / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0

    while not game_over:

        while game_close == True:
            dis.fill(蓝色)
            消息显示("你输了! 按 Q-退出 或 C-再玩一次", 红色)
            我的分数(Length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        游戏循环()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        dis.fill(蓝色)
        pygame.draw.rect(dis, 绿色, [foodx, foody, snake_block, snake_block])
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        画蛇(snake_block, snake_List)
        我的分数(Length_of_snake - 1)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

游戏循环()
