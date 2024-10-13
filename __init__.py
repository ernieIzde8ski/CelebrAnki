import os
import random
from typing import TYPE_CHECKING, Any, Literal, Union, cast

from anki.sound import AVTag
from aqt import gui_hooks, mw, qconnect
from aqt.sound import AVPlayer, clearAudioQueue, play
from aqt.webview import AnkiWebView, AnkiWebViewKind
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QFileDialog

if TYPE_CHECKING:
    assert mw is not None

addon_path: str = os.path.dirname(__file__)
user_files: str = os.path.join(addon_path, "user_files")
config = cast(dict[str, Any], mw.addonManager.getConfig(__name__))

sound: Union[str, list[str], Literal[0]] = config["sound"]
sound_files: list[str]

if sound and isinstance(sound, list):
    sound_files = config["sound"]
elif sound:  # `sound` must be a string
    sound_files = [config["sound"]]
    setting = {"sound": sound_files}
    mw.addonManager.writeConfig(__name__, setting)
else:
    sound_files = [os.path.join(user_files, "nyt.mp3")]
    setting = {"sound": sound_files}
    mw.addonManager.writeConfig(__name__, setting)


def play_sound(webview: AnkiWebView):
    if webview.kind != AnkiWebViewKind.MAIN:
        return
    clearAudioQueue()
    sound_file = random.choice(sound_files)
    mw.progress.single_shot(1, lambda: play(sound_file), False)


gui_hooks.webview_did_inject_style_into_page.append(play_sound)


def _play_tags(self: AVPlayer, tags: list[AVTag]):
    self._enqueued = tags[:]
    self._play_next_if_idle()


AVPlayer.play_tags = _play_tags


def update_sound():
    global sound_files, config
    (file_names, _) = QFileDialog.getOpenFileNames(
        mw, "Change sound", user_files, "Sound Files (*.wav *.mp3 *.mp4)"
    )
    file_names.sort()
    if file_names != sound_files:
        sound_files = file_names
        setting = {"sound": sound_files}
        mw.addonManager.writeConfig(__name__, setting)
        gui_hooks.webview_did_inject_style_into_page.remove(play_sound)
        gui_hooks.webview_did_inject_style_into_page.append(play_sound)


action = QAction("Change completion jingle")
qconnect(action.triggered, update_sound)
mw.form.menuTools.addAction(action)
