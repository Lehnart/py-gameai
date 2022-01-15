from engine.esper import World
from engine.systems.collision_rect.components import CollisionRectComponent
from engine.systems.collision_rect.events import RectCollisionEvent
from engine.systems.collision_rect.processors import CollisionRectProcessor
from engine.systems.event.components import EventComponent
from engine.systems.event.processors import EventProcessor
from engine.systems.input.components import InputComponent
from engine.systems.input.processors import InputProcessor
from engine.systems.limit_rect.components import RectLimitComponent
from engine.systems.limit_rect.events import OutOfLimitEvent
from engine.systems.limit_rect.processors import LimitRectProcessor
from engine.systems.rect.components import RectComponent
from engine.systems.rect.processors import RectProcessor
from engine.systems.render.components import WindowComponent
from engine.systems.render.processors import RenderProcessor
from engine.systems.sound.components import SoundComponent
from engine.systems.sound.processors import SoundProcessor
from engine.systems.speed.components import SpeedComponent
from engine.systems.speed.events import MoveEvent
from engine.systems.speed.processors import SpeedProcessor
from engine.systems.sprite.processors import SpriteProcessor
from engine.systems.sprite_rect.components import RectSpriteComponent
from engine.systems.sprite_rect.processors import RectSpriteProcessor
from engine.systems.sprite_text.components import TextSpriteComponent
from engine.systems.sprite_text.processors import TextSpriteProcessor
from py_breakout.callbacks import BounceWallCallback, bounce_paddle
from py_breakout.config import *


class PyBreakout(World):

    def __init__(self):
        super().__init__()
        self._is_running: bool = True

        # Window entity
        window = WindowComponent(WINDOW_SIZE)
        self.create_entity(window)

        # Blocks
        ww, wh = WINDOW_SIZE
        x = 0
        y = BLOCKS_Y0
        for j in range(BLOCKS_N_ROW):
            x = 0
            for i in range(BLOCKS_N_COL):
                rect = RectComponent(x, y, ww / BLOCKS_N_COL * 0.9, BLOCKS_H)
                rect_collide = CollisionRectComponent(pygame.Rect(x, y, ww / BLOCKS_N_COL * 0.9, BLOCKS_H))
                rect_sprite = RectSpriteComponent(pygame.Rect(x, y, ww / BLOCKS_N_COL * 0.9, BLOCKS_H), BLOCK_COLOR_PER_ROW[j])
                bounce_sound = SoundComponent(BLOCK_BOUNCE_SOUND)
                paddle1 = self.create_entity(rect, rect_sprite, rect_collide, bounce_sound)
                x += ww / BLOCKS_N_COL
            y += BLOCKS_H + BLOCKS_H_STEP

        # paddle entity
        rect = RectComponent(*PADDLE_RECT)
        rect_collide = CollisionRectComponent(pygame.Rect(*PADDLE_RECT))
        rect_limit = RectLimitComponent(*WINDOW_LIMITS)
        rect_sprite = RectSpriteComponent(pygame.Rect(*PADDLE_RECT), pygame.Color("white"))
        bounce_sound = SoundComponent(PADDLE_BOUNCE_SOUND)
        paddle1 = self.create_entity(rect, rect_limit, rect_sprite, rect_collide, bounce_sound)

        self.add_component(
            paddle1,
            InputComponent(
                {
                    pygame.K_LEFT: lambda w: w.publish(MoveEvent(paddle1, -w.process_dt * PADDLE_SPEED, 0.)),
                    pygame.K_RIGHT: lambda w: w.publish(MoveEvent(paddle1, +w.process_dt * PADDLE_SPEED, 0.)),
                }
            )
        )

        # score
        left_score_text = TextSpriteComponent("000", SCORE_FONT, pygame.Color("white"), SCORE_LEFT_POS)
        left_score = self.create_entity(left_score_text)

        # ball
        rect = RectComponent(*BALL_RECT)
        rect_collide = CollisionRectComponent(pygame.Rect(*BALL_RECT))
        rect_limit = RectLimitComponent(*WINDOW_LIMITS)
        rect_speed = SpeedComponent(*BALL_SPEED)
        rect_sprite = RectSpriteComponent(pygame.Rect(*BALL_RECT), pygame.Color("white"))
        bounce_sound = SoundComponent(WALL_BOUNCE_SOUND)
        ball = self.create_entity(rect, rect_limit, rect_sprite, rect_speed, rect_collide, bounce_sound)
        self.add_component(
            ball,
            EventComponent(
                {
                    OutOfLimitEvent: BounceWallCallback(ball),
                    RectCollisionEvent: bounce_paddle
                }
            )
        )

        self.add_processor(InputProcessor(), 20)
        self.add_processor(SpeedProcessor(), 19)
        self.add_processor(RectProcessor(), 18)
        self.add_processor(RectSpriteProcessor(), 17)
        self.add_processor(SpriteProcessor(), 16)
        self.add_processor(TextSpriteProcessor(), 15)
        self.add_processor(LimitRectProcessor(), 13)
        self.add_processor(CollisionRectProcessor(), 12)
        self.add_processor(EventProcessor(), 11)
        self.add_processor(RenderProcessor(), 9)
        self.add_processor(SoundProcessor(), 8)

    def is_running(self) -> bool:
        return self._is_running


def run():
    game_world = PyBreakout()
    while game_world.is_running():
        game_world.process()


if __name__ == '__main__':
    run()