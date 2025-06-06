import pygame
import random
import math

# ============================================
# 게임 초기화 및 기본 설정
# ============================================
pygame.init()  # 파이게임 시작!

# 화면 크기 설정
SCREEN_WIDTH = 800   # 가로 800픽셀
SCREEN_HEIGHT = 600  # 세로 600픽셀
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaxyan Shooter")  # 게임 제목

# 색상 정의 (RGB 값으로 색깔 만들기)
BLACK = (0, 0, 0)       # 검정색 - 배경용
WHITE = (255, 255, 255) # 흰색 - 텍스트용
RED = (255, 0, 0)       # 빨간색 - 적과 적 총알용
GREEN = (0, 255, 0)     # 초록색 - 플레이어와 플레이어 총알용
BLUE = (0, 0, 255)      # 파란색 - 강화된 플레이어용
YELLOW = (255, 255, 0)  # 노란색 - UI와 엔진 불꽃용
PURPLE = (255, 0, 255)  # 보라색 - 예비용

# ============================================
# 플레이어 클래스 (우리가 조종하는 우주선)
# ============================================
class Player:
    def __init__(self):
        """플레이어 초기 설정"""
        self.x = SCREEN_WIDTH // 2      # 화면 가운데서 시작
        self.y = SCREEN_HEIGHT - 80     # 화면 아래쪽에 위치
        self.width = 40                 # 우주선 가로 크기
        self.height = 30                # 우주선 세로 크기
        self.speed = 5                  # 이동 속도
        self.health = 3                 # HP력
        self.max_health = 3             # 최대 HP력
        self.bullet_power = 1           # 총알 파워 (1: 단발, 2: 더블샷)
        
    def move(self, keys):
        """키보드 입력으로 우주선 이동"""
        # 왼쪽 화살표: 왼쪽으로 이동 (화면 밖으로 나가지 않게 체크)
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        # 오른쪽 화살표: 오른쪽으로 이동
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        # 위쪽 화살표: 위로 이동
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        # 아래쪽 화살표: 아래로 이동
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
    
    def shoot(self):
        """총알 발사 (업그레이드에 따라 단발 또는 더블샷)"""
        bullets = []
        if self.bullet_power == 1:
            # 기본 단발: 우주선 가운데서 총알 1개 발사
            bullets.append(Bullet(self.x + self.width//2, self.y))
        elif self.bullet_power == 2:
            # 더블샷: 우주선 양쪽에서 총알 2개 발사
            bullets.append(Bullet(self.x + self.width//2 - 10, self.y))
            bullets.append(Bullet(self.x + self.width//2 + 10, self.y))
        return bullets
    
    def draw(self, screen):
        """우주선을 화면에 그리기"""
        # 우주선 모양을 삼각형으로 그리기 (꼭짓점들의 좌표)
        points = [
            (self.x + self.width//2, self.y),                    # 앞쪽 뾰족한 부분
            (self.x, self.y + self.height),                      # 왼쪽 뒤
            (self.x + self.width//4, self.y + self.height - 5),  # 왼쪽 안쪽
            (self.x + 3*self.width//4, self.y + self.height - 5),# 오른쪽 안쪽
            (self.x + self.width, self.y + self.height)          # 오른쪽 뒤
        ]
        # Power Up Shot 상태에 따라 색상 변경 (강화되면 파란색)
        color = BLUE if self.bullet_power == 2 else GREEN
        pygame.draw.polygon(screen, color, points)
        
        # 엔진 불꽃 효과 (뒤쪽에 작은 노란 원)
        pygame.draw.circle(screen, YELLOW, (self.x + self.width//2, self.y + self.height + 5), 3)

# ============================================
# 총알 클래스 (플레이어와 적이 쏘는 총알)
# ============================================
class Bullet:
    def __init__(self, x, y, direction=1):
        """총알 초기 설정"""
        self.x = x                      # 총알 x 좌표
        self.y = y                      # 총알 y 좌표
        self.width = 3                  # 총알 가로 크기
        self.height = 10                # 총알 세로 크기
        self.speed = 7 * direction      # 총알 속도 (direction: 1=위로, -1=아래로)
        # 총알 색상 (플레이어=초록, 적=빨강)
        self.color = GREEN if direction == 1 else RED
        
    def move(self):
        """총알 이동"""
        self.y -= self.speed  # y좌표를 변경해서 총알 이동
        
    def draw(self, screen):
        """총알을 화면에 그리기 (작은 사각형)"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
    def is_off_screen(self):
        """총알이 화면 밖으로 나갔는지 확인"""
        return self.y < 0 or self.y > SCREEN_HEIGHT

# ============================================
# 적 클래스 (우리가 물리쳐야 할 적 우주선)
# ============================================
class Enemy:
    def __init__(self):
        """적 초기 설정"""
        self.x = random.randint(0, SCREEN_WIDTH - 30)  # 화면 위쪽 랜덤 위치에서 시작
        self.y = random.randint(-100, -40)             # 화면 위쪽 밖에서 시작
        self.width = 30                                # 적 가로 크기
        self.height = 25                               # 적 세로 크기
        self.speed = random.randint(2, 4)              # 이동 속도 (랜덤)
        self.shoot_timer = random.randint(60, 180)     # 총알 발사 타이머
        self.move_pattern = random.choice(['straight', 'zigzag'])  # 이동 패턴 선택
        self.zigzag_timer = 0                          # 지그재그 이동용 타이머
        
    def move(self):
        """적 이동 (패턴에 따라 다르게 이동)"""
        if self.move_pattern == 'straight':
            # 직선 이동: 그냥 아래로 내려옴
            self.y += self.speed
        elif self.move_pattern == 'zigzag':
            # 지그재그 이동: 아래로 내려오면서 좌우로 흔들림
            self.y += self.speed
            self.zigzag_timer += 1
            if self.zigzag_timer % 30 < 15:  # 15프레임마다 방향 바꿈
                self.x += 1  # 오른쪽으로
            else:
                self.x -= 1  # 왼쪽으로
                
        # 화면 경계 체크 (적이 화면 밖으로 나가지 않게)
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            
    def draw(self, screen):
        """적을 화면에 그리기 (거꾸로 된 삼각형 모양)"""
        points = [
            (self.x + self.width//2, self.y + self.height),  # 아래쪽 뾰족한 부분
            (self.x, self.y),                                # 왼쪽 위
            (self.x + self.width//4, self.y + 5),            # 왼쪽 안쪽
            (self.x + 3*self.width//4, self.y + 5),          # 오른쪽 안쪽
            (self.x + self.width, self.y)                    # 오른쪽 위
        ]
        pygame.draw.polygon(screen, RED, points)  # 빨간색으로 그리기
        
    def is_off_screen(self):
        """적이 화면 아래로 나갔는지 확인"""
        return self.y > SCREEN_HEIGHT
        
    def should_shoot(self):
        """적이 총알을 쏠 때인지 확인"""
        self.shoot_timer -= 1  # 타이머 감소
        if self.shoot_timer <= 0:
            # 타이머가 0이 되면 총알 발사하고 타이머 리셋
            self.shoot_timer = random.randint(120, 240)
            return True
        return False

# ============================================
# 별 배경 클래스 (우주 느낌을 위한 움직이는 별들)
# ============================================
class Star:
    def __init__(self):
        """별 초기 설정"""
        self.x = random.randint(0, SCREEN_WIDTH)   # 화면 어디든 랜덤 위치
        self.y = random.randint(0, SCREEN_HEIGHT)  # 화면 어디든 랜덤 위치
        self.speed = random.randint(1, 3)          # 별마다 다른 속도
        
    def move(self):
        """별 이동 (아래로 떨어지는 효과)"""
        self.y += self.speed
        # 별이 화면 아래로 나가면 다시 위쪽에서 시작
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, screen):
        """별을 화면에 그리기 (작은 흰 점)"""
        pygame.draw.circle(screen, WHITE, (self.x, self.y), 1)

# ============================================
# 충돌 검사 함수 (두 사각형이 겹치는지 확인)
# ============================================
def check_collision(rect1_x, rect1_y, rect1_w, rect1_h, rect2_x, rect2_y, rect2_w, rect2_h):
    """두 사각형이 충돌했는지 확인하는 함수"""
    return (rect1_x < rect2_x + rect2_w and      # 왼쪽 경계 체크
            rect1_x + rect1_w > rect2_x and      # 오른쪽 경계 체크
            rect1_y < rect2_y + rect2_h and      # 위쪽 경계 체크
            rect1_y + rect1_h > rect2_y)         # 아래쪽 경계 체크

# ============================================
# 메인 게임 함수 (게임의 핵심 루프)
# ============================================
def main():
    clock = pygame.time.Clock()  # 게임 속도 조절용 시계
    
    # ========================================
    # 게임 객체들 생성
    # ========================================
    player = Player()          # 플레이어 우주선
    bullets = []              # 플레이어가 쏜 총알들
    enemy_bullets = []        # 적들이 쏜 총알들
    enemies = []              # 적 우주선들
    stars = []                # 배경 별들
    
    # 별 배경 50개 만들기
    for _ in range(50):
        stars.append(Star())
    
    # ========================================
    # 게임 변수들 (Score, Level, Coins 등)
    # ========================================
    score = 0                 # 현재 Score
    coins = 0                 # Coins
    level = 1                 # 현재 Level
    enemy_spawn_timer = 0     # 적 생성 타이머
    shoot_timer = 0           # 연속 발사용 타이머
    shoot_delay = 10          # 총알 발사 간격 (10프레임마다 발사)
    game_over = False         # 게임 오버 상태
    show_shop = False         # SHOP 열림 상태
    font = pygame.font.Font(None, 36)      # 큰 글씨용 폰트
    shop_font = pygame.font.Font(None, 28) # SHOP용 폰트
    
    # ========================================
    # 메인 게임 루프 (게임이 실행되는 동안 계속 반복)
    # ========================================
    running = True
    while running:
        # ====================================
        # 이벤트 처리 (키보드, 마우스 입력 등)
        # ====================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # X버튼 클릭하면 게임 종료
                running = False
            elif event.type == pygame.KEYDOWN:  # 키를 눌렀을 때
                if event.key == pygame.K_s and not game_over:
                    # S키: SHOP 열기/닫기
                    show_shop = not show_shop
                elif event.key == pygame.K_r and game_over:
                    # R키: 게임 재시작 (게임 오버일 때만)
                    player = Player()
                    bullets = []
                    enemy_bullets = []
                    enemies = []
                    score = 0
                    coins = 0
                    level = 1
                    shoot_timer = 0
                    show_shop = False
                    game_over = False
                elif show_shop and event.key == pygame.K_1:
                    # 1키: Restore Health 구매 (SHOP에서만, 5Coins, 체력이 최대가 아닐 때)
                    if coins >= 5 and player.health < player.max_health:
                        coins -= 5
                        player.health += 1
                elif show_shop and event.key == pygame.K_2:
                    # 2키: Power Up Shot 구매 (SHOP에서만, 10Coins, 아직 업그레이드 안했을 때)
                    if coins >= 10 and player.bullet_power == 1:
                        coins -= 10
                        player.bullet_power = 2
        
        # ====================================
        # 게임 로직 처리 (게임 오버가 아니고 SHOP이 열려있지 않을 때)
        # ====================================
        if not game_over and not show_shop:
            # 플레이어 이동 (방향키 입력 확인)
            keys = pygame.key.get_pressed()
            player.move(keys)
            
            # 연속 총알 발사 처리 (스페이스바를 누르고 있는 동안)
            if keys[pygame.K_SPACE]:
                shoot_timer += 1
                if shoot_timer >= shoot_delay:  # 설정된 간격마다 총알 발사
                    new_bullets = player.shoot()
                    bullets.extend(new_bullets)
                    shoot_timer = 0  # 타이머 리셋
            else:
                shoot_timer = 0  # 스페이스바를 누르지 않으면 타이머 리셋
            
            # Level 계산 (Score 500점마다 Level 1씩 증가, 최대 10Level)
            level = min(10, (score // 500) + 1)
            
            # 적 생성 (Level이 높을수록 적이 더 자주 나타남)
            enemy_spawn_timer += 1
            spawn_rate = max(30, 90 - (level - 1) * 7)  # Level업마다 생성 속도 증가
            if enemy_spawn_timer > spawn_rate:
                enemies.append(Enemy())
                enemy_spawn_timer = 0
            
            # 적들 이동 및 총알 발사
            for enemy in enemies[:]:  # [:] 는 리스트 복사 (반복 중 수정 방지)
                enemy.move()
                if enemy.is_off_screen():  # 적이 화면 밖으로 나가면 제거
                    enemies.remove(enemy)
                elif enemy.should_shoot():  # 적이 총알 쏠 시간이면 발사
                    enemy_bullets.append(Bullet(enemy.x + enemy.width//2, enemy.y + enemy.height, -1))
            
            # ================================
            # 충돌 검사들
            # ================================
            
            # 1. 플레이어 총알과 적 충돌
            for bullet in bullets[:]:
                for enemy in enemies[:]:
                    if check_collision(bullet.x, bullet.y, bullet.width, bullet.height,
                                     enemy.x, enemy.y, enemy.width, enemy.height):
                        bullets.remove(bullet)  # 총알 제거
                        enemies.remove(enemy)   # 적 제거
                        score += 10             # Score 증가
                        
                        # 10% 확률로 Coins 획득 (1~100 중 1~10이면 Coins 획득)
                        if random.randint(1, 100) <= 10:
                            coins += 1
                        break  # 한 총알은 한 적만 맞출 수 있음
            
            # 2. 적 총알과 플레이어 충돌
            for bullet in enemy_bullets[:]:
                if check_collision(bullet.x, bullet.y, bullet.width, bullet.height,
                                 player.x, player.y, player.width, player.height):
                    enemy_bullets.remove(bullet)  # 총알 제거
                    player.health -= 1            # 플레이어 체력 감소
                    if player.health <= 0:        # 체력이 0이 되면 게임 오버
                        game_over = True
            
            # 3. 적과 플레이어 직접 충돌
            for enemy in enemies[:]:
                if check_collision(enemy.x, enemy.y, enemy.width, enemy.height,
                                 player.x, player.y, player.width, player.height):
                    enemies.remove(enemy)  # 적 제거
                    player.health -= 1     # 플레이어 체력 감소
                    if player.health <= 0: # 체력이 0이 되면 게임 오버
                        game_over = True
        
        # ====================================
        # 총알과 적 이동 (SHOP이 열려있지 않을 때만)
        # ====================================
        if not show_shop:
            # 플레이어 총알들 이동
            for bullet in bullets[:]:
                bullet.move()
                if bullet.is_off_screen():  # 총알이 화면 밖으로 나가면 제거
                    bullets.remove(bullet)
            
            # 적 총알들 이동
            for bullet in enemy_bullets[:]:
                bullet.move()
                if bullet.is_off_screen():  # 총알이 화면 밖으로 나가면 제거
                    enemy_bullets.remove(bullet)
        
        # 별 배경은 항상 움직임 (SHOP이 열려도 계속 움직여서 시각 효과 유지)
        for star in stars:
            star.move()
        
        # ====================================
        # 화면 그리기
        # ====================================
        screen.fill(BLACK)  # 화면을 검정색으로 지우기
        
        # 배경 별들 그리기
        for star in stars:
            star.draw(screen)
        
        if show_shop:
            # ================================
            # SHOP 화면 그리기
            # ================================
            # 반투명 검정 배경 (게임 화면을 약간 어둡게)
            shop_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            shop_bg.set_alpha(180)  # 투명도 설정
            shop_bg.fill(BLACK)
            screen.blit(shop_bg, (0, 0))
            
            # SHOP 제목
            shop_title = font.render("=== SHOP ===", True, YELLOW)
            screen.blit(shop_title, (SCREEN_WIDTH//2 - 80, 100))
            
            # 현재 Coins 표시
            coin_text = shop_font.render(f"Coins: {coins}", True, WHITE)
            screen.blit(coin_text, (SCREEN_WIDTH//2 - 70, 150))
            
            # SHOP 아이템 1: Restore Health
            # 구매 가능하면 초록색, 불가능하면 빨간색으로 표시
            item1_color = GREEN if coins >= 5 and player.health < player.max_health else RED
            item1_text = shop_font.render("1. Restore Health (5 Coins)", True, item1_color)
            item1_status = f"HP: {player.health}/{player.max_health}"
            item1_status_text = pygame.font.Font(None, 20).render(item1_status, True, WHITE)
            screen.blit(item1_text, (SCREEN_WIDTH//2 - 100, 200))
            screen.blit(item1_status_text, (SCREEN_WIDTH//2 - 80, 220))
            
            # SHOP 아이템 2: Power Up Shot
            item2_color = GREEN if coins >= 10 and player.bullet_power == 1 else RED
            item2_text = shop_font.render("2. Power Up Shot (10 Coins)", True, item2_color)
            item2_status = "Already Upgraded" if player.bullet_power == 2 else "Double Shot Available"
            item2_status_text = pygame.font.Font(None, 20).render(item2_status, True, WHITE)
            screen.blit(item2_text, (SCREEN_WIDTH//2 - 100, 260))
            screen.blit(item2_status_text, (SCREEN_WIDTH//2 - 80, 280))
            
            # SHOP 조작법 안내
            close_text = shop_font.render("S Key: Close Shop", True, WHITE)
            buy_text = pygame.font.Font(None, 24).render("Use Number Keys to Buy", True, WHITE)
            screen.blit(close_text, (SCREEN_WIDTH//2 - 70, 350))
            screen.blit(buy_text, (SCREEN_WIDTH//2 - 60, 380))
            
        elif not game_over:
            # ================================
            # 게임 진행 중 화면 그리기
            # ================================
            
            # 플레이어 우주선 그리기
            player.draw(screen)
            
            # 모든 총알들 그리기
            for bullet in bullets:
                bullet.draw(screen)
            for bullet in enemy_bullets:
                bullet.draw(screen)
                
            # 모든 적들 그리기
            for enemy in enemies:
                enemy.draw(screen)
            
            # ============================
            # 게임 정보 UI 그리기
            # ============================
            score_text = font.render(f"Score: {score}", True, WHITE)
            health_text = font.render(f"HP: {player.health}", True, WHITE)
            level_text = font.render(f"Level: {level}/10", True, YELLOW)
            coins_text = font.render(f"Coins: {coins}", True, YELLOW)
            
            screen.blit(score_text, (10, 10))    # 왼쪽 위
            screen.blit(health_text, (10, 50))
            screen.blit(level_text, (10, 90))
            screen.blit(coins_text, (10, 130))
            
            # 다음 Level까지 필요한 Score 표시 (오른쪽 위)
            if level < 10:
                next_level_score = level * 500
                remaining_score = next_level_score - score
                next_level_text = pygame.font.Font(None, 24).render(f"Next Level: {remaining_score} points", True, WHITE)
                screen.blit(next_level_text, (SCREEN_WIDTH - 230, 10))
            else:
                # 최고 Level 달성 시
                max_level_text = pygame.font.Font(None, 24).render("Max Level!", True, RED)
                screen.blit(max_level_text, (SCREEN_WIDTH - 120, 10))
            
            # 조작법 표시 (화면 아래)
            control_font = pygame.font.Font(None, 24)
            control_text = control_font.render("Arrow Keys: Move, Space: Shoot, S: Shop", True, WHITE)
            screen.blit(control_text, (10, SCREEN_HEIGHT - 30))
            
            # Power Up Shot 상태 표시 (오른쪽 위)
            if player.bullet_power == 2:
                power_text = pygame.font.Font(None, 20).render("Double Shot Active!", True, BLUE)
                screen.blit(power_text, (SCREEN_WIDTH - 150, 50))
        
        else:
            # ================================
            # 게임 오버 화면 그리기
            # ================================
            game_over_text = font.render("Game Over!", True, RED)
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            final_level_text = font.render(f"Level Reached: {level}/10", True, YELLOW)
            final_coins_text = font.render(f"Coins Earned: {coins}", True, YELLOW)
            restart_text = font.render("Press R to Restart", True, WHITE)
            
            # 화면 가운데에 게임 오버 정보 표시
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 80))
            screen.blit(final_score_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 40))
            screen.blit(final_level_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 10))
            screen.blit(final_coins_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 50))
        
        # 화면 업데이트 (그린 것들을 실제로 보여주기)
        pygame.display.flip()
        
        # 60FPS로 게임 속도 제한 (1초에 60번 반복)
        clock.tick(60)
    
    # 게임 종료
    pygame.quit()

# ============================================
# 게임 시작! (이 파일을 직접 실행했을 때만 게임 시작)
# ============================================
if __name__ == "__main__":
    main()
