import pygame
import sys
import random

# --- INITIAL SETUP ---
pygame.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ashvaka Smristi: Molecular Physics Kernel")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

# --- PARAMETER PASSING FROM STREAMLIT ---
temp_val = float(sys.argv[1]) if len(sys.argv) > 1 else 37
ext_count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
int_count = int(sys.argv[3]) if len(sys.argv) > 3 else 20
mode = sys.argv[4] if len(sys.argv) > 4 else "Passive"
voltage_val = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0

# --- COLORS ---
COLOR_BG = (15, 5, 5) 
COLOR_LIPID = (220, 180, 130) 
COLOR_PROTEIN = (52, 152, 219) 

# --- SPECIES CONFIGURATION ---
SPECIES = {
    "Water": {"color": (52, 152, 219), "radius": 3, "mode": "Passive"},
    "Oxygen": {"color": (241, 196, 15), "radius": 3, "mode": "Passive"},
    "Glucose": {"color": (46, 204, 113), "radius": 6, "mode": "Facilitated"},
    "Sodium": {"color": (230, 126, 34), "radius": 4, "mode": "Active"},
    "Potassium": {"color": (155, 89, 182), "radius": 4, "mode": "Active"},
    "Protein": {"color": (231, 76, 60), "radius": 8, "mode": "Blocked"}
}

# --- CAMERA STATE ---
def reset_cam(): return 1.0, WIDTH//2, HEIGHT//2
zoom, cam_x, cam_y = reset_cam()

class Molecule:
    def __init__(self, species_name, side):
        self.name = species_name
        config = SPECIES[species_name]
        self.color = config["color"]
        self.radius = config["radius"]
        self.type_mode = config["mode"]
        self.selected = False
        
        self.x = random.randint(50, WIDTH-50)
        self.y = random.randint(50, 250) if side == "ext" else random.randint(380, 600)
        
        # Velocity scales with temperature
        base_speed = (temp_val / 25) + 1
        self.vx = random.uniform(-base_speed, base_speed)
        self.vy = random.uniform(-base_speed, base_speed)

    def update(self):
        nx, ny = self.x + self.vx, self.y + self.vy
        in_channel = 400 < nx < 500
        hitting_membrane = 290 < ny < 340
        
        if hitting_membrane:
            # Active transport logic
            if self.type_mode == "Active" and mode == "Active (ATP Required)":
                if in_channel: self.y = ny 
                else: self.vy *= -1
            # Facilitated/Passive logic
            elif (self.type_mode == "Passive" or self.type_mode == "Facilitated") and in_channel:
                self.y = ny
            # Blocked (Proteins) or general rejection
            else:
                self.vy *= -1
        else:
            self.x, self.y = nx, ny

        if self.x < 0 or self.x > WIDTH: self.vx *= -1
        if self.y < 0 or self.y > HEIGHT: self.vy *= -1

    def check_click(self, mouse_pos, zoom, off_x, off_y):
        sx = self.x * zoom + off_x
        sy = self.y * zoom + off_y
        dist = ((mouse_pos[0] - sx)**2 + (mouse_pos[1] - sy)**2)**0.5
        return dist < (self.radius * zoom + 5)

# --- INITIALIZATION ---
mols = []
for _ in range(ext_count):
    mols.append(Molecule(random.choice(["Water", "Oxygen", "Glucose", "Sodium"]), "ext"))
for _ in range(int_count):
    mols.append(Molecule(random.choice(["Water", "Potassium", "Protein"]), "int"))

selected_mol = None

# --- MAIN RENDER LOOP ---
while True:
    screen.fill(COLOR_BG)
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if selected_mol: selected_mol.selected = False
            selected_mol = None
            for m in mols:
                if m.check_click(mouse_pos, zoom, cam_x - (WIDTH//2)*zoom, cam_y - (HEIGHT//2)*zoom):
                    m.selected = True
                    selected_mol = m
                    break

    # Navigation Controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]: zoom, cam_x, cam_y = reset_cam()
    if keys[pygame.K_EQUALS]: zoom += 0.02
    if keys[pygame.K_MINUS]: zoom = max(0.4, zoom - 0.02)
    if keys[pygame.K_LEFT]: cam_x += 10
    if keys[pygame.K_RIGHT]: cam_x -= 10
    if keys[pygame.K_UP]: cam_y += 10
    if keys[pygame.K_DOWN]: cam_y -= 10

    off_x = cam_x - (WIDTH//2) * zoom
    off_y = cam_y - (HEIGHT//2) * zoom

    # 1. Draw Bilayer

    for x in range(-200, WIDTH+200, 20):
        if 400 < x < 500: continue 
        zx = x * zoom + off_x
        zy1, zy2 = 295 * zoom + off_y, 335 * zoom + off_y
        pygame.draw.circle(screen, COLOR_LIPID, (int(zx), int(zy1)), int(6*zoom))
        pygame.draw.circle(screen, COLOR_LIPID, (int(zx), int(zy2)), int(6*zoom))

    # 2. Draw Protein Channel
    
    pygame.draw.rect(screen, COLOR_PROTEIN, (400*zoom+off_x, 280*zoom+off_y, 100*zoom, 70*zoom), 3)
    
    # 3. Update & Draw Molecules
    # 3. Update & Draw Molecules
    for m in mols:
        m.update()
        mx, my = m.x * zoom + off_x, m.y * zoom + off_y
        
        # Draw the molecule
        pygame.draw.circle(screen, m.color, (int(mx), int(my)), int(m.radius * zoom))
        
        # LABELING: If selected, show detailed info box
        if m.selected:
            # Highlight ring
            pygame.draw.circle(screen, (255, 255, 255), (int(mx), int(my)), int((m.radius + 4) * zoom), 2)
            
            # Info Box Background
            info_rect = pygame.Rect(int(mx) + 15, int(my) - 40, 160, 65)
            pygame.draw.rect(screen, (20, 20, 20), info_rect) # Darker box for contrast
            pygame.draw.rect(screen, (255, 255, 255), info_rect, 1) # White border
            
            # Text Labels
            name_lbl = font.render(f"ID: {m.name}", True, m.color)
            mode_lbl = font.render(f"Path: {m.type_mode}", True, (200, 200, 200))
            side_lbl = font.render("Side: Extracellular" if m.y < 300 else "Side: Intracellular", True, (150, 150, 150))
            
            screen.blit(name_lbl, (int(mx) + 20, int(my) - 38))
            screen.blit(mode_lbl, (int(mx) + 20, int(my) - 22))
            screen.blit(side_lbl, (int(mx) + 20, int(my) - 6))
    # 4. HUD
    pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, 40))
    hud_text = f"Mode: {mode} | Zoom: {zoom:.1f}x"
    if "Active" in mode: hud_text += f" | Potential: {voltage_val} mV"
    screen.blit(font.render(hud_text, True, (255, 255, 255)), (15, 10))

    pygame.display.flip()
    clock.tick(60)