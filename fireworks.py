import pygame
import random
import math
import time

# 初始化Pygame
pygame.init()

# 设置窗口
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("烟花效果 - 自动发射")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),    # 红色
    (0, 255, 0),    # 绿色
    (0, 0, 255),    # 蓝色
    (255, 255, 0),  # 黄色
    (255, 0, 255),  # 紫色
    (0, 255, 255),  # 青色
    (255, 165, 0),  # 橙色
    (255, 192, 203) # 粉色
]

class Particle:
    def __init__(self, x, y, color, is_secondary=False, shape_type="circle", angle=None, distance=None):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 1.2 if is_secondary else 1.5
        self.is_secondary = is_secondary
        self.shape_type = shape_type
        self.initial_x = x
        self.initial_y = y
        
        if is_secondary:
            # 二次绽放使用更小的角度范围，形成更紧凑的形状
            phi = random.uniform(0, math.pi * 2)
            theta = random.uniform(0, math.pi / 6)
            speed = random.uniform(1, 2)
        else:
            if shape_type == "circle":
                # 完美圆形分布
                # 在球面上均匀分布的方法
                u = random.uniform(0, 1)
                v = random.uniform(0, 1)
                phi = 2 * math.pi * u
                theta = math.acos(2 * v - 1)
                speed = random.uniform(4, 7)  # 增大速度形成更大圆
            
            elif shape_type == "ring":
                # 环形分布
                phi = random.uniform(0, math.pi * 2)
                theta = random.uniform(math.pi/3, math.pi/2.5)  # 在较窄的角度范围内形成环
                speed = random.uniform(5, 6)  # 固定速度
            
            elif shape_type == "heart":
                # 心形分布
                if angle is not None:
                    phi = angle
                else:
                    phi = random.uniform(0, math.pi * 2)
                # 调整心形大小
                speed = 6 + random.uniform(-0.5, 0.5)
                # 心形公式调整
                theta = math.pi/2  # 固定角度
            
            elif shape_type == "star":
                # 星形分布
                if angle is not None and distance is not None:
                    phi = angle
                    speed = distance
                else:
                    # 五角星的五个顶点
                    points = 5
                    # 随机选择一个方向
                    point_angle = random.randint(0, points-1) * (2 * math.pi / points)
                    # 在顶点附近随机偏移
                    phi = point_angle + random.uniform(-0.1, 0.1)
                    # 根据是否在顶点来调整速度
                    if random.random() < 0.6:  # 顶点
                        speed = random.uniform(5, 7)
                    else:  # 内部
                        speed = random.uniform(2, 3)
                    
                theta = random.uniform(0, math.pi / 4)
            
            elif shape_type == "spiral":
                # 螺旋形
                arms = 3  # 螺旋臂数量
                arm = random.randint(0, arms-1)
                t = random.uniform(0, 1)  # 螺旋参数
                phi = (2 * math.pi / arms) * arm + t * 10  # 旋转角度
                speed = 2 + t * 5  # 速度随参数增加
                theta = math.pi/3
            
            elif shape_type == "double_ring":
                # 双环形
                phi = random.uniform(0, math.pi * 2)
                if random.random() < 0.5:
                    theta = random.uniform(math.pi/6, math.pi/5)  # 内环
                    speed = random.uniform(3, 4)
                else:
                    theta = random.uniform(math.pi/3, math.pi/2.5)  # 外环
                    speed = random.uniform(5, 6)
            
            else:  # 默认或其他形状
                phi = random.uniform(0, math.pi * 2)
                theta = random.uniform(0, math.pi/3)
                speed = random.uniform(3, 6)
            
        self.vx = speed * math.sin(theta) * math.cos(phi)
        self.vy = speed * math.sin(theta) * math.sin(phi)
        
        # 心形特殊处理
        if shape_type == "heart" and not is_secondary:
            t = phi  # 参数t
            # 心形方程
            # x = a(2cos(t) - cos(2t))
            # y = a(2sin(t) - sin(2t))
            scale = 0.4
            self.vx = speed * scale * (2 * math.cos(t) - math.cos(2*t))
            self.vy = -speed * scale * (2 * math.sin(t) - math.sin(2*t))  # 负号使心形朝上
        
        self.lifetime = 100 if is_secondary else 150  # 增加主绽放寿命
        self.alpha = 255
        self.gravity = 0.015 if is_secondary else 0.02  # 进一步减小重力
        
        # 彩虹渐变效果（对部分形状）
        if shape_type in ["rainbow", "spiral"] and not is_secondary:
            # 基于角度的颜色渐变
            hue = (phi / (2 * math.pi)) * 360
            self.color = self.hsv_to_rgb(hue, 1, 1)

    def hsv_to_rgb(self, h, s, v):
        # HSV转RGB简化版
        h = h % 360
        h_i = int(h / 60) % 6
        f = h / 60 - h_i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        if h_i == 0: r, g, b = v, t, p
        elif h_i == 1: r, g, b = q, v, p
        elif h_i == 2: r, g, b = p, v, t
        elif h_i == 3: r, g, b = p, q, v
        elif h_i == 4: r, g, b = t, p, v
        else: r, g, b = v, p, q
        
        return (int(r * 255), int(g * 255), int(b * 255))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        self.alpha = int(255 * (self.lifetime / (100 if self.is_secondary else 150)))

    def draw(self, screen):
        if self.alpha > 0:
            color_with_alpha = (*self.color, self.alpha)
            surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, color_with_alpha, (self.radius, self.radius), self.radius)
            screen.blit(surface, (int(self.x - self.radius), int(self.y - self.radius)))

class Firework:
    def __init__(self):
        self.reset()
        self.active = False

    def reset(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = HEIGHT
        self.target_y = random.randint(50, HEIGHT // 2)
        self.speed = -5
        self.particles = []
        self.secondary_particles = []
        self.exploded = False
        self.secondary_exploded = False
        self.color = random.choice(COLORS)
        self.explosion_time = 0
        self.active = False
        # 随机选择绽放形状
        self.shape_type = random.choice([
            "circle", "ring", "heart", "star", 
            "spiral", "double_ring", "rainbow"
        ])

    def launch(self):
        if not self.active and not self.exploded:
            self.active = True

    def update(self):
        if not self.active:
            return

        if not self.exploded:
            self.y += self.speed
            if self.y <= self.target_y:
                self.explode()
                self.exploded = True
                self.explosion_time = pygame.time.get_ticks()
        else:
            # 更新主粒子
            for particle in self.particles[:]:
                particle.update()
                if particle.lifetime <= 0:
                    self.particles.remove(particle)
            
            # 检查是否需要二次绽放
            if not self.secondary_exploded and len(self.particles) > 0:
                current_time = pygame.time.get_ticks()
                if current_time - self.explosion_time > 500:
                    self.secondary_explode()
                    self.secondary_exploded = True
            
            # 更新二次绽放粒子
            for particle in self.secondary_particles[:]:
                particle.update()
                if particle.lifetime <= 0:
                    self.secondary_particles.remove(particle)
            
            # 如果所有粒子都消失，重置烟花
            if not self.particles and not self.secondary_particles:
                self.reset()

    def explode(self):
        # 主绽放，使用更均匀的分布
        particle_count = 500
        
        if self.shape_type == "heart":
            # 心形需要更精确的角度分布
            for i in range(particle_count):
                angle = (i / particle_count) * math.pi * 2
                self.particles.append(Particle(self.x, self.y, self.color, 
                                              shape_type=self.shape_type, angle=angle))
        
        elif self.shape_type == "star":
            # 星形需要特定角度和距离
            points = 5
            for i in range(particle_count):
                # 部分粒子形成星尖
                if i % 10 < 6:  # 60%的粒子在星尖
                    point_idx = random.randint(0, points-1)
                    angle = point_idx * (2 * math.pi / points)
                    angle += random.uniform(-0.1, 0.1)  # 微小偏移
                    distance = random.uniform(5, 7)  # 星尖距离
                else:  # 剩余粒子填充星内部
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(2, 3)  # 内部距离
                self.particles.append(Particle(self.x, self.y, self.color, 
                                             shape_type=self.shape_type, angle=angle, distance=distance))
        
        else:
            # 其他形状使用默认分布
            for _ in range(particle_count):
                self.particles.append(Particle(self.x, self.y, self.color, shape_type=self.shape_type))

    def secondary_explode(self):
        # 二次绽放
        for particle in self.particles[:]:
            if random.random() < 0.3:
                for _ in range(3):
                    # 根据原始形状调整二次绽放
                    if self.shape_type in ["rainbow", "spiral"]:
                        # 保持原始粒子的颜色
                        self.secondary_particles.append(
                            Particle(particle.x, particle.y, particle.color, True, "circle")
                        )
                    else:
                        self.secondary_particles.append(
                            Particle(particle.x, particle.y, self.color, True)
                        )

    def draw(self, screen):
        if not self.exploded and self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)
        for particle in self.particles:
            particle.draw(screen)
        for particle in self.secondary_particles:
            particle.draw(screen)

def main():
    clock = pygame.time.Clock()
    fireworks = [Firework() for _ in range(8)]  # 增加烟花数量
    running = True
    
    # 自动发射参数
    last_launch_time = 0
    min_launch_interval = 500  # 最小发射间隔(毫秒)
    max_launch_interval = 1500  # 最大发射间隔(毫秒)
    next_launch_time = pygame.time.get_ticks() + random.randint(min_launch_interval, max_launch_interval)
    
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # 按ESC退出
                    running = False
        
        # 自动发射烟花
        if current_time >= next_launch_time:
            # 找到一个未激活的烟花
            for firework in fireworks:
                if not firework.active and not firework.exploded:
                    firework.launch()
                    next_launch_time = current_time + random.randint(min_launch_interval, max_launch_interval)
                    break
        
        screen.fill(BLACK)
        
        # 更新和绘制烟花
        active_count = 0
        for firework in fireworks:
            firework.update()
            firework.draw(screen)
            if firework.active or firework.exploded:
                active_count += 1
        
        # 如果活跃的烟花不多，发射更多
        if active_count < 3 and current_time - last_launch_time > 1000:
            for firework in fireworks:
                if not firework.active and not firework.exploded:
                    firework.launch()
                    last_launch_time = current_time
                    break
        
        # 显示提示文字
        font = pygame.font.Font(None, 24)
        text = font.render("按ESC键退出", True, WHITE)
        text_rect = text.get_rect(bottomright=(WIDTH-10, HEIGHT-10))
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main() 