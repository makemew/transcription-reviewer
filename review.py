import sys
import os
import pandas as pd
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QProgressBar

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QInputDialog
)

from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt

sys.stdout.reconfigure(encoding='utf-8')

CSV_FILE = r"data.csv"
AUDIO_FOLDER = r"adresses"

UUID_COLUMN = "call_uuid"
TEXT_COLUMN = "transcript"

PROGRESS_FILE = "progress.txt"


class ReviewApp(QWidget):

    def __init__(self):
        super().__init__()

        

        self.df = pd.read_excel(
            "data.xlsx",
            header=0
        )

        print(self.df.columns.tolist())

        self.prepare_columns()

        self.current_index = self.load_progress()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0) 

        self.playback_speed = 1.0

        self.player.positionChanged.connect(self.update_audio_progress)
        self.player.durationChanged.connect(self.update_audio_duration)
        
        self.init_ui()

        self.load_record()

    def prepare_columns(self):

        if "status" not in self.df.columns:
            self.df["status"] = ""

        self.save_csv()

    def init_ui(self):

        self.setWindowTitle("Audio Transcription Reviewer")
        self.resize(1200, 700)

        layout = QVBoxLayout()

        self.progress_label = QLabel()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(len(self.df) - 1)
        layout.addWidget(self.progress_bar)

        self.audio_progress = QProgressBar()
        self.audio_progress.setRange(0, 0) 
    
        layout.addWidget(self.audio_progress)

        layout.addWidget(self.progress_label)

        self.uuid_label = QLabel()
        self.uuid_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self.uuid_label)

        self.audio_label = QLabel()
        layout.addWidget(self.audio_label)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        buttons = QHBoxLayout()

        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.clicked.connect(self.previous_record)

        self.play_btn = QPushButton("▶ Open Audio")
        self.play_btn.clicked.connect(self.open_audio)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(lambda: self.set_status("OK"))

        self.fixed_btn = QPushButton("FIXED")
        self.fixed_btn.clicked.connect(lambda: self.set_status("FIXED"))

        self.skip_btn = QPushButton("SKIP")
        self.skip_btn.clicked.connect(lambda: self.set_status("SKIP"))

        self.search_btn = QPushButton("Find UUID")
        self.search_btn.clicked.connect(self.search_uuid)

        buttons.addWidget(self.prev_btn)
        buttons.addWidget(self.play_btn)
        buttons.addWidget(self.ok_btn)
        buttons.addWidget(self.fixed_btn)
        buttons.addWidget(self.skip_btn)
        buttons.addWidget(self.search_btn)

        self.speed_label = QLabel("Speed: 1.0x")

        self.speed_down = QPushButton("-")
        self.speed_up = QPushButton("+")

        self.speed_down.clicked.connect(self.decrease_speed)
        self.speed_up.clicked.connect(self.increase_speed)

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(self.speed_down)
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_up)

        layout.addLayout(speed_layout)

        layout.addLayout(buttons)

        self.setLayout(layout)

        QShortcut(
            QKeySequence(Qt.Key.Key_Return),
            self,
            activated=lambda: self.set_status("OK")
        )

        QShortcut(
            QKeySequence("Ctrl+S"),
            self,
            activated=self.save_current
        )

        QShortcut(
            QKeySequence(Qt.Key.Key_Backspace),
            self,
            activated=self.previous_record
        )

        QShortcut(
            QKeySequence(Qt.Key.Key_Space),
            self,
            activated=self.open_audio
        )

        QShortcut(
            QKeySequence("Ctrl+R"),
            self,
            activated=lambda: self.set_status("OK")
        )

        QShortcut(
            QKeySequence("Ctrl+E"),
            self,
            activated=self.previous_record
        )

    def load_record(self):

        if self.current_index >= len(self.df):

            QMessageBox.information(
                self,
                "Finished",
                "All records reviewed."
            )
            return

        row = self.df.iloc[self.current_index]

        uuid = str(row[UUID_COLUMN])

        text = str(row[TEXT_COLUMN]) \
            if pd.notna(row[TEXT_COLUMN]) else ""

        status = str(row["status"])

        self.progress_label.setText(
            f"Record {self.current_index + 1}/{len(self.df)}"
            f" | Status: {status}"
        )

        self.uuid_label.setText(f"UUID: {uuid}")

        self.text_edit.setPlainText(text)

        audio_path = os.path.join(
            AUDIO_FOLDER,
            f"{uuid}.wav"
        )

        self.audio_label.setText(audio_path)
        self.progress_bar.setValue(self.current_index)

    def save_csv(self):

        self.df.to_csv(
            CSV_FILE,
            index=False,
            encoding="utf-8-sig"
        )

    def save_progress(self):

        with open(PROGRESS_FILE, "w") as f:
            f.write(str(self.current_index))

    def load_progress(self):

        if os.path.exists(PROGRESS_FILE):

            try:
                with open(PROGRESS_FILE) as f:
                    return int(f.read().strip())
            except:
                pass

        pending = self.df[
            self.df["status"].fillna("") == ""
        ]

        if len(pending):
            return pending.index[0]

        return 0

    def save_current(self):

        text = self.text_edit.toPlainText().strip()

        self.df.at[
            self.current_index,
            TEXT_COLUMN
        ] = text

        self.save_csv()

    def set_status(self, status):
        self.save_current()

        self.df.at[self.current_index, "status"] = status
        self.save_csv()

        self.current_index += 1
        self.save_progress()
        
        self.load_record()

        self.open_audio()
        
    def previous_record(self):

        if self.current_index > 0:

            self.save_current()

            self.current_index -= 1

            self.save_progress()

            self.load_record()

            self.open_audio()

    def open_audio(self):
        uuid = str(self.df.iloc[self.current_index][UUID_COLUMN])
        audio_path = os.path.join(AUDIO_FOLDER, f"{uuid}.wav")

        if not os.path.exists(audio_path):
            self.audio_label.setText(f"Файл не найден: {audio_path}")
            return

        self.player.setSource(QUrl.fromLocalFile(audio_path))
        self.player.play()
        self.audio_label.setText(f"Playing: {audio_path}")

    def search_uuid(self):

        uuid, ok = QInputDialog.getText(
            self,
            "Find UUID",
            "UUID:"
        )

        if not ok:
            return

        matches = self.df[
            self.df[UUID_COLUMN].astype(str) == uuid
        ]

        if len(matches) == 0:

            QMessageBox.warning(
                self,
                "Not found",
                uuid
            )

            return

        self.current_index = matches.index[0]

        self.save_progress()

        self.load_record()

    def update_audio_duration(self, duration):
        self.audio_progress.setRange(0, duration)

    def update_audio_progress(self, position):
        self.audio_progress.setValue(position)
    
    def update_audio_duration(self, duration):
        self.audio_progress.setRange(0, duration)

    def apply_speed(self):
        self.player.setPlaybackRate(self.playback_speed)
        self.speed_label.setText(f"Speed: {self.playback_speed:.1f}x")

    def increase_speed(self):
        self.playback_speed = min(3.0, self.playback_speed + 0.1)
        self.apply_speed()

    def decrease_speed(self):
        self.playback_speed = max(0.5, self.playback_speed - 0.1)
        self.apply_speed()
        

app = QApplication(sys.argv)

window = ReviewApp()

window.show()

sys.exit(app.exec())