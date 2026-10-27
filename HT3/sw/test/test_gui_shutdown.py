import os
import sys
import unittest
from unittest import mock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import gui_worker

class GuiShutdown(unittest.TestCase):
    def make_gui(self):
        gui=gui_worker.gui_cworker.__new__(gui_worker.gui_cworker)
        gui._gui_cworker__threadrun=True
        gui._gui_cworker__main=mock.Mock()
        return gui

    def test_returning_mainloop_is_never_reentered(self):
        gui=self.make_gui()
        # A second call raises instead of hanging if the old busy loop returns.
        gui._gui_cworker__main.mainloop.side_effect=[None, AssertionError('mainloop restarted')]
        with mock.patch.object(gui_worker._thread,'start_new_thread'):
            self.assertFalse(gui.run())
        gui._gui_cworker__main.mainloop.assert_called_once_with()
        self.assertFalse(gui._gui_cworker__threadrun)

    def test_exception_stops_display_worker(self):
        gui=self.make_gui()
        gui._gui_cworker__main.mainloop.side_effect=RuntimeError('display disconnected')
        with mock.patch.object(gui_worker._thread,'start_new_thread'):
            with self.assertRaisesRegex(RuntimeError,'display disconnected'):
                gui.run()
        self.assertFalse(gui._gui_cworker__threadrun)

    def test_close_handler_stops_worker_before_destroy(self):
        gui=self.make_gui()
        gui._gui_cworker__main.destroy.side_effect=lambda: self.assertFalse(gui._gui_cworker__threadrun)
        gui._gui_cworker__ende()
        gui._gui_cworker__main.destroy.assert_called_once_with()
