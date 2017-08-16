'''
constant definitions for gui
'''

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen, QBrush


AbilityLabelStyle = (
    "background-color: rgb(61, 61, 61, 240); border-style: outset; "
    "border-color: rgb(61, 61, 61, 240); border-top-left-radius: "
    "10px; border-bottom-left-radius: 10px; font: bold 14px; "
    "text-align: right; color: rgb(218, 218, 218, 240);"
)
AbilityButtonCommonStyle = (
    "border-top-right-radius:10px; border-bottom-right-radius: 10px; "
    "font: bold 14px; border-width: 2px; border-style: outset; "
    "border-color: rgb(61, 61, 61, 240); color: rgb(61, 61, 61, 240);"
)
AbilityButtonDisabledStyle = "background-color: rgb(156, 156, 156, 255);"
AbilityButtonEnabledStyleList = [
    "background-color: rgb(108, 240, 236, 255);",
    "background-color: rgb(152, 240, 108, 255);",
    "background-color: rgb(240, 108, 108, 255);",
    "background-color: rgb(240, 217, 108, 255);",
    "background-color: rgb(108, 150, 240, 255);",
    "background-color: rgb(154, 108, 240, 255);",
    "background-color: rgb(236, 108, 240, 255);",
    "background-color: rgb(238, 182, 143, 255);",
]
AbilityYDelta = 24
AbilityHeight = 21
AbilityLabelWidth = 150
AbilityButtonWidth = 30

FrameColor = QColor(85, 85, 85)
FrameWidth = 3
FramePen = QPen()
FramePen.setWidth(FrameWidth)
FramePen.setColor(FrameColor)

BulletColor = QColor(241, 78, 84)
BulletBrush = QBrush(BulletColor, Qt.SolidPattern)

HeroColor = QColor(0, 178, 255)
HeroBrush = QBrush(HeroColor, Qt.SolidPattern)
HeroBarrelColor = QColor(153, 153, 153)
HeroBarrelBrush = QBrush(HeroBarrelColor, Qt.SolidPattern)

PolygonColors = {
    3: QColor(252, 118, 119),
    4: QColor(255, 232, 105),
    5: QColor(118, 141, 252),
}
PolygonBrushes = {
    e: QBrush(color, Qt.SolidPattern)
    for (e, color)
    in PolygonColors.items()
}

HealthBarBackgroundColor = FrameColor
HealthBarBackgroundBrush = QBrush(HealthBarBackgroundColor)
HealthBarForegroundColor = QColor(134, 198, 128)
HealthBarForegroundBrush = QBrush(HealthBarForegroundColor)

HeroNameColor = QColor(24, 24, 24)
HeroNamePen = QPen()
HeroNamePen.setColor(HeroNameColor)
HeroNamePen.setWidth(3)
