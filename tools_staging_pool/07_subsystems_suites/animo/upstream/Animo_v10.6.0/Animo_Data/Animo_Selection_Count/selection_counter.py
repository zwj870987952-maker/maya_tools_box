import maya.cmds as cmds

try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui


class SelectionCounter(QtWidgets.QLabel):
    
    def __init__(self, parent=None):
        super().__init__("0", parent)
        
        self.selection_job = None
        self._base_size = 32
        self._base_height = 22
        self._base_font_size = 12
        
        # Animation for idle state
        self._idle_animation = None
        self._opacity_effect = None
        
        self.setAlignment(QtCore.Qt.AlignCenter)
        self._apply_style(0)
        
        # Setup idle animation
        self._setup_idle_animation()
        
        self.start_selection_job()
    
    def set_scaled_size(self, scale_func):
        width = scale_func(self._base_size)
        height = scale_func(self._base_height)
        self.setFixedSize(width, height)
    
    def _setup_idle_animation(self):
        """Setup pulsing animation for idle state (0 selection)"""
        # Create opacity effect
        self._opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)
        
        # Create animation group for idle (0 selection) - more noticeable
        self._idle_animation = QtCore.QSequentialAnimationGroup(self)
        
        anim1 = QtCore.QPropertyAnimation(self._opacity_effect, b"opacity")
        anim1.setDuration(1000)  # 1 second
        anim1.setStartValue(1.0)
        anim1.setEndValue(0.4)  # Fade to 40%
        anim1.setEasingCurve(QtCore.QEasingCurve.InOutSine)
        
        anim2 = QtCore.QPropertyAnimation(self._opacity_effect, b"opacity")
        anim2.setDuration(1000)  # 1 second
        anim2.setStartValue(0.4)
        anim2.setEndValue(1.0)
        anim2.setEasingCurve(QtCore.QEasingCurve.InOutSine)
        
        self._idle_animation.addAnimation(anim1)
        self._idle_animation.addAnimation(anim2)
        self._idle_animation.setLoopCount(-1)
    
    def _start_idle_animation(self):
        """Start the idle pulsing animation (0 selection)"""
        if self._idle_animation and self._idle_animation.state() != QtCore.QAbstractAnimation.Running:
            self._idle_animation.start()
    
    def _stop_idle_animation(self):
        """Stop the idle animation"""
        if self._idle_animation:
            self._idle_animation.stop()
        if self._opacity_effect:
            self._opacity_effect.setOpacity(1.0)
    
    def _apply_style(self, count):
        if count == 0:
            bg_color = "#444"
            text_color = "#999"
            # Start pulsing when nothing selected
            self._start_idle_animation()
        elif count <= 20:
            bg_color = "#4a3a5c"
            text_color = "#fff"
            # Stop animation when selected
            self._stop_idle_animation()
        elif count <= 50:
            bg_color = "#4d3a4d"
            text_color = "#ddd"
            self._stop_idle_animation()
        else:
            bg_color = "#4d3a4f"
            text_color = "#eee"
            self._stop_idle_animation()
        
        self.setStyleSheet("""
            QLabel {{
                background-color: {0};
                color: {1};
                border-radius: 3px;
                font-size: {2}px;
                font-weight: bold;
            }}
        """.format(bg_color, text_color, self._base_font_size))
    
    def start_selection_job(self):
        self.stop_selection_job()
        try:
            self.selection_job = cmds.scriptJob(event=["SelectionChanged", self.update_count])
        except:
            pass
    
    def stop_selection_job(self):
        try:
            if self.selection_job and cmds.scriptJob(exists=self.selection_job):
                cmds.scriptJob(kill=self.selection_job, force=True)
                self.selection_job = None
        except:
            pass
    
    def update_count(self):
        try:
            selected = cmds.ls(selection=True)
            count = len(selected) if selected else 0
            self.setText(str(count))
            self._apply_style(count)
        except:
            self.setText("?")
    
    def showEvent(self, event):
        QtWidgets.QLabel.showEvent(self, event)
        self.update_count()
        self.start_selection_job()
    
    def hideEvent(self, event):
        QtWidgets.QLabel.hideEvent(self, event)
        self.stop_selection_job()
        self._stop_idle_animation()
    
    def __del__(self):
        self.stop_selection_job()
