import logging
import os
import time
from enum import Enum

import cv2
import numpy as np
from PyQt6.QtCore import *

from mainDir.inputDevice.systemWidget.inputDevice_stingerPlayer import InputDevice_StingerAnimation


class MIX_TYPE(Enum):
    FADE = 0
    WIPE_LEFT_TO_RIGHT = 1
    WIPE_RIGHT_TO_LEFT = 2
    WIPE_TOP_TO_BOTTOM = 3
    WIPE_BOTTOM_TO_TOP = 4
    WIPE_STINGER = 5
    FADE_STILL = 6


class MixBus017_NoThread(QObject):
    _fade = 0
    fadeTime = 100
    _wipe = 0
    _wipeTime = 90
    effectType = MIX_TYPE.FADE
    stingerObject = None
    isStingerLoaded = {}
    isStillLoaded = {}
    stills = {}

    _wipe_position_leftToRight_list = []
    _wipe_position_rightToLeft_list = []
    _wipe_position_topToBottom_list = []
    _wipe_position_bottomToTop_list = []
    _wipe_position_stinger_list = []

    def __init__(self, videoHub, parent=None):
        super().__init__(parent)
        self.videoHub = videoHub
        self.previewInput = self.videoHub.getInputDevice(1)
        self.programInput = self.videoHub.getInputDevice(2)
        self.autoMix_timer = QTimer(self)
        self.autoMix_timer.timeout.connect(self._fader)
        self._init_wipe_positions()
        # Variabili per il calcolo del frame rate
        self.total_frames = 0
        self.total_time = 0
        self.start_time = time.time()
        self.last_fps = 0
        self.actualPreviewIndex = 1
        self.actualProgramIndex = 2
        self._wipe_position_leftToRight_list = np.linspace(0, 1920, self._wipeTime)
        self._wipe_position_rightToLeft_list = np.linspace(1920, 0, self._wipeTime)
        self._wipe_position_topToBottom_list = np.linspace(0, 1080, self._wipeTime)
        self._wipe_position_bottomToTop_list = np.linspace(1080, 0, self._wipeTime)
        self._wipe_position_stinger_list = np.linspace(0, 1920, self._wipeTime)


    def _init_wipe_positions(self):
        """
        This function initializes the wipe positions based on the wipe time.
        :return:
        """
        _wipe_step = max(1, self._wipeTime)
        self._wipe_position_leftToRight_list = np.linspace(0, 1920, _wipe_step)
        self._wipe_position_rightToLeft_list = np.linspace(1920, 0, _wipe_step)
        self._wipe_position_topToBottom_list = np.linspace(0, 1080, _wipe_step)
        self._wipe_position_bottomToTop_list = np.linspace(1080, 0, _wipe_step)
        self._wipe_position_stinger_list = []

    def setEffectType(self, effectType):
        """
        This function sets the effect type.
        :param effectType:
        :return:
        """
        self.effectType = effectType
        self._fade = 0
        self._wipe = 0
        self.autoMix_timer.stop()
        self._init_wipe_positions()

    def getMixed(self):
        """
        This function returns the mixed frame based on the effect type.
        """
        self.previewInput.captureFrame()
        self.programInput.captureFrame()
        prw_frame = self.previewInput.getFrame()
        prg_frame = self.programInput.getFrame()

        # Update frame rate calculation
        self.total_frames += 1
        self.total_time += time.time() - self.start_time
        self.start_time = time.time()

        # Calculate FPS
        if self.total_time > 0:
            self.last_fps = self.total_frames / self.total_time

        if self._fade == 0:
            return prw_frame, prg_frame
        else:
            if self.effectType == MIX_TYPE.FADE:
                return prw_frame, cv2.addWeighted(prw_frame, self._fade, prg_frame, 1 - self._fade, 0)
            elif self.effectType == MIX_TYPE.WIPE_LEFT_TO_RIGHT:
                return prw_frame, self.wipeLeftToRight(prw_frame, prg_frame)
            elif self.effectType == MIX_TYPE.WIPE_RIGHT_TO_LEFT:
                return prw_frame, self.wipeRightToLeft(prw_frame, prg_frame)
            elif self.effectType == MIX_TYPE.WIPE_TOP_TO_BOTTOM:
                return prw_frame, self.wipeTopToBottom(prw_frame, prg_frame)
            elif self.effectType == MIX_TYPE.WIPE_BOTTOM_TO_TOP:
                return prw_frame, self.wipeBottomToTop(prw_frame, prg_frame)
            elif self.effectType == MIX_TYPE.WIPE_STINGER:
                print(f"doing Stinger: _wipe: {self._wipe}")
                if self.stingerObject:
                    return prw_frame, self.stinger(prw_frame, prg_frame)
                else:
                    return prw_frame, prg_frame
            elif self.effectType == MIX_TYPE.FADE_STILL and self.isStillLoaded:
                return prw_frame, cv2.addWeighted(self.still.getFrame(), self._fade, prg_frame, 1 - self._fade, 0)

    def getFps(self):
        """
        Return the current FPS during mixing.
        """
        return self.last_fps

    def setFade(self, value: int):
        """
        This function sets the fade value. It also maps the slider value (0-100)
        to the appropriate index for the wipe or stinger effect.
        :param value: Value from the slider (0-100)
        :return:
        """
        if value == 0:
            self._fade = 0
        else:
            self._fade = value / 100

            if self.effectType == MIX_TYPE.WIPE_LEFT_TO_RIGHT:
                self._wipe = self.map_value(value, 0, 100, 0, len(self._wipe_position_leftToRight_list) - 1)
            elif self.effectType == MIX_TYPE.WIPE_RIGHT_TO_LEFT:
                self._wipe = self.map_value(value, 0, 100, 0, len(self._wipe_position_rightToLeft_list) - 1)
            elif self.effectType == MIX_TYPE.WIPE_TOP_TO_BOTTOM:
                self._wipe = self.map_value(value, 0, 100, 0, len(self._wipe_position_topToBottom_list) - 1)
            elif self.effectType == MIX_TYPE.WIPE_BOTTOM_TO_TOP:
                self._wipe = self.map_value(value, 0, 100, 0, len(self._wipe_position_bottomToTop_list) - 1)
            elif self.effectType == MIX_TYPE.WIPE_STINGER:
                if self.stingerObject:
                    self._wipe = self.map_value(value, 0, 100, 0, self.stingerObject.getLength())
                else:
                    print(f"WARNING FROM MIXBUS: Stinger object is None.")
                    self._wipe = 0


    @staticmethod
    def map_value(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def cut(self):
        """
        This function swaps the preview and program inputs.
        :return:
        """
        self._fade = 0
        self._wipe = 0
        self.previewInput, self.programInput = self.programInput, self.previewInput

    def autoMix(self):
        """
        This function starts the timer that will update the fade value.
        :return:
        """
        print(f"AutoMix started.")
        self.autoMix_timer.start(1000 // 60)

    def _fader(self):
        """
        Handles fade and transition effects over time.
        """
        if self.effectType == MIX_TYPE.FADE:
            self._fade += 0.01
            if self._fade >= 1:
                self.autoMix_timer.stop()
                self.cut()
        elif self.effectType in [MIX_TYPE.WIPE_LEFT_TO_RIGHT, MIX_TYPE.WIPE_RIGHT_TO_LEFT,
                                 MIX_TYPE.WIPE_TOP_TO_BOTTOM, MIX_TYPE.WIPE_BOTTOM_TO_TOP]:
            self._wipe += 1
            self._fade += 0.01
            if self._wipe >= len(self._wipe_position_leftToRight_list) - 1:
                self.autoMix_timer.stop()
                self.cut()
        elif self.effectType == MIX_TYPE.WIPE_STINGER:
            self._wipe += 1
            self._fade += 0.01
            print(f"_fader: Stinger position: {self._wipe}")
            if self.stingerObject:
                if self._wipe >= self.stingerObject.getLength() - 1:
                    print(f"Stinger: Stinger position: {self._wipe} - {self.stingerObject.getLength()}")
                    self.autoMix_timer.stop()
                    self.cut()
            else:
                print(f"WARNING FROM MIXBUS: Stinger object is None.")
                self.autoMix_timer.stop()
                self.cut()
        elif self.effectType == MIX_TYPE.FADE_STILL:
            self._fade += 0.01
            if self._fade >= 1:
                self.autoMix_timer.stop()
        else:
            raise ValueError(f"Unknown effect type: {self.effectType}")

    def wipeLeftToRight(self, preview_frame, program_frame):
        """
            This function creates a wipe effect from left to right.
            I talk about how to create a wipe effect in the 4.2 - Wipe Left To Right
            you can find it at:
            https://github.com/AlessioMichelassi/openPyVision_013/wiki/Chapter-4
        :param preview_frame: the preview frame from input 1
        :param program_frame: the program frame from input 2
        :return: the frame with the wipe effect
        """
        wipe_position = int(self._wipe_position_leftToRight_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[:, :wipe_position] = preview_frame[:, :wipe_position]
        return wipe_frame

    def wipeRightToLeft(self, preview_frame, program_frame):
        """
            This function creates a wipe effect from left to right.
            I talk about how to create a wipe effect in the 4.3 - Wipe Right To Left
            you can find it at:
            https://github.com/AlessioMichelassi/openPyVision_013/wiki/Chapter-4
        :param preview_frame: the preview frame from input 1
        :param program_frame: the program frame from input 2
        :return: the frame with the wipe effect
        """
        wipe_position = int(self._wipe_position_rightToLeft_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[:, wipe_position:] = preview_frame[:, wipe_position:]
        return wipe_frame

    def wipeTopToBottom(self, preview_frame, program_frame):
        """
            This function creates a wipe effect from left to right.
            I talk about how to create a wipe effect in the 4.4 - Wipe Up And Down
            you can find it at:
            https://github.com/AlessioMichelassi/openPyVision_013/wiki/Chapter-4
        :param preview_frame: the preview frame from input 1
        :param program_frame: the program frame from input 2
        :return: the frame with the wipe effect
        """
        wipe_position = int(self._wipe_position_topToBottom_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[:wipe_position, :] = preview_frame[:wipe_position, :]
        return wipe_frame

    def wipeBottomToTop(self, preview_frame, program_frame):
        """
            This function creates a wipe effect from left to right.
            I talk about how to create a wipe effect in the 4.4 - Wipe Up And Down
            you can find it at:
            https://github.com/AlessioMichelassi/openPyVision_013/wiki/Chapter-4
        :param preview_frame: the preview frame from input 1
        :param program_frame: the program frame from input 2
        :return: the frame with the wipe effect
        """
        wipe_position = int(self._wipe_position_bottomToTop_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[wipe_position:, :] = preview_frame[wipe_position:, :]
        return wipe_frame

    def stinger(self, preview_frame, program_frame):
        """
            This function creates a stinger effect.
            I talk about how to create a stinger effect in the 4.5 - Stinger
            you can find it at:

            """
        print(f"stinger: Stinger position: {self._wipe}")
        self.stingerObject.setIndex(self._wipe)
        preMult, inv_mask = self.stingerObject.getFrames()

        if self._wipe < self.stingerObject.getLength() // 2:
            program_masked = cv2.multiply(program_frame, inv_mask, dtype=cv2.CV_8U)
            result = cv2.add(preMult, program_masked)
            return np.ascontiguousarray(result)
        else:
            preview_masked = cv2.multiply(preview_frame, inv_mask, dtype=cv2.CV_8U)
            result = cv2.add(preMult, preview_masked)
            return np.ascontiguousarray(result)

    def parseTallySignal(self, tally_data):
        """
        Update MixBus state based on data received from the TallyManager.

        :param tally_data: Dictionary containing tally commands and data.
        """
        print(f"MixBus received tally data: {tally_data}")
        logging.debug(f"MixBus received tally data: {tally_data}")
        tally_data['sender'] = 'mixBus'
        cmd = tally_data.get('cmd')
        if cmd == 'cut':
            self.cut()
        elif cmd == 'auto':
            logging.info(f"AutoMix command received.")
            self.autoMix()
        elif cmd == 'faderChange':
            fade_value = int(float(tally_data.get('fade', 0)) * 100)
            self.setFade(fade_value)
        elif cmd == 'effectChange':
            effect = tally_data.get('effect')
            effect_enum = getattr(MIX_TYPE, effect.replace(" ", "_").upper(), MIX_TYPE.FADE)
            print(f"Effect {effect} changed to {effect_enum}")
            self.setEffectType(effect_enum)
            logging.info(f"Effect changed to {effect_enum}")
        elif cmd == 'previewChange':
            logging.info(f"Preview input change to {tally_data['preview']}")
            self.actualPreviewIndex = int(tally_data['preview'])
            new_preview_input = self.videoHub.getInputDevice(self.actualPreviewIndex)
            self.previewInput = new_preview_input
        elif cmd == 'programChange':
            logging.info(f"Program input change to {tally_data['program']}")
            self.actualProgramIndex = int(tally_data['program'])
            new_program_input = self.videoHub.getInputDevice(self.actualProgramIndex)
            self.programInput = new_program_input
        elif cmd == 'inputChanged':
            position = int(tally_data.get('position'))
            if position == self.actualPreviewIndex:
                self.previewInput = self.videoHub.getInputDevice(position)
            elif position == self.actualProgramIndex:
                self.programInput = self.videoHub.getInputDevice(position)
        elif cmd == 'stingerReady':
            print("*** FROM MIX BUS: Stinger ready.")
            print(f"Stinger ready at position {tally_data['position']}")
            logging.info(f"Stinger ready at position {tally_data['position']}")
            position = tally_data.get('position')
            self.stingerObject = self.videoHub.getStingerPlayer(position)
            if self.stingerObject:
                print(f"Stinger object at position {position} is not None.")
                print(f"Stinger object at position {position}: {self.stingerObject}")
                print(f"Stinger lenght: {self.stingerObject.getLength()}")
            else:
                raise ValueError(f"Stinger object at position {position} is None.")
        elif cmd == 'stillImageReady':
            position = tally_data.get('position')
            stillImage = self.videoHub.getStillImage(position)
            if stillImage:
                self.setStill(position, stillImage)
                self.isStillLoaded[position] = True
        else:
            logging.warning(f"Unknown command received in getTally: {cmd}")


