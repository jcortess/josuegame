
"""
Josué English Adventure - Pygame Knight Edition

Run:
    pip install pygame
    python josue_english_adventure_pygame_knight.py
"""

import json
import os
import random
import sys
from dataclasses import dataclass

import pygame


WIDTH, HEIGHT = 1100, 720
FPS = 60
SAVE_FILE = "josue_pygame_save.json"
QUESTIONS_PER_LEVEL = 2

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
NAVY = (30, 59, 91)
BLUE = (90, 169, 230)
LIGHT_BLUE = (220, 236, 255)
GREEN = (94, 193, 130)
RED = (210, 85, 85)
GOLD = (232, 191, 77)
PURPLE = (132, 91, 181)
GRAY = (110, 120, 140)
DARK = (40, 48, 60)
PANEL = (248, 251, 255)
SILVER = (196, 204, 216)
STEEL = (126, 139, 159)
BROWN = (120, 78, 48)


@dataclass
class Door:
    rect: pygame.Rect
    text: str
    is_correct: bool


class EnglishAdventureGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Josué English Adventure - Knight Edition")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_xl = pygame.font.SysFont("arial", 44, bold=True)
        self.font_l = pygame.font.SysFont("arial", 30, bold=True)
        self.font_m = pygame.font.SysFont("arial", 24)
        self.font_s = pygame.font.SysFont("arial", 18)

        self.running = True
        self.scene = "menu"
        self.player_name = "Josué"
        self.hero_style = "knight"
        self.score = 0
        self.high_score = 0
        self.level_index = 0
        self.question_index = 0
        self.lives = 3
        self.total_correct = 0
        self.total_questions = 0
        self.missed_questions = []
        self.weak_topics = {}
        self.badges = []
        self.message = ""
        self.message_timer = 0
        self.timer_mode = False
        self.question_time_limit = 20
        self.question_time_left = self.question_time_limit
        self.last_tick = 0
        self.boss_battle = False
        self.result_lines = []
        self.final_rank = ""
        self.level_report = []
        self.level_report_title = ""
        self.pending_next_scene = None
        self.game_level_summaries = []
        self.last_run_report_text = ""
        self.monster_mood = "idle"
        self.monster_effect_timer = 0
        self.monster_hp = 0
        self.monster_max_hp = 0

        self.hero = pygame.Rect(120, HEIGHT - 150, 64, 84)
        self.hero_speed = 5
        self.move_x = 0
        self.move_y = 0
        self.anim_time = 0
        self.facing = 1  # 1 right, -1 left

        self.doors = []
        self.stars = self.make_stars(40)
        self.menu_buttons = []
        self.levels = self.build_levels()
        self.boss_questions = []

        self.load_progress()
        self.build_menu_buttons()

    def build_levels(self):
        question_file = "question_bank_20_per_topic.json"
        if not os.path.exists(question_file):
            raise FileNotFoundError(f"Question bank not found: {question_file}")

        try:
            with open(question_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            levels = data.get("levels", [])
            if not levels:
                raise ValueError("No levels found in question bank")

            prepared_levels = []
            for level in levels:
                questions = level.get("questions", [])
                if len(questions) < QUESTIONS_PER_LEVEL:
                    raise ValueError(f"Level '{level.get('name', 'Unknown')}' has fewer than QUESTIONS_PER_LEVEL variable questions.")
                selected_questions = random.sample(questions, QUESTIONS_PER_LEVEL)
                prepared_level = dict(level)
                prepared_level["questions"] = selected_questions
                prepared_levels.append(prepared_level)

            return prepared_levels
        except Exception as e:
            raise RuntimeError(f"Error loading question bank: {e}")

    def make_stars(self, count):
        return [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)] for _ in range(count)]

    def build_menu_buttons(self):
        self.menu_buttons = [
            ("Start Adventure", pygame.Rect(WIDTH // 2 - 180, 300, 360, 60)),
            ("Toggle Timer: OFF", pygame.Rect(WIDTH // 2 - 180, 380, 360, 60)),
            ("Change Hero", pygame.Rect(WIDTH // 2 - 180, 460, 360, 60)),
            ("Quit", pygame.Rect(WIDTH // 2 - 180, 540, 360, 60)),
        ]

    def load_progress(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.high_score = data.get("high_score", 0)
            self.badges = data.get("badges", [])
            self.player_name = data.get("player_name", self.player_name)
            self.hero_style = data.get("hero_style", self.hero_style)
        except Exception:
            pass

    def save_progress(self):
        data = {
            "high_score": self.high_score,
            "badges": self.badges,
            "player_name": self.player_name,
            "hero_style": self.hero_style,
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def set_message(self, text, duration=1500):
        self.message = text
        self.message_timer = pygame.time.get_ticks() + duration

    def award_badge(self, badge):
        if badge not in self.badges:
            self.badges.append(badge)
            self.save_progress()
            self.set_message(f"Badge unlocked: {badge}", 2200)

    def reset_run(self):
        self.score = 0
        self.level_index = 0
        self.question_index = 0
        self.lives = 3
        self.total_correct = 0
        self.total_questions = 0
        self.missed_questions = []
        self.weak_topics = {}
        self.result_lines = []
        self.final_rank = ""
        self.level_report = []
        self.level_report_title = ""
        self.pending_next_scene = None
        self.game_level_summaries = []
        self.last_run_report_text = ""
        self.boss_battle = False
        self.move_x = 0
        self.move_y = 0
        self.monster_mood = "idle"
        self.monster_effect_timer = 0
        self.monster_hp = 5
        self.monster_max_hp = 5

    def current_level_pool(self):
        return self.boss_questions if self.boss_battle else self.levels[self.level_index]["questions"]

    def current_question(self):
        return self.current_level_pool()[self.question_index]

    def setup_question_scene(self):
        if self.question_index == 0:
            self.monster_max_hp = len(self.current_level_pool())
            self.monster_hp = len(self.current_level_pool())
        #self.monster_mood = "idle"
        options = self.current_question()["options"][:]
        random.shuffle(options)
        self.doors = []
        door_w, door_h = 280, 120
        positions = [(90, 420), (410, 420), (730, 420)]
        for i, opt in enumerate(options):
            rect = pygame.Rect(positions[i][0], positions[i][1], door_w, door_h)
            self.doors.append(Door(rect, opt, opt == self.current_question()["answer"]))
        self.hero.x = WIDTH // 2 - self.hero.width // 2
        self.hero.y = 300
        self.question_time_left = self.question_time_limit
        self.last_tick = pygame.time.get_ticks()
        self.scene = "question"

    def start_game(self):
        self.reset_run()
        self.scene = "level_intro"

    def start_boss_battle(self):
        pool = []
        for level in self.levels:
            pool.extend(level["questions"])
        self.boss_questions = random.sample(pool, min(10, len(pool)))
        self.boss_battle = True
        self.question_index = 0
        self.lives = 3
        self.scene = "boss_intro"

    def answer_current(self, door):
        q = self.current_question()
        self.total_questions += 1
        if door.is_correct:
            self.score += 15 if self.boss_battle else 10
            self.total_correct += 1
            self.monster_hp = max(0, self.monster_hp - 1)
            self.monster_mood = "hurt"
            self.monster_effect_timer = pygame.time.get_ticks() + 1200
            self.level_report.append({
                "question": q["question"],
                "your_answer": door.text,
                "correct_answer": q["answer"],
                "is_correct": True,
            })
            self.set_message("Correct! The monster is getting weaker!", 1000)
        else:
            self.lives -= 1
            self.missed_questions.append(q)
            self.weak_topics[q["topic"]] = self.weak_topics.get(q["topic"], 0) + 1
            self.monster_mood = "happy"
            self.monster_effect_timer = pygame.time.get_ticks() + 1200
            self.level_report.append({
                "question": q["question"],
                "your_answer": door.text,
                "correct_answer": q["answer"],
                "is_correct": False,
            })
            self.set_message(f"Wrong. The monster feels stronger! Correct: {q['answer']}", 1500)

        if self.lives <= 0:
            self.finish_run(False)
            return

        self.question_index += 1
        if self.question_index >= len(self.current_level_pool()):
            if self.boss_battle:
                self.finish_run(True)
            else:
                completed_level = self.levels[self.level_index]
                self.store_level_summary(completed_level["name"])
                next_scene = "boss_intro" if self.level_index + 1 >= len(self.levels) else "level_intro"
                self.level_index += 1
                self.question_index = 0
                if self.level_index == 1:
                    self.award_badge("Daily Hero")
                self.show_level_report(f"Level Report: {completed_level['name']}", next_scene)
        else:
            self.setup_question_scene()

    def handle_question_timeout(self):
        q = self.current_question()
        self.lives -= 1
        self.missed_questions.append(q)
        self.weak_topics[q["topic"]] = self.weak_topics.get(q["topic"], 0) + 1
        self.monster_mood = "happy"
        self.monster_effect_timer = pygame.time.get_ticks() + 1200
        self.level_report.append({
            "question": q["question"],
            "your_answer": "No answer (time up)",
            "correct_answer": q["answer"],
            "is_correct": False,
        })
        self.set_message(f"Time up! The monster feels stronger! Correct: {q['answer']}", 1400)
        if self.lives <= 0:
            self.finish_run(False)
            return
        self.question_index += 1
        if self.question_index >= len(self.current_level_pool()):
            if self.boss_battle:
                self.finish_run(True)
            else:
                completed_level = self.levels[self.level_index]
                self.store_level_summary(completed_level["name"])
                next_scene = "boss_intro" if self.level_index + 1 >= len(self.levels) else "level_intro"
                self.level_index += 1
                self.question_index = 0
                self.show_level_report(f"Level Report: {completed_level['name']}", next_scene)
        else:
            self.setup_question_scene()


    def show_level_report(self, title, next_scene):
        self.level_report_title = title
        self.pending_next_scene = next_scene
        self.scene = "level_report"


    def store_level_summary(self, title):
        correct = sum(1 for item in self.level_report if item["is_correct"])
        wrong = len(self.level_report) - correct
        self.game_level_summaries.append({
            "title": title,
            "correct": correct,
            "wrong": wrong,
        })

    def build_nutshell_report(self):
        accuracy = int((self.total_correct / self.total_questions) * 100) if self.total_questions else 0
        lines = []
        lines.append("======================================")
        lines.append("      JOSUE ENGLISH GAME REPORT")
        lines.append("======================================")
        lines.append(f"Player: {self.player_name}")
        lines.append(f"Final Score: {self.score} *")
        lines.append(f"Accuracy: {accuracy}%")
        lines.append(f"Total Correct: {self.total_correct}")
        lines.append(f"Total Questions: {self.total_questions}")
        lines.append(f"Final Rank: {self.final_rank}")
        lines.append(f"High Score: {self.high_score} *")
        lines.append("")
        lines.append("LEVEL SUMMARY")
        if self.game_level_summaries:
            for item in self.game_level_summaries:
                lines.append(f"- {item['title']}: {item['correct']} correct, {item['wrong']} wrong")
        else:
            lines.append("- No level data available")
        lines.append("")
        lines.append("WEAK TOPICS")
        if self.weak_topics:
            weak = sorted(self.weak_topics.items(), key=lambda x: (-x[1], x[0]))
            for topic, count in weak:
                lines.append(f"- {topic}: {count}")
        else:
            lines.append("- None")
        lines.append("")
        lines.append("BADGES")
        if self.badges:
            lines.append(", ".join(self.badges))
        else:
            lines.append("None")
        lines.append("======================================")
        self.last_run_report_text = "\n".join(lines)
        return self.last_run_report_text

    def save_nutshell_report(self):
        if not self.last_run_report_text:
            self.build_nutshell_report()
        safe_name = self.player_name.replace(" ", "_")
        filename = f"game_report_{safe_name}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.last_run_report_text)
        self.set_message(f"Report saved as {filename}", 2200)
        return filename

    def finish_run(self, reached_end):
        accuracy = int((self.total_correct / self.total_questions) * 100) if self.total_questions else 0
        if reached_end and self.boss_battle:
            self.final_rank = "ULTIMATE ENGLISH CHAMPION 👑"
            self.award_badge("Final Boss Winner")
        elif self.score >= 220:
            self.final_rank = "ENGLISH CHAMPION 🔥"
        elif self.score >= 170:
            self.final_rank = "SUPER STUDENT 🌟"
        else:
            self.final_rank = "BRAVE HERO 💪"

        if accuracy == 100 and self.total_questions > 0:
            self.award_badge("Accuracy Master")
        if self.score > self.high_score:
            self.high_score = self.score
            self.award_badge("New High Score")
        if self.missed_questions:
            self.award_badge("Practice Warrior")

        self.save_progress()
        self.build_nutshell_report()
        self.result_lines = [
            f"Player: {self.player_name}",
            f"Score: {self.score}",
            f"Accuracy: {accuracy}%",
            f"High Score: {self.high_score} ",
            f"Rank: {self.final_rank}",
            f"Badges: {', '.join(self.badges) if self.badges else 'None'}",
        ]
        if self.weak_topics:
            weak = sorted(self.weak_topics.items(), key=lambda x: (-x[1], x[0]))
            self.result_lines.append("Weak topics:")
            for topic, count in weak[:5]:
                self.result_lines.append(f"- {topic}: {count}")
        else:
            self.result_lines.append("Weak topics: None")
        self.scene = "results"

    def draw_background(self):
        #self.screen.fill((237, 244, 255))
        self.screen.fill((0, 0, 0))
        for star in self.stars:
            pygame.draw.circle(self.screen, WHITE, (star[0], star[1]), star[2])
            star[0] -= star[2]
            if star[0] < 0:
                star[0] = WIDTH
                star[1] = random.randint(0, HEIGHT)

    def draw_title(self, text, y=40, color=NAVY):
        surf = self.font_xl.render(text, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, y))
        self.screen.blit(surf, rect)

    def draw_panel(self, rect, color=PANEL, border=NAVY):
        pygame.draw.rect(self.screen, color, rect, border_radius=18)
        pygame.draw.rect(self.screen, border, rect, 3, border_radius=18)

    def draw_text_center(self, text, font, color, x, y):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(x, y))
        self.screen.blit(surf, rect)

    def wrap_text(self, text, font, width):
        words = text.split()
        lines, current = [], ""
        for word in words:
            test = current + (" " if current else "") + word
            if font.size(test)[0] <= width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw_multiline(self, text, font, color, x, y, width, center=True, line_gap=8):
        lines = self.wrap_text(text, font, width)
        cy = y
        for line in lines:
            surf = font.render(line, True, color)
            rect = surf.get_rect(center=(x, cy)) if center else surf.get_rect(topleft=(x, cy))
            self.screen.blit(surf, rect)
            cy += surf.get_height() + line_gap

    def draw_knight(self):
        x, y, w, h = self.hero
        moving = self.move_x != 0 or self.move_y != 0
        self.anim_time += 0.18 if moving else 0.05
        bob = int(3 * __import__("math").sin(self.anim_time * 2))
        leg_swing = int(6 * __import__("math").sin(self.anim_time * 4)) if moving else 0
        sword_swing = int(8 * __import__("math").sin(self.anim_time * 5)) if moving else 0

        helmet = pygame.Rect(x + 12, y + 2 + bob, 40, 28)
        visor = pygame.Rect(x + 22, y + 12 + bob, 20, 10)
        body = pygame.Rect(x + 16, y + 30 + bob, 32, 26)
        cape_points = [(x + 16, y + 34 + bob), (x + 4, y + 72 + bob), (x + 20, y + 70 + bob)]
        shield = pygame.Rect(x + (2 if self.facing == 1 else 42), y + 34 + bob, 18, 26)

        pygame.draw.ellipse(self.screen, SILVER, helmet)
        pygame.draw.ellipse(self.screen, STEEL, helmet, 2)
        pygame.draw.rect(self.screen, DARK, visor, border_radius=4)
        pygame.draw.rect(self.screen, STEEL, body, border_radius=6)
        pygame.draw.rect(self.screen, SILVER, body, 2, border_radius=6)
        pygame.draw.polygon(self.screen, RED, cape_points)
        pygame.draw.polygon(self.screen, (150, 40, 40), cape_points, 2)
        pygame.draw.ellipse(self.screen, BLUE, shield)
        pygame.draw.ellipse(self.screen, NAVY, shield, 2)
        pygame.draw.line(self.screen, GOLD, (shield.centerx, shield.y + 4), (shield.centerx, shield.bottom - 4), 2)
        pygame.draw.line(self.screen, GOLD, (shield.x + 4, shield.centery), (shield.right - 4, shield.centery), 2)

        torso_center_x = x + 32
        arm_y = y + 42 + bob
        sword_hand_x = torso_center_x + (16 * self.facing)
        pygame.draw.line(self.screen, STEEL, (torso_center_x - 10, arm_y), (x + 8, arm_y + 8), 5)
        pygame.draw.line(self.screen, STEEL, (torso_center_x + 10, arm_y), (sword_hand_x, arm_y + 6), 5)
        sword_tip_x = sword_hand_x + (28 * self.facing)
        sword_tip_y = arm_y - 18 + sword_swing
        pygame.draw.line(self.screen, SILVER, (sword_hand_x, arm_y + 6), (sword_tip_x, sword_tip_y), 4)
        pygame.draw.line(self.screen, BROWN, (sword_hand_x - 4 * self.facing, arm_y + 8), (sword_hand_x + 4 * self.facing, arm_y + 4), 4)

        hip_y = y + 56 + bob
        pygame.draw.line(self.screen, DARK, (torso_center_x - 6, hip_y), (torso_center_x - 8, y + 82 + bob + leg_swing), 5)
        pygame.draw.line(self.screen, DARK, (torso_center_x + 6, hip_y), (torso_center_x + 8, y + 82 + bob - leg_swing), 5)

    def draw_monster(self, monster_name, x, y, scale=1.0):
        t = pygame.time.get_ticks() / 220.0
        mood = self.monster_mood        

        if mood == "hurt":
            bob = int(7 * __import__("math").sin(t * 3))
            tint_add = 40
        elif mood == "happy":
            bob = int(2 * __import__("math").sin(t))
            tint_add = 0
        else:
            bob = int(4 * __import__("math").sin(t))
            tint_add = 0

        sx = int(90 * scale)
        sy = int(90 * scale)

        # HP bar
        if self.scene == "question":
            bar_w = int(110 * scale)
            bar_x = x
            bar_y = y - int(20 * scale)
            pygame.draw.rect(self.screen, (230, 230, 230), (bar_x, bar_y, bar_w, 10), border_radius=5)
            ratio = 0 if self.monster_max_hp == 0 else self.monster_hp / self.monster_max_hp
            pygame.draw.rect(self.screen, RED if ratio < 0.4 else GOLD if ratio < 0.7 else GREEN, (bar_x, bar_y, int(bar_w * ratio), 10), border_radius=5)
            pygame.draw.rect(self.screen, DARK, (bar_x, bar_y, bar_w, 10), 2, border_radius=5)

        def face(eye_y_offset=0):
            if mood == "happy":
                pygame.draw.arc(self.screen, BLACK, (x + int(20 * scale), y + int(18 * scale) + bob + eye_y_offset, int(16 * scale), int(10 * scale)), 3.4, 5.8, 2)
                pygame.draw.arc(self.screen, BLACK, (x + int(54 * scale), y + int(18 * scale) + bob + eye_y_offset, int(16 * scale), int(10 * scale)), 3.4, 5.8, 2)
            else:
                pygame.draw.circle(self.screen, WHITE, (x + int(28 * scale), y + int(28 * scale) + bob + eye_y_offset), int(8 * scale))
                pygame.draw.circle(self.screen, WHITE, (x + int(62 * scale), y + int(28 * scale) + bob + eye_y_offset), int(8 * scale))
                pygame.draw.circle(self.screen, BLACK, (x + int(28 * scale), y + int(28 * scale) + bob + eye_y_offset), int(3 * scale))
                pygame.draw.circle(self.screen, BLACK, (x + int(62 * scale), y + int(28 * scale) + bob + eye_y_offset), int(3 * scale))

            if mood == "hurt":
                pygame.draw.arc(self.screen, BLACK, (x + int(24 * scale), y + int(44 * scale) + bob, int(44 * scale), int(20 * scale)), 3.4, 5.8, 3)
                # tears
                pygame.draw.line(self.screen, BLUE, (x + int(24 * scale), y + int(36 * scale) + bob), (x + int(20 * scale), y + int(48 * scale) + bob), 2)
                pygame.draw.line(self.screen, BLUE, (x + int(66 * scale), y + int(36 * scale) + bob), (x + int(70 * scale), y + int(48 * scale) + bob), 2)
            elif mood == "happy":
                pygame.draw.arc(self.screen, BLACK, (x + int(24 * scale), y + int(42 * scale) + bob, int(44 * scale), int(18 * scale)), 0.2, 2.9, 3)
            else:
                pygame.draw.line(self.screen, BLACK, (x + int(28 * scale), y + int(52 * scale) + bob), (x + int(62 * scale), y + int(52 * scale) + bob), 3)

        if monster_name == "Routine Monster":
            body = pygame.Rect(x, y + bob, sx, sy)
            base = (min(255, GREEN[0] + tint_add), min(255, GREEN[1] + tint_add), min(255, GREEN[2] + tint_add))
            pygame.draw.ellipse(self.screen, base, body)
            pygame.draw.ellipse(self.screen, (40, 120, 60), body, 3)
            face()
            pygame.draw.line(self.screen, base, (x + int(10 * scale), y + int(45 * scale) + bob), (x - int(18 * scale), y + int(30 * scale) + bob), 6)
            pygame.draw.line(self.screen, base, (x + int(80 * scale), y + int(45 * scale) + bob), (x + int(108 * scale), y + int(30 * scale) + bob), 6)

        elif monster_name == "Now vs Every Day":
            body = pygame.Rect(x, y + bob, sx, sy)
            pygame.draw.rect(self.screen, PURPLE, body, border_radius=18)
            pygame.draw.rect(self.screen, (86, 52, 130), body, 3, border_radius=18)
            clock_r = pygame.Rect(x + int(18 * scale), y + int(16 * scale) + bob, int(54 * scale), int(54 * scale))
            pygame.draw.ellipse(self.screen, WHITE, clock_r)
            pygame.draw.ellipse(self.screen, NAVY, clock_r, 3)
            cx, cy = clock_r.center
            pygame.draw.line(self.screen, NAVY, (cx, cy), (cx, cy - int(14 * scale)), 3)
            pygame.draw.line(self.screen, NAVY, (cx, cy), (cx + int(10 * scale), cy), 3)
            pygame.draw.circle(self.screen, RED, (cx, cy), int(3 * scale))
            face()
            pygame.draw.line(self.screen, PURPLE, (x + int(6 * scale), y + int(22 * scale) + bob), (x - int(18 * scale), y + int(10 * scale) + bob), 5)
            pygame.draw.line(self.screen, PURPLE, (x + int(84 * scale), y + int(22 * scale) + bob), (x + int(108 * scale), y + int(10 * scale) + bob), 5)

        elif monster_name == "Yesterday Dragon":
            base = (255, min(255, 140 + tint_add), 80)
            pygame.draw.ellipse(self.screen, base, (x, y + int(16 * scale) + bob, int(95 * scale), int(58 * scale)))
            pygame.draw.polygon(self.screen, base, [(x + int(74 * scale), y + int(30 * scale) + bob), (x + int(118 * scale), y + int(8 * scale) + bob), (x + int(102 * scale), y + int(48 * scale) + bob)])
            pygame.draw.polygon(self.screen, (255, 190, 60), [(x + int(20 * scale), y + int(18 * scale) + bob), (x + int(34 * scale), y - int(8 * scale) + bob), (x + int(46 * scale), y + int(18 * scale) + bob)])
            pygame.draw.polygon(self.screen, (255, 190, 60), [(x + int(46 * scale), y + int(16 * scale) + bob), (x + int(60 * scale), y - int(10 * scale) + bob), (x + int(72 * scale), y + int(16 * scale) + bob)])
            face(-4)
            if mood == "hurt":
                pygame.draw.line(self.screen, BLUE, (x + int(84 * scale), y + int(36 * scale) + bob), (x + int(82 * scale), y + int(52 * scale) + bob), 2)
            pygame.draw.line(self.screen, RED, (x + int(106 * scale), y + int(32 * scale) + bob), (x + int(126 * scale), y + int(42 * scale) + bob), 6)

        elif monster_name == "When-While Wizard":
            pygame.draw.ellipse(self.screen, PURPLE, (x + int(18 * scale), y + int(8 * scale) + bob, int(55 * scale), int(28 * scale)))
            pygame.draw.rect(self.screen, PURPLE, (x + int(34 * scale), y + int(26 * scale) + bob, int(24 * scale), int(52 * scale)), border_radius=8)
            pygame.draw.polygon(self.screen, (106, 61, 154), [(x + int(46 * scale), y + int(42 * scale) + bob), (x + int(8 * scale), y + int(92 * scale) + bob), (x + int(84 * scale), y + int(92 * scale) + bob)])
            face(-6)
            pygame.draw.line(self.screen, BROWN, (x + int(80 * scale), y + int(20 * scale) + bob), (x + int(112 * scale), y - int(10 * scale) + bob), 5)
            orb_color = LIGHT_BLUE if mood != "happy" else GOLD
            pygame.draw.circle(self.screen, GOLD, (x + int(116 * scale), y - int(14 * scale) + bob), int(10 * scale))
            pygame.draw.circle(self.screen, orb_color, (x + int(116 * scale), y - int(14 * scale) + bob), int(5 * scale))

        elif monster_name == "Story Giant":
            pygame.draw.rect(self.screen, STEEL, (x + int(14 * scale), y + int(16 * scale) + bob, int(72 * scale), int(82 * scale)), border_radius=16)
            pygame.draw.rect(self.screen, SILVER, (x + int(14 * scale), y + int(16 * scale) + bob, int(72 * scale), int(82 * scale)), 3, border_radius=16)
            face(12)
            pygame.draw.rect(self.screen, RED if mood != "hurt" else BLUE, (x + int(22 * scale), y + int(62 * scale) + bob, int(56 * scale), int(12 * scale)), border_radius=6)
            pygame.draw.line(self.screen, STEEL, (x + int(24 * scale), y + int(98 * scale) + bob), (x + int(12 * scale), y + int(122 * scale) + bob), 6)
            pygame.draw.line(self.screen, STEEL, (x + int(76 * scale), y + int(98 * scale) + bob), (x + int(88 * scale), y + int(122 * scale) + bob), 6)

        else:
            pygame.draw.circle(self.screen, RED, (x + int(45 * scale), y + int(45 * scale) + bob), int(40 * scale))
            face()

    def draw_hud(self):
        pygame.draw.rect(self.screen, WHITE, (0, 0, WIDTH, 82))
        pygame.draw.line(self.screen, LIGHT_BLUE, (0, 82), (WIDTH, 82), 3)
        left = f"{self.player_name} | Score: {self.score}  | Lives: {'♥ ' * self.lives}"
        right = f"High Score: {self.high_score} "
        self.screen.blit(self.font_m.render(left, True, NAVY), (20, 22))
        right_surf = self.font_m.render(right, True, NAVY)
        self.screen.blit(right_surf, (WIDTH - right_surf.get_width() - 20, 22))
        if self.timer_mode and self.scene == "question":
            timer_text = f"⏳ {self.question_time_left}s"
            timer_surf = self.font_l.render(timer_text, True, RED)
            self.screen.blit(timer_surf, (WIDTH // 2 - timer_surf.get_width() // 2, 18))

    def draw_menu(self):
        self.draw_title("Josué English Adventure", 90)
        self.draw_text_center("Knight Edition", self.font_l, PURPLE, WIDTH // 2, 140)
        self.draw_text_center("Type to change player name", self.font_s, GRAY, WIDTH // 2, 175)
        self.draw_text_center(f"Player: {self.player_name}", self.font_m, DARK, WIDTH // 2, 205)
        self.draw_text_center("Hero: Animated Knight", self.font_m, DARK, WIDTH // 2, 238)
        self.draw_text_center(f"High Score: {self.high_score} ", self.font_m, PURPLE, WIDTH // 2, 268)

        self.menu_buttons[1] = ("Toggle Timer: ON" if self.timer_mode else "Toggle Timer: OFF", self.menu_buttons[1][1])
        self.menu_buttons[2] = ("Change Hero (Knight)", self.menu_buttons[2][1])

        for label, rect in self.menu_buttons:
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            color = BLUE if hovered else NAVY
            self.draw_panel(rect, color=color, border=WHITE)
            self.draw_text_center(label, self.font_l, WHITE, rect.centerx, rect.centery)

        self.hero.x, self.hero.y = WIDTH // 2 - 32, 610
        self.move_x = 1
        self.move_y = 0
        self.facing = 1
        self.draw_knight()
        self.move_x = 0

        badges_text = ", ".join(self.badges) if self.badges else "None yet"
        panel = pygame.Rect(150, 650, 800, 50)
        self.draw_panel(panel, color=WHITE, border=LIGHT_BLUE)
        self.draw_multiline(f"Badges: {badges_text}", self.font_s, DARK, WIDTH // 2, 664, 740)

    def draw_level_intro(self):
        level = self.levels[self.level_index]
        self.draw_title(f"Level {self.level_index + 1}: {level['name']}", 120)
        panel = pygame.Rect(170, 180, 760, 250)
        self.draw_panel(panel)
        self.draw_text_center(f"Boss: {level['boss']}", self.font_l, RED, WIDTH // 2, 240)
        self.draw_text_center(f"Topic: {level['topic']}", self.font_m, NAVY, WIDTH // 2, 290)
        self.draw_multiline("Press ENTER to begin. Beat all questions to move forward.", self.font_m, DARK, WIDTH // 2, 340, 600)
        self.draw_text_center("Use arrow keys to move in every direction.", self.font_s, GRAY, WIDTH // 2, 395)
        self.draw_monster(level['boss'], 770, 235, 1.0)

    def draw_boss_intro(self):
        self.draw_title("Final Boss Battle", 120, RED)
        panel = pygame.Rect(170, 180, 760, 250)
        self.draw_panel(panel, color=(255, 244, 246), border=RED)
        self.draw_multiline("10 mixed questions. 3 lives. This is the final test.", self.font_l, DARK, WIDTH // 2, 250, 650)
        self.draw_text_center("Press ENTER to start", self.font_l, RED, WIDTH // 2, 360)
        self.draw_text_center("No mercy. No excuses.", self.font_m, PURPLE, WIDTH // 2, 410)
        self.draw_monster("Story Giant", 760, 230, 1.15)

    def draw_question_scene(self):
        q = self.current_question()
        self.draw_hud()

        top_panel = pygame.Rect(90, 110, 920, 180)
        self.draw_panel(top_panel)
        self.draw_text_center(q["prompt"], self.font_m, PURPLE, WIDTH // 2, 145)
        self.draw_multiline(q["question"], self.font_l, DARK, WIDTH // 2, 195, 820)

        self.draw_text_center("Walk to a door and press ENTER or SPACE", self.font_s, GRAY, WIDTH // 2, 315)
        monster_name = "Story Giant" if self.boss_battle else self.levels[self.level_index]["boss"]
        #Posicion del mounstro
        self.draw_monster(monster_name, 80, 620, 0.9)

        mood_text = {
            "idle": "Monster is waiting...",
            "hurt": "Monster is crying and losing power!",
            "happy": "Monster is smiling and gaining confidence!",
        }.get(self.monster_mood, "Monster is waiting...")
        #Posicion del texto del mounstro
        self.draw_text_center(mood_text, self.font_s, RED if self.monster_mood == "happy" else BLUE if self.monster_mood == "hurt" else GRAY, 250, 620)

        for door in self.doors:
            color = BLUE
            if door.rect.colliderect(self.hero):
                color = GREEN
            self.draw_panel(door.rect, color=color, border=NAVY)
            self.draw_multiline(door.text, self.font_m, WHITE, door.rect.centerx, door.rect.centery - 8, door.rect.width - 20)

        self.draw_knight()


    def draw_level_report(self):
        self.draw_title(self.level_report_title or "Level Report", 95)
        panel = pygame.Rect(70, 140, 960, 500)
        self.draw_panel(panel)

        correct = sum(1 for item in self.level_report if item["is_correct"])
        wrong = len(self.level_report) - correct
        self.draw_text_center(f"Correct: {correct}   Wrong: {wrong}", self.font_l, NAVY, WIDTH // 2, 185)

        y = 235
        for idx, item in enumerate(self.level_report, start=1):
            status_color = GREEN if item["is_correct"] else RED
            status_text = "✓ Correct" if item["is_correct"] else "✗ Wrong"
            self.draw_multiline(f"{idx}. {item['question']}", self.font_s, DARK, WIDTH // 2, y, 860)
            y += 24
            self.draw_multiline(f"{status_text} | Your answer: {item['your_answer']} | Correct: {item['correct_answer']}", self.font_s, status_color, WIDTH // 2, y, 860)
            y += 34

        self.draw_text_center("Press ENTER to continue", self.font_m, PURPLE, WIDTH // 2, 605)

    def draw_results(self):
        self.draw_title("Mission Complete", 110)
        panel = pygame.Rect(120, 160, 860, 470)
        self.draw_panel(panel)
        self.draw_text_center(self.final_rank, self.font_l, RED if "CHAMPION" in self.final_rank else NAVY, WIDTH // 2, 210)

        y = 270
        for line in self.result_lines:
            self.draw_multiline(line, self.font_m, DARK, WIDTH // 2, y, 720)
            y += 40

        preview = self.last_run_report_text.split("\n")[:8] if self.last_run_report_text else []
        preview_y = 470
        for line in preview:
            self.draw_multiline(line, self.font_s, DARK, WIDTH // 2, preview_y, 760)
            preview_y += 22

        self.draw_text_center("Press S to save report | R to play again | ESC for menu", self.font_m, PURPLE, WIDTH // 2, 620)

    def update_timer(self):
        if not self.timer_mode or self.scene != "question":
            return
        now = pygame.time.get_ticks()
        if now - self.last_tick >= 1000:
            self.question_time_left -= 1
            self.last_tick = now
            if self.question_time_left <= 0:
                self.handle_question_timeout()

    def update_message(self):
        if self.message and pygame.time.get_ticks() > self.message_timer:
            self.message = ""

    def draw_message(self):
        if not self.message:
            return
        panel = pygame.Rect(WIDTH // 2 - 220, HEIGHT - 90, 440, 50)
        self.draw_panel(panel, color=(255, 252, 230), border=GOLD)
        self.draw_text_center(self.message, self.font_s, DARK, panel.centerx, panel.centery)

    def handle_menu_click(self, pos):
        for idx, (_, rect) in enumerate(self.menu_buttons):
            if rect.collidepoint(pos):
                if idx == 0:
                    self.start_game()
                elif idx == 1:
                    self.timer_mode = not self.timer_mode
                elif idx == 2:
                    self.set_message("Knight hero selected", 1000)
                elif idx == 3:
                    self.running = False

    def update_continuous_movement(self):
        if self.scene != "question":
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()

        target_x = mouse_x - self.hero.width // 2
        target_y = mouse_y - self.hero.height // 2

        dx = target_x - self.hero.x
        dy = target_y - self.hero.y

        self.move_x = 0
        self.move_y = 0

        if abs(dx) > 3:
            self.move_x = self.hero_speed if dx > 0 else -self.hero_speed
            self.facing = 1 if dx > 0 else -1

        if abs(dy) > 3:
            self.move_y = self.hero_speed if dy > 0 else -self.hero_speed

        self.hero.x += self.move_x
        self.hero.y += self.move_y

        self.hero.x = max(20, min(WIDTH - self.hero.width - 20, self.hero.x))
        self.hero.y = max(300, min(HEIGHT - self.hero.height - 20, self.hero.y))

    def handle_question_key(self, event):
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            for door in self.doors:
                if door.rect.colliderect(self.hero):
                    self.answer_current(door)
                    break
                    
    def handle_question_click(self, pos):
        for door in self.doors:
            if door.rect.collidepoint(pos):
                self.answer_current(door)
                break

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and self.scene == "menu":
                self.handle_menu_click(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and self.scene == "question":
                self.handle_question_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                if self.scene == "menu":
                    if event.key == pygame.K_RETURN:
                        self.start_game()
                    elif event.key == pygame.K_t:
                        self.timer_mode = not self.timer_mode
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.unicode.isprintable() and len(self.player_name) < 14 and event.unicode not in "\r\t":
                        self.player_name += event.unicode

                elif self.scene == "level_intro" and event.key == pygame.K_RETURN:
                    self.setup_question_scene()

                elif self.scene == "boss_intro" and event.key == pygame.K_RETURN:
                    self.setup_question_scene()

                elif self.scene == "question":
                    self.handle_question_key(event)

                elif self.scene == "level_report":
                    if event.key == pygame.K_RETURN:
                        self.level_report = []
                        if self.pending_next_scene == "boss_intro":
                            self.start_boss_battle()
                        else:
                            self.scene = "level_intro"
                            self.pending_next_scene = None

                elif self.scene == "results":
                    if event.key == pygame.K_r:
                        self.start_game()
                    elif event.key == pygame.K_s:
                        self.save_nutshell_report()
                    elif event.key == pygame.K_ESCAPE:
                        self.scene = "menu"

    def update_monster_state(self):
        if self.monster_effect_timer and pygame.time.get_ticks() > self.monster_effect_timer:
            self.monster_mood = "idle"
            self.monster_effect_timer = 0

    def draw(self):
        self.draw_background()
        if self.scene == "menu":
            self.draw_menu()
        elif self.scene == "level_intro":
            self.draw_level_intro()
        elif self.scene == "boss_intro":
            self.draw_boss_intro()
        elif self.scene == "question":
            self.draw_question_scene()
        elif self.scene == "level_report":
            self.draw_level_report()
        elif self.scene == "results":
            self.draw_results()
        self.draw_message()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update_continuous_movement()
            self.update_timer()
            self.update_message()
            self.update_monster_state()
            self.draw()

        pygame.quit()
        sys.exit()


def main():
    game = EnglishAdventureGame()
    game.run()


if __name__ == "__main__":
    main()
