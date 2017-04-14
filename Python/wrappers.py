import re
import time
from main import window

class Wrapper(object):

    def __init__(self, subprocess):
        self._subprocess = subprocess

    def call(self, cmd):
        p = self._subprocess.Popen(cmd, shell=True, stdout=self._subprocess.PIPE,
            stderr=self._subprocess.PIPE)
        out, err = p.communicate()
        return p.returncode, out.rstrip(), err.rstrip()

class NetworkInfo(Wrapper):

    def __init__(self, subprocess):
        Wrapper.__init__(self, subprocess)

    def network_status(self):
        iwcode, iwconfig, err = self.call("iwconfig")
        wlcode, wlan, err = self.call("ifconfig wlan0")
        etcode, eth, err = self.call("ifconfig eth0")
        ssid = None
        wip = None
        eip = None
        if iwcode == 0 and 'ESSID' in iwconfig:
            ssid = re.findall('ESSID:"([^"]*)', iwconfig)[0]
        if wlcode == 0 and 'inet addr' in wlan:
            wip = re.findall('inet addr:([^ ]*)', wlan)[0]
        if etcode == 0 and 'inet addr' in eth:
            eip = re.findall('inet addr:([^ ]*)', eth)[0]
        ret = ''
        if ssid:
            ret = ssid
        if wip:
            ret = ret + '\n' + wip
        elif eip:
            ret = ret + eip
        if not ssid and not wip and not eip:
            ret = 'No Network'
        return ret


class Identify(Wrapper):
    """ A class which wraps calls to the external identify process. """

    def __init__(self, subprocess):
        Wrapper.__init__(self, subprocess)
        self._CMD = 'identify'

    def summary(self, filepath):
        code, out, err = self.call(self._CMD + " " + filepath)
        if code != 0:
            raise Exception(err)
        return out

    def mean_brightness(self, filepath):
        code, out, err = self.call(self._CMD + ' -format "%[mean]" ' + filepath)
        if code != 0:
            raise Exception(err)
        return out

class GPhoto(Wrapper):
    """ A class which wraps calls to the external gphoto2 process. """

    def __init__(self, subprocess):
        Wrapper.__init__(self, subprocess)
        self._CMD = 'gphoto2'
        self._shutter_choices = None
        self._iso_choices = None
        self.camera_detected = True

    def detect_camera(self):
        code, out, err = self.call(self._CMD + " --set-config /main/settings/capturetarget=1")
        if code != 0:
            window.no_camera()
        else:
            window.camera_detected = True
            print("CAMERA INITIALIZED")
            print("***********" + str(window.camera_detected) + "**********************")

    def set_capture_target(self):
        code, out, err = self.call(self._CMD + " --set-config /main/settings/capturetarget=1")
        if code != 0:
            # window.no_camera()
            return False
        print("CAMERA INITIALIZED")
        return True

    def get_camera_date_time(self):
        code, out, err = self.call(self._CMD + " --get-config /main/status/datetime")
        if code != 0:
            window.no_camera()
        timestr = None
        for line in out.split('\n'):
            if line.startswith('Current:'):
                timestr = line[line.find(':'):]
        if not timestr:
            raise Exception('No time parsed from ' + out)
        stime = time.strptime(timestr, ": %Y-%m-%d %H:%M:%S")
        return stime


    def capture_image_and_download(self):
        code, out, err = self.call(self._CMD + " --capture-image-and-download")
        if code != 0:
            window.no_camera()
        filename = None
        out = out.decode("utf-8")
        for line in out.split('\n'):
            if line.startswith('Saving file as '):
                filename = line.split('Saving file as ')[1]
        return filename


    


    def capture_image(self):
        print("********************")
        code, out, err = self.call(self._CMD + " --capture-image")
        if code != 0:
            if self.camera_detected:
                window.show_popup()
                self.camera_detected = False
        else:
            print("CAPTUREING")


    def focus_trigger(self):
        code, out, err = self.call(self._CMD + " --capture-image")
        if code != 0:
            window.no_camera()
        


    def trigger(self):
        code, out, err = self.call(self._CMD + " --set-config /main/actions/eosremoterelease=2")
        code, out, err = self.call(self._CMD + " --set-config /main/actions/eosremoterelease=4")
        if code != 0:
            window.no_camera()
        # out = out.decode("utf-8")


    def bulb_trigger(self, shutter_time):
        code, out, err = self.call(self._CMD + " --set-config /main/actions/eosremoterelease=5")
        if code != 0:
            window.no_camera()
        time.sleep(shutter_time)
        code, out, err = self.call(self._CMD + " --set-config /main/actions/eosremoterelease=4")
        if code != 0:
            window.no_camera()
        

    def get_shutter_speeds(self):
        code, out, err = self.call([self._CMD + " --get-config /main/capturesettings/shutterspeed"])
        if code != 0:
            window.no_camera()
        choices = {}
        current = None
        out = out.decode("utf-8")
        for line in out.split('\n'):
            if line.startswith('Choice:'):
                choices[line.split(' ')[2]] = line.split(' ')[1]
            if line.startswith('Current:'):
                current = line.split(' ')[1]
        self._shutter_choices = choices
        return current, choices

    def set_shutter_speed(self, secs=None, index=None):
        code, out, err = None, None, None
        if secs:
            if self._shutter_choices == None:
                self.get_shutter_speeds()
            code, out, err = self.call([self._CMD + " --set-config /main/capturesettings/shutterspeed=" + str(self._shutter_choices[secs])])
        if index:
            code, out, err = self.call([self._CMD + " --set-config /main/capturesettings/shutterspeed=" + str(index)])

    def get_isos(self):
        code, out, err = self.call([self._CMD + " --get-config /main/imgsettings/iso"])
        if code != 0:
            window.no_camera()
        choices = {}
        current = None
        out = out.decode("utf-8")
        for line in out.split('\n'):
            if line.startswith('Choice:'):
                choices[line.split(' ')[2]] = line.split(' ')[1]
            if line.startswith('Current:'):
                current = line.split(' ')[1]
        self._iso_choices = choices
        return current, choices

    def set_iso(self, iso=None, index=None):
        code, out, err = None, None, None
        if iso:
            if self._iso_choices == None:
                self.get_isos()
            code, out, err = self.call([self._CMD + " --set-config /main/imgsettings/iso=" + str(self._iso_choices[iso])])
        if index:
            code, out, err = self.call([self._CMD + " --set-config /main/imgsettings/iso=" + str(index)])
