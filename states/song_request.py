from aiogram.fsm.state import State, StatesGroup


class SongRequest(StatesGroup):
    waiting_for_song = State()


class FeedbackState(StatesGroup):
    waiting_for_feedback = State()